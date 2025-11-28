---
title: "[翻訳] 検索関連性向上への第一歩"
emoji: "🔍"
type: "tech"
topics: ["opensearch", "relevance", "search"]
  - "opensearch"
  - "関連性"
  - "検索精度"
  - "検索エンジン"
published: true
publication_name: "opensearch"
published_at: 2025-08-13
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/taking-your-first-steps-towards-search-relevance/

## 検索結果がイマイチだと感じていませんか?

完璧な検索結果が得られたら素晴らしいと思いませんか? 実際、検索の世界では、多くの実務者がそれを奇跡と呼ぶでしょう。検索結果の品質向上への取り組みに終わりはありません。Learning to Rank、セマンティック検索、ハイブリッド検索といった AI を活用した技術があっても、検索の専門家たちは常により良い結果を追求し続けています。ある意味、新しい技術を追加することで課題が増えることもあります。

検索結果に問題を抱えているのはあなただけではありません。[OpenSearch 3.1](https://opensearch.org/blog/get-started-with-opensearch-3-1/) では、実験を通じて検索関連性を改善・微調整するための包括的なツールキットである Search Relevance Workbench が導入されました。

Search Relevance Workbench は、あらゆる経験レベルの検索専門家向けに設計されています。この 3 部構成の記事シリーズの最初の記事では、検索実務者が直面する一般的な課題を探り、このツールキットがガイダンスとサポートを提供しながらこれらの問題を解決する方法を紹介します。この最初の記事は、問題のある検索クエリがあることは認識しているものの、調査・診断の方法がわからないユーザーを対象としています。

## 原因不明の問題を抱えるクエリ

検索品質の改善への道のりは、多くの場合、理想的とは言えない結果をもたらすユーザークエリから始まります。しかし、検索チームやプロダクトチームのすべてのメンバーが、包括的な検索関連性ツール一式にアクセスできるわけではありません。最初のステップとして情報を収集するために、視覚的な探索から始めたいユーザーもいます。

検索実務者の一般的な目標は、問題のあるクエリを理解し、検索結果の品質を向上させるために追求する価値のあるアイデアを生み出すことです。従来、このような状況では、検索エンジンがクエリの診断や修正手段をほとんど、あるいはまったく提供していなかったため、検索チームは独自の評価ツールやプロセスを構築していました。

これらのユーザーはクエリ文字列 (ユーザーが検索バーに入力する内容) は知っているかもしれませんが、その後何が起こるかは把握していません。これは、警告灯が点灯している車を運転しているようなもので、問題を調査したり修正したりするための整備士のツールがない状態です。

Search Relevance Workbench は、問題のあるクエリを視覚的に探索する方法を提供することで、このギャップに対処します。異なる検索設定間で検索結果を比較できるユーザーインターフェースを提供し、チームが検索パフォーマンスを効果的に診断・改善できるようにします。

## 新しいツールキット: Search Relevance Workbench

本記事に沿って進めるには、付属のリポジトリをクローンしてください。

```bash
git clone https://github.com/o19s/srw-blogs.git
cd srw-blogs
docker compose up -d
```

次に、サンプルデータと素早くセットアップするためのスクリプトが含まれている SRW バックエンドリポジトリをクローンします。

```bash
git clone https://github.com/opensearch-project/search-relevance.git
cd search-relevance/src/test/scripts
./demo_hybrid_optimizer.sh
```

このスクリプトは、Search Relevance Workbench バックエンド機能が有効になった OpenSearch インスタンスをセットアップします。ハイブリッド検索の設定を探索できるように、商品データ (埋め込みを含む) をインデックスします。

キーワード検索を実行して、いくつかの商品を見てみましょう。[http://localhost:5601](http://localhost:5601/) の OpenSearch Dashboards にアクセスし、Dev Tools で以下の multi_match クエリを実行します。

```json
GET ecommerce/_search
{
  "query": {
    "multi_match": {
      "query": "laptop",
      "fields": ["id", "title", "category", "bullet_points", "description", "brand", "color"]
    }
  },
  "_source": ["id", "title", "category", "brand"]
}
```

ecommerce インデックスの複数のフィールド ("id", "title", "category", "bullet*points", "description", "brand", "color") で \_laptop* を検索しています。しかし、取得した結果はあまり良くありません。ラップトップデスク、折りたたみベッドテーブル、防水ラップトップケース、ラップトップバックパックなどが表示されます。これは EC サイトでよくあるアクセサリー問題のようです。探している商品ではなく、それらの商品のアクセサリーが多く表示されてしまいます。

検索の専門家として、キーワードベースとベクトルベースの検索を組み合わせたハイブリッド検索アプローチが結果をどのように変えるか興味があるかもしれません。ハイブリッド検索クエリを実行するには、まずニューラル検索コンポーネントに使用できる model_id を知る必要があります。デモスクリプトはすでにモデルのアップロードを処理しており、使用準備が整っています。続行するには、以下のリクエストを使用してモデルを検索し、レスポンスで model_id を見つけてください。

```json
POST /_plugins/_ml/models/_search
{
  "query": {
    "match_all": {}
  },
  "size": 1
}
```

これでハイブリッド検索クエリを実行する準備ができました。model_id (この場合は lZBXE5gBRVO0vZIAKepk) をコピーし、以下のリクエストをカスタマイズして、あなたの model_id を使用してください。

```json
GET ecommerce/_search?search_pipeline=normalization-pipeline
{
  "query": {
    "hybrid": {
      "queries": [
        {
          "multi_match": {
            "query": "laptop",
            "fields": ["id", "title", "category", "bullet_points", "description", "brand", "color"]
          }
        },
        {
          "neural": {
            "title_embedding": {
              "query_text": "laptop",
              "k": 100,
              "model_id": "lZBXE5gBRVO0vZIAKepk"
            }
          }
        }
      ]
    }
  },
  "size": 10,
  "_source": ["id", "title", "category", "brand"]
}
```

ハイブリッド検索シナリオでのスコア正規化に必要な "normalization-pipeline" 検索パイプラインを使用していることに注意してください。このパイプラインが必要な理由の詳細については、[スコアの正規化と結合に関するドキュメント](https://docs.opensearch.org/docs/latest/search-plugins/search-pipelines/normalization-processor/)を参照してください。

結果を見ると、改善されているようです。1 位に Lenovo Chromebook、3 位に HP ラップトップなどが表示されています。関連性の低い結果もまだいくつか表示されていますが、全体的に変更は有望に見えます。

しかし、2 つのブラウザウィンドウを開いて横に並べ、すべてのアイテムを 1 つずつ比較しないと、2 つの結果セットの違いを評価するのは困難です。

ここで最初の Search Relevance Workbench ツールが役立ちます。個別クエリの横並び比較ツールです。

## 単一クエリ: アドホックな探索と即時フィードバック

まだ行っていない場合は、以下の 3 つのステップでフロントエンドプラグインを有効化してください。

1. OpenSearch Dashboards で Management > Dashboards Management > Advanced Settings に移動
2. Experimental Search Relevance Workbench のトグルをオンにする
3. 変更を保存

フロントエンド機能を有効化すると、Search Relevance Workbench の "Single Query Comparison" に移動して単一クエリ比較ツールにアクセスできます。

この最初のツールでは、インデックスに対して実行される 2 つのクエリを指定できます。結果が比較され、2 つの違いをすばやく把握できます。

比較したい 2 つのクエリは、どちらも _ecommerce_ インデックスを対象としています。

Query 1 は、パイプラインなしで複数のフィールドを対象とした従来のキーワードベース検索を表しています。クエリ本体は先ほど実行したキーワードクエリと似ていますが、2 つの変更点があります。

- 商品画像を表示するための追加の _image_ フィールドを返すようにしています。
- ユーザーのクエリ文字列の代わりに変数 '%SearchText%' を使用しています。

```json
{
  "query": {
    "multi_match": {
      "query": "%SearchText%",
      "fields": [
        "id",
        "title",
        "category",
        "bullet_points",
        "description",
        "brand",
        "color"
      ]
    }
  },
  "_source": ["id", "title", "category", "brand", "image"]
}
```

Query 2 は、キーワードマッチングとタイトル埋め込みに対するニューラル検索を組み合わせたハイブリッド検索クエリです。'normalization-pipeline' を使用し、キーワードクエリと同様の変更を加えたクエリ本体を持っています。このクエリでは、あなた固有の model_id を使用することを忘れないでください。

```json
{
  "query": {
    "hybrid": {
      "queries": [
        {
          "multi_match": {
            "query": "%SearchText%",
            "fields": [
              "id",
              "title",
              "category",
              "bullet_points",
              "description",
              "brand",
              "color"
            ]
          }
        },
        {
          "neural": {
            "title_embedding": {
              "query_text": "%SearchText%",
              "k": 100,
              "model_id": "lZBXE5gBRVO0vZIAKepk"
            }
          }
        }
      ]
    }
  },
  "size": 10,
  "_source": ["id", "title", "category", "brand", "image"]
}
```

"Search" ボタンをクリックすると、2 つの結果リストが取得・比較され、違いが視覚的にハイライト表示されます。

デフォルトでは、Search Relevance Workbench は取得したドキュメントの ID を表示します。コンテンツをより解釈しやすくするために、提供されているドロップダウンボックスを使用してより説明的なフィールドに変更できます。この場合、"Title" を選択するとより分かりやすくなります。

提供された詳細を見ると、両方のクエリが返す結果が 4 件あり、それぞれに固有のアイテムが 6 件ずつあることがわかります。

結果リストを見ると、主にラップトップアクセサリーを返していたクエリが、主にラップトップを返すクエリに変換されたことがわかります。

このツールがアドホックな探索に役立つ理由は、ユーザーが変更を一目で素早く確認できることです。これにより、特定のクエリに対する変更の潜在的な影響を評価できます。_laptop_ クエリの場合、大幅な改善が見られます。関連性の低い商品が結果から削除されています。全体的に、Query 2 の結果はより説得力があり、検索品質の観点からハイブリッド検索への切り替えは明らかに理にかなっています。

しかし、単一のクエリはアドホックなチェックには有用ですが、変更が全体的な検索品質にどのような影響を与えるか、またはユーザーベース全体でより広範なパターンを明らかにするかについて、完全な全体像を提供することはほとんどありません。変更を適切に評価し、新たなパターンを特定するには、クエリセット全体でパフォーマンスを評価する必要があります。

## 複数クエリ: 新たなパターンを発見するための評価範囲の拡大

複数のクエリを評価するために、Search Relevance Workbench の 2 つの主要な概念を使用します。[クエリセット](https://docs.opensearch.org/docs/latest/search-plugins/search-relevance/query-sets/)と[検索設定](https://docs.opensearch.org/docs/latest/search-plugins/search-relevance/search-configurations/)です。

### クエリセット

クエリセットは、検索アプリケーションのドメインに関連するクエリのコレクションです。クエリセットにはさまざまな種類があります。既知アイテムクエリなど特定のタイプのクエリを含むセットもあれば、すべてのクエリタイプを代表することを目指すセットもあります。通常、クエリセットは実際のユーザークエリからサンプリングされます。Search Relevance Workbench はこのプロセスをサポートしています。

本記事では、[付属の GitHub リポジトリ](https://github.com/o19s/srw-blogs/blob/main/part1/blog_query_set.txt)で提供されている手動で作成されたクエリセットを使用します。

```
{"queryText": "laptop"}
{"queryText": "red shoes"}
{"queryText": "in-ear headphones"}
{"queryText": "portable bluetooth speakers"}
{"queryText": "stainless steel mending plates"}
{"queryText": "funny shirt birthday present"}
```

これらの 6 つのクエリを含むテキストファイルを Search Relevance Workbench の入力フォームにドラッグ＆ドロップすることで、クエリセットを作成できます。

"Create Query Set" ボタンで確認すると、このクエリセットが対応する OpenSearch インデックスに保存されます。

### 検索設定

検索設定は、実験中にクエリをどのように実行するかを Search Relevance Workbench に指示します。各設定は、単一クエリの横並び表示と同様に、クエリ本体とオプションの検索パイプラインで構成されます。

横並び比較で使用したのと同じクエリ本体を使用して、より深い探索のための 2 つの検索設定を作成します。

まず、キーワード検索用の検索設定を作成しましょう。

- Search Configuration Name: keyword
- Index: ecommerce

クエリ:

```json
{
  "query": {
    "multi_match": {
      "query": "%SearchText%",
      "fields": [
        "id",
        "title",
        "category",
        "bullet_points",
        "description",
        "brand",
        "color"
      ]
    }
  },
  "_source": ["id", "title", "category", "brand", "image"]
}
```

ハイブリッド検索用の検索設定を作成します。クエリをあなたの model*id で更新し、検索パイプラインを \_normalization-pipeline* に設定することを忘れないでください。

- Search Configuration Name: hybrid search
- Index: ecommerce

クエリ:

```json
{
  "query": {
    "hybrid": {
      "queries": [
        {
          "multi_match": {
            "query": "%SearchText%",
            "fields": [
              "id",
              "title",
              "category",
              "bullet_points",
              "description",
              "brand",
              "color"
            ]
          }
        },
        {
          "neural": {
            "title_embedding": {
              "query_text": "%SearchText%",
              "k": 100,
              "model_id": "lZBXE5gBRVO0vZIAKepk"
            }
          }
        }
      ]
    }
  },
  "size": 10,
  "_source": ["id", "title", "category", "brand", "image"]
}
```

### クエリセット比較実験の実行

要件 (クエリセットと 2 つの検索設定) が揃ったので、クエリセット比較を実行できます。これは 2 つの結果リストを一目で比較するだけでなく、クエリセット内のすべてのクエリからのすべての結果リストを比較します。

左側のナビゲーションで Query Set Comparison に移動し、作成したクエリセット ("SRW Blog Post Query Set") と検索設定 (keyword & hybrid search) を選択して、評価を開始します。

"Start Evaluation" ボタンをクリックすると、バックエンドがクエリセットの 6 つのクエリを各検索設定で実行します。システムは 12 個のクエリすべて (6 つのクエリを 2 つの異なる設定で実行) を実行し、結果リストの変化を計算します。実験の概要ページには、'COMPLETED' ステータスで完了した実験が表示されます。

結果を表示してインサイトを得るには、リンクされた実験 ID をクリックします。実験の詳細 (使用されたクエリセットと 2 つの検索設定) の後のセクションには、2 つの異なる検索設定によって生成された結果リスト間の変化を示す計算されたメトリクスの概要が表示されます。

4 つのメトリクスはすべて、変化の異なる側面を測定します。Jaccard は単純な集合の重複を測定し、frequency-weighted similarity は共通アイテムにより重要性を与えることで重複を定量化します。Rank-Biased Overlap (RBO) はランク付けされたリスト間の一致を評価し、上位の一致により高い価値を置きます。RBO50 と RBO90 は、ユーザーの注意が上位の結果にどれだけ集中しているかを示します。例えば、RBO50 は上位の結果をより重視し、ユーザーが後続の各結果を見る可能性が 50% 低いと仮定しています。

低い Jaccard 類似度 (下のスクリーンショットの 0.21 のような) は、結果リストに大きな違いがあることを示し、ハイブリッド検索設定が多くの新しいドキュメントを取り込んでいることを示唆しています。より高い RBO 値、特に RBO50 のような低いカットオフでは、ユーザーが最も注目する上位の結果が設定間でより一貫していることを意味します。

これらの集計メトリクスは、検索設定間の違いの概要を提供します。個々のクエリをより詳しく見るには、任意のクエリを選択すると、個別クエリの結果比較と同様のビューが表示されます。

クエリを調べることで、異なる検索設定がどのように影響するかを確認し、その潜在的なメリットとリスクの両方を評価できます。個々のクエリのメトリクスにより、特定のクエリグループの傾向を明らかにすることで、より広範な結論を導き出すことができます。この例では、特定のカテゴリを目指すクエリ (_laptop, in-ear headphones_) は大きな変化を受けやすい一方、非常にターゲットを絞ったクエリ (_stainless steel mending plates_) はそれほど変化しないようです。

この特定のケースでは、ハイブリッド検索の導入により、上位 10 件の結果に大きな変化がもたらされます。6 つのクエリすべてをレビューすることで、これらの変化が検索品質を向上させるかどうかを視覚的に評価できます。この主観的なレビューと客観的なメトリクスの組み合わせは、検索関連性の課題に対処し、初期評価を行うための確固たる基盤を提供します。

## まとめ

この 3 部構成の記事シリーズの最初の記事では、Search Relevance Workbench が検索品質を向上させるためのインサイトを素早く得るのにどのように役立つかを示しました。始めるために必要なのは 2 つの要素だけです。

- クエリセット: テストクエリのコレクション
- 2 つの検索設定: 探索したいクエリパターン

これで、独自のデータで実験するためのツールと知識が揃いました。問題のあるクエリをいくつか選択し、2 つの検索設定を作成し、違いを分析することから始めましょう! このプロセスにより、より良い検索結果への道を阻んでいるものが素早く明らかになります。また、OpenSearch がより[関連性の高い検索](https://opensearch.org/platform/search-relevance/)結果を提供し、根底にある意図と最も意味のある結果を結びつけることを可能にする方法も探索できます。

次の記事では、変化の測定を超えて、検索関連性の定量的な測定を探求します。検索設定間の違いだけでなく、どの設定がより優れているかを判断する方法を学びます。お楽しみに!
