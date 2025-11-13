---
title: "Amazon Quick Suite と GitHub MCP でソフトウェアについて質問できる Chat Agent を作る"
emoji: "🤖"
type: "tech"
publication_name: "aws_japan"
topics: ["quicksuite", "AWS", "github", awsaiagentblogfes"]
published: false
---

## はじめに

こんにちは！ AWS のソリューションアーキテクトの榎本です。普段は OpenSearch や Kafka のサポートを中心に活動しています。

本ブログは AWS AI Agent ブログ祭り(Zenn: [#awsaiagentblogfes](https://zenn.dev/topics/awsaiagentblogfes), X: [#AWS_AI_AGENT_ブログ祭り](https://x.com/hashtag/AWS_AI_AGENT_%E3%83%96%E3%83%AD%E3%82%B0%E7%A5%AD%E3%82%8A))の第 N 日目です。

:::message
📚 **第 N-1 日目の記事はこちら！**
- [記事タイトル](記事URL)
- [記事タイトル](記事URL)
:::

Amazon Quick Suite は 2025 年 10 月に一般提供が開始された AWS サービスです。Agentic AI プラットフォームとして多くの Agent 機能に加え、Amazon QuickSight を Quick Sight として吸収しており、BI 機能もカバーする統合的な環境として提供しています。2025 年 10 月から行われているブログリレーの中でも今日まで Amazon Quick Suite に関する記事が投稿されているので、是非チェックしてみてください。

## 今回のお題
突然ですが、GitHub MCP を皆さん活用されていますか？ [GitHub MCP Server](https://github.com/github/github-mcp-server/tree/main)は、AI ツールを GitHub プラットフォームに直接接続する MCP サーバーの一種です。リポジトリやコードファイルの読み取り、Issue や PR の管理、コードの分析、ワークフローの自動化を、すべて自然言語でのやり取りを通じて実行できるようになります。

私自身も、担当しているサービスがオープンソースの OpenSearch や Kafka のマネージドサービスということもあって、リリースノートを起点とした各種機能の詳細なまとめ情報の作成や、特定のコード実装の探索など、随所でお世話になっています。
普段はローカルの Amazon Q Developer CLI をメインで使用しているのですが、ふと「Quick Suite の Chat agent と組み合わせてみたら面白いのでは？」と思い、実際に組み合わせを試してみました。

今回の記事では、GitHub MCP 連携方法、Agent からの使用方法や使用感を解説していきます。

## 前提条件

本記事の内容を試すには、以下を準備する必要があります。Amazon Quick Suite のセットアップ手順については、12 日目の記事「[Quick Suite で穴場の観光地をリサーチ](https://zenn.dev/aws_japan/articles/accommodation-research)」などを参考にしてみてください。

- Amazon Quick Suite のアカウント
- GitHub アカウント

## セットアップ手順
### GitHub Apps の作成
GitHub MCP Server はローカルとリモートが用意されています。Amazon Quick Suite はローカル MCP サーバーには対応していないため、今回は[リモート MCP サーバー](https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md)を使用します。
Amazon Quick Suite から リモートの GitHub MCP Server へアクセスするには認証が必要となるため、[GitHub Apps](https://docs.github.com/ja/enterprise-cloud@latest/apps/creating-github-apps/about-creating-github-apps/best-practices-for-creating-a-github-app) の認証情報を使用します。

以降の手順は記事執筆時のものです。最新の手順は GitHub のドキュメントをご確認ください。

1. Developer Settings -> [GitHub Apps](https://github.com/settings/apps) にアクセスし、New GitHub App を選択します。
![](/images/amazon-quick-suite-github-mcp-oss-chat-agent-2025-11-13_8.webp)
2. Register new GitHub App にて、項目ごとに以下の値を入力します。その他の項目はデフォルトのままで OK です。
  - GitHub App name: Amazon Quick Suite
  - Homepage URL: https://quicksight.aws.amazon.com/
  - Identifying and authorizing users
  - Callback URL: https://us-east-1.quicksight.aws.amazon.com/sn/oauthcallback (リージョンはお使いの Amazon Quick Suite のリージョンに合わせて変更してください)
  ![](/images/amazon-quick-suite-github-mcp-oss-chat-agent-2025-11-13_9.webp)
  - Webhook: Active チェックを OFF にします
  ![](/images/amazon-quick-suite-github-mcp-oss-chat-agent-2025-11-13_10.webp)
  - Permissions: Repository permissions 内の **Contents**、**Issues**、**Pull requests** への Access を `read-only` にセットします
  ![](/images/amazon-quick-suite-github-mcp-oss-chat-agent-2025-11-13_11.webp)
3. 画面最下部の `Create GitHub App` ボタンを押します。
![](/images/amazon-quick-suite-github-mcp-oss-chat-agent-2025-11-13_12.webp)
4. 作成完了後、**Client secrets** セクションの `Generate a new client secret` ボタンを押してシークレットを生成します。
![](/images/amazon-quick-suite-github-mcp-oss-chat-agent-2025-11-13_14.webp)
5. アプリケーションの Client ID と Client secret を記録しておきます。Amazon Quick Suite へ登録する際に必要です。
![](/images/amazon-quick-suite-github-mcp-oss-chat-agent-2025-11-13_13.webp)

### Amazon Quick Suite の設定
作成した GitHub Apps の認証情報を元に、Quick Suite 側に GitHub MCP サーバーの情報を登録していきます。
まずは Quick Suite のメニューから `Integrations` を選択します

![](/images/amazon-quick-suite-github-mcp-oss-chat-agent-2025-11-13.webp)

一覧から `Model Context Protocol` を選択します。

![](/images/amazon-quick-suite-github-mcp-oss-chat-agent-2025-11-13_1.webp)

**Connect** セクションにて、以下の情報を入力し `Next` ボタンを押します。

- Name: GitHub
- Description: 任意で OK です
- MCP server endpoint: https://api.githubcopilot.com/mcp/

![](/images/amazon-quick-suite-github-mcp-oss-chat-agent-2025-11-13_2.webp)

**Authenticate** セクションでは、以下の情報を入力して `Create and continue` ボタンを押します。

Token URL および Authorization URL については 

- Authentication settings: User authentication を選択
- Client ID: コピーした GitHub Apps の Client ID
- Client secret: コピーした GitHub Apps の Client secret 
- Token URL: https://github.com/login/oauth/access_token
- Authorization URL: https://github.com/login/oauth/authorize
- Redirect URL: https://us-east-1.quicksight.aws.amazon.com/sn/oauthcallback

![](/images/amazon-quick-suite-github-mcp-oss-chat-agent-2025-11-13_15.webp)

承認のためのポップアップが表示されたら、`Authorize Amazon Quick SUite` ボタンを押します。

![](/images/amazon-quick-suite-github-mcp-oss-chat-agent-2025-11-13_16.webp)

ポップアップが閉じられ Review セクションに進みます。"Retrieving actions. This might take up to a minute. You can close and return to view the list later." と表示されたら完了までしばし待ちましょう

![](/images/amazon-quick-suite-github-mcp-oss-chat-agent-2025-11-13_17.webp)

ツールの一覧が表示されたら `Next` ボタンを押します。

![](/images/amazon-quick-suite-github-mcp-oss-chat-agent-2025-11-13_18.webp)

任意のメンバーに MCP をシェアする場合はユーザーもしくはグループ名を検索して `Share` ボタンから共有が可能です。本記事では共有者の追加はせずに `Next` ボタンを押します。

![](/images/amazon-quick-suite-github-mcp-oss-chat-agent-2025-11-13_19.webp)

Integrations の Actions タブに切り替え、GitHub のステータスが **Available** になるまで待機します。ステータスが Available になったら、`GitHub` の名前部分をクリックします。

![](/images/amazon-quick-suite-github-mcp-oss-chat-agent-2025-11-13_21.webp)

左下に "Not signed in" と表示されていることを確認し、右上の `Sign in` ボタンを押します。

![](/images/amazon-quick-suite-github-mcp-oss-chat-agent-2025-11-13_22.webp)

GitHub の認証が求められた場合は認証を実施してください。**Sign in** ボタンが **Re-Connect** に変化したら準備は完了です。

### Chat agent の構築
では、実際に Chat agent を作成していきましょう。Quick Suite の Chat agents メニューから新規のエージェント作成画面に進みます。

![](/images/amazon-quick-suite-github-mcp-oss-chat-agent-2025-11-13_23.webp)

以下のプロンプトを入力し、`Generate` ボタンを押しましょう。

```
あなたは経験豊富なソフトウェアエンジニアです。GitHubの情報を活用して、開発者の質問に対して技術的に正確で実用的な回答を提供します。GitHubの情報を参照する際は、最新の情報を確認し、リポジトリの構造、コミット履歴、プルリクエスト、イシューなどの関連情報を総合的に分析して回答してください。コードレビューやベストプラクティスに関するアドバイスも積極的に提供してください。質問に対しては必ず GitHub のから最新のコードを参照してから回答してください。
```

Chat agent が作成されました。ACTIONS を展開すると先ほど登録した GitHub MCP がリンクされていることが確認できます。

![](/images/amazon-quick-suite-github-mcp-oss-chat-agent-2025-11-13_33.webp)

## Chat agent の活用

では、実際に活用していきましょう。OpenSearch 3 系列の最新バージョンについての質問です。

```
OpenSearch 3 系列の最新バージョンは？
```

![](/images/amazon-quick-suite-github-mcp-oss-chat-agent-2025-11-13_34.webp)

よさそうですね。実際にこの記事を執筆している 2025 年 11 月 13 日時点では 3.3.2 が最新バージョンです。有用そうなので `Launch chat agent` からチャットエージェントをリリースします。

![](/images/amazon-quick-suite-github-mcp-oss-chat-agent-2025-11-13_28.webp)

Successfully launched chat agent と表示されました。

![](/images/amazon-quick-suite-github-mcp-oss-chat-agent-2025-11-13_29.webp)

Chat agents 一覧に戻ると、作成した "GitHub Expert Engineer" が表示されています。Action から Chat を選択してもう少し活用してみましょう。Expand を選択するとチャット画面を広くとることができます。

![](/images/amazon-quick-suite-github-mcp-oss-chat-agent-2025-11-13_31.webp)

では質問してみましょう。先ほどの OpenSearch 3.x 最新バージョンについて質問した時の回答に "Star-Tree" というものがありましたね。この機能について質問してみましょう。

```
OpenSearch の Star-Tree 機能 について解説してください。
```

![](/images/amazon-quick-suite-github-mcp-oss-chat-agent-2025-11-13_35.webp)

GitHub のツールを使用していることが分かりますね。機能の特徴や利点が正しく解説されています。

観点を変えて、盛り上がっている Issue をピックアップしてみます。

```
OpenSearch Project で議論が盛り上がっている Open ステータスの RFC Issue の Top-10 を抽出して。
```

![](/images/amazon-quick-suite-github-mcp-oss-chat-agent-2025-11-14.webp)

活発に議論されている RFC がリストアップされました。

比較のために複数のリポジトリを参照することもできました。

```
Valkey と OpenSearch のベクトル検索の特徴について実装から比較して
```

![](/images/amazon-quick-suite-github-mcp-oss-chat-agent-2025-11-14_1.webp)


## まとめ

本記事では、Amazon Quick Suite と GitHub MCP を組み合わせて、OSS について質問できる Chat Agent を構築する方法を試してみました。
Quick Suite では、現状バックエンドで使われている LLM を自由に選択することはできないため、よりコーディング性能が高いモデルを使用したい場合は Amazon Q Developer CLI などを使用した方が自由が利きます。一方で軽量に使用するなら Quick Suite は面白い選択肢になりえますし、Flows などから使用することで深い調査を自動化できる可能性もあります。MCP と Flows の組み合わせについては私自身もまだ模索中ですが、何かしら形になりましたらアップデート記事の形で公開できればと思います！



