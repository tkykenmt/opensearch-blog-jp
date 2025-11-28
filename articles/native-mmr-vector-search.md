---
title: "[翻訳] ネイティブ MMR によるベクトル検索の多様性向上"
emoji: "🔍"
type: "tech"
topics: ["opensearch", "vectorsearch", "mmr"]
published: true
publication_name: opensearch
published_at: 2025-11-17
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/improving-vector-search-diversity-through-native-mmr/

検索と推薦システムにおいて、関連性の高い結果を返すことは課題の半分に過ぎません。同様に重要なのは多様性です。つまり、ユーザーがほぼ重複した結果ではなく、さまざまな結果を見られるようにすることです。OpenSearch 3.3 は、k-NN およびニューラルクエリに対するネイティブの Maximal Marginal Relevance (MMR) をサポートし、これを簡単に実現できます。

## MMR とは

MMR は、関連性と多様性のバランスを取る再ランキングアルゴリズムです。

- **関連性**。結果がクエリにどれだけ一致するか
- **多様性**。結果が互いにどれだけ異なるか

MMR は、クエリに関連し、かつ以前に選択された結果とあまり似ていない結果を反復的に選択します。トレードオフは `diversity` パラメータで制御します (0 = 関連性を優先、1 = 多様性を優先)。

ベクトル検索では、埋め込みが類似した結果をクラスター化することが多いため、MMR は特に有用です。MMR がなければ、上位 k 件の結果がすべてほぼ同一になる可能性があります。

## OpenSearch のネイティブ MMR

以前は、MMR は外部でのみ実装でき、カスタムパイプラインと追加のコーディングが必要でした。現在、OpenSearch は `knn_vector` を使用した k-NN およびニューラルクエリで直接ネイティブ MMR をサポートしています。これにより、セットアップが簡素化され、レイテンシが削減されます。

## MMR の使用方法

以下のセクションでは、再ランキングに MMR を使用する方法を示します。

### 前提条件

再ランキングに MMR を使用する前に、必要な[システム生成検索プロセッサファクトリ](https://docs.opensearch.org/latest/search-plugins/search-pipelines/system-generated-search-processors/)がクラスターで有効になっていることを確認してください。

```json
PUT _cluster/settings
{
  "persistent": {
    "cluster.search.enabled_system_generated_factories": [
      "mmr_over_sample_factory",
      "mmr_rerank_factory"
    ]
  }
}
```

これらのファクトリにより、OpenSearch は MMR に必要なオーバーサンプリングと再ランキングのステップを自動的に実行できます。

### 例: ニューラル検索での多様性の向上

密な埋め込みモデルによって生成された製品説明を保存する `semantic` フィールドを持つニューラル検索インデックスがあるとします。[このガイド](https://docs.opensearch.org/latest/field-types/supported-field-types/semantic/)に従ってインデックスを設定できます。

#### サンプルデータのインデックス作成

いくつかの製品説明の例をインデックスに登録します。

```json
PUT /_bulk
{ "update": { "_index": "my-nlp-index", "_id": "1" } }
{ "doc": {"product_description": "Red apple from USA."}, "doc_as_upsert": true }
{ "update": { "_index": "my-nlp-index", "_id": "2" } }
{ "doc": {"product_description": "Red apple from usa."}, "doc_as_upsert": true }
{ "update": { "_index": "my-nlp-index", "_id": "3" } }
{ "doc": {"product_description": "Crispy apple."}, "doc_as_upsert": true }
{ "update": { "_index": "my-nlp-index", "_id": "4" } }
{ "doc": {"product_description": "Red apple."}, "doc_as_upsert": true }
{ "update": { "_index": "my-nlp-index", "_id": "5" } }
{ "doc": {"product_description": "Orange juice from usa."}, "doc_as_upsert": true }
```

#### MMR なしのクエリ

"Red apple" の標準的なニューラル検索クエリは次のようになります。

```json
GET /my-npl-index/_search
{
  "size": 3,
  "_source": { "exclude": ["product_description_semantic_info"] },
  "query": {
    "neural": {
      "product_description": { "query_text": "Red apple" }
    }
  }
}
```

結果は以下の通りです。

```json
"hits": [
    { "_id": "4", "_score": 0.956, "_source": {"product_description": "Red apple."} },
    { "_id": "1", "_score": 0.743, "_source": {"product_description": "Red apple from USA."} },
    { "_id": "2", "_score": 0.743, "_source": {"product_description": "Red apple from usa."} }
]
```

すべての上位結果が非常に似ていることに注目してください。ユーザーが見るものにはほとんど多様性がありません。

#### MMR ありのクエリ

MMR を追加することで、関連性を維持しながら上位結果を多様化できます。

```json
GET /my-npl-index/_search
{
  "size": 3,
  "_source": { "exclude": ["product_description_semantic_info"] },
  "query": {
    "neural": {
      "product_description": { "query_text": "Red apple" }
    }
  },
  "ext": {
    "mmr": {
      "candidates": 10,
      "diversity": 0.4
    }
  }
}
```

結果は以下の通りです。

```json
"hits": [
    { "_id": "4", "_score": 0.956, "_source": {"product_description": "Red apple."} },
    { "_id": "1", "_score": 0.743, "_source": {"product_description": "Red apple from USA."} },
    { "_id": "3", "_score": 0.611, "_source": {"product_description": "Crispy apple."} }
]
```

MMR を使用することで、上位ヒットの関連性を犠牲にすることなく、より多様な結果 ("Crispy apple" など) を取得できます。

## OpenSearch での MMR 再ランキングのベンチマーク

MMR 再ランキングのパフォーマンスへの影響を評価するために、[ベクトル検索](https://github.com/opensearch-project/opensearch-benchmark-workloads/blob/main/vectorsearch/params/corpus/10million/faiss-cohere-768-dp.json)と[ニューラル検索](https://github.com/opensearch-project/opensearch-benchmark-workloads/blob/main/neural_search/params/semanticfield/neural_search_semantic_field_dense_model.json)の両方のワークロードで OpenSearch 3.3 のベンチマークテストを実行しました。これらのテストは、MMR によって導入されるレイテンシのトレードオフを定量化し、より多様な検索結果の利点を示すのに役立ちました。

### クラスター構成

次の OpenSearch クラスター構成を使用しました。

- バージョン: OpenSearch 3.3
- データノード: 3 × r6g.2xlarge
- クラスターマネージャーノード: 3 × c6g.xlarge
- ベンチマークインスタンス: c6g.large

### ベクトル検索のパフォーマンス

100 万の事前計算された埋め込みを含む `cohere-1m` データセットを使用して、k-NN クエリを評価しました。次の表は、k の異なる値と MMR 候補サイズに対するクエリレイテンシ (ミリ秒単位) をまとめたものです。

| **k** | **クエリサイズ** | **MMR 候補** | **k-NN (p50 ms)** | **k-NN (p90 ms)** | **k-NN + MMR (p50 ms)** | **k-NN + MMR (p90 ms)** | **p50 Δ (%)** | **p90 Δ (%)** | **p50 Δ (ms)** | **p90 Δ (ms)** |
| ----- | ---------------- | ------------ | ----------------- | ----------------- | ----------------------- | ----------------------- | ------------- | ------------- | -------------- | -------------- |
| 1     | 1                | 1            | 6.70              | 7.19              | 8.22                    | 8.79                    | 22.7          | 22.2          | 1.52           | 1.60           |
| 10    | 10               | 10           | 8.09              | 8.64              | 9.14                    | 9.62                    | 13.0          | 11.3          | 1.05           | 0.98           |
| 10    | 10               | 30           | 8.09              | 8.64              | 10.83                   | 11.48                   | 33.9          | 32.9          | 2.74           | 2.84           |
| 10    | 10               | 50           | 8.09              | 8.64              | 11.76                   | 12.55                   | 45.4          | 45.3          | 3.67           | 3.91           |
| 10    | 10               | 100          | 8.09              | 8.64              | 15.81                   | 16.73                   | 95.5          | 93.6          | 7.72           | 8.09           |
| 20    | 20               | 100          | 8.13              | 8.57              | 18.66                   | 19.62                   | 129.6         | 129.0         | 10.54          | 11.05          |
| 50    | 50               | 100          | 8.23              | 8.74              | 28.55                   | 29.63                   | 247.0         | 239.0         | 20.32          | 20.89          |

### ニューラル検索のパフォーマンス

ニューラル検索では、50 万以上のドキュメントを含む Quora データセットを使用しました。次の表は、MMR 再ランキングありとなしのクエリレイテンシを示しています。

| **k** | **クエリサイズ** | **MMR 候補** | **Neural (p50 ms)** | **Neural (p90 ms)** | **Neural + MMR (p50 ms)** | **Neural + MMR (p90 ms)** | **p50 Δ (%)** | **p90 Δ (%)** | **p50 Δ (ms)** | **p90 Δ (ms)** |
| ----- | ---------------- | ------------ | ------------------- | ------------------- | ------------------------- | ------------------------- | ------------- | ------------- | -------------- | -------------- |
| 1     | 1                | 1            | 113.59              | 122.22              | 113.08                    | 122.38                    | -0.46         | 0.13          | -0.52          | 0.16           |
| 10    | 10               | 10           | 112.03              | 122.90              | 113.88                    | 122.63                    | 1.66          | -0.22         | 1.86           | -0.27          |
| 10    | 10               | 30           | 112.03              | 122.90              | 119.57                    | 127.65                    | 6.73          | 3.86          | 7.54           | 4.75           |
| 10    | 10               | 50           | 112.03              | 122.90              | 122.56                    | 133.34                    | 9.40          | 8.50          | 10.53          | 10.45          |
| 10    | 10               | 100          | 112.03              | 122.90              | 130.52                    | 139.95                    | 16.51         | 13.87         | 18.49          | 17.05          |
| 20    | 20               | 100          | 112.41              | 122.85              | 131.18                    | 141.09                    | 16.69         | 14.85         | 18.77          | 18.24          |
| 50    | 50               | 100          | 114.86              | 121.02              | 141.24                    | 152.42                    | 22.97         | 25.94         | 26.38          | 31.40          |

### 主な発見

パフォーマンス観察から得られた主な発見は以下のとおりです。

1. MMR はレイテンシを追加し、増加量は MMR 候補の数とクエリサイズに比例して大きくなります。
2. MMR なしの k-NN およびニューラルクエリは、k の増加を効率的に処理します。計算時間のほとんどは上位 k 候補の選択ではなく、グラフトラバーサル (`ef_search`) に費やされます。

MMR 候補の数を選択する際は、多様性とクエリレイテンシのバランスを考慮する必要があります。候補が多いほど結果の多様性は向上しますが、レイテンシが増加するため、ワークロードに適した値を選択してください。

## クロスクラスター検索での MMR の使用

現在、[クロスクラスター検索](https://docs.opensearch.org/latest/search-plugins/cross-cluster-search/)の場合、OpenSearch はリモートクラスターのインデックスマッピングからベクトルフィールド情報を自動的に解決できません。そのため、MMR を使用する際にベクトルフィールドの詳細を明示的に指定する必要があります。

```json
POST /my-index/_search
{
  "query": {
    "neural": {
      "my_vector_field": {
        "query_text": "query text",
        "model_id": "<your model id>"
      }
    }
  },
  "ext": {
    "mmr": {
      "diversity": 0.5,
      "candidates": 10,
      "vector_field_path": "my_vector_field",
      "vector_field_data_type": "float",
      "vector_field_space_type": "l2"
    }
  }
}
```

クエリは、MMR 構成に次のパラメータを使用します。

- `vector_field_path`。MMR 再ランキングに使用するベクトルフィールドへのパス
- `vector_field_data_type`。ベクトルのデータ型 (例: `float`)
- `vector_field_space_type`。類似性計算に使用される距離メトリック (例: `l2`)
- `candidates` と `diversity`。ローカル MMR クエリと同様に、候補の数と多様性の重みを制御します

この情報を指定することで、リモートクラスター間でクエリを実行する場合でも、MMR が多様性を正しく計算し、結果を再ランキングできます。

## まとめ

OpenSearch の MMR により、関連性と多様性の両方を備えた検索結果を簡単に提供できます。結果をインテリジェントに再ランキングすることで、MMR はより幅広いオプションを返し、冗長性を減らし、ユーザーにとってより豊かで魅力的な検索体験を作り出すのに役立ちます。

ベクトル検索の多様性を向上させたい場合、OpenSearch の MMR はすぐに試せる強力なツールです。

## 今後の予定

将来的には、以下の更新により MMR をさらに使いやすく、より柔軟にする予定です。

- **リモートクラスターのサポート向上**。ベクトルフィールド情報を手動で指定する必要がなくなります。
- **クエリタイプのサポート拡張**。現在、MMR は `knn_vector` を使用する k-NN クエリまたはニューラルクエリでのみ機能します。`bool` や `hybrid` クエリなどの追加のクエリタイプをサポートし、MMR がより広範な検索シナリオを強化できるようにすることを目指しています。
