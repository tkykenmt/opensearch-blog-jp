---
title: "[翻訳] OpenSearch ベクトルエンジンにおける効率的なフィルタリング"
emoji: "🔍"
type: "tech"
topics: ["opensearch", "vectorsearch", "knn", "faiss", "検索"]
published: true
published_at: 2023-10-18
publication_name: "opensearch"
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/efficient-filters-in-knn/

[OpenSearch 2.9](https://github.com/opensearch-project/opensearch-build/blob/main/release-notes/opensearch-release-notes-2.9.0.md) のリリースで、Facebook AI Similarity Search (Faiss) エンジンを使用するクエリに対して、効率的なフィルタリング (filter-while-search) 機能を導入しました。このアップデートにより、OpenSearch ベクトルエンジンにおける従来のプレフィルタリングとポストフィルタリングの制限を克服しています。[OpenSearch 2.10 リリース](https://github.com/opensearch-project/opensearch-build/blob/main/release-notes/opensearch-release-notes-2.10.0.md)では、Inverted File (IVF) アルゴリズムを使用したフィルタリングのサポートを追加し、効率的なフィルタの全体的なパフォーマンスをさらに向上させました。これにより、ユーザーはフィルタ付きベクトル類似検索を大規模に実行できるようになりました。

効率的なフィルタの詳細に入る前に、まずフィルタリングの概念を理解しましょう。フィルタリングにより、ユーザーはデータの特定のサブセット内で検索範囲を絞り込むことができます。ベクトル検索の文脈では、クエリベクトルとフィルタで構成されるクエリに対して、フィルタで設定された条件を満たすデータポイントの中から最近傍を見つけることが目的です。これを説明するために、ベクトル検索に特化した例を見てみましょう。

商品カタログを格納するインデックスがあり、画像がベクトルとして表現されているとします。同じインデックスには、評価、アップロード日、レビュー総数なども格納されています。エンドユーザーは類似商品を検索したい (ベクトルとして提供) が、評価 4 以上の商品のみを求めています。このようなクエリに対して望ましい結果を提供するには、ベクトル検索と組み合わせたフィルタリングが必要です。

## 背景

OpenSearch ベクトルエンジンには、近似最近傍 (ANN) 検索を実行するための 3 つの異なるエンジンがサポートされています。[Lucene](https://github.com/apache/lucene) (Java 実装)、[Faiss](https://github.com/facebookresearch/faiss) (C++ 実装)、[Nmslib](https://github.com/nmslib/nmslib) (C++ 実装) です。これらのエンジンは、最近傍検索に使用される下流ライブラリの抽象化です。Lucene と Nmslib は ANN 検索に HNSW アルゴリズムをサポートし、Faiss は HNSW と IVF (プロダクト量子化エンコーディング技術の有無を含む) をサポートしています。詳細については、[k-NN ドキュメント](https://opensearch.org/docs/latest/search-plugins/knn/knn-index/)を参照してください。

OpenSearch バージョン 2.8 時点で、ベクトルエンジンは 3 つのフィルタリングアプローチをサポートしています。[スコアリングスクリプトフィルタ](https://opensearch.org/docs/2.8/search-plugins/knn/filter-search-knn/#scoring-script-filter) (プレフィルタリング)、[Boolean フィルタ](https://opensearch.org/docs/2.8/search-plugins/knn/filter-search-knn/#boolean-filter-with-ann-search) (ポストフィルタリング)、[Lucene k-NN フィルタ](https://opensearch.org/docs/2.8/search-plugins/knn/filter-search-knn/#using-a-lucene-k-nn-filter) (効率的なフィルタリング機能を提供しますが、Lucene エンジンのみをサポート) です。

## 効率的なフィルタリングとは

ベクトル検索には、基本的に 2 種類のフィルタリングがあります。

1. **プレフィルタリング**は、1 つ以上のフィルタを含むクエリに対して、まずコーパス全体にフィルタを適用してフィルタ済みドキュメントセットを生成します。その後、フィルタ済みドキュメントに対してベクトル検索を実行します。一般的に、フィルタ済みドキュメントに対するベクトル検索は、完全検索を実行するか、実行時にフィルタ済みドキュメント ID で新しい HNSW グラフを作成してから検索を実行します。これらのアプローチは計算コストが高く、スケーラビリティに問題があります。

2. **ポストフィルタリング**は、1 つ以上のフィルタを含むクエリに対して、まずベクトル検索を実行し、その結果のドキュメントにフィルタを適用します。このアプローチには、フィルタ適用後の結果総数が k 未満になる可能性があるという問題があります。

このように、プレフィルタリングとポストフィルタリングの両方に制限があります。ここで効率的なフィルタリングが改善を提供します。まず、ベクトル検索における効率的なフィルタリングの背後にあるアイデアを理解しましょう。

1. まずフィルタを適用して filterIds を特定し、コーパス全体で ANN 検索を実行する際に、filterIds セットに存在する docIds のみを考慮します。
2. filterIds を使用してコーパス全体で ANN 検索を実行するタイミングと、完全検索を実行するタイミングをインテリジェントに判断します。例えば、フィルタ済みドキュメントセットが小さい場合、ANN 検索の精度が低下する可能性があるため、効率的なフィルタリングは完全検索を実行して精度を優先します。

以下の図に、Faiss を使用した効率的なフィルタによるベクトル検索フローの例を示します。

![効率的なフィルタの高レベルフロー](/images/opensearch-efficient-filters-in-knn/efficient-filters-high-level-flow-1024x497.jpg)

Faiss エンジンを使用するインデックスでフィルタ付き検索が実行されると、ベクトル検索エンジンはフィルタ付き ANN 検索を使用するか、完全検索を実行するかを決定します。アルゴリズムは以下の変数を使用します。

- **N**: インデックス内のドキュメント数
- **P**: フィルタ適用後のドキュメントサブセット内のドキュメント数 (P <= N)
- **k**: レスポンスで返すベクトルの最大数
- **R**: フィルタ付き ANN 検索実行後に返される結果数
- **FT (フィルタ閾値)**: `knn.advanced.filtered_exact_search_threshold` 設定で定義されるインデックスレベルの閾値で、完全検索への切り替えを指定
- **MDC (最大距離計算数)**: FT (フィルタ閾値) が設定されていない場合に完全検索で許可される最大距離計算数。この値は変更できません。

以下のフローチャートにアルゴリズムの概要を示します。

![効率的なフィルタのフローチャート](/images/opensearch-efficient-filters-in-knn/efficient-filters-flow-chart.jpg)

## 効率的なフィルタを使用したベクトル検索の実行

まず、OpenSearch クラスターが起動していることを確認してください。完全な OpenSearch ディストリビューションのセットアップについては、[こちらのドキュメント](https://opensearch.org/downloads.html)を参照してください。実験に入る前に、OpenSearch で k-NN ワークロードを実行する方法を確認しましょう。まず、インデックスを作成する必要があります。インデックスは、簡単に検索できるようにドキュメントのセットを格納します。k-NN の場合、インデックスのマッピングは OpenSearch に使用するアルゴリズムとそのパラメータを指示します。まず、検索アルゴリズムとして HNSW を使用するインデックスを作成します。

```json
PUT my-hnsw-filter-index
{
  "settings": {
    "index": {
      "knn": true,
      "number_of_shards": 1,
      "number_of_replicas": 0
    }
  },
  "mappings": {
    "properties": {
      "my_vector": {
        "type": "knn_vector",
        "dimension": 4,
        "method": {
          "name": "hnsw",
          "space_type": "l2",
          "engine": "faiss"
        }
      }
    }
  }
}
```

インデックス作成でサポートされるさまざまなパラメータの詳細については、[こちらのドキュメント](https://opensearch.org/docs/latest/search-plugins/knn/knn-index/)を参照してください。

インデックスを作成したら、データを投入できます。

```json
POST _bulk
{ "index": { "_index": "my-hnsw-filter-index", "_id": "1" } }
{ "my_vector": [1.5, 2.5, 3.5, 4.5], "price": 12.2, "size": "xl" }
{ "index": { "_index": "my-hnsw-filter-index", "_id": "2" } }
{ "my_vector": [2.5, 3.5, 4.5, 5.5], "price": 7.1, "size": "xl" }
{ "index": { "_index": "my-hnsw-filter-index", "_id": "3" } }
{ "my_vector": [3.5, 4.5, 5.5, 6.5], "price": 12.9, "size": "l" }
{ "index": { "_index": "my-hnsw-filter-index", "_id": "4" } }
{ "my_vector": [5.5, 6.5, 7.5, 8.5], "price": 1.2, "size": "l" }
{ "index": { "_index": "my-hnsw-filter-index", "_id": "5" } }
{ "my_vector": [4.5, 5.5, 6.5, 9.5], "price": 3.7, "size": "xl" }
{ "index": { "_index": "my-hnsw-filter-index", "_id": "6" } }
{ "my_vector": [1.5, 5.5, 4.5, 6.4], "price": 10.3, "size": "xl" }
{ "index": { "_index": "my-hnsw-filter-index", "_id": "7" } }
{ "my_vector": [2.5, 3.5, 5.6, 6.7], "price": 5.5, "size": "m" }
{ "index": { "_index": "my-hnsw-filter-index", "_id": "8" } }
{ "my_vector": [4.5, 5.5, 6.7, 3.7], "price": 4.4, "size": "s" }
{ "index": { "_index": "my-hnsw-filter-index", "_id": "9" } }
{ "my_vector": [1.5, 5.5, 4.5, 6.4], "price": 8.9, "size": "xl" }
```

インデックスにドキュメントを追加したら、標準的なベクトル類似検索を次のように実行できます。

```json
GET my-hnsw-filter-index/_search
{
  "size": 2,
  "query": {
    "knn": {
      "my_vector": {
        "vector": [2, 3, 5, 6],
        "k": 2
      }
    }
  }
}
```

同じインデックスを使用して効率的なフィルタリングを実行できます。

### 効率的なフィルタ

以下に示すように、**filter 句**は **knn query** 句の内部にあります。これにより、OpenSearch ベクトルエンジンはフィルタによって生成された docIds を使用して以下を行います。

1. ANN 検索または完全検索のどちらを使用して上位 K 件の結果を計算するかを決定する
2. HNSW グラフなどの基盤となるデータ構造を使用して ANN 検索を実行する際に、適切な DocIds セットを選択するよう ANN 検索アルゴリズムを誘導する

```json
POST my-hnsw-filter-index/_search
{
  "size": 2,
  "query": {
    "knn": {
      "my_vector": {
        "vector": [2, 3, 5, 6],
        "k": 2,
        "filter": {
          "bool": {
            "must": [
              {
                "range": {
                  "price": {
                    "gte": 7,
                    "lte": 13
                  }
                }
              },
              {
                "term": {
                  "size": "xl"
                }
              }
            ]
          }
        }
      }
    }
  }
}
```

### 実験

次に、いくつかの実験を実行して、トレードオフとこれらの異なるフィルタリング技術が実際にどのように機能するかを確認します。これらの実験では、フィルタ付き検索の精度とクエリレイテンシに焦点を当てます。

具体的には、以下の検索メトリクスを計算します。

- **Latency p99 (ms)、Latency p90 (ms)、Latency p50 (ms)**: 各パーセンタイルでのクエリレイテンシ (ミリ秒)
- **recall@K**: フィルタ付き検索で返された K 件の結果に含まれる、上位 K 件の正解最近傍の割合
- **recall@1**: フィルタ付き検索で返された上位結果に含まれる、最初の正解最近傍の割合

フィルタリング技術は 2 種類のフィルタでテストします。

1. **緩いフィルタ**: このフィルタ設定では、ドキュメントの 80% がフィルタ付きベクトル検索の対象となります ([Filter Spec 参照](https://github.com/opensearch-project/k-NN/blob/main/benchmarks/perf-tool/release-configs/faiss-hnsw/filtering/relaxed-filter/relaxed-filter-spec.json))
2. **厳しいフィルタ**: このフィルタ設定では、ドキュメントの 20% がフィルタ付きベクトル検索の対象となります ([Filter Spec 参照](https://github.com/opensearch-project/k-NN/blob/main/benchmarks/perf-tool/release-configs/faiss-hnsw/filtering/restrictive-filter/restrictive-filter-spec.json))

データセットの観点では、128 次元の 100 万レコードを持つ [sift-128 データセット](http://corpus-texmex.irisa.fr/)を使用し、すべてのドキュメントに 3 つの基本属性 (age、color、taste) と値を追加してフィルタリングに使用します。これを実現するには[このコード](https://github.com/opensearch-project/k-NN/blob/main/benchmarks/perf-tool/add-filters-to-dataset.py)を使用できます。

実験を実行するには、以下の手順で行います。

1. データセットをクラスターに投入し、force merge API を実行してセグメント数を 1 に減らす
2. 投入が完了したら、[warmup API](https://opensearch.org/docs/latest/search-plugins/knn/api/#warmup-operation) を使用して検索ワークロード用にクラスターを準備する
3. 10,000 件のテストクエリをクラスターに対して 10 回実行し、集計結果を収集する

### パラメータ選択

実験を実行する際の難しい点の 1 つは、パラメータの選択です。すべてをテストするには多くのパラメータの組み合わせがあります。例えば、HNSW の m、ef_search、ef_construction などのアルゴリズムパラメータや、シャード数などの OpenSearch インデックスパラメータがあります。そのため、すべての実験で HNSW アルゴリズムのパラメータ値を固定し、シャード数の値を変更します。フィルタリングと同様に、この変数は精度とレイテンシの調整において重要な役割を果たします。これらの実験で使用できるパラメータを以下に示します。

| Config Id | m  | ef_search | ef_construction | number of shards | K   | Size |
|-----------|----|-----------|-----------------|--------------------|-----|------|
| config1   | 16 | 100       | 256             | 1                  | 100 | 100  |
| config2   | 16 | 100       | 256             | 8                  | 100 | 100  |
| config3   | 16 | 100       | 256             | 24                 | 100 | 100  |

### クラスター構成

| Key               | Value       |
|-------------------|-------------|
| Data Node Type    | r5.4xlarge  |
| Data Node Count   | 3           |
| Leader Node       | c6.xlarge   |
| Leader Node Count | 3           |

クラスターは[このリポジトリ](https://github.com/opensearch-project/opensearch-cluster-cdk)を使用して作成しました。

### 結果

上記のプロセスに従うと、以下の結果が期待できます。

**config1 の結果:**

| Filtering Technique              | Filter Spec Engine | p50(ms) | p90(ms) | p99(ms) | recall@K | recall@1 |
|----------------------------------|-------------------|---------|---------|---------|----------|----------|
| Efficient Filtering Relaxed      | Faiss             | 17      | 17      | 18      | 0.9978   | 1        |
| Efficient Filtering Restrictive  | Faiss             | 27      | 28      | 28      | 1        | 1        |

**config2 の結果:**

| Filtering Technique              | Filter Spec Engine | p50(ms) | p90(ms) | p99(ms) | recall@K | recall@1 |
|----------------------------------|-------------------|---------|---------|---------|----------|----------|
| Efficient Filtering Relaxed      | Faiss             | 11.9    | 12      | 13      | 0.9998   | 1        |
| Efficient Filtering Restrictive  | Faiss             | 5       | 6       | 7       | 1        | 1        |

**config3 の結果:**

| Filtering Technique              | Filter Spec Engine | p50(ms) | p90(ms) | p99(ms) | recall@K | recall@1 |
|----------------------------------|-------------------|---------|---------|---------|----------|----------|
| Efficient Filtering Relaxed      | Faiss             | 9       | 9       | 10      | 0.9998   | 1        |
| Efficient Filtering Restrictive  | Faiss             | 4       | 5       | 8       | 1        | 1        |

## まとめ

本記事では、OpenSearch におけるベクトル検索での効率的なフィルタの動作について説明しました。結果からわかるように、同様のデータセットに対してすべてのシャード構成で 0.99 の recall@K と 1 の recall@1 を達成する実験を実行できます。実験でのレイテンシはシャード数の変更に伴って変化しますが、これはシャード数が多いほど並列性が向上するため予想通りです。

## FAQ

### 自分のユースケースに最適なフィルタは何ですか？

どのシナリオでどのフィルタを使用すべきかについては、[こちらの表](https://opensearch.org/docs/latest/search-plugins/knn/filter-search-knn/#filtered-search-optimization)を参照してください。新しいフィルタ最適化が導入されるたびに、この表を更新し続けています。

### 効率的なフィルタはどのエンジンで使用できますか？

効率的なフィルタは、HNSW アルゴリズム (k-NN プラグインバージョン 2.9 以降) または IVF アルゴリズム (k-NN プラグインバージョン 2.10 以降) を使用する Faiss エンジンでサポートされています。OpenSearch 2.9 より前は、効率的なフィルタは Lucene エンジンでのみサポートされており、Lucene Filters と呼ばれていました。最新のサポートマトリックスについては、[こちらのドキュメント](https://opensearch.org/docs/latest/search-plugins/knn/filter-search-knn/#:~:text=The%20following%20table%20summarizes%20the%20preceding%20filtering%20use%20cases.)を参照してください。

## 参考資料

1. Meta issue: https://github.com/opensearch-project/k-NN/issues/903
2. Filters enhancement for restrictive filters: https://github.com/opensearch-project/k-NN/issues/1049
