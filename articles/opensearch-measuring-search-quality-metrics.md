---
title: "[翻訳] 検索品質メトリクスの測定と改善"
emoji: "📊"
type: "tech"
topics: ["opensearch", "search", "metrics", "relevance"]
published: true
publication_name: "opensearch"
published_at: 2025-09-17
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/measuring-and-improving-search-quality-metrics/

![タイトル画像](/images/opensearch-measuring-search-quality-metrics/0_title_image.jpg)
_画像出典: DALL·E 3 で作成_

## 変化の観測から検索品質の測定へ

この 3 部構成シリーズの最初の記事では、ある検索設定から別の設定に切り替える際の[変化の測定方法](https://opensearch.org/blog/taking-your-first-steps-towards-search-relevance/)に焦点を当てました。検索結果のドキュメントがどのように遷移するかを視覚的に探索し、メトリクスを使ってこの変化を客観的に定量化しました。

変化はリスクの重要な指標です。測定される変化が大きいほど、基盤となる検索アルゴリズムの調整はリスクが高くなります。具体的な差異を目視で確認することで、検索担当者は潜在的な品質への影響について第一印象を得ることができます。

しかし、変化を定量化するだけでは、2 つの結果リストがどれだけ異なるかがわかるだけで、この変化の品質については何もわかりません。

この記事では、変化の測定を超えて、関連性と検索結果の品質を理解することを目指します。判定 (judgment) の概念、検索品質の定量化における役割、そして [OpenSearch 3.1 でリリースされた](https://opensearch.org/blog/get-started-with-opensearch-3-1/) Search Relevance Workbench が、体系的な検索品質改善への次のステップをどのようにサポートするかを紹介します。

## 目標: 検索品質の定量化

検索品質の測定は、あらゆる検索チームにとって基盤となる資産です。測定できないものは改善できないからです。検索担当者として、「良い」結果とは何か、またはそれにつながるアイデアについて直感を持っているかもしれませんが、それを証明するには体系的なアプローチが必要です。

体系的なアプローチの必要性は、単に結果を目視で比較することを超えています。Search Relevance Workbench には、これを支援するいくつかの機能があります。最初の記事で紹介したクエリセットと検索設定の概念を引き続き使用します。

- [クエリセット](https://docs.opensearch.org/docs/latest/search-plugins/search-relevance/query-sets/): クエリセットは、検索アプリケーションのドメインに関連するクエリのコレクションです。
- 検索設定: [検索設定](https://docs.opensearch.org/docs/latest/search-plugins/search-relevance/search-configurations/)は、Search Relevance Workbench 内の実験でクエリをどのように実行するかを指定します。

これらの概念を超えて、Search Relevance Workbench で検索品質を測定する方法を探っていきましょう。

## Search Relevance Workbench: メトリクスと判定リスト

判定リストは検索品質を定量化するための基盤となる資産であり、良い検索結果と悪い検索結果がどのようなものかを示してくれます。簡単に言えば、判定リストにはクエリ、ドキュメント、評価の 3 つ組が含まれています。

例: `t towels kitchen, B08TB56XBX, 1.0`

この 3 つ組は、クエリ「t towels kitchen」に対して、ID「B08TB56XBX」のドキュメントの評価が 1.0 であることを示しています。検索品質を適切に測定するには、複数の判定が必要であり、そのため判定リストという用語を使用します。

通常、判定は暗黙的と明示的の 2 種類に分類されます。暗黙的判定は、どの結果が表示されクリックされたかなど、ユーザーの行動から導き出される評価です。従来、明示的判定は人間によって行われていましたが、現在では大規模言語モデル (LLM) がこの役割を担うことが増えています。[Search Relevance Workbench はすべての種類の判定をサポートしています](https://docs.opensearch.org/latest/search-plugins/search-relevance/judgments/)。

- [User Behavior Insights (UBI) スキーマ仕様](https://docs.opensearch.org/docs/latest/search-plugins/ubi/index/)に準拠したデータに基づいて暗黙的判定を生成できます。
- API または内部/外部でホストされたモデルに OpenSearch を接続することで、LLM を活用して判定を生成する機能を提供しています。
- すでに判定を生成するプロセスを持っている OpenSearch ユーザーのために、Search Relevance Workbench はそれらをインポートすることもできます。

この 3 部構成シリーズの最初の記事では、キーワード検索設定とハイブリッド検索設定の間の変化を測定し、そのような切り替えがどれほど異なり、潜在的に有用であるかの印象を得ることに焦点を当てました。

### Search Relevance Workbench を使用した OpenSearch のセットアップ

このシリーズの最初のパートをすでに実行し、OpenSearch のインストールが準備できている場合は、セットアップ手順をスキップして、前提条件の検証セクションに進むことができます。

**環境のセットアップ**
このガイドに従うには、Search Relevance Workbench を備えた OpenSearch インスタンスが必要です。以下の手順では、必要なリポジトリをクローンし、必要なすべてのデータとプラグインを備えたローカル OpenSearch クラスターを起動します。これらの手順に従うことで、サンプルの e コマース製品データを含む OpenSearch セットアップを構成し、検索結果の品質を測定するために使用します。

まず、[このブログ記事シリーズに付随するリポジトリ](https://github.com/o19s/srw-blogs)をクローンします。

```bash
git clone https://github.com/o19s/srw-blogs.git
```

次に、リポジトリのディレクトリに移動し、Docker コンテナを起動します。

```bash
cd srw-blogs
docker compose up -d
```

**OpenSearch のセットアップとデータのインデックス作成**
次に、[Search Relevance Workbench バックエンドリポジトリ](https://github.com/opensearch-project/search-relevance)をクローンします。このリポジトリにはサンプルデータとすべてを素早くセットアップするスクリプトが含まれています。

```bash
git clone https://github.com/opensearch-project/search-relevance.git
```

スクリプトディレクトリに移動し、セットアップスクリプトを実行します。

```bash
cd search-relevance/src/test/scripts
./demo_hybrid_optimizer.sh
```

このスクリプトは以下のアクションを実行します。Search Relevance Workbench バックエンド機能を備えた OpenSearch インスタンスをセットアップし、製品データ (埋め込みを含む) をインデックス化し、キーワード検索とハイブリッド検索の両方の設定の検索品質を測定するための環境を準備します。

### クエリセットの作成

このシリーズの最初の記事では、検索設定間の変更の影響を理解するためにクエリセットを使用しました。ここでは、同様のクエリセットを使用して、次のレベルの洞察、つまり異なる検索設定が検索品質に与える影響を測定します。

このガイドでは、[このシリーズに付随する GitHub リポジトリ](https://github.com/o19s/srw-blogs/blob/main/freshman/freshman_blog_query_set.txt)で提供されているクエリセットを手動で作成します。

```json
{"queryText": "laptop"}
{"queryText": "red shoes"}
{"queryText": "in-ear headphones"}
{"queryText": "portable bluetooth speakers"}
{"queryText": "stainless steel mending plates"}
{"queryText": "funny shirt birthday present"}
```

このファイルは、Search Relevance Workbench の OpenSearch Dashboards UI でドラッグアンドドロップ機能を使用してアップロードできます。または、対応する API を使用することもできます。[前回のブログ記事](https://opensearch.org/blog/taking-your-first-steps-towards-search-relevance/)に従ってすでにこのクエリセットを作成している場合は、それを使用してください。

クエリセットを作成する API 呼び出しは以下の通りです。

```json
PUT _plugins/_search_relevance/query_sets
{
  "name": "SRW Blog Post Query Set",
  "description": "A query set for the SRW blog post with six queries",
  "sampling": "manual",
  "querySetQueries": [
    {"queryText": "laptop"},
    {"queryText": "red shoes"},
    {"queryText": "in-ear headphones"},
    {"queryText": "portable bluetooth speakers"},
    {"queryText": "stainless steel mending plates"},
    {"queryText": "funny shirt birthday present"}
  ]
}
```

### 検索設定の作成

次に、キーワード検索用とハイブリッド検索用の 2 つの検索設定を作成する必要があります。最初のブログ記事と同じ設定を使用します。すでにインストールにこれらがある場合は、再利用できます。

API を使用して検索設定を 1 つずつアップロードできます。

**キーワード検索設定の作成**
まず、キーワード検索用の検索設定を作成しましょう。

```json
PUT _plugins/_search_relevance/search_configurations
{
  "name": "keyword",
  "query": """{"query":{"multi_match":{"query":"%SearchText%","fields":["id","title","category","bullet_points","description","brand","color"]}}}""",
  "index": "ecommerce"
}
```

ハイブリッド検索設定を作成するには、まずユーザークエリの埋め込みを生成するために使用される `model_id` を見つける必要があります。以下のように検索して ID を見つけることができます。

```json
POST /_plugins/_ml/models/_search
{
  "query": {
    "match_all": {}
  },
  "size": 1
}
```

レスポンスは以下のようになります。`_source` フィールドの `model_id` に注目してください。これを次のステップで使用します。

```json
{
  "took": 62,
  "timed_out": false,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": {
      "value": 11,
      "relation": "eq"
    },
    "max_score": 1,
    "hits": [
      {
        "_index": ".plugins-ml-model",
        "_id": "VI1WMZgBm3ZaLrDFy2Ij_2",
        "_version": 1,
        "_seq_no": 3,
        "_primary_term": 1,
        "_score": 1,
        "_source": {
          "model_version": "1",
          "created_time": 1753174432098,
          "chunk_number": 2,
          "last_updated_time": 1753174432098,
          "model_format": "TORCH_SCRIPT",
          "name": "huggingface/sentence-transformers/all-MiniLM-L6-v2",
          "is_hidden": false,
          "model_id": "VI1WMZgBm3ZaLrDFy2Ij",
          "total_chunks": 10,
          "algorithm": "TEXT_EMBEDDING"
        }
      }
    ]
  }
}
```

**ハイブリッド検索設定の作成**

これでハイブリッド検索設定を作成できます。`VI1WMZgBm3ZaLrDFy2Ij` を自分の `model_id` に置き換えることを忘れないでください。

```json
PUT _plugins/_search_relevance/search_configurations
{
  "name":"hybrid search",
  "index":"ecommerce",
  "query":"{\"query\":{\"hybrid\":{\"queries\":[{\"multi_match\":{\"query\":\"%SearchText%\",\"fields\":[\"id\",\"title\",\"category\",\"bullet_points\",\"description\",\"brand\",\"color\"]}},{\"neural\":{\"title_embedding\":{\"query_text\":\"%SearchText%\",\"k\":100,\"model_id\":\"VI1WMZgBm3ZaLrDFy2Ij\"}}}]}},\"size\":10,\"_source\":[\"id\",\"title\",\"category\",\"brand\",\"image\"]}",
  "searchPipeline":"normalization-pipeline"
}
```

**代表的なクエリセットの重要性**
検索品質を体系的に測定するには、ユーザーベース全体を反映する幅広く代表的なクエリセットを使用することが重要です。理想的には、クエリセットは実際のユーザークエリからサンプリングされます。[Search Relevance Workbench はこれをサポートしており](https://docs.opensearch.org/docs/latest/search-plugins/search-relevance/query-sets/)、[Probability-Proportional-to-Size サンプリング](https://opensourceconnections.com/blog/2022/10/13/how-to-succeed-with-explicit-relevance-evaluation-using-probability-proportional-to-size-sampling/)と呼ばれるサンプリング手法を提供しています。ただし、このブログ記事の目的では、6 つのクエリのセットで明確で理解しやすい例として十分です。

### 前提条件の検証

検索品質実験を実行するために必要なものがすべて揃っていることを確認するには、Search Relevance Workbench UI に移動します。

1. Web ブラウザを開き、[http://localhost:5601](http://localhost:5601/) にアクセスします。
2. 左側のナビゲーションメニューで **Search Relevance** を選択します。
   **注意:** Search Relevance Workbench は OpenSearch 3.1 時点でオプトイン機能です。まだ有効にしていない場合は、**Management > Dashboards Management > Advanced Settings** に移動し、**Experimental Search Relevance Workbench** のトグルをオンにして、変更を保存する必要があります。

**クエリセットの確認**
次に、クエリセットが存在することを確認します。

1. **Query Sets** セクションに移動します。
2. **SRW Blog Post Query Set** という名前のクエリセットを選択します。
3. 詳細ビューで、作成した 6 つのクエリが表示されるはずです。

![クエリセットの詳細](/images/opensearch-measuring-search-quality-metrics/1_query_set_details-1.png)

**検索設定の確認**
検索設定が存在することを確認するには、**Search Configurations** セクションに移動します。**keyword** と **hybrid search** の両方の設定がリストに表示されるはずです。

まず、**keyword** 設定を選択します。

キーワード検索の詳細が表示され、先ほど作成した設定と一致するはずです。インデックス名 **ecommerce** と multi-match クエリが表示されます。

![キーワード検索設定](/images/opensearch-measuring-search-quality-metrics/2_keyword_search_configuration.png)

次に、**hybrid search** 設定を選択します。クエリはキーワード設定で使用されたものとは異なり、ハイブリッド検索クエリが含まれています。

![ハイブリッド検索設定](/images/opensearch-measuring-search-quality-metrics/3_hybrid_search_configuration.png)

### 判定リストの理解

設定が確認できたので、検索品質を測定するために必要な新しい要素、判定リストに目を向けましょう。

このガイドでは、2 つの検索設定で取得するすべてのクエリ-ドキュメントペアの評価を含む判定リストをインポートします。まず、その構造を見てみましょう。

```json
{
  "name": "SRW Blog Post Judgments",
  "description": "Imported judgment list for the SRW blog post",
  "type": "IMPORT_JUDGMENT",
  "judgmentRatings": [
    {
      "query": "funny shirt birthday present",
      "ratings": [
        {
          "docId": "B07PH417T1",
          "rating": "3.000"
        },
        {
          "docId": "B08ZM5VN5S",
          "rating": "0.000"
        },
        …
```

この JSON 構造は、判定がどのように整理されているかを示しています。`judgmentRatings` の各エントリはクエリに対応し、各クエリ内には特定のドキュメントの評価リストがあります。各評価は `docId` と数値の `rating` を含む 3 つ組です。これにより、特定のクエリに対する各ドキュメントの関連性を定量化できます。

### 判定リストのアップロード

Search Relevance Workbench の外部でコンパイルされた `IMPORT_JUDGMENT` タイプの判定リストをインポートします。これにより、判定リストを使用して検索品質を測定することに集中できます。判定リストの作成というトピックは、それ自体で別のブログ記事を書くに値するほど広範なので、この記事の最後に始めるための実用的なヒントをいくつか共有します。

各クエリに対して、インポートされたリストは一連の判定を提供し、それぞれが `docId` (検索インデックス内のドキュメントの一意の識別子) と 0 から 3 のスケールの `rating` で構成されています。評価は、特定のクエリに対するドキュメントの関連性を示します。評価が高いほど、ドキュメントの関連性が高くなります。

- **0:** まったく関連性がない。
- **1:** わずかに関連性がある。関連する情報が含まれているが、クエリに直接対応していない。
- **2:** 中程度に関連性がある。クエリの一部に対応しているか、一般的に有用。
- **3:** 非常に関連性が高い。クエリに直接回答し、非常に有用。

このガイドでは、LLM **GPT-4o mini** によって作成された明示的判定リストを使用します。このリストは、プロセスを示すために Search Relevance Workbench にインポートするためにすでにフォーマットされています。

判定リストをアップロードするには、クローンしたリポジトリのルートディレクトリから以下の `curl` コマンドを実行します。このコマンドは、判定リストを Search Relevance Workbench の対応する API エンドポイントに POST します。

```bash
curl -s -X PUT "localhost:9200/_plugins/_search_relevance/judgments" \
  -H "Content-type: application/json" \
  --data-binary @./part2/judgments.json
```

API は、新しくアップロードされた判定リストの一意の ID で応答します。

```json
{ "judgment_id": "4451a0ee-5b59-44d3-97d7-af893f2b81d3" }
```

これですべての前提条件が整ったので、すべてのピースを組み合わせて実験を作成し実行します。

### 検索品質を測定するための検索メトリクスの計算

検索品質のための信頼できる「物差し」を作成するという目標に戻ると、必要なすべてのコンポーネントが揃いました。**クエリセット**、2 つの**検索設定** (キーワード検索用とハイブリッド検索用)、そしてクエリ-ドキュメントペアの関連性評価を提供する**判定リスト**です。

Search Relevance Workbench では、検索品質メトリクスを計算するプロセスは実験内に組み込まれています。最初のブログ記事では、検索結果リストの比較を示しました。ここでは、次の実験タイプである**検索評価実験** (ポイントワイズ実験とも呼ばれる) を紹介します。

[検索評価実験](https://docs.opensearch.org/docs/latest/search-plugins/search-relevance/evaluate-search-quality/)には 5 つのパラメータが必要です。

- `querySetId`: クエリセットの ID。
- `searchConfigurationList`: 比較に使用する検索設定 ID のリスト。
- `judgmentList`: 検索精度の評価に使用する判定リストの ID。
- `size`: メトリクス計算のために結果に返すドキュメント数。
- `type: POINTWISE_EVALUATION` は、判定に対して検索設定を評価するためのタイプです。

Search Relevance Workbench のフロントエンドは、この実験の設定を支援します。OpenSearch Dashboards で、**Search Relevance > Experiments > Search Evaluation** に移動します。

2 つの検索設定 (**keyword** と **hybrid search**) の検索品質を測定し、どちらがより良いパフォーマンスを発揮するかを判断するために、2 つの別々の実験を作成します。

両方の実験は同じ**クエリセット**と**判定リスト**を使用します。唯一の違いは、それぞれで使用される検索設定です。

これら 2 つの実験を作成し、一方にキーワード検索設定を、もう一方にハイブリッド検索設定を割り当てます。設定が完了したら、**Start Evaluation ボタン**を選択して各実験を確認します。

![実験の定義](/images/opensearch-measuring-search-quality-metrics/4_experiment_definition.png)

**実験プロセス**
実験プロセス中、クエリセット内の 6 つのクエリそれぞれについて、対応する検索設定を使用して上位 10 件の検索結果が取得されます。これにより、検索設定ごとに最大 60 のクエリ-ドキュメントペアが生成されます。各ペアについて、実験は判定リストで関連性評価をチェックします。

すべてのクエリ-ドキュメントペアに判定があるわけではないことは一般的であり、まったく問題ありません。通常、判定が利用できない場合、検索メトリクスはドキュメントが無関係であると仮定します。判定が欠落する理由はいくつかあります。

- **明示的判定:** 人間または LLM による判定の場合、異なる検索設定が以前に評価されていない新しい上位 N ドキュメントのセットを返す可能性があります。
- **暗黙的判定:** ユーザーの行動に基づく判定は、ユーザーが接触したクエリ-ドキュメントペアに対してのみ作成できます。ドキュメントがユーザーの検索結果に表示されなかった場合、判定を形成するための行動データはありません。

![実験の概要](/images/opensearch-measuring-search-quality-metrics/5_experiments_overview.png)

**実験完了の確認**
開始後すぐに、2 つの実験が実験概要テーブルに表示されるはずです。両方がタイプ **Evaluation** で、ステータスが **COMPLETED** であることを確認してステータスを検証できます。

最初の実験を選択すると、結果ビューに移動します。

![単一実験の結果ビュー](/images/opensearch-measuring-search-quality-metrics/6_single_experiment_result_view.png)

**検索メトリクスとその意味**
表示される検索メトリクスは **Precision、Mean Average Precision (MAP)**、および **Normalized Discounted Cumulative Gain (NDCG)** です。さらに、**Judgment Coverage (Coverage)** が計算され、他のメトリクスの信頼性についてユーザーに感覚を与えます。

- **Coverage:** Coverage@k は、検索結果内のクエリ-ドキュメントペアのうち、関連性判定を持つものの割合を表します。返されたデータのうちどれだけが関連性について評価されているかを示し、計算されたメトリクスの信頼性の尺度を提供します。
- **Precision:** Precision@k は、取得されたドキュメントのうち関連性のあるものの割合を測定します。特定のランク k に対して、Precision@k は上位 k 件の結果の中の関連ドキュメント数を k で割ったものです。
- **MAP:** MAP@k は、異なる再現率レベルにわたる品質の単一数値の尺度です。単一のクエリに対して、Average Precision (AP) は各関連ドキュメントのランクで計算された精度値の平均です。MAP は、すべてのクエリにわたるこれらの AP スコアの平均です。
- **NDCG:** NDCG@k は、結果リスト内の位置に基づいてドキュメントの有用性 (ゲイン) を測定します。ゲインはリストの上部から蓄積され、下位ランクのドキュメントの関連性は「割引」されます。スコアは 0 から 1 の間に正規化され、1 は完璧なランキングを表します。

### 集計検索メトリクスの解釈

2 つの実験が完了したので、結果を見てみましょう。集計メトリクスは、ハイブリッド検索アプローチを使用した検索設定が勝者であることを示しています。

以下はキーワード検索設定のメトリクスです。

![キーワード検索評価結果](/images/opensearch-measuring-search-quality-metrics/7_keyword_search_eval_results.png)

以下はハイブリッド検索設定のメトリクスです。

![ハイブリッド検索評価結果](/images/opensearch-measuring-search-quality-metrics/8_hybrid_search_eval_results.png)

これらの数値を解釈しましょう。**judgment coverage** は両方の検索設定で等しく (0.93)、**precision** も同様です (0.82)。しかし、**MAP** (0.60 vs. 0.55) と **NDCG** (0.82 vs. 0.69) のスコアはハイブリッド検索の方が高くなっています。

同一の precision スコア 0.82 は、両方の検索設定が関連ドキュメントの取得において同等に効果的であることを示しています。このメトリクスでは、関連ドキュメントはゼロ以外の判定評価を持つものとして定義されています [(この定義は将来の実装で変更される可能性があります)](https://github.com/opensearch-project/search-relevance/issues/30)。

より高い **MAP** スコアは、ハイブリッド検索設定が関連ドキュメントをより頻繁に上位に配置することを示しています。

より高い **NDCG** スコアは、取得された結果が理想的な関連ドキュメントのセットに近いだけでなく、判定リスト内のすべてのクエリ-ドキュメント判定に従った理想的なランキングにも近いことを示しています。

### 個別クエリの検索メトリクスの解釈

集計メトリクスは一般的な方向性を提供しますが、個別のクエリレベルを見ることは常に重要です。個別クエリのメトリクスを調べることで、ハイブリッド検索設定から最も恩恵を受ける**クエリのクラス**を理解するのに役立ちます。さらに、アプリケーションにとって特に重要なクエリの検索品質が低下しないことを確認できます。

以下のスクリーンショットでは、キーワード検索設定の個別検索メトリクス (左側) がハイブリッド検索設定のもの (右側) と並べて表示されています。

![サイドバイサイドのクエリ検索評価結果](/images/opensearch-measuring-search-quality-metrics/9_side_by_side_query_search_eval_results.png)

6 つのクエリの結果を見ると、ハイブリッド検索設定でキーワード検索よりも低い個別メトリクスは 2 つだけであることがわかります。

- **「Red shoes」**: 「red shoes」の precision は 0.60 から 0.50 に低下し、上位 10 件の結果の judgment coverage も 0.60 から 0.50 に減少しました。これは、ハイブリッド検索がキーワード検索よりも 1 つ少ない関連結果を取得したことを意味します。しかし、MAP と NDCG のスコアは増加しており、1 つ少ない関連ドキュメントを取得したにもかかわらず、結果の順序が改善されたことを示しています。
- **「Stainless steel mending plates」**: このクエリの NDCG は完璧な 1.00 から 0.93 に低下しました。これは、取得された結果の順序が悪化したことを示していますが、結果は全体的にまだ高品質です。

### ダッシュボードでの実験結果の表示

表形式は、個別クエリ (特にトップパフォーマー、低パフォーマー、またはビジネスクリティカルなもの) のメトリクスを調べるのに優れていますが、数十、数百、または数千のクエリを含むクエリセットでは扱いにくくなります。

実験結果をより簡単に視覚的に探索できるようにするため、Search Relevance Workbench はバージョン 3.2 からダッシュボードと統合されています。**Experiments** 概要ページの右上隅にある対応するボタンを選択してダッシュボードをインストールできます。

![ダッシュボードインストールボタン](/images/opensearch-measuring-search-quality-metrics/10_install_dashboards_button.png)

表示されるモーダルでインストールを確認すると、ダッシュボードが探索可能になります。

![ダッシュボードインストール確認ボタン](/images/opensearch-measuring-search-quality-metrics/11_confirm_install_dashboards_button.png)

ダッシュボードのインストールが成功したら、実験概要テーブルの視覚化アイコンを選択して、興味のある実験の結果を探索できます。アイコンは、表示したい特定の実験の行にあり、スクリーンショットでは青色でマークされています。

![実験テーブルの視覚化アイコン](/images/opensearch-measuring-search-quality-metrics/Screenshot-2025-09-16-at-3.58.12-PM.png)

これにより、実験のダッシュボードが開き、その詳細と結果の包括的な概要が提供されます。

![評価の視覚化](/images/opensearch-measuring-search-quality-metrics/12_eval_visualization.png)

ダッシュボードは、実験結果を分析するための 4 つの視覚化を提供します。

- **Deep Dive Summary:** このペインは、NDCG、MAP、Precision、Coverage の集計メトリクスを表示し、**Experiment** 詳細ページの数値と同一です。
- **Deep Dive Query Scores:** この視覚化は、個別クエリのパフォーマンスを NDCG スコア (高い順から低い順) でランク付けし、最高および最低パフォーマンスのクエリを素早く特定するのに役立ちます。
- **Deep Dive Score Densities:** このペインを使用して、クエリセット全体でメトリクス値がどのように分布しているかを理解します。x 軸はメトリクス値を示し、y 軸はその頻度を示し、パフォーマンスの低下が広範囲に及んでいるか集中しているかを判断するのに役立ちます。
- **Deep Dive Score Scatterplot:** このインタラクティブビューは、Score Densities ペインと同じ分布データを表示し、各クエリは個別のポイントとして表されます。パフォーマンスの極端な位置にある特定のクエリを調査するために使用します。ポイントは、同じ x 軸メトリクス値を維持しながら重複を防ぐために垂直方向に散らばっています。

これらのダッシュボードは、外れ値を特定し、実験から得られる検索メトリクスの分布を理解するのに非常に役立ちます。

**オフラインからオンライン実験へ**
実験に戻ると、減少した検索メトリクスは非常に少なく、特に個別クエリレベルの他のすべてのメトリクスが増加していることを考えると、許容できるように見えます。6 クエリセットでのオフライン実験から検索品質メトリクスを分析することで、純粋なキーワードベースの検索戦略からハイブリッドへの切り替えが、エンドユーザーの検索結果品質を向上させる可能性があることを確信できるようになりました。

おめでとうございます！2 つの検索設定のパフォーマンスを比較するためのオフライン検索品質評価を正常に実行しました。

この仮説を検証するための次の論理的なステップは、**オンライン実験**であり、ユーザートラフィックの一部にハイブリッド検索を公開します。**A/B テスト**は、[チームドラフトインターリービングによるオンラインテスト](https://opensourceconnections.com/blog/2025/08/06/a-b-testing-with-team-draft-interleaving/)の形で Search Relevance Workbench のロードマップに含まれています。チームドラフトインターリービングサポートについての考えを共有するために、[GitHub でのディスカッションに参加](https://github.com/opensearch-project/OpenSearch/issues/18383)できます。

## 判定リストの構築: 実用的なヒント

このブログ記事で示したように、検索品質の測定には 3 つの主要なコンポーネントが必要です。**クエリセット**、**検索設定**、および**判定リスト**です。これらの中で作成が最も難しいのは判定リストであることが多いため、始めるための実用的なヒントをいくつか紹介します。

### 明示的判定

人間または LLM を使用して判定リストを作成する場合、高品質なリストは以下のガイドラインに従うことに依存します。

- **明確なタスクを定義する:** 判定者に明確で簡潔なタスク定義を提供します。この活動に固有の主観性を減らすために、クエリ-ドキュメントペアをどのように評価するかについてできるだけ多くの情報を提供します。
- **バイアスを最小化する:** バイアスの影響を最小化するツールまたは設計フレームワークを使用します。[Quepid](https://go.quepidapp.com/) などの人間または LLM の評価を収集するためのツールは、一般的なバイアスを軽減するのに役立ちます。独自の判定収集プロセスを設計する場合は、既知のバイアスに積極的に対抗するようにしてください。
- **一致度を測定する:** 異なる方法を使用して判定を収集し、それらの間の一致度を測定します。2 人の異なる判定者が 100% 一致することはまずありません。判定者が一致する場合と一致しない場合を調べることで、タスク定義をより良い整合性と明確さのために改善する方法についての追加の洞察を得ることができます。

Search Relevance Workbench の LLM 支援判定リスト作成機能を探索することをお勧めします。結果の判定を確認して、それらがあなたの直感と期待にどれだけ一致するかを確認してください。判定者としての LLM は活発な研究分野であり、近い将来この分野でさらなる発展が期待できます。

### 暗黙的判定

暗黙的判定の品質は、収集された行動データとそのデータを判定にマッピングするために使用される基礎モデルに大きく依存します。高品質な判定リストを確保するには、以下のヒントに従ってください。

- **適切な情報を収集する。** 最低限、ユーザーが閲覧したドキュメントとそれに続くインタラクション (例: クリック、カートに追加) を、位置情報とともに収集する必要があります。デバイスタイプやログインステータスなどのより多くのコンテキストデータは、判定のバイアスを除去するのに役立ちます。[UBI](https://docs.opensearch.org/latest/search-plugins/ubi/index/) などのオープンスタンダードがこれに役立ちます。
- **クリックモデルを理解する。** 行動データには、位置バイアスや表示バイアスなどのバイアスが含まれていることがよくあります。選択したクリックモデルとその実装がデータのバイアスをどのように除去するかを理解することが重要です。
- **Search Relevance Workbench で暗黙的判定を探索する。** UBI 標準に準拠したユーザー行動データがある場合、[ワークベンチに実装された Clicks over Expected Clicks モデルを使用して暗黙的判定を計算](https://docs.opensearch.org/latest/search-plugins/search-relevance/judgments/#implicit-judgments)できます。

### すべての判定リストに対する一般的なヒント

すべての判定リストのベストプラクティスは、オンラインでテストすることです。リスト内の判定に従っていくつかのクエリの結果をソートし、結果を観察します。これは、連続スケールを使用する暗黙的判定に特に有用です。また、ユーザーのフィードバックが判定者と一致しない場合、明示的判定の問題を明らかにするのにも役立ちます。

## まとめ

Search Relevance Workbench を使用して、単純な変化検出から検索品質を評価するための体系的でメトリクス駆動のアプローチへと進歩しました。このプロセス (クエリセット、判定リスト、オフライン実験を使用) は、検索設定について情報に基づいた決定を行うための堅牢な基盤を提供します。

この 3 部構成シリーズの次の最終記事では、検索関連性最適化ライフサイクル内で複雑な実験をセットアップする方法と、ワークベンチがどのように支援できるかについて説明します。

この方法論を独自の検索プラットフォームに適用することをお勧めします。Search Relevance Workbench ツールセットに関するフィードバックを [OpenSearch フォーラム](https://forum.opensearch.org/)でお待ちしています。
