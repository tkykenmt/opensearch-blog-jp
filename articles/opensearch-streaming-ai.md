---
title: "[翻訳] OpenSearch における AI モデルとエージェントのリアルタイムストリーミング機能の紹介"
emoji: "🔄"
type: "tech"
topics: ["opensearch"]
published: false
publication_name: "opensearch"
published_at: 2025-11-18
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/introducing-real-time-streaming-for-ai-models-and-agents-in-opensearch/

今日のペースの速いデジタル世界では、待つことは選択肢ではありません。特に AI を活用したアプリケーションにおいてはなおさらです。ストリーミング技術は、この課題に対する重要なソリューションとして登場し、システムがレスポンスを提供する方法を根本的に変えています。完全な出力を表示する前に待つのではなく、ストリーミングは段階的なデータ配信を可能にし、利用可能になった情報をチャンクで送信します。このアプローチは、モデル予測やエージェント実行などの AI 操作において特に価値があります。これらの操作では、レスポンスが長くなる可能性があり、生成時間が予測できないためです。

OpenSearch は現在、ストリーミング機能をサポートしており、リアルタイムデータ処理と継続的なクエリ実行を可能にしています。OpenSearch 3.3 から実験的機能として利用可能な Predict Stream API と Execute Stream Agent API がこの機能を提供し、非ストリーミング版と同じコア機能を提供しながら、レスポンスを段階的に配信します。この新機能により、ライブデータストリームを効率的に処理でき、バッチではなく到着時にデータを処理および分析することが可能になります。これにより、リモートモデル予測や、マルチステップ実行プロセスの可視性が必要な複雑なエージェントワークフローなどのアプリケーションに最適です。

## 前提条件

ストリーミングを使用する前に、以下の前提条件を満たしていることを確認してください。

### 1. 必要なプラグインのインストール

ストリーミング機能は以下のプラグインに依存しています。これらは OpenSearch ディストリビューションに含まれていますが、明示的にインストールする必要があります。

```bash
bin/opensearch-plugin install transport-reactor-netty4
bin/opensearch-plugin install arrow-flight-rpc
```

詳細については、[プラグインのインストール](https://docs.opensearch.org/latest/install-and-configure/plugins/) を参照してください。

### 2. OpenSearch 設定の構成

`opensearch.yml` ファイルまたは Docker Compose 設定に以下の設定を追加します。

```yaml
opensearch.experimental.feature.transport.stream.enabled: true

# セキュリティ設定に基づいて選択
http.type: reactor-netty4        # セキュリティ無効
http.type: reactor-netty4-secure # セキュリティ有効

# マルチノードクラスタ設定 (該当する場合)
# opensearch.yml には network.host IP、Docker にはノード名を使用
arrow.flight.publish_host: <ip>
arrow.flight.bind_host: <ip>

# セキュリティ有効クラスタ設定 (該当する場合)
transport.stream.type.default: FLIGHT-SECURE
flight.ssl.enable: true
transport.ssl.enforce_hostname_verification: false
```

セキュリティデモ証明書を使用している場合は、`opensearch.yml` ファイルで `plugins.security.ssl.transport.enforce_hostname_verification: false` を `transport.ssl.enforce_hostname_verification: false` に変更してください。

実験的機能の有効化の詳細については、[実験的機能フラグ](https://docs.opensearch.org/latest/install-and-configure/configuring-opensearch/experimental/) を参照してください。

### 3. JVM オプションの設定

`jvm.options` ファイルに以下の設定を追加します。

```
-Dio.netty.allocator.numDirectArenas=1
-Dio.netty.noUnsafe=false
-Dio.netty.tryUnsafe=true
-Dio.netty.tryReflectionSetAccessible=true
--add-opens=java.base/java.nio=org.apache.arrow.memory.core,ALL-UNNAMED
```

### 4. ストリーミング機能フラグの有効化

この機能は OpenSearch 3.3 ではまだ実験的であるため、ストリーミング API を使用する前にストリーミング機能フラグを有効にする必要があります。

ストリーミングを有効にするには、以下のコマンドを実行します。

```json
PUT /_cluster/settings
{
    "persistent": {
        "plugins.ml_commons.stream_enabled": true
    }
}
```

## はじめに

すべての前提条件を完了したら、以下の手順に従って OpenSearch でストリーミングを実装します。

### ステップ 1: モデル予測ストリーミングのセットアップ

#### 1. 互換性のある外部ホストモデルの登録

現在、ストリーミング機能は以下のモデルプロバイダーでサポートされています。

- [OpenAI Chat Completion](https://platform.openai.com/docs/api-reference/completions)
- [Amazon Bedrock Converse Stream](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_ConverseStream.html)

このチュートリアルでは、Amazon Bedrock Converse Stream モデルを使用した登録プロセスを示します。

Amazon Bedrock Converse Stream モデルを登録するには、以下のリクエストを送信します。

```json
POST /_plugins/_ml/models/_register
{
    "name": "Bedrock converse stream",
    "function_name": "remote",
    "description": "bedrock claude model",
    "connector": {
        "name": "Amazon Bedrock Converse",
        "description": "Test connector for Amazon Bedrock Converse",
        "version": 1,
        "protocol": "aws_sigv4",
        "credential": {
            "access_key": "{{access_key}}",
            "secret_key": "{{secret_key}}",
            "session_token": "{{session_token}}"
        },
        "parameters": {
            "region": "{{aws_region}}",
            "service_name": "bedrock",
            "response_filter": "$.output.message.content[0].text",
            "model": "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
        },
        "actions": [{
            "action_type": "predict",
            "method": "POST",
            "headers": {
                "content-type": "application/json"
            },
            "url": "https://bedrock-runtime.${parameters.region}.amazonaws.com/model/${parameters.model}/converse",
            "request_body": "{\"messages\":[{\"role\":\"user\",\"content\":[{\"type\":\"text\",\"text\":\"${parameters.inputs}\"}]}]}"
        }]
    }
}
```

#### 2. Predict Stream API の実行

Predict Stream API を実行するには、モデルタイプに対応する `_llm_interface` パラメータを含める必要があります。

- OpenAI Chat Completion: `openai/v1/chat/completions`
- Amazon Bedrock Converse Stream: `bedrock/converse/claude`

Predict Stream API を実行するには、以下のリクエストを送信します。

```json
POST /_plugins/_ml/models/yFT0m5kB-SbOBOkMDNIa/_predict/stream
{
  "parameters": {
    "inputs": "Can you summarize Prince Hamlet of William Shakespeare in around 100 words?",
    "_llm_interface": "bedrock/converse/claude"
  }
}
```

#### サンプルレスポンス

ストリーミング形式は Server-Sent Events (SSE) を使用し、各チャンクにはモデルのレスポンスの一部が含まれます。各データ行は、モデルが出力を生成する際にリアルタイムで送信される個別のチャンクを表します。

各チャンクには以下の主要な要素があります。

- `content` — このチャンクで生成されたテキストフラグメント (例: 単語やフレーズ)
- `is_last` — これが最後のチャンクかどうかを示すブール値フラグ (中間チャンクの場合は `false`、最後のチャンクの場合は `true`)

### ステップ 2: エージェントストリーミングのセットアップ

注: Execute Stream Agent API は現在、**会話型エージェント**のみをサポートしています。他のエージェントタイプは現時点ではストリーミングと互換性がありません。

#### 1. 互換性のある外部ホストモデルの登録

現在、ストリーミング機能は以下のモデルプロバイダーでサポートされています。

- [OpenAI Chat Completion](https://platform.openai.com/docs/api-reference/completions)
- [Amazon Bedrock Converse Stream](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_ConverseStream.html)

このチュートリアルでは、Amazon Bedrock Converse Stream モデルを使用した登録プロセスを示します。エージェント実行コネクタに使用される `request_body` パラメータは、モデル予測コネクタで使用されるものとは異なることに注意してください。

Amazon Bedrock Converse Stream モデルを登録するには、以下のリクエストを送信します。

```json
POST /_plugins/_ml/models/_register
{
    "name": "Bedrock converse stream",
    "function_name": "remote",
    "description": "bedrock claude model",
    "connector": {
        "name": "Amazon Bedrock Converse",
        "description": "Test connector for Amazon Bedrock Converse",
        "version": 1,
        "protocol": "aws_sigv4",
        "credential": {
            "access_key": "{{access_key}}",
            "secret_key": "{{secret_key}}",
            "session_token": "{{session_token}}"
        },
        "parameters": {
            "region": "{{aws_region}}",
            "service_name": "bedrock",
            "model": "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
        },
        "actions": [{
            "action_type": "predict",
            "method": "POST",
            "headers": {
                "content-type": "application/json"
            },
            "url": "https://bedrock-runtime.${parameters.region}.amazonaws.com/model/${parameters.model}/converse",
            "request_body": "{ \"system\": [{\"text\": \"${parameters.system_prompt}\"}], \"messages\": [${parameters._chat_history:-}{\"role\":\"user\",\"content\":[{\"text\":\"${parameters.prompt}\"}]}${parameters._interactions:-}]${parameters.tool_configs:-} }"
        }]
    }
}
```

#### 2. 会話型エージェントの登録

エージェントを登録する際は、モデルタイプに対応する `_llm_interface` パラメータを含める必要があります。

- OpenAI Chat Completion: `openai/v1/chat/completions`
- Amazon Bedrock Converse Stream: `bedrock/converse/claude`

エージェントを登録するには、以下のリクエストを送信します。

```json
POST /_plugins/_ml/agents/_register
{
    "name": "Chat agent",
    "type": "conversational",
    "description": "this is a test agent",
    "llm": {
        "model_id": "<your_model_id>",
        "parameters": {
            "max_iteration": 5,
            "system_prompt": "You are a helpful assistant...",
            "prompt": "${parameters.question}"
        }
    },
    "memory": {
        "type": "conversation_index"
    },
    "parameters": {
        "_llm_interface": "bedrock/converse/claude"
    },
    "tools": [
        {
            "type": "IndexMappingTool",
            "name": "DemoIndexMappingTool",
            "description": "Tool to get index mapping of index",
            "parameters": {
                "index": "${parameters.index}",
                "input": "${parameters.question}"
            }
        },
        {
            "type": "ListIndexTool",
            "name": "RetrieveIndexMetaTool",
            "description": "Use this tool to get OpenSearch index information..."
        }
    ],
    "app_type": "chat_with_rag"
}
```

#### 3. Execute Stream Agent API の実行

Execute Stream Agent API を実行するには、以下のリクエストを送信します。

```json
POST /_plugins/_ml/agents/37YmxZkBphfsuvK7qIj4/_execute/stream
{
    "parameters": {
        "question": "How many indices are in my cluster?"
    }
}
```

#### サンプルレスポンス

ストリーミング形式は SSE を使用し、各チャンクにはエージェントのレスポンスの一部が含まれます。各データ行は、エージェントが出力を生成する際にリアルタイムで送信される個別のチャンクを表します。

各チャンクには以下の主要な要素があります。

- `content` — このチャンクで生成されたテキストまたはデータフラグメント (例: 単語やフレーズ)
- `is_last` — これが最後のチャンクかどうかを示すブール値フラグ (中間チャンクの場合は `false`、最後のチャンクの場合は `true`)
- `memory_id` — 会話メモリセッションの一意の識別子
- `parent_interaction_id` — 会話内の関連するインタラクションをリンクする識別子

## まとめ

OpenSearch のストリーミング機能は、レスポンシブでリアルタイムな AI エクスペリエンスを提供する上で大きな前進を表しています。Predict Stream API と Execute Stream Agent API を通じて段階的なデータ配信を可能にすることで、AI を活用したアプリケーションとのインタラクション方法を変革し、ローディングスピナーを即座の段階的なフィードバックに置き換えることができます。会話型 AI インターフェース、コンテンツ生成ツール、エージェントベースのワークフローを構築する場合でも、ストリーミングはより魅力的で透明性の高いユーザーエクスペリエンスの基盤を提供します。

**始める準備はできましたか?** OpenSearch 環境でストリーミングを実装し、その違いを直接体験してください。この機能が実験的段階から一般提供に進化するにつれて、モデルとエージェントのサポートの拡大や追加機能が期待されます。

## 次のステップ

- [Predict Stream](https://docs.opensearch.org/latest/ml-commons-plugin/api/train-predict/predict-stream/) と [Execute Stream Agent](https://docs.opensearch.org/latest/ml-commons-plugin/api/agent-apis/execute-stream-agent/) API リファレンスを参照してください
- [OpenSearch フォーラム](https://forum.opensearch.org/) でフィードバックを共有してください
- 今後のリリースでストリーミングサポートが拡大するにつれて、最新情報をお待ちください
