---
title: "[翻訳] 新しい semantic フィールド: OpenSearch でセマンティック検索をシンプルに"
emoji: "🧠"
type: "tech"
topics: ["opensearch", "semanticsearch", "vectorsearch", "machinelearning", "nlp"]
published: true
publication_name: "opensearch"
published_at: 2025-07-31
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/the-new-semantic-field-simplifying-semantic-search-in-opensearch/

セマンティック検索は、機械学習 (ML) モデルを使用して非構造化テキストからデンスまたはスパースベクトルエンベディングを生成することで、検索結果の関連性を向上させます。従来、セマンティック検索を有効にするには、エンベディングフィールドの定義、インジェストパイプラインのセットアップ、すべてのクエリへのモデル ID の含有など、いくつかの手動ステップが必要でした。

OpenSearch 3.1 では、`semantic` フィールドタイプによりこのプロセスが効率化されました。ML モデルを登録・デプロイし、そのモデル ID をインデックスマッピングで参照するだけで済みます。OpenSearch が残りの作業を処理します。必要なエンベディングフィールドを自動的に作成し、インジェスト中にエンベディングを生成し、クエリ実行時にモデルを解決します。以下の図は、`semantic` フィールドを使用したセマンティック検索を示しています。

![semantic フィールドのフローチャート](/images/opensearch-semantic-field-intro/semantic_field_future_state.png)

## semantic フィールドの使い方

`semantic` フィールドを使用するには、以下の手順に従います。

1. **モデルの登録とデプロイ**: Hugging Face などの ML モデルを OpenSearch に登録・デプロイします。
2. **semantic フィールドを持つインデックスの作成**: `semantic` フィールドを含むインデックスマッピングを定義し、モデル ID を使用してモデルにリンクします。
3. **ドキュメントのインデックス作成**: 生のテキストドキュメントを直接インデックスします。OpenSearch が自動的にエンベディングを生成・保存します。
4. **セマンティック検索クエリの実行**: `neural` クエリを使用して、エンベディングを手動で処理することなくデータをセマンティック検索します。

各ステップの詳細を次のセクションで説明します。

### ステップ 1: モデルの登録とデプロイ

まず、テキストエンベディングモデルを登録・デプロイします。例えば、以下のリクエストは Hugging Face の事前学習済み sentence transformer モデルを登録します。

```json
PUT _plugins/_ml/models/_register?deploy=true
{
  "name": "huggingface/sentence-transformers/all-MiniLM-L6-v2",
  "version": "1.0.2",
  "model_format": "TORCH_SCRIPT"
}
```

デプロイ後、モデルの設定を取得して主要な詳細を確認します。

```json
GET /_plugins/_ml/models/No0hhZcBnsM8JstbBkjQ
{
    "name": "huggingface/sentence-transformers/all-MiniLM-L6-v2",
    "model_group_id": "Lo0hhZcBnsM8JstbA0hg",
    "algorithm": "TEXT_EMBEDDING",
    "model_version": "1",
    "model_format": "TORCH_SCRIPT",
    "model_state": "DEPLOYED",
    "model_config": {
        "model_type": "bert",
        "embedding_dimension": 384,
        "additional_config": {
            "space_type": "l2"
        },
        ...
    },
    ...
}
```

レスポンスには `embedding_dimension` や `space_type` などのメタデータが含まれます。OpenSearch はこの情報を使用して、インデックスマッピングで `semantic` フィールドを定義する際に、基盤となるエンベディングフィールドを自動的に作成します。

### ステップ 2: semantic フィールドを持つインデックスの作成

インデックス作成と検索にモデルを使用するには、`semantic` フィールドを持つインデックスを作成し、モデル ID を指定します。

```json
PUT /my-nlp-index
{
  "settings": {
    "index.knn": true
  },
  "mappings": {
    "properties": {
      "id": {
        "type": "text"
      },
      "text": {
        "type": "semantic",
        "model_id": "No0hhZcBnsM8JstbBkjQ"
      }
    }
  }
}
```

OpenSearch は自動的に `knn_vector` フィールドを追加し、関連するモデルメタデータを `text_semantic_info` フィールドに保存します。マッピングを確認するには、以下のリクエストを送信します。

```json
GET /my-nlp-index/_mappings
{
    "my-nlp-index": {
        "mappings": {
            "properties": {
                "id": {
                    "type": "text"
                },
                "text": {
                    "type": "semantic",
                    "model_id": "No0hhZcBnsM8JstbBkjQ",
                    "raw_field_type": "text"
                },
                "text_semantic_info": {
                    "properties": {
                        "embedding": {
                            "type": "knn_vector",
                            "dimension": 384,
                            "method": {
                                "engine": "faiss",
                                "space_type": "l2",
                                "name": "hnsw",
                                "parameters": {}
                            }
                        },
                        "model": {
                            "properties": {
                                "id": {
                                    "type": "text",
                                    "index": false
                                },
                                "name": {
                                    "type": "text",
                                    "index": false
                                },
                                "type": {
                                    "type": "text",
                                    "index": false
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
```

### ステップ 3: ドキュメントのインデックス作成

`semantic` フィールドを使用すると、カスタムインジェストパイプラインを定義する必要がなく、ドキュメントを直接インデックスできます。以下の例では [Flickr 画像データセット](https://www.kaggle.com/datasets/hsankesara/flickr-image-dataset)のデータを使用しています。各ドキュメントには画像の説明を含むテキストフィールドと画像 ID 用の `id` フィールドが含まれています。

```json
PUT /my-nlp-index/_doc/1
{
    "text": "A West Virginia university women 's basketball team , officials , and a small gathering of fans are in a West Virginia arena .",
    "id": "4319130149.jpg"
}
```

```json
PUT /my-nlp-index/_doc/2
{
    "text": "A wild animal races across an uncut field with a minimal amount of trees .",
    "id": "1775029934.jpg"
}
```

OpenSearch は関連付けられたモデルを使用して自動的にエンベディングを生成します。ドキュメントを取得して確認できます。

```json
GET /my-nlp-index/_doc/1
{
    "_index": "my-nlp-index",
    "_id": "1",
    "_version": 1,
    "_seq_no": 0,
    "_primary_term": 1,
    "found": true,
    "_source": {
        "text": "A West Virginia university women 's basketball team , officials , and a small gathering of fans are in a West Virginia arena .",
        "id": "4319130149.jpg",
        "text_semantic_info": {
            "model": {
                "name": "huggingface/sentence-transformers/all-MiniLM-L6-v2",
                "id": "No0hhZcBnsM8JstbBkjQ",
                "type": "TEXT_EMBEDDING"
            },
            "embedding": [
                -0.086742505
                ...
            ]
        }
    }
}
```

レスポンスには `text_semantic_info` フィールドにエンベディングとモデルメタデータが含まれます。

### ステップ 4: neural 検索クエリの実行

セマンティック検索を実行するには、`semantic` フィールドで [neural クエリ](https://docs.opensearch.org/docs/latest/query-dsl/specialized/neural/)を使用します。OpenSearch はマッピングで定義されたモデルを使用してクエリエンベディングを生成します。

```json
GET /my-nlp-index/_search
{
  "_source": {
    "excludes": [
      "text_semantic_info"
    ]
  },
  "query": {
    "neural": {
      "text": {
        "query_text": "wild west",
        "k": 1
      }
    }
  }
}
```

クエリは以下の結果を返します。

```json
{
    "took": 15,
    "timed_out": false,
    "_shards": {
        "total": 1,
        "successful": 1,
        "skipped": 0,
        "failed": 0
    },
    "hits": {
        "total": {
            "value": 1,
            "relation": "eq"
        },
        "max_score": 0.42294958,
        "hits": [
            {
                "_index": "my-nlp-index",
                "_id": "2",
                "_score": 0.42294958,
                "_source": {
                    "text": "A wild animal races across an uncut field with a minimal amount of trees .",
                    "id": "1775029934.jpg"
                }
            }
        ]
    }
}
```

## スパースモデルでの semantic フィールドの使用

スパースモデルで `semantic` フィールドを使用する方法は、デンスモデルと似ていますが、いくつかの違いがあります。

スパースモデルは 2 つのモードをサポートしています。

* **Bi-encoder モード**: ドキュメントとクエリの両方のエンベディングに同じモデルを使用します。
* **Doc-only モード**: インジェスト時にドキュメントエンベディングを生成するモデルと、クエリ時に使用するモデルが異なります。

bi-encoder モードを使用するには、通常どおり `semantic` フィールドを定義します。

```json
PUT /my-nlp-index
{
  "mappings": {
    "properties": {
      "id": {
        "type": "text"
      },
      "text": {
        "type": "semantic",
        "model_id": "No0hhZcBnsM8JstbBkjQ"
      }
    }
  }
}
```

doc-only モードを使用するには、マッピングに `search_model_id` を追加します。

```json
PUT /my-nlp-index
{
  "mappings": {
    "properties": {
      "id": {
        "type": "text"
      },
      "text": {
        "type": "semantic",
        "model_id": "No0hhZcBnsM8JstbBkjQ",
        "search_model_id": "TY2piZcBnsM8Jstb-Uhv"
      }
    }
  }
}
```

スパースエンベディングは `rank_features` フィールドタイプを使用します。このフィールドは次元や距離空間の設定を必要としません。

```json
GET /my-nlp-index
{
    "my-nlp-index": {
        "mappings": {
            "properties": {
                "id": {
                    "type": "text"
                },
                "text": {
                    "type": "semantic",
                    "model_id": "R42oiZcBnsM8JstbUUgc",
                    "search_model_id": "TY2piZcBnsM8Jstb-Uhv",
                    "raw_field_type": "text"
                },
                "text_semantic_info": {
                    "properties": {
                        "embedding": {
                            "type": "rank_features"
                        },
                        "model": {
                            "properties": {
                                "id": {
                                    "type": "text",
                                    "index": false
                                },
                                "name": {
                                    "type": "text",
                                    "index": false
                                },
                                "type": {
                                    "type": "text",
                                    "index": false
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
```

## 組み込みアナライザーの使用

スパースクエリ用に組み込みの[検索アナライザー](https://docs.opensearch.org/docs/latest/vector-search/ai-search/neural-sparse-with-pipelines/#sparse-encoding-modelanalyzer-compatibility)をオプションで指定することもできます。このアプローチは、検索関連性がわずかに低下する代わりに、より高速な検索を提供します。

```json
{
  "mappings": {
    "properties": {
      "id": {
        "type": "text"
      },
      "text": {
       "type": "semantic",
        "model_id": "R42oiZcBnsM8JstbUUgc",
        "semantic_field_search_analyzer": "bert-uncased"
      }
    }
  }
}
```

## まとめ

`semantic` フィールドにより、OpenSearch ワークフローにセマンティック検索を簡単に導入できます。自動エンベディングとインデックス作成でデンスモデルとスパースモデルの両方をサポートすることで、カスタムパイプラインや手動のフィールド管理が不要になります。事前学習済みモデルで試して、ドキュメント検索体験を効率化してください。

## 次のステップ

`semantic` フィールドに関する次のブログ記事では、OpenSearch における `semantic` フィールドの高度な使い方について説明します。長いテキストのチャンキング、外部ホスト型またはカスタムモデルの使用、クロスクラスターサポートの実装、モデル ID の更新などの高度な機能について詳しく説明します。このブログ記事をお楽しみに。理解を深め、より強力な検索機能を活用してください！
