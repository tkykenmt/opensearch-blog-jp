---
title: "[翻訳] OpenSearch の ML 推論プロセッサ入門: レビュー要約とセマンティック検索"
emoji: "🤖"
type: "tech"
topics: ["opensearch", "machinelearning", "semanticsearch", "llm", "ai"]
published: true
publication_name: "opensearch"
published_at: 2025-07-15
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/introduction-to-ml-inference-processors-in-opensearch-review-summarization-and-semantic-search/

AI が情報との関わり方を革新する時代において、従来のキーワードベースの検索はますます不十分になっています。ユーザーは検索エンジンがコンテキストを理解し、自然言語を解釈し、インテリジェントな結果を提供することを期待しています。そのため、機械学習 (ML) 機能を検索操作に直接統合する能力がますます重要になっています。OpenSearch の ML 推論プロセッサは、ML モデルをインジェストおよび検索ワークフローにシームレスに統合することで、この問題を解決します。次世代のエンタープライズ検索プラットフォームを構築する場合でも、既存の検索インフラストラクチャを AI 機能で強化する場合でも、ML 推論プロセッサは現代のユーザーの期待に応えるインテリジェントな検索体験の基盤を提供します。

## ML 推論プロセッサとは

OpenSearch は 3 種類の ML 推論プロセッサを提供しており、それぞれがインジェストパイプラインまたは検索パイプラインで特定の目的を果たします。

* **ML 推論インジェストプロセッサ** (2.14 でリリース): ドキュメントのインデックス作成中にモデル推論を実行し、ML モデルを使用してドキュメントを保存前にエンリッチまたは変換できます。例えば、インデックス作成中にテキストエンベディングを生成したり、ドキュメントにセンチメントラベルを追加したりできます。
* **ML 検索リクエストプロセッサ** (2.16 でリリース): 検索クエリが実行される前にモデル推論を実行し、クエリの強化や変換を可能にします。ML モデルの出力に基づいてクエリを書き換えることができ、クエリの理解と拡張に特に有用です。
* **ML 検索レスポンスプロセッサ** (2.16 でリリース): 検索結果がユーザーに返される前にモデル推論を実行して検索結果をエンリッチし、結果の再ランキングや検索結果への ML 生成サマリーの追加などの機能を可能にします。

以下の図は、ML 推論プロセッサが OpenSearch のインデックス作成、クエリ、検索結果処理とどのように統合されるかを示しています。ユーザークエリまたはドキュメント、モデル呼び出し、エンリッチされたレスポンスを含むエンドツーエンドのフローを示しています。

![OpenSearch 機械学習推論プロセッサの図](/images/opensearch-ml-inference-processors-intro/ml-inference-processors.png)

## 主なメリット

ML 推論プロセッサは以下の主要なメリットを提供します。

* 柔軟性: ローカルおよび外部 ML モデルの両方をサポート
* リアルタイム処理: インジェストおよび検索操作中に ML 推論を実行
* カスタマイズ性: 入出力マッピングの豊富な設定オプション
* 使いやすさ: 検索/インジェストパイプラインで ML 推論プロセッサを設定すると、すべてのインジェスト/検索操作に自動的に適用

## 一般的なユースケース

ML 推論プロセッサは様々な高度な検索機能を実現します。

* セマンティック検索: テキストエンベディングを使用してドキュメントを生成・検索
* マルチモーダル検索: テキストと画像検索を組み合わせ
* クエリ理解: ML ベースの理解でクエリを強化
* 結果ランキング: ML モデルを使用して結果の関連性を向上
* ドキュメントエンリッチメント: インデックス作成中に ML 生成メタデータを追加

## はじめに: 検索と要約パイプライン

ML 推論検索レスポンスプロセッサを使用して、テキストエンベディングモデルによるセマンティック検索と大規模言語モデル (LLM) による要約生成を実装する実践的な例を見ていきましょう。

### ステップ 1: OpenSearch にモデルを登録

まず、エンベディング生成用のテキストエンベディングモデルと要約用の LLM の 2 つのモデルを登録する必要があります。この例では、`amazon.titan-embed-text-v2:0` テキストエンベディングモデルと `us.anthropic.claude-3-7-sonnet-20250219-v1:0` LLM を使用します。

テキストエンベディングモデルを登録します。

```json
POST /_plugins/_ml/connectors/_create
{
  "name": "Amazon Bedrock: amazon.titan-embed-text-v2:0",
  "function_name": "remote",
  "description": "amazon.titan-embed-text-v2:0 model to generate embeddings",
  "connector": {
    "name": "Amazon Bedrock Connector: embedding",
    "description": "The connector to bedrock Titan embedding model",
    "version": 1,
    "protocol": "aws_sigv4",
    "parameters": {
        "region": "{{aws_region}}",
        "service_name": "bedrock",
        "model": "amazon.titan-embed-text-v2:0",
        "dimensions": 1024,
        "normalize": true,
        "embeddingTypes": ["float"]
    },
    "credential": {
        "access_key": "{{access_key}}",
        "secret_key": "{{secret_key}}",
        "session_token": "{{session_token}}"
    },
    "actions": [
        {
        "action_type": "predict",
        "method": "POST",
        "url": "https://bedrock-runtime.${parameters.region}.amazonaws.com/model/${parameters.model}/invoke",
        "headers": {
            "content-type": "application/json",
            "x-amz-content-sha256": "required"
        },
            "request_body": "{ \"inputText\": \"${parameters.inputText}\", \"dimensions\": ${parameters.dimensions}, \"normalize\": ${parameters.normalize}, \"embeddingTypes\": ${parameters.embeddingTypes} }"
        }
    ]
  }
}
```

レスポンスのモデル ID をメモしておきます。以降のステップで使用します。

```json
{
    "task_id": "BkfyvJcBIkSrvQFRJf_E",
    "status": "CREATED",
    "model_id": "B0fyvJcBIkSrvQFRJf_j"
}
```

このモデルは以下のモデル入力スキーマを必要とします。入力テキストからエンベディングを生成するには、以下のリクエストを実行します。リクエストにテキストエンベディングモデルのモデル ID を指定します。

```json
POST /_plugins/_ml/models/B0fyvJcBIkSrvQFRJf_j/_predict
{
  "parameters": {
    "inputText": "cute women jacket"
  }
}
```

レスポンスのモデル出力スキーマをメモしておきます。

```json
{
    "inference_results": [
        {
            "output": [
                {
                    "name": "response",
                    "dataAsMap": {
                        "embedding": [
                            -0.09490113705396652,
                            0.09895417094230652,
                            0.02126065082848072, 
                            ...],
                        "embeddingsByType": {
                            "float": [
                                -0.09490113705396652,
                                0.09895417094230652,
                                0.02126065082848072,
                                ... ]
                        },
                        "inputTextTokenCount": 5
                    }
                }
            ],
            "status_code": 200
        }
    ]
}
```

次に、LLM を登録します。

```json
POST /_plugins/_ml/connectors/_create
{
  "name": "Amazon Bedrock: claude-3-7-sonnet-20250219-v1:0",
  "function_name": "remote",
  "description": "claude-3-7-sonnet-20250219-v1:0 model to generate review summary",
  "connector": {
    "name": "Amazon Bedrock Connector: claude-3-7-sonnet-20250219-v1:0",
    "description": "The connector to bedrock claude-3-7-sonnet-20250219-v1:0",
    "version": 1,
    "protocol": "aws_sigv4",
    "parameters": {
        "region": "{{aws_region}}",
        "service_name": "bedrock",
        "max_tokens": 8000,
        "temperature": 1,
        "anthropic_version": "bedrock-2023-05-31",
        "model": "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    },
    "credential": {
        "access_key": "{{access_key}}",
        "secret_key": "{{secret_key}}",
        "session_token": "{{session_token}}"
    },
    "actions": [
        {
            "action_type": "predict",
            "method": "POST",
            "headers": {
                "content-type": "application/json"
            },
            "url": "https://bedrock-runtime.${parameters.region}.amazonaws.com/model/${parameters.model}/invoke",
            "request_body": "{ \"anthropic_version\": \"${parameters.anthropic_version}\", \"max_tokens\": ${parameters.max_tokens}, \"temperature\": ${parameters.temperature}, \"messages\": ${parameters.messages} }"
        }
    ]
  }
}
```

レスポンスのモデル ID をメモしておきます。

```json
{
    "task_id": "AkfavJcBIkSrvQFRP_9s",
    "status": "CREATED",
    "model_id": "A0favJcBIkSrvQFRP_-N"
}
```

このモデルは以下のモデル入力スキーマを必要とします。

```json
POST /_plugins/_ml/models/A0favJcBIkSrvQFRP_-N/_predict
{
    "parameters": {
        "context": "Recently, i have been so wanting to get a lightwash denim jacket and i found the piece right here! i love that its cropped and so easy to wear. its not stiff at all and sized right. i got an xs my normal size and its so comfy and surprisingly soft. great find but just a bit pricey.. but probably bc its paige. too bad pilcrow couldn't have made something like this.",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "you are a helpful assistant, help me summarize the context from ${parameters.context}, and show me the summary in 60 words."
                    }
                ]
            }
        ]
    }
}
```

レスポンスのモデル出力スキーマをメモしておきます。

```json
{
    "inference_results": [
        {
            "output": [
                {
                    "name": "response",
                    "dataAsMap": {
                        "id": "msg_bdrk_01EA4VRf9YVK1hVZeGojqDNc",
                        "type": "message",
                        "role": "assistant",
                        "model": "claude-3-7-sonnet-20250219",
                        "content": [
                            {
                                "type": "text",
                                "text": "# Summary\n\nThe author found a cropped light-wash denim jacket by Paige that they love. The jacket is comfortable, soft, not stiff, and fits well in their usual XS size. While they're pleased with the purchase, they feel it's somewhat expensive and wish a more affordable brand like Pilcrow offered a similar style."
                            }
                        ],
                        "stop_reason": "end_turn",
                        "usage": {
                            "input_tokens": 123.0,
                            "cache_creation_input_tokens": 0.0,
                            "cache_read_input_tokens": 0.0,
                            "output_tokens": 77.0
                        }
                    }
                }
            ],
            "status_code": 200
        }
    ]
}
```

### ステップ 2: インジェストパイプラインの作成

次に、ドキュメントのエンベディングを自動生成するインジェストパイプラインを作成します。このパイプラインは ML 推論プロセッサを使用して、各受信ドキュメントの `review_text` フィールドからテキストを抽出し、そのテキストを登録済みのテキストエンベディングモデルに送信し、モデルのレスポンスから生成されたエンベディングを取得し、そのエンベディングを新しい `review_embedding` フィールドとしてドキュメントに追加します。

```json
PUT /_ingest/pipeline/titan_embedding_pipeline
{
  "description": "Generate review_embedding for ingested documents",
  "processors": [
    {
      "ml_inference": {
        "model_id": "B0fyvJcBIkSrvQFRJf_j",
        "input_map": [
          {
            "inputText": "review_text"
          }
        ],
        "output_map": [
          {
            "review_embedding": "embedding"
          }
        ]
      }
    }
  ]
}
```

すべてのインジェストされたドキュメントにエンベディングパイプラインを自動適用し、k-NN 検索を設定するインデックスを作成します。

```json
PUT /product-search-and-summarize
{
  "settings": {
    "index": {
      "default_pipeline": "titan_embedding_pipeline",
      "knn": true,
      "knn.algo_param.ef_search": 100
    }
  },
  "mappings": {
    "properties": {
      "review_embedding": {
        "type": "knn_vector",
        "dimension": 1024 
      }
    }
  }
}
```

### ステップ 3: サンプルドキュメントのインジェスト

パイプラインをテストするためにサンプル商品レビュードキュメントをインデックスします。エンベディングは自動的に生成されます。

```json
POST /_bulk
{
  "index": {
    "_index": "clothing_reviews",
    "_id": "11364"
  }
}
{
  "review_id": 11364,
  "clothing_id": 956,
  "age": 83,
  "title": "Great gift!!",
  "review_text": "Got this poncho for christmas and loved it the moment i got it out of the box!! great quality and looks great cant go wrong with this purchase.",
  "rating": 5,
  "recommended": true,
  "positive_feedback_count": 0,
  "division_name": "General Petite",
  "department_name": "Jackets",
  "class_name": "Jackets"
}
{
  "index": {
    "_index": "clothing_reviews",
    "_id": "16373"
  }
}
{
  "review_id": 16373,
  "clothing_id": 956,
  "age": 39,
  "title": "Great \"cardigan\"",
  "review_text": "If you're very small-framed and/or petite, i would size down in this. unless you want a really slouchy look and fit. i have very broad shoulders and very large biceps, and typically wear a m/l in retailer tops. sometimes if a top is a pullover style (as opposed to button-down) i have to size up to a 12 to get the top to accommodate my shoulder width and biceps. so i was leery the size 8/italian 44 would fit, but it does, with room to spare, albeit it is not as loose or long in the ar",
  "rating": 4,
  "recommended": true,
  "positive_feedback_count": 5,
  "division_name": "General",
  "department_name": "Jackets",
  "class_name": "Jackets"
}
```

### ステップ 4: 検索パイプラインの設定

検索クエリを強化するために、設定された LLM を使用して検索レスポンスの要約を生成する検索パイプラインを作成します。

`ml_inference` 検索リクエストプロセッサは、`review_embedding` フィールドを使用して match クエリを k-NN クエリに書き換えるように設定されています。`query.match.review_text.query` をエンベディングモデルの `inputText` パラメータにマッピングし、レビューテキストのベクトル表現を生成します。このプロセッサの出力は `embedding` に格納され、その後 k-NN クエリでエンベディングに基づいて類似のレビューを見つけるために使用されます。

`ml_inference` 検索レスポンスプロセッサの設定は、ML 推論を使用して要約を生成するための 3 部構成のマッピングプロセスを確立します。まず、`input_map` は各検索結果から `review_text` フィールドを取得し、モデル用のコンテキスト変数にマッピングします。次に、`model_config` はこの入力を Claude モデル用の構造化された `messages` 配列としてフォーマットし、実際のレビューテキストのプレースホルダーとして `${parameters.context}` を使用します。最後に、`output_map` はモデルのレスポンス (Claude の出力の `content[0].text` にある) を検索結果の `review_summary` に格納するよう指示します。この完全なフローにより、パイプラインは検索結果を ML モデルを通じて自動的に処理し、生成された要約をレスポンスに添付できます。すべて単一のパイプライン定義で設定されます。

セマンティック検索と自動要約を組み合わせた検索パイプラインを作成し、リクエストプロセッサとレスポンスプロセッサの両方を設定します。

```json
PUT /_search/pipeline/summarization_pipeline
{
    "description": "conduct semantic search for product review and summarize reviews",
    "request_processors": [
        {
            "ml_inference": {
                "tag": "embedding",
                "description": "This processor is to rewriting match query to knn query during search",
                "model_id": "B0fyvJcBIkSrvQFRJf_j",
                "query_template": "{\"query\":{\"knn\":{\"review_embedding\":{\"vector\":${modelPredictionOutcome},\"k\":5}}}}",
                "input_map": [
                    {
                        "inputText": "query.match.review_text.query"
                    }
                ],
                "output_map": [
                    {
                        "modelPredictionOutcome": "embedding"
                    }
                ]
            }
        }
    ],
    "response_processors": [
        {
            "ml_inference": {
                "tag": "summarization",
                "description": "This processor is to summarize reviews during search response",
                "model_id": "A0favJcBIkSrvQFRP_-N",
                "input_map": [
                    {
                        "context": "review_text"
                    }
                ],
                "output_map": [
                    {
                        "review_summary": "content[0].text"
                    }
                ],
                "model_config": {
                    "messages": "[{\"role\":\"user\",\"content\":[{\"type\":\"text\",\"text\":\"you are a helpful assistant, help me summarize the context from ${parameters.context}, and show me the summary in 20 words.\"}]}]"
                },
                "one_to_one": true,
                "ignore_missing": false,
                "ignore_failure": false
            }
        }
    ]
}
```

### ステップ 5: ドキュメントの検索

これで ML 強化パイプラインを使用して検索を実行できます。自然言語の質問を自動的にベクトルエンベディングに変換し、類似のレビューを見つけるセマンティック検索クエリを実行します。

```json
GET /product-search-and-summarize/_search?search_pipeline=summarization_search_pipeline
{
    "query": {
        "match": {
            "review_text":  "I am planning for a vacation to France. Find me a nice jacket"
        }
    }
}
```

検索レスポンスは、`review_summary` フィールドに AI 生成の要約とともに、意味的に関連するドキュメントを返します。これはベクトル類似性マッチングと自動テキスト要約の両方を示しています。

```json
{
    "took": 109,
    "timed_out": false,
    "_shards": {
        "total": 1,
        "successful": 1,
        "skipped": 0,
        "failed": 0
    },
    "hits": {
        "total": {
            "value": 2,
            "relation": "eq"
        },
        "max_score": 0.38024604,
        "hits": [
            {
                "_index": "product-search-and-summarize",
                "_id": "2",
                "_score": 0.38024604,
                "_source": {
                    "review_embedding": [
                        -0.02479235,
                        -0.018683413,
                        0.024477331,
                       ...
                    ],
                    "review_id": 16373,
                    "clothing_id": 956,
                    "department_name": "Jackets",
                    "rating": 4,
                    "title": "Great \"cardigan\"",
                    "recommended": true,
                    "positive_feedback_count": 5,
                    "division_name": "General",
                    "review_text": "If you're very small-framed and/or petite, i would size down in this. unless you want a really slouchy look and fit. i have very broad shoulders and very large biceps, and typically wear a m/l in retailer tops. sometimes if a top is a pullover style (as opposed to button-down) i have to size up to a 12 to get the top to accommodate my shoulder width and biceps. so i was leery the size 8/italian 44 would fit, but it does, with room to spare, albeit it is not as loose or long in the ar",
                    "review_summary": "This top runs large. If you're petite, size down unless you prefer a slouchy fit. Size 8/Italian 44 fits even with broad shoulders.",
                    "class_name": "Jackets",
                    "age": 39
                }
            },
            {
                "_index": "product-search-and-summarize",
                "_id": "1",
                "_score": 0.34915876,
                "_source": {
                    "review_embedding": [
                        -0.025242768,
                        0.041105438,
                        0.073424794,
                        ...
                    ],
                    "review_id": 11359,
                    "clothing_id": 956,
                    "department_name": "Jackets",
                    "rating": 5,
                    "title": "Love!!!",
                    "recommended": true,
                    "positive_feedback_count": 1,
                    "division_name": "General Petite",
                    "review_text": "I fell in love with this poncho at first sight. the colors are neutral so it can be worn with a lot. i'm a typical m and it does run large so i went with a s and it's perfect. long enough to cover leggings and great for the in between seasons. i've worn it at least five times since purchase and get compliments every time.",
                    "review_summary": "Poncho is loved for neutral colors, versatility. Buyer got size small despite being medium. Covers leggings, receives compliments.",
                    "class_name": "Jackets",
                    "age": 37
                }
            }
        ]
    },
    "profile": {
        "shards": []
    }
}
```

### まとめ

OpenSearch の ML 推論プロセッサは、従来のキーワードベースの検索と現代の AI 駆動体験のギャップを埋める、検索技術における大きな飛躍を表しています。この記事で示した実践的な例を通じて、これらのプロセッサがセマンティック検索用のエンベディングモデルとコンテンツ要約用の LLM をシームレスに統合し、よりインテリジェントでユーザーフレンドリーな検索体験を作成できることを見てきました。

インジェスト時のエンベディング処理と検索時の要約処理の組み合わせは、OpenSearch の ML 推論プロセッサの柔軟性とパワーを示しています。このアーキテクチャは、ベクトル類似性マッチングによる検索関連性の向上だけでなく、検索結果の簡潔な AI 生成要約を提供することでユーザー体験も向上させます。

## 次のステップ

ML 推論プロセッサの詳細については、[ML 推論プロセッサ](https://docs.opensearch.org/docs/latest/ingest-pipelines/processors/ml-inference/)、[ML 推論検索リクエストプロセッサ](https://docs.opensearch.org/docs/latest/search-plugins/search-pipelines/ml-inference-search-request/)、[ML 推論検索レスポンスプロセッサ](https://docs.opensearch.org/docs/latest/search-plugins/search-pipelines/ml-inference-search-response/)のドキュメントを参照してください。

特定のユースケースについては、[セマンティック検索チュートリアル](https://docs.opensearch.org/docs/latest/tutorials/vector-search/semantic-search/index/)を参照してください。

皆様の貢献をお待ちしています！共有したいユースケースがある場合は、対応するチュートリアルをドキュメントに追加することを検討してください。
