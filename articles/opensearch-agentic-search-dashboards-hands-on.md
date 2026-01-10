---
title: "[翻訳] OpenSearch 3.4 の OpenSearch Dashboards におけるエージェント検索: ハンズオンユースケースと実例"
emoji: "🤖"
type: "tech"
topics: ["opensearch", "ai", "search", "dashboards", "agent"]
published: true
publication_name: "opensearch"
published_at: 2026-01-08
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/opensearch-3-4s-agentic-search-in-opensearch-dashboards-hands-on-use-cases-and-examples/

OpenSearch 3.4 で利用可能になった新しいエージェント検索 (agentic search) のユーザー体験を発表できることを嬉しく思います。OpenSearch Dashboards のこのインターフェースは、エージェントの設定、自然言語クエリを使用したテスト、下流アプリケーション統合のための設定エクスポートを効率的に行う方法を提供します。

## エージェント検索とは

エージェント検索は、複雑な検索構文を書く代わりに自然言語クエリを使用できるようにすることで、データとのやり取りを変革します。インテリジェントなエージェントが質問を解釈し、自動的に検索を計画し、関連する結果を返します。その際、意思決定プロセスを完全に透明化します。詳細については、[以前のブログ記事](https://opensearch.org/blog/introducing-agentic-search-in-opensearch-transforming-data-interaction-through-natural-language/)を参照してください。エージェント検索の機能とアーキテクチャの詳細な概要については、[エージェント検索のドキュメント](https://docs.opensearch.org/latest/vector-search/ai-search/agentic-search/index/)を参照してください。

## OpenSearch Dashboards でのエージェント検索の使用

OpenSearch Dashboards でエージェント検索にアクセスするには、**OpenSearch Dashboards** > **OpenSearch Plugins** > **AI Search Flows** に移動し、新しいエージェント検索ワークフローを作成します。インターフェースには 2 つの主要なセクションがあります。左側にエージェント設定オプション、右側に検索実行機能があります。インターフェースコンポーネント、エージェントタイプ、利用可能なツール、設定オプションの詳細については、[エージェント検索の設定](https://docs.opensearch.org/latest/vector-search/ai-search/building-agentic-search-flows/)を参照してください。

## 実例

エージェント検索が複雑な検索シナリオを直感的な自然言語インタラクションに変換する方法を示す実用的なユースケースを見ていきましょう。次のセクションの例では、以下の事前設定されたリソースを使用します。

* デプロイ済みの Amazon Bedrock Claude 4.5 エージェント。環境へのこのモデルのデプロイ方法、およびエージェント検索と互換性のある他の推奨モデルについては、[エージェント検索のドキュメント](https://docs.opensearch.org/latest/vector-search/ai-search/agentic-search/index/)を参照してください。
* `demo_amazon_fashion` という名前のインデックス。このインデックスは、MIT ライセンスの [Fashion Products Images Dataset](https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-dataset) を使用して作成され、価格と評価の合成値が追加されています。または、商品データを含む任意のインデックスを使用できます。
* 顧客 ID に基づく注文履歴を含む Model Context Protocol (MCP) サーバーへのコネクタ。外部 MCP サーバーへの接続については、[MCP コネクタのドキュメント](https://docs.opensearch.org/latest/ml-commons-plugin/agents-tools/mcp/mcp-connector/)を参照してください。

### 例 1: E コマース会話型検索

会話型エージェントを使用すると、自然言語で質問し、フォローアップの質問で検索を絞り込むことができます。エージェントは会話全体でコンテキストを維持し、結果を段階的に絞り込んで最も関連性の高い結果を返します。この機能を示すアプリケーションを構築してみましょう。

#### ステップ 1: エージェントの作成

データ構造の理解、効果的なクエリの計画、関連する結果の取得を可能にするさまざまなインデックス関連ツールを備えた会話型エージェントを作成します。

1. **Create agent** を選択します。
2. 名前を入力します: `My conversational agent`
3. モデルを選択します: `Bedrock Claude 4.5`
4. 以下のツールを有効にします: **Query Planning**、**Search Index**、**List Index**、**Index Mapping**
5. **Create** を選択します。

以下の画像に、完成したエージェント設定フォームを示します。

![エージェント設定フォーム](/images/opensearch-agentic-search-dashboards-hands-on/blog-1.png)

#### ステップ 2: エージェント検索の実行

エージェントをテストします。

1. `demo_amazon_fashion` インデックスを選択します。
2. 検索クエリを入力します。例: `Blue shades for my dad`
3. **Search** を選択します。

エージェントがクエリ DSL を生成し、検索結果を返します。生成された DSL クエリを以下の画像に示します。

![生成されたクエリ DSL](/images/opensearch-agentic-search-dashboards-hands-on/blog-2-gen-query.png)

以下の画像に対応する検索結果を示します。すべての結果が男性用の青いサングラスであり、正確なクエリ解釈を示しています。

![検索結果](/images/opensearch-agentic-search-dashboards-hands-on/blog-3-results.png)

エージェントの意思決定プロセスを理解するには、以下の画像に示すエージェントサマリーを確認してください。

![エージェントサマリー](/images/opensearch-agentic-search-dashboards-hands-on/blog-4-agent-summary.png)

次に、フォローアップの質問をして検索を絞り込みます。

1. 上部の **Query** の横にある **Continue conversation** を選択します。
2. クエリを `Do you have any black ones from Ray-Ban?` に更新します。
3. **Search** を選択します。

エージェントは元のクエリからのコンテキストを維持しながら、新しい制約を適用します。結果には、Ray-Ban の男性用黒サングラスが含まれるようになりました。以下の画像に絞り込まれた検索結果を示します。**View more** を選択すると、検索結果の詳細を表示できます。

![絞り込まれた検索結果](/images/opensearch-agentic-search-dashboards-hands-on/blog-5-ray-ban.png)

追加のクエリを実行すると、エージェントはコンテキストを維持するために会話履歴を継続的に参照および更新します。履歴を削除して新しい会話を開始するには、**Clear conversation** を選択します。

#### ステップ 3: エージェントのチューニング

パフォーマンスと結果の品質を最適化するために、エージェントを微調整し、さまざまな設定を反復的にテストできます。

まず、OpenAI の最新モデル GPT-5 にモデルを交換してみましょう。このモデルは、強化された推論機能と複雑で多面的なクエリの理解の向上を提供します。モデルをデプロイした後、以下の手順を実行します。

1. **Configure Agent** の下で、**Model** ドロップダウンを選択します。
2. `OpenAI GPT-5` を選択します。
3. **Update agent** を選択します。
4. **Agentic Search** の下で、**Search** を選択して更新されたエージェントを使用して新しい検索を実行し、パフォーマンスを評価します。

新しいモデルを使用してクエリ `Men's blue shirts` を実行した後の結果を以下の画像に示します。

![GPT-5 での検索結果](/images/opensearch-agentic-search-dashboards-hands-on/blog-6-gpt-scaled.png)

次に、モデルの利用可能なツールを更新してみましょう。エージェントの柔軟性を高め、リアルタイム情報へのアクセスを可能にするために、Web Search ツールを有効にします。

1. **Configure Agent** > **Tools** > **Web Search** の下で、**Enable** を選択します。ツールフォームが自動的に展開されます。
2. **Engine** に `duckduckgo` と入力します。これは最もシンプルなオプションで、追加の権限や設定は必要ありません。
3. **Update agent** を選択します。
4. **Agentic Search** の下で、**Search** を選択して更新されたエージェントを使用して新しい検索を実行します。エージェントは、インデックスされたデータセットの範囲を超える情報を必要とする質問に対応できるようになりました。

外部情報の取得が必要な新しい検索クエリを試して、結果を評価します。クエリ `Shoes from the brand Serena Williams wears` を入力し、**Search** を選択します。生成されたクエリは、以下の画像に示すように、Nike ブランドでフィルタリングされています。

![Web 検索クエリ](/images/opensearch-agentic-search-dashboards-hands-on/blog-7-web-query.png)

以下の画像にクエリ結果を示します。

![Web 検索結果](/images/opensearch-agentic-search-dashboards-hands-on/blog-8-web-results.png)

エージェントはまず Web を検索して Serena Williams に関連する靴ブランド (Nike) を特定し、それを生成されたクエリに組み込み、最終的に Nike の靴を返しました。以下の画像のエージェントサマリーに示されています。

![Web 検索エージェントサマリー](/images/opensearch-agentic-search-dashboards-hands-on/blog-9-web-summary.png)

次に、MCP サーバーと統合して、エージェントが注文履歴を表示できるようにし、よりカスタマイズされたパーソナライズされた検索体験を実現します。このサーバーには、注文履歴の詳細を返すために使用できる `simple_get_order_history` ツールがあります。

1. **Configure Agent** > **MCP Servers** の下で、**Add MCP server** を選択します。
2. **MCP Server** ドロップダウンから `Customer Order History MCP Server` を選択します。
3. **Tool filters** に `simple_get_order_history` と入力して、エージェントのアクセスを制限し、MCP サーバーからこのツールのみを利用可能にします。このツールはパラメータを取らず、デフォルトの注文履歴を返します。
4. **Update agent** を選択します。

以下の画像に MCP サーバーの設定を示します。

![MCP サーバー設定](/images/opensearch-agentic-search-dashboards-hands-on/blog-10-mcp.png)

注文履歴を使用して類似の商品やブランドを見つけ、アスレチックショーツを検索してみましょう。クエリを `Athletic shorts similar to my order history` に更新します。生成されたクエリを以下の画像に示します。

![MCP クエリ](/images/opensearch-agentic-search-dashboards-hands-on/blog-11-query.png)

以下の画像に結果を示します。Adidas と Nike のアスレチックショーツが含まれています。

![MCP 検索結果](/images/opensearch-agentic-search-dashboards-hands-on/blog-12-results.png)

以下の画像に、エージェントが注文履歴に Nike と Adidas ブランドが存在することを判断し、DSL クエリに対応するブランドフィルターを適用した方法を示すエージェントサマリーを示します。

![MCP エージェントサマリー](/images/opensearch-agentic-search-dashboards-hands-on/blog-13-summary.png)

#### ステップ 4: 設定のエクスポート

テストが完了し、設定を下流アプリケーションに統合する準備ができたら、右上隅の **Export** を選択します。このビューでは、エージェント検索を支える基盤となる検索パイプラインに関する詳細情報と、新規または既存のシステムに統合する方法が表示されます。パイプライン設定の詳細を以下の画像に示します。

![パイプライン設定](/images/opensearch-agentic-search-dashboards-hands-on/blog-17-pipeline.png)

統合用のクエリ形式の例を以下の画像に示します。

![クエリ形式の例](/images/opensearch-agentic-search-dashboards-hands-on/blog-18-query.png)

### 例 2: 高速商品フィルタリング

フローエージェントは、マルチターンの会話や複雑な推論が不要な場合に、会話型エージェントよりも大幅に高速な単一クエリ検索機能を提供します。この効率性を活用するアプリケーションを構築してみましょう。

#### ステップ 1: エージェントの作成

フローエージェントを作成します。

1. **Create agent** を選択します。
2. 名前を入力します: `My flow agent`
3. エージェントタイプを **Flow** に変更します。
4. **Query Planning** ツールの下で、`Bedrock Claude 4.5` を選択します。
5. **Create** を選択します。

以下の画像にフローエージェントの設定フォームを示します。

![フローエージェント設定](/images/opensearch-agentic-search-dashboards-hands-on/blog-14-flow.png)

#### ステップ 2: エージェント検索の実行

直接商品検索を実行してエージェントをテストします。

1. `demo_amazon_fashion` インデックスを選択します。
2. 検索クエリを入力します。例: `Women's running shoes under $100`
3. **Search** を選択します。

エージェントは最適化されたクエリ DSL を生成して検索を実行し、100 ドル未満の女性用ランニングシューズを返します。以下の画像にフローエージェントのクエリ生成を示します。

![フローエージェントクエリ](/images/opensearch-agentic-search-dashboards-hands-on/blog-15-flow-query.png)

以下の画像に一致する商品結果を示します。

![フローエージェント結果](/images/opensearch-agentic-search-dashboards-hands-on/blog-16-flow-results.png)

#### ステップ 3: エージェントのチューニング

前の例と同様に、クエリ生成に異なるモデルを使用してエージェントのパフォーマンスをテストできます。

## 今後の予定

検索体験を変革する準備はできましたか? まず OpenSearch Dashboards でエージェント検索をテストし、得られた知見を活用して強力な本番アプリケーションを構築してください。詳細と例については、以下のリソースを参照してください。

* **まず実験**: 事前設定されたエージェントで [ML playground](https://ml.playground.opensearch.org/app/opensearch-flow#/workflows) でエージェント検索を試してください。
* **実装の計画**: [エージェント検索 OpenSearch Dashboards ドキュメント](https://docs.opensearch.org/latest/vector-search/ai-search/building-agentic-search-flows/)を確認してください。
* **アーキテクチャの理解**: [エージェント検索ドキュメント](https://docs.opensearch.org/latest/vector-search/ai-search/agentic-search/index/)を参照してください。
* **例から学ぶ**: [以前のエージェント検索ブログ記事](https://opensearch.org/blog/introducing-agentic-search-in-opensearch-transforming-data-interaction-through-natural-language/)を読んでください。
