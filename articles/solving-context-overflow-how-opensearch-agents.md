---
title: "[翻訳] OpenSearch エージェントのコンテキスト管理で長い会話でも賢く動作させる"
emoji: "🔍"
type: "tech"
topics: ["opensearch", "ai", "llm", "agent"]
publication_name: "opensearch"
published: true
published_at: 2026-04-13
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/solving-context-overflow-how-opensearch-agents-stay-smart-in-long-conversations/

AI エージェントが高度化し、複数のツールを使いながら長い会話を処理するようになると、コンテキストの効率的な管理が重要になります。本記事では、OpenSearch 3.5 で導入された OpenSearch エージェント向けの**コンテキスト管理**機能を紹介します。

## 問題: コンテキストウィンドウのオーバーフロー

現在の AI エージェントには、コンテキストウィンドウの制限という課題があります。エージェントが長い会話を行い、複数のツールを使い、やり取りの履歴が蓄積されると、トークンの上限にすぐ到達します。コンテキストが LLM の上限を超えるとリクエストは失敗し、コンテキストが肥大化するとパフォーマンスが低下します。不要なトークンの処理はコストを増加させ、無関係なコンテキストがモデルを混乱させるとハルシネーションが増えます。

この問題に対する従来のアプローチは、トークン上限に達したら古いメッセージを単純に切り捨てるという粗い方法でした。しかし、これでは貴重なコンテキストが失われ、エージェントが一貫性のある長時間の会話を維持できなくなります。

## 解決策: インテリジェントなコンテキストエンジニアリング

コンテキスト管理は、エージェントのコンテキストを動的にエンジニアリングできる高度なフックベースのシステムを導入します。エージェントは以下のことが可能になります。

- 古いやり取りをインテリジェントに要約し、重要な情報を保持する
- スライディングウィンドウを適用して直近のコンテキストを維持する
- ツール出力が大きくなりすぎた場合に戦略的にトランケートする
- 複数の戦略を組み合わせてコンテキストを最適化する

## コンテキスト管理の仕組み

コンテキスト管理は、エージェントの実行を特定のポイントでインターセプトするフックベースのアーキテクチャで動作します。`pre_llm` フックは LLM にリクエストを送信する前にコンテキストを最適化し、`post_tool` フックはツール実行完了後にコンテキストを処理します。各フックでは、エージェントのコンテキストを最適化するために連携して動作するコンテキストマネージャーのチームを構成できます。

### コンテキストマネージャー

コンテキスト管理の特徴は柔軟に使える点です。異なるコンテキストマネージャーを組み合わせたり、ユースケースに合わせてパラメータを調整したり、最適なパフォーマンスを見つけるためにしきい値を試したり、複数の戦略を組み合わせて包括的にコンテキストを最適化したりできます。まずは控えめな設定から始めて、エージェントのパフォーマンスと要件に基づいて徐々に調整することをお勧めします。

OpenSearch には 3 つの組み込みコンテキストマネージャーがあります。

#### スライディングウィンドウマネージャー

**スライディングウィンドウマネージャー**は、直近のやり取りのスライディングウィンドウを維持し、上限に達すると古いメッセージを自動的に削除します。以下の例では、直近 6 件のメッセージを保持し、メッセージ数が 20 を超えたときに起動するスライディングウィンドウマネージャーの設定方法を示します。

```json
{
  "type": "SlidingWindowManager",
  "config": {
    "max_messages": 6,
    "activation": {
      "message_count_exceed": 20
    }
  }
}
```

#### 要約マネージャー

**要約マネージャー**は、LLM を使用して古いやり取りをインテリジェントに要約し、重要な情報を保持しながらトークン数を削減します。以下の例では、直近 10 件のメッセージを保持し、古いメッセージを元のサイズの 30% に圧縮し、トークン数が 200,000 を超えたときに起動する要約の設定を示します。

```json
{
  "type": "SummarizationManager",
  "config": {
    "summary_ratio": 0.3,
    "preserve_recent_messages": 10,
    "activation": {
      "tokens_exceed": 200000
    }
  }
}
```

#### ツール出力トランケートマネージャー

**ツール出力トランケートマネージャー**は、指定された上限を超えるツール出力をトランケートし、単一の大きな出力がコンテキストを圧迫するのを防ぎます。以下の例では、ツール出力を 100,000 文字に制限します。

```json
{
  "type": "ToolsOutputTruncateManager",
  "config": {
    "max_output_length": 100000
  }
}
```

## スマートなアクティベーションルール

コンテキストマネージャーは**アクティベーションルール**を使用して、最適化が必要なタイミングを判断します。`tokens_exceed` ルールは推定トークン数がしきい値を超えたときに起動し、`message_count_exceed` ルールはメッセージ数が上限を超えたときに起動します。複数のルールを `AND` ロジックで組み合わせることで、きめ細かい制御が可能です。これにより、エージェントは要約のようなコストの高い処理を本当に必要なときだけ実行します。

## 実際のユースケース

コンテキスト管理は、エージェントがリソース制約を管理しながら長い会話を維持する必要があるシナリオでうまく機能します。

### カスタマーサービスエージェント

複数の短いやり取りを処理するカスタマーサービスエージェントでは、スライディングウィンドウマネージャーで直近のメッセージのみを保持し、大きなツール出力をトランケートするように設定できます。以下の例では、直近 6 件のメッセージを維持し (15 件を超えたら起動)、ツール出力を 50,000 文字に制限するコンテキスト管理設定を作成します。

```
POST /_plugins/_ml/context_management/customer-service-optimizer
{
  "description": "Optimized context management for customer service interactions",
  "hooks": {
    "pre_llm": [
      {
        "type": "SlidingWindowManager",
        "config": {
          "max_messages": 6,
          "activation": {
            "message_count_exceed": 15
          }
        }
      }
    ],
    "post_tool": [
      {
        "type": "ToolsOutputTruncateManager",
        "config": {
          "max_output_length": 50000
        }
      }
    ]
  }
}
```

### ツールを多用するリサーチアシスタント

多くのツールを使用し、大量のコンテキストを蓄積するリサーチアシスタントでは、要約と出力トランケートを組み合わせることができます。以下の例では、古いメッセージを要約し (直近 8 件を保持)、トークン数が 150,000 を超えたときに起動し、ツール出力を 80,000 文字に制限する設定を作成します。

```
POST /_plugins/_ml/context_management/research-assistant-optimizer
{
  "description": "Context management for research agents with extensive tool interactions",
  "hooks": {
    "pre_llm": [
      {
        "type": "SummarizationManager",
        "config": {
          "summary_ratio": 0.4,
          "preserve_recent_messages": 8,
          "activation": {
            "tokens_exceed": 150000
          }
        }
      }
    ],
    "post_tool": [
      {
        "type": "ToolsOutputTruncateManager",
        "config": {
          "max_output_length": 80000
        }
      }
    ]
  }
}
```

## コンテキスト管理の実装

コンテキスト管理を実装するには、まず上記のユースケースで示したように、必要なマネージャーとルールを含むコンテキスト管理設定を作成します。次に、設定名を参照してエージェントを登録します。以下の例では、カスタマーサービスオプティマイザー設定を使用して会話型エージェントを登録します。

```
POST /_plugins/_ml/agents/_register
{
  "name": "my-smart-agent",
  "type": "conversational",
  "llm": {
    "model_id": "your-llm-model-id"
  },
  "context_management_name": "customer-service-optimizer"
}
```

登録後、エージェントを実行すると、インテリジェントなコンテキスト最適化が動作します。個々の実行に対して異なるコンテキスト管理テンプレートを指定することもできます。以下の例では、リサーチアシスタントオプティマイザー設定を使用してエージェントを実行します。

```
POST /_plugins/_ml/agents/agent-id/_execute
{
  "parameters": {
    "question": "How can I help you today?"
  },
  "context_management_name": "research-assistant-optimizer"
}
```

デプロイ後は、エージェントのパフォーマンスを監視し、観測された動作やリソース使用パターンに基づいて設定を調整してください。

## 今後の予定

コンテキスト管理は OpenSearch 3.5 で利用可能です。[コンテキスト管理のドキュメント](https://opensearch.org/docs/latest/ml-commons-plugin/context-management/)を参照し、ユースケースに最適な設定を見つけるためにさまざまな構成を試してみてください。

フックベースのアーキテクチャは拡張性を考慮して設計されており、より高度なコンテキスト最適化戦略の基盤となります。特定のユースケース向けにカスタムコンテキストマネージャーを構築したり、エージェントライフサイクルの異なるポイントに新しい実行フックを追加したり、高度なアクティベーションルールを実装したりできます。

OpenSearch コミュニティへの貢献を歓迎します。新しいコンテキスト最適化戦略のアイデアやフックシステムの拡張に興味がある方は、[コントリビューションガイドライン](https://github.com/opensearch-project/ml-commons/blob/main/CONTRIBUTING.md)を参照し、[GitHub](https://github.com/opensearch-project/ml-commons) や[コミュニティフォーラム](https://forum.opensearch.org/)で会話に参加してください。
