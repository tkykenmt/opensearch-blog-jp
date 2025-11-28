---
title: "[翻訳] OpenSearch におけるベクトル放射状検索の理解"
emoji: "🎯"
type: "tech"
topics: ["opensearch", "vectorsearch", "knn", "machinelearning", "search"]
published: true
publication_name: "opensearch"
published_at: 2024-06-24
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/vector-radial-search/

OpenSearch バージョン 2.14 以前では、OpenSearch k-NN プラグインは近似ベクトル類似検索に対して top K クエリのみを提供していました。OpenSearch 2.14 では、新しいタイプのベクトル検索である「放射状検索 (radial search)」が導入されました。放射状検索は [k-NN 検索](https://opensearch.org/docs/latest/search-plugins/knn/radial-search-knn/) と [ニューラル検索](https://opensearch.org/docs/latest/query-dsl/specialized/neural/) の両方でサポートされています。

放射状検索は、OpenSearch k-NN プラグインの機能を近似 top K 検索を超えて拡張します。放射状検索を使用すると、クエリポイントから指定された最大距離または最小スコア閾値内にあるベクトル空間内のすべてのポイントを検索できます。これにより、検索操作の柔軟性と有用性が向上します。

例えば、特定のドキュメントに最も類似したドキュメントを検索したい場合、最も類似した上位 K 件のドキュメントを取得するクエリを実行できます (K = top N)。しかし、K が最適に選択されていない場合、無関係な結果を受け取ったり、関連する結果を見逃したりする可能性があります。ベクトル放射状検索を使用すると、閾値 (例: 類似度スコア > 0.95) を使用して、高い類似性を持つすべてのドキュメントを取得するクエリを実行できます。

## 検索半径の定義

検索半径は以下の方法で定義できます。

- **最大距離 (max_distance)**: ベクトル空間内の物理的な距離閾値を指定し、クエリポイントからこの距離内にあるすべてのポイントを特定します。このアプローチは、空間的な近接性や絶対距離の測定が必要なアプリケーションに特に有用です。以下の画像は、[L2 空間タイプ](https://opensearch.org/docs/latest/search-plugins/knn/radial-search-knn/#spaces) と `max_distance` = 25.0 を使用した放射状検索の例を示しています。各円内の数字は、クエリターゲットからのポイントの距離を表しています。`max_distance` が 25.0 以内のすべてのポイントが結果に含まれます。

![最大距離を使用した放射状検索](/images/opensearch-vector-radial-search-guide/radial-search-with-min-score.png)

- **最小スコア (min_score)**: 類似度スコアの閾値を定義し、クエリポイントに対してそのスコア以上を満たすすべてのポイントを取得します。これは、特定のメトリクスに基づく相対的な類似性が物理的な近接性よりも重要な場合に有用です。以下の画像は、`min_score` = 0.90 を使用した放射状検索の例を示しています。各円内の数字は、クエリターゲットに対するポイントの OpenSearch スコアを表しています。スコアが 0.90 以上のすべてのポイントが結果に含まれます。

![最小スコアを使用した放射状検索](/images/opensearch-vector-radial-search-guide/radial-search-with-min-score-1.png)

## 放射状検索を使用するタイミング

以下のシナリオでは、top K ベクトル検索の代わりに放射状検索を使用します。

- **近接性ベースのフィルタリング**: クエリポイントから特定の距離内にあるすべてのアイテムを見つける必要がある場合。固定数の上位結果を返す従来の k-NN 検索とは異なり、放射状検索では指定された距離閾値内にあるすべてのアイテムを見つけることができます。
- **閾値固有のクエリ**: 基準を満たすアイテムのみが結果に含まれることを確認する必要がある場合。放射状検索では、特定の類似度または距離の閾値を定義でき、これは異常検出や地理空間検索などのタスクに不可欠です。
- **動的な範囲調整**: 許容される類似度または距離の範囲が変動する可能性がある場合。放射状検索はより柔軟な検索結果を提供します。

## サポートされる構成

OpenSearch 2.14 以降、OpenSearch k-NN プラグインを使用して Lucene または Faiss エンジンのいずれかで放射状検索を実行できます。以下の表は、エンジン別の放射状検索のユースケースをまとめています。

| エンジン | フィルターサポート | ネストフィールドサポート | 検索タイプ |
|---------|------------------|----------------------|----------|
| Lucene | あり | なし | 近似 |
| Faiss | あり | あり | 近似 |

## 空間タイプ

空間タイプは、k 最近傍を決定するために 2 点間の距離を測定するために使用される関数に対応します。さまざまな空間タイプの距離とスコアの計算方法の詳細については、[空間タイプ](https://opensearch.org/docs/latest/search-plugins/knn/radial-search-knn/#spaces) を参照してください。

## ベクトル放射状検索の使用開始

以下の例は、放射状検索を始めるのに役立ちます。

### 前提条件

放射状検索で k-NN インデックスを使用するには、`index.knn` を `true` に設定して k-NN インデックスを作成します。`knn_vector` データ型の 1 つ以上のフィールドを指定します。

```json
PUT knn-index-test
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 1,
    "index.knn": true
  },
  "mappings": {
    "properties": {
      "my_vector": {
        "type": "knn_vector",
        "dimension": 2,
        "method": {
            "name": "hnsw",
            "space_type": "l2",
            "engine": "faiss",
            "parameters": {
              "ef_construction": 100,
              "m": 16,
              "ef_search": 100
            }
          }
      }
    }
  }
}
```

インデックスを作成したら、データを追加します。

```json
PUT _bulk?refresh=true
{"index": {"_index": "knn-index-test", "_id": "1"}}
{"my_vector": [7.0, 8.2], "price": 4.4}
{"index": {"_index": "knn-index-test", "_id": "2"}}
{"my_vector": [7.1, 7.4], "price": 14.2}
{"index": {"_index": "knn-index-test", "_id": "3"}}
{"my_vector": [7.3, 8.3], "price": 19.1}
{"index": {"_index": "knn-index-test", "_id": "4"}}
{"my_vector": [6.5, 8.8], "price": 1.2}
{"index": {"_index": "knn-index-test", "_id": "5"}}
{"my_vector": [5.7, 7.9], "price": 16.5}
```

### 最大距離とフィルターを使用した放射状検索

以下の例は、`max_distance` とフィルターを使用した放射状検索を示しています。

```json
GET knn-index-test/_search
{
  "query": {
    "knn": {
      "my_vector": {
        "vector": [7.1, 8.3],
        "max_distance": 2,
        "filter": {
          "range": {
            "price": {
              "gte": 1,
              "lte": 5
            }
          }
        }
      }
    }
  }
}
```

二乗ユークリッド距離 (L2²) が 2 以内で、価格が 1〜5 の範囲内にあるすべてのドキュメントが結果に返されます。

```json
{
    ...
    "hits": {
        "total": {
            "value": 2,
            "relation": "eq"
        },
        "max_score": 0.98039204,
        "hits": [
            {
                "_index": "knn-index-test",
                "_id": "1",
                "_score": 0.98039204,
                "_source": {
                    "my_vector": [7.0,8.2],
                    "price": 4.4
                }
            },
            {
                "_index": "knn-index-test",
                "_id": "4",
                "_score": 0.62111807,
                "_source": {
                    "my_vector": [6.5,8.8],
                    "price": 1.2
                }
            }
        ]
    }
}
```

### 最小スコアとフィルターを使用した放射状検索

以下の例は、`min_score` とレスポンスフィルターを使用した放射状検索を示しています。

```json
GET knn-index-test/_search
{
    "query": {
        "knn": {
            "my_vector": {
                "vector": [7.1, 8.3],
                "min_score": 0.95,
                "filter": {
                    "range": {
                        "price": {
                            "gte": 1,
                            "lte": 5
                        }
                    }
                }
            }
        }
    }
}
```

スコアが 0.9 以上で、価格が 1〜5 の範囲内にあるすべてのドキュメントが結果に返されます。

```json
{
    ...
    "hits": {
        "total": {
            "value": 1,
            "relation": "eq"
        },
        "max_score": 0.98039204,
        "hits": [
            {
                "_index": "knn-index-test",
                "_id": "1",
                "_score": 0.98039204,
                "_source": {
                    "my_vector": [7.0, 8.2],
                    "price": 4.4
                }
            }
        ]
    }
}
```

## ベクトル放射状検索を使用したニューラル検索

ニューラル検索も放射状検索をサポートしています。以下は放射状検索のニューラルクエリの例です。

以下の例は、`k` 値が `100` で、範囲クエリと term クエリを含むフィルターを使用した検索を示しています。

```json
GET /my-nlp-index/_search
{
  "query": {
    "neural": {
      "passage_embedding": {
        "query_text": "Hi world",
        "query_image": "iVBORw0KGgoAAAAN...",
        "k": 100,
        "filter": {
          "bool": {
            "must": [
              {
                "range": {
                  "rating": {
                    "gte": 8,
                    "lte": 10
                  }
                }
              },
              {
                "term": {
                  "parking": "true"
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

以下の例は、`min_score` が `0.95` で、前述のクエリと同じフィルターを使用した k-NN 放射状検索を示しています。

```json
GET /my-nlp-index/_search
{
  "query": {
    "neural": {
      "passage_embedding": {
        "query_text": "Hi world",
        "query_image": "iVBORw0KGgoAAAAN...",
        "min_score": 0.95,
        "filter": {
          "bool": {
            "must": [
              {
                "range": {
                  "rating": {
                    "gte": 8,
                    "lte": 10
                  }
                }
              },
              {
                "term": {
                  "parking": "true"
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

## ベンチマーク

以下のクラスター構成を使用して放射状検索のベンチマークを実行しました。

| OpenSearch バージョン | リーダーノード数 | リーダーノードタイプ | リーダーノードディスク容量 | データノード数 | データノードタイプ | データノードディスク容量 | プライマリシャード数 | レプリカ数 | アベイラビリティゾーン | テストクライアントタイプ |
|---------------------|----------------|-------------------|----------------------|--------------|------------------|---------------------|-------------------|-----------|---------------------|---------------------|
| 2.14 | 3 | c6g.xlarge | 50 GB | 3 | r6g.2xlarge | 100 GB | 3 | 1 | us-east-1 | m5.2xlarge |

### ベンチマークツール

ベンチマークには [OpenSearch Benchmark](https://opensearch.org/docs/latest/benchmark/) を使用しました。

### データセット

ベンチマークには以下のデータセットを使用しました。

| 名前 | 次元数 | ドキュメント数 | クエリ数 | 空間タイプ |
|-----|-------|-------------|---------|----------|
| cohere-wikipedia-22-12-en-embeddings | 768 | 1M | 10k | 内積 |

データセットは、top K 閾値と放射状閾値の真の近傍を含むように更新されました。ベンチマークでは、top K は放射状検索の最小スコアと最大距離の閾値を設定する際に考慮される最近傍の数を指します。例えば、top K 100 の設定は、これらの閾値を決定するためにクエリポイントに最も近い 100 番目のドキュメントを使用したことを意味します。以下の表は閾値の構成をまとめています。

| 閾値名 | 最小スコア閾値 | 真の近傍の中央値 | 真の近傍の平均値 | 近傍が 0 のクエリターゲット数 |
|-------|--------------|----------------|----------------|--------------------------|
| threshold1 | 161 | 118 | 83.1888 | 4048 |
| threshold2 | 156 | 1186 | 421.8486 | 1661 |
| threshold3 | 154 | 2959 | 778.0673 | 941 |

### アルゴリズム

使用したアルゴリズムは以下のように構成されました。

| アルゴリズム名 | ef construction | ef search | hnsw m |
|-------------|-----------------|-----------|--------|
| HNSW | 256 | 256 | 16 |

### 結果

以下の表はベンチマーク結果を示しています。

| クエリ閾値 | エンジンタイプ | クエリタイプ | 検索: 50 パーセンタイルサービス時間 (ms) | 検索: 90 パーセンタイルサービス時間 (ms) | 検索: 99 パーセンタイルサービス時間 (ms) | 再現率 |
|----------|-------------|-----------|-------------------------------------|-------------------------------------|-------------------------------------|-------|
| min score threshold1 | Faiss | min_score | 6.24 | 7.33 | 11.11 | 0.99 |
| min score threshold2 | Faiss | min_score | 7.76 | 13.58 | 26.83 | 0.98 |
| min score threshold3 | Faiss | min_score | 6.89 | 12.13 | 25.59 | 0.98 |
| min score threshold1 | Lucene | min_score | 4.42 | 17.01 | 50.14 | 0.85 |
| min score threshold2 | Lucene | min_score | 13.02 | 54.16 | 118.65 | 0.90 |
| min score threshold3 | Lucene | min_score | 22.56 | 84.5 | 161.62 | 0.92 |

## まとめ

OpenSearch 2.14 ではベクトル放射状検索が導入され、k-NN プラグインの機能が大幅に拡張されました。この強力な機能により、距離またはスコアの閾値に基づく検索が可能になり、さまざまなアプリケーションに対してより高い柔軟性を提供します。Lucene と Faiss の両方のエンジンでサポートされており、放射状検索は多様なユースケースに対応します。

このブログ記事の例を試して、ベクトル放射状検索を使用して検索を改善し、パフォーマンスを向上させてください。ベクトル放射状検索の詳細については、[放射状検索のドキュメント](https://opensearch.org/docs/latest/search-plugins/knn/radial-search-knn/) を参照してください。
