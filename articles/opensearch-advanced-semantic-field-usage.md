---
title: "[翻訳] OpenSearch における semantic フィールドの高度な使い方"
emoji: "🔍"
type: "tech"
topics: ["opensearch", "semanticsearch", "machinelearning", "vectorsearch", "nlp"]
published: true
publication_name: "opensearch"
published_at: 2025-07-23
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/advanced-usage-of-the-semantic-field-in-opensearch/

[前回のブログ記事](https://opensearch.org/blog/the-new-semantic-field-simplifying-semantic-search-in-opensearch/)では、OpenSearch の新しい `semantic` フィールドを紹介し、基本的なセットアップについて説明しました。本記事では、テキストチャンキングの有効化、リモートクラスターでの利用、カスタムモデルや外部ホスト型モデルの使用、フィールドに関連付けられたモデル ID の更新など、`semantic` フィールドの高度な設定について詳しく解説します。また、現在の制限事項についても詳しく説明します。

## テキストチャンキングを使用した semantic フィールドの利用方法

実際のユースケースでは、入力テキストがモデルの最大長を超えることがあり、これにより切り捨てが発生して検索精度が低下する可能性があります。この問題に対処するため、自動テキストチャンキングを有効にできます。

デフォルトでは、ネストフィールドに関連する検索オーバーヘッドを避けるためにチャンキングは無効になっています。有効にするには、`chunking` フラグを使用します。

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
        "model_id": "No0hhZcBnsM8JstbBkjQ",
        "chunking": true
      }
    }
  }
}
```

チャンキングが有効になっていることを確認するには、インデックスマッピングを確認します。

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
                    "raw_field_type": "text",
                    "chunking": true
                },
                "text_semantic_info": {
                    "properties": {
                        "chunks": {
                            "type": "nested",
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
                                "text": {
                                    "type": "text"
                                }
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

レスポンスには `text_semantic_info.chunks` の下に `nested` フィールドが含まれ、各チャンクには独自の `embedding` と対応するテキストが含まれます。

### チャンキングを使用したドキュメントのインデックス作成

長いドキュメントをインデックスすると、OpenSearch はテキストをチャンクに分割し、各チャンクに対してエンベディングを生成します。

```json
PUT /my-nlp-index/_doc/1
{
    "text": "Nestled high in the heart...stretches up the slopes...",
    "id": "4319130149.jpg"
}
```

```json
GET /my-nlp-index/_doc/1
{
    "_index": "my-nlp-index",
    "_id": "1",
    "_version": 2,
    "_seq_no": 2,
    "_primary_term": 1,
    "found": true,
    "_source": {
        "text": "Nestled high in the heart...stretches up the slopes...",
        "id": "1775029934.jpg",
        "text_semantic_info": {
            "chunks": [
                {
                    "text": "Nestled high in the heart... ",
                    "embedding": [
                        0.011091858,
                        ...
                    ]
                },
                {
                    "text": "stretches up the slopes...",
                    "embedding": [
                        0.012340585,
                        ...
                    ]
                }
            ],
            "model": {
                "name": "huggingface/sentence-transformers/all-MiniLM-L6-v2",
                "id": "No0hhZcBnsM8JstbBkjQ",
                "type": "TEXT_EMBEDDING"
            }
        }
    }
}
```

各チャンクは `text_semantic_info.chunks` の下に、独自のエンベディングベクトルとともに表示されます。

## リモートクラスターでの semantic フィールドの使用

OpenSearch はクロスクラスター検索をサポートしていますが、`neural` クエリは現在、リモートクラスターからの `semantic` フィールドの設定の自動解決をサポートしていません。回避策として、クエリ内で基盤となるエンベディングフィールドを明示的に指定できます。

スパースモデルの場合は、以下のリクエストを使用します。

```json
GET /my-nlp-index/_search
{
  "_source": {
    "excludes": [
      "text_semantic_info"
    ]
  },
  "query": {
    "neural_sparse": {
      "text_semantic_info.embedding": {
        "query_text": "wild west",
        "analyzer": "bert-uncased"
      }
    }
  }
}
```

チャンキングが有効な場合は、ネストクエリを使用します。

```json
GET /my-nlp-index/_search
{
  "_source": {
    "excludes": [
      "text_semantic_info"
    ]
  },
  "query": {
    "nested": {
      "path": "text_semantic_info.chunks",
      "neural_sparse": {
        "text_semantic_info.chunks.embedding": {
            "query_text": "wild west",
            "model_id": "No0hhZcBnsM8JstbBkjQ"
        }
      }
    }
  }
}
```

## neural sparse two-phase processor を使用した semantic フィールドの利用

スパースエンベディングを使用する場合、`semantic` フィールドを使用すると、モデルやアナライザーを手動で指定せずに `neural` クエリを使用できます。この場合、OpenSearch はフィールドマッピングに基づいてこれらを自動的に解決します。ただし、この利便性には制限があります。検索レイテンシを改善できる [neural_sparse_two_phase_processor](https://docs.opensearch.org/docs/latest/search-plugins/search-pipelines/neural-sparse-query-two-phase-processor/) は、`semantic` フィールドに対して直接クエリを実行する場合、現在サポートされていません。

回避策として、`semantic` フィールドをバイパスし、基盤となる `embedding` フィールド (例: `text_semantic_info.embedding`) に対して直接 `neural_sparse` クエリを実行できます。クロスクラスター検索で使用されるアプローチと同様に、このアプローチにより、インデックス作成時の自動エンベディング生成の恩恵を受けながら、`neural_sparse_two_phase_processor` を使用できます。

## カスタムモデルまたは外部ホスト型モデルでの semantic フィールドの使用

[カスタム](https://docs.opensearch.org/docs/latest/ml-commons-plugin/custom-local-models/)モデルまたは[外部ホスト型](https://docs.opensearch.org/docs/latest/ml-commons-plugin/remote-models/index/)モデルを使用するには、モデル登録時に必要なモデル設定を提供します。OpenSearch はこのメタデータを使用して、適切な `knn_vector` または `rank_features` フィールドを構築します。

### カスタムモデルの登録

`function_name` は、デンスモデルの場合は `TEXT_EMBEDDING` に、スパースモデルの場合はモデルの機能に応じて `SPARSE_ENCODING` または `SPARSE_TOKENIZE` に設定する必要があります。

**例: デンスモデルの登録**

```json
POST /_plugins/_ml/models/_register
{
    "name": "huggingface/sentence-transformers/msmarco-distilbert-base-tas-b",
    "version": "1.0.1",
    "model_group_id": "wlcnb4kBJ1eYAeTMHlV6",
    "description": "This is a port of the DistilBert TAS-B Model to sentence-transformers model: It maps sentences & paragraphs to a 768 dimensional dense vector space and is optimized for the task of semantic search.",
    "function_name": "TEXT_EMBEDDING",
    "model_format": "TORCH_SCRIPT",
    "model_content_size_in_bytes": 266352827,
    "model_content_hash_value": "acdc81b652b83121f914c5912ae27c0fca8fabf270e6f191ace6979a19830413",
    "model_config": {
        "model_type": "distilbert",
        "embedding_dimension": 768,
        "framework_type": "sentence_transformers",
        "all_config": "{\"_name_or_path\":\"old_models/msmarco-distilbert-base-tas-b/0_Transformer\",\"activation\":\"gelu\",\"architectures\":[\"DistilBertModel\"],\"attention_dropout\":0.1,\"dim\":768,\"dropout\":0.1,\"hidden_dim\":3072,\"initializer_range\":0.02,\"max_position_embeddings\":512,\"model_type\":\"distilbert\",\"n_heads\":12,\"n_layers\":6,\"pad_token_id\":0,\"qa_dropout\":0.1,\"seq_classif_dropout\":0.2,\"sinusoidal_pos_embds\":false,\"tie_weights_\":true,\"transformers_version\":\"4.7.0\",\"vocab_size\":30522}",
        "additional_config": {
            "space_type": "l2"
        }
    },
    "created_time": 1676073973126,
    "url": "https://artifacts.opensearch.org/models/ml-models/huggingface/sentence-transformers/msmarco-distilbert-base-tas-b/1.0.1/torch_script/sentence-transformers_msmarco-distilbert-base-tas-b-1.0.1-torch_script.zip"
}
```

### 外部ホスト型モデルの登録

外部ホスト型モデルは `function_name` として `remote` を使用する必要があります。`model_config` で `model_type` を明示的に定義します。

**例: 外部ホスト型デンスモデルの登録**

```json
POST /_plugins/_ml/models/_register
{
    "name": "remote-dense-model",
    "function_name": "remote",
    "model_group_id": "1jriBYsBq7EKuKzZX131",
    "description": "test model",
    "connector_id": "a1eMb4kBJ1eYAeTMAljY",
    "model_config": {
        "model_type": "TEXT_EMBEDDING",
        "embedding_dimension": 768,
        "additional_config": {
            "space_type": "l2"
        }
    }
}
```

**例: 外部ホスト型スパースモデルの登録**

```json
POST /_plugins/_ml/models/_register
{
    "name": "remote-sparse-model",
    "function_name": "remote",
    "model_group_id": "1jriBYsBq7EKuKzZX131",
    "description": "test model",
    "connector_id": "a1eMb4kBJ1eYAeTMAljY",
    "model_config": {
        "model_type": "SPARSE_ENCODING"
    }
}
```

## semantic フィールドのモデル ID の更新

`semantic` フィールドで使用されるモデル ID を更新できます。これは以下の場合に便利です。

* モデルの新しいバージョンに切り替えたい場合
* 再デプロイされたモデルが新しいモデル ID を生成した場合

モデル ID を更新するには、Update Mapping API を使用します。デンスモデルの場合、新しいモデルが同じ `embedding_dimension` と `space_type` を持っていることを確認してください。これらのパラメータは `knn_vector` フィールドで固定されており、インデックス作成後に変更できません。

## 制限事項

`semantic` フィールドはセマンティック検索を簡素化するように設計されていますが、現在、高度なユースケースに影響を与える可能性のあるいくつかの制限があります。

* **リモートクラスターのサポート**: `semantic` フィールドに対する neural クエリは、クロスクラスター検索ではサポートされていません。リモートインデックスからドキュメントを取得できますが、セマンティッククエリにはローカルのモデル設定とインデックスマッピングへのアクセスが必要です。
* **マッピングの制約**: `semantic` フィールドは動的マッピングをサポートしていません。インデックスマッピングで明示的に定義する必要があります。また、別のフィールドの `fields` セクションで `semantic` フィールドを使用することはできません。つまり、マルチフィールド設定はサポートされていません。

## まとめ

OpenSearch の `semantic` フィールドは、モデル推論、エンベディング生成、フィールドマッピングを単一の宣言的なステップで処理することで、ニューラル検索アプリケーションの開発を効率化します。デンスモデルとスパースモデルの両方をサポートし、カスタムインジェストパイプラインの必要性を排除します。本記事では、テキストチャンキング、クロスクラスター検索、カスタムモデルやリモートモデルの統合などの高度な機能について説明しました。この機能にはいくつかの制限がありますが、セマンティック検索の実装に対する障壁を大幅に下げます。コミュニティからのフィードバックに基づいた継続的な改善を楽しみにしています。

## 今後の展望

現在の制限に対処するため、既存のセマンティック検索機能に対するいくつかの改善に取り組んでいます。

* [リモートクエリのサポート改善](https://github.com/opensearch-project/neural-search/issues/1353): クラスター間でモデル設定を取得・解決することで、リモートクラスターの `semantic` フィールドに対する `neural` クエリを可能にします。
* [二段階スパースクエリのサポート](https://github.com/opensearch-project/neural-search/issues/1352): `semantic` フィールドと `neural_sparse_two_phase_processor` の互換性を有効にし、レイテンシを削減してスパース検索のパフォーマンスを向上させます。
