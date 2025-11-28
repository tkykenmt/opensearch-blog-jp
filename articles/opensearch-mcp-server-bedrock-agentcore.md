---
title: "[翻訳] Amazon Bedrock AgentCore で OpenSearch MCP サーバーをホスティングする"
emoji: "🤖"
type: "tech"
topics: ["opensearch", "mcp", "aws", "bedrock"]
published: true
publication_name: "opensearch"
published_at: 2025-08-27
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/hosting-opensearch-mcp-server-with-amazon-bedrock-agentcore/

[OpenSearch MCP サーバー](https://github.com/opensearch-project/opensearch-mcp-server-py)は、Model Context Protocol (MCP) を通じて AI エージェントが OpenSearch クラスターと対話できるようにします。OpenSearch MCP サーバーはローカルで実行することもできますが、Amazon Bedrock AgentCore Runtime でホスティングすることで、どこからでもアクセス可能なスケーラブルでマネージドなソリューションを実現できます。

この記事では、OpenSearch MCP サーバーを Bedrock AgentCore にデプロイする 2 つの方法を紹介します。AWS CloudFormation テンプレートを使用した簡単なセットアップ方法と、AgentCore CLI を使用した手動設定方法です。

## 前提条件

開始する前に、以下を準備してください。

- OpenSearch クラスター
- サポートされている Bedrock AgentCore リージョンへのアクセス: `us-east-1`、`us-west-2`、`eu-central-1`、または `ap-southeast-2`

**注意**: Bedrock AgentCore はこれら 4 つの AWS リージョンでのみ利用可能ですが、MCP サーバーはパブリックインターネット経由で他のリージョンの OpenSearch クラスターに接続できます。

## 方法 1: CloudFormation テンプレートを使用する (Amazon OpenSearch Service ユーザー向け)

最も簡単に始める方法は、[OpenSearch MCP サーバー CloudFormation テンプレート](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/cfn-template-mcp-server.html)を使用することです。このテンプレートは必要なリソースをすべて自動的にプロビジョニングします。

### テンプレートのデプロイ

CloudFormation テンプレートには以下のパラメータが必要です。

**必須**:

- **Agent name**: MCP サーバーの名前
- **OpenSearch endpoint**: クラスターのエンドポイント URL
- **OpenSearch Region**: クラスターが配置されている AWS リージョン

**オプション**:

- **Amazon Elastic Container Registry (Amazon ECR) repository**: コンテナイメージを保存するリポジトリ。指定しない場合は自動作成されます
- **Execution role**: AgentCore Runtime 用の IAM ロール。指定しない場合は適切な権限を持つロールが自動作成されます
- **OAuth Discovery URL、Allowed Clients IDs、Allowed Audience**: OAuth 2.0 設定。指定しない場合は Amazon Cognito リソースが自動作成されます

### 出力の確認

デプロイが完了すると、以下の重要な出力が生成されます。

- **AgentCoreArn**: Bedrock AgentCore Runtime の Amazon リソースネーム (ARN)
- **TokenEndpoint**: ディスカバリーエンドポイントから取得したトークンエンドポイント
- **MCPServerEndpoint**: ホストされた MCP サーバーの URL

### アクセストークンの取得

MCP サーバーを使用するには、OAuth 認証サーバーから JWT トークンを取得する必要があります。自動作成された Cognito を使用している場合は、以下の手順でトークンを取得します。

1. **CloudFormation Resources** タブに移動します
2. **CognitoUserPool** を見つけ、**Physical ID** を選択します
3. **App clients** に移動し、**Client ID** と **Client Secret** をメモします

次にトークンを取得します。

```bash
export TOKEN_ENDPOINT="<YOUR TOKEN ENDPOINT>"
export CLIENT_ID="<YOUR CLIENT ID>"
export CLIENT_SECRET="<YOUR CLIENT SECRET>"

curl --http1.1 -X POST $TOKEN_ENDPOINT \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=$CLIENT_ID&client_secret=$CLIENT_SECRET"
```

レスポンスにはトークンが含まれます。

```json
{"access_token":"xxxxx","expires_in":3600,"token_type":"Bearer"}
```

**注意**: Cognito トークンはデフォルトで 60 分ごとに期限切れになります。

## 方法 2: Bedrock AgentCore CLI を使用する

Bedrock AgentCore CLI を直接使用することもできます。

### MCP サーバーコードの作成

まず、MCP サーバーの実装を作成します。

**opensearch_mcp_server.py**

```python
from mcp_server_opensearch import streaming_server
import asyncio
import os

os.environ["OPENSEARCH_URL"] = "https://your-opensearch-endpoint.com"
os.environ["AWS_REGION"] = "us-east-1"

if __name__ == "__main__":
    asyncio.run(streaming_server.serve(port=8000, host="0.0.0.0", stateless=True))
```

注意: OpenSearch クラスターと AgentCore Runtime が同じリージョンにある場合、`AWS_REGION` はオプションです。AgentCore が生成する Dockerfile には `AWS_REGION` が環境変数として設定されます。

**requirements.txt**

```
opensearch-mcp-server-py>=0.3.1
```

### OAuth の設定 (オプション)

既存の OAuth 認証サーバーがない場合は、[Bedrock AgentCore ドキュメント](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-mcp.html#runtime-mcp-appendix)の手順に従って Amazon Cognito を使用して作成します。

### AgentCore デプロイの設定

AgentCore ツールキットをインストールします。

```bash
pip install bedrock-agentcore-starter-toolkit
```

デプロイを設定します。

```bash
agentcore configure -e opensearch_mcp_server.py --protocol MCP
```

プロンプトに従って以下を設定します。

- 実行ロールの自動作成 (または既存のロールを指定)
- ECR リポジトリの自動作成 (または既存のリポジトリを指定)
- `requirements.txt` ファイルの選択
- ディスカバリー URL とクライアント ID を使用した OAuth 認証サーバーの設定

### AgentCore Runtime へのデプロイ

MCP サーバーをデプロイします。

```bash
agentcore launch
```

デプロイが成功したら、MCP サーバーの URL を生成します。

```bash
export AWS_REGION="<YOUR AWS REGION>"
export AGENT_ARN="<YOUR AGENT ARN>"
export ENCODED_AGENT_ARN=$(echo $AGENT_ARN | sed 's/:/%3A/g; s/\//%2F/g')
echo "https://bedrock-agentcore.$AWS_REGION.amazonaws.com/runtimes/$ENCODED_AGENT_ARN/invocations?qualifier=DEFAULT"
```

## OpenSearch アクセスの設定

どちらのデプロイ方法を使用した場合でも、MCP サーバーがデータにアクセスできるように、AgentCore 実行ロールを OpenSearch バックエンドロールにマッピングする必要があります。

適切なバックエンドロールマッピングを設定するには、[Amazon OpenSearch Service のきめ細かなアクセス制御](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/fgac.html#fgac-access-control)の手順に従ってください。

## ホストされた MCP サーバーの使用

以下のセクションでは、新しくホストされた MCP サーバーのテスト方法と使用方法を説明します。

### Amazon Q Developer CLI でのテスト

MCP サーバーをテストする最も簡単な方法は、Amazon Q Developer CLI を使用することです。`~/.aws/amazonq/mcp.json` を設定します。

```json
{
  "mcpServers": {
    "opensearch-mcp-server": {
      "command": "mcp-proxy",
      "timeout": 60000,
      "args": [
        "<YOUR MCP URL>",
        "--transport",
        "streamablehttp"
      ],
      "env": {
        "API_ACCESS_TOKEN": "<YOUR ACCESS TOKEN>"
      }
    }
  }
}
```

Amazon Q Developer CLI を起動します。

```bash
$ q
✓ opensearch-mcp-server loaded in 3.22 s
```

ツールが利用可能であることを確認します。

```
> /tools

Tool                   Permission
Built-in:
- execute_bash         * trust read-only commands
- fs_read              * trusted
- fs_write             * not trusted
- report_issue         * trusted
- use_aws              * trust read-only commands

opensearch-mcp-server (MCP):
- ClusterHealthTool    * not trusted
- CountTool            * not trusted
- ExplainTool          * not trusted
- GetShardsTool        * not trusted
- IndexMappingTool     * not trusted
- ListIndexTool        * not trusted
- MsearchTool          * not trusted
- SearchIndexTool      * not trusted
```

これで OpenSearch データについて質問できるようになりました。活用例については、「[Unlocking agentic AI experiences with OpenSearch](https://opensearch.org/blog/unlocking-agentic-ai-experiences-with-opensearch/)」を参照してください。

### カスタムエージェントでの使用

ホストされた MCP サーバーは、MCP 互換の任意のエージェントと統合できます。以下は Strands Agents フレームワークを使用した例です。

```python
import os
import requests
from strands import Agent
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client

def get_bearer_token(discovery_url: str, client_id: str, client_secret: str):
    response = requests.get(discovery_url)
    discovery_data = response.json()
    token_endpoint = discovery_data['token_endpoint']

    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(token_endpoint, data=data, headers=headers)
    token_data = response.json()
    return token_data['access_token']

if __name__ == "__main__":
    discovery_url = os.environ["DISCOVERY_URL"]
    client_id = os.environ["CLIENT_ID"]
    client_secret = os.environ["CLIENT_SECRET"]
    mcp_url = os.environ["MCP_URL"]

    bearer_token = get_bearer_token(discovery_url, client_id, client_secret)

    opensearch_mcp_client = MCPClient(lambda: streamablehttp_client(mcp_url, {
        "authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }))

    with opensearch_mcp_client:
        tools = opensearch_mcp_client.list_tools_sync()
        agent = Agent(tools=tools)
        agent("list indices")
```

## まとめ

OpenSearch MCP サーバーを Amazon Bedrock AgentCore Runtime でホスティングすることで、OpenSearch と AI エージェントを統合するためのスケーラブルでマネージドなソリューションを実現できます。CloudFormation による迅速なデプロイを選択しても、CLI による方法を選択しても、複数のエージェントやアプリケーションに対応できる堅牢なクラウドホスト型 MCP サーバーを構築できます。

ホスト型アプローチは、OAuth 認証ときめ細かなアクセス制御によるエンタープライズグレードのセキュリティを提供しながら、インフラストラクチャ管理の必要性を排除します。これにより、AI エージェントから OpenSearch データへの信頼性が高くスケーラブルなアクセスが必要な本番環境のデプロイに最適です。

さっそく始めてみましょう。最速のセットアップには CloudFormation テンプレートを、デプロイ設定をより細かく制御したい場合は CLI 方式をお試しください。
