---
title: "[翻訳] OpenSearch で flat object を使用する"
emoji: "📦"
type: "tech"
topics: ["opensearch", "elasticsearch", "mapping", "json", "検索"]
published: true
published_at: 2023-06-13
publication_name: "opensearch"
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/flat-object/

[OpenSearch 2.7](https://opensearch.org/blog/get-started-opensearch-2-7-0/) で新しい `flat_object` フィールドタイプが導入されました。このフィールドタイプは、多数のフィールドを持つオブジェクトや、ドキュメント内のフィールド名が不明な場合に便利です。`flat_object` フィールドタイプは JSON オブジェクト全体を文字列として扱います。JSON オブジェクト内のサブフィールドには `flat_object` フィールド名または標準のドットパス表記でアクセスできますが、高速検索用にはインデックス化されません。本記事では、flat object がどのようにデータ構造のマッピングを簡素化し、OpenSearch での検索体験を向上させるかを探ります。

## ダイナミックマッピング

OpenSearch では、[*マッピング*](https://opensearch.org/docs/latest/field-types/index/) がデータの構造を定義します。フィールド名、型、インデックス設定、分析設定を指定し、データが正しく整理・解釈されることを保証します。カスタムマッピングを指定しない場合、OpenSearch はドキュメントのアップロード時に自動的に構造を推論します。このプロセスは *ダイナミックマッピング* と呼ばれ、OpenSearch がドキュメントのデータ構造を検出し、対応するマッピングファイルを生成します。

## ダイナミックマッピングの限界

ドキュメントが複雑なデータ構造や深くネストされたフィールドを持つ場合、ダイナミックマッピングに依存すると、インデックス内のマッピングされたフィールド数が数百から数千に急速に増加する可能性があります。この「マッピング爆発」はクラスターのパフォーマンスに悪影響を与えます。

マッピング爆発の症状には以下が含まれます。

- `OutOfMemoryError`: マッピングがメモリに収まらないほど大きくなると、OutOfMemoryError が発生し、クラスターやノードが利用不能になる可能性があります。
- `MapperParsingException`: 一意のフィールド名の数が多すぎると、クラスターは `MapperParsingException` や `IllegalArgumentException` などの例外をスローし、マッピング更新が失敗したことを示します。
- パフォーマンス低下: マッピングが大きくなると、インデックス作成と検索操作のパフォーマンスが低下する可能性があります。多数のフィールドを処理するにはより多くのリソースと処理時間が必要となり、インデックス作成の遅延やクエリレイテンシの増加につながる可能性があります。
- ストレージ要件の増加: マッピング内の各フィールドにはストレージスペースが必要です。マッピング爆発により、インデックスのストレージ要件が大幅に増加し、ディスクスペースの使用率に影響を与え、リソース制約につながる可能性があります。

さらに、ドキュメント構造に不慣れな場合、長いドットパスを持つ深くネストされたインデックスを検索するのは不便です。flat object はこれらの問題を両方解決します。

## ユースケース

`flat_object` フィールドタイプの実際のユースケースを示すために、新しい ML Commons リモートモデル推論プロジェクトを使用します。このプロジェクトでは、テンプレートドキュメントを保存・検索できます。機械学習モデルテンプレートの一部のフィールドは、ユーザー定義のキーバリューペアです。これらはユーザーがその場で作成するため、これらのドキュメントを保存するインデックスのマッピングを事前に定義することは困難です。

### サンプルドキュメント

例えば、OpenSearch を OpenAI と Amazon Bedrock に接続してモデル推論を行う以下の 2 つのテンプレートドキュメントを考えてみましょう。

```json
PUT test-index/_doc/1 
{
    "Metadata":{
        "connector_name": "OpenAI Connector",
        "description": "The connector to public OpenAI model service for GPT 3.5",
        "version": 1
    },
    "Parameters": {
        "endpoint": "api.openai.com",
        "protocol": "HTTP",
        "auth": "API_Key",
        "content_type" : "application/json",
        "model": "gpt-3.5-turbo"
    }
}
```

```json
PUT test-index/_doc/2 
{
    "Metadata":{
        "connector_name": "Amazon BedRock",
        "description": "The connector to Bedrock for the generative AI models",
        "version": 2
    },
   "Parameters": {
        "label": "default_label",
        "host": "localhost",
        "port": 8080,
        "protocol": "HTTP",
        "auth": "API_Key",
        "content_type" : "application/json",
        "policy":{
            "policy_id":"p_0001",
            "policy_name":"default_policy"
            }
    } 
}
```

### flat object を使用しないマッピング

`test-index` のマッピングを指定せず、OpenSearch にダイナミックマッピングを適用させると、インデックスにアップロードされた 1 つの JSON ドキュメントに対して、OpenSearch はすべてのフィールドとサブフィールドのマッピングを生成します。したがって、OpenSearch は以下のマッピングを生成し、上記ドキュメントのすべてのフィールドとサブフィールドを追跡できます。

```json
{
  "test-index": {
    "mappings": {
      "properties": {
        "Metadata": {
          "properties": {
            "connector_name": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "description": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "version": {
              "type": "long"
            }
          }
        },
        "Parameters": {
          "properties": {
            "auth": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "content_type": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "endpoint": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "host": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "label": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "model": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "policy": {
              "properties": {
                "policy_id": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "policy_name": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                }
              }
            },
            "port": {
              "type": "long"
            },
            "protocol": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword",
                  "ignore_above": 256
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

しかし、モデルサービスには多くのパラメータがある場合や、各モデルサービスが異なるパラメータを持つ場合にモデルサービスの数が増加することがよくあります。ダイナミックマッピングでは、すべてのサブフィールドがインデックス可能なフィールドであるため、マッピングファイルが非常に大きくなる可能性があります。

### flat object を使用しない検索

モデルパラメータを検索する場合、サブフィールドへのドットパスを事前に知っておく必要があります。例えば、id が `p_0001` のポリシーを検索する場合、正確なドットパス `Parameters.policy.policy_id` を使用する必要があります。

```json
GET /test-index/_search
{
  "query": {
    "match": {"Parameters.policy.policy_id": "p_0001"}
  }
}
```

### flat object を使用したマッピング

`flat_object` フィールドタイプを使用すると、`Parameters` フィールド全体を JSON オブジェクトではなく文字列として保存し、サブフィールドのフィールド名を指定する必要がありません。

```json
PUT /test-index/
{
  "mappings": {
    "properties": {
      "Parameters": {
        "type": "flat_object"
      }
    }
  }
}
```

同じドキュメントをアップロードした後、`test-index` のマッピングを確認できます。

```json
GET /test-index/_mappings
```

`flat_object` としてマッピングされた `Parameters` フィールドが唯一のインデックス可能なフィールドです。そのサブフィールドはインデックス化されないため、マッピング爆発を効果的に防止します。

```json
{
  "test-index": {
    "mappings": {
      "properties": {
        "Metadata": {
          "properties": {
            "connector_name": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "description": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "version": {
              "type": "long"
            }
          }
        },
        "Parameters": {
          "type": "flat_object"
        }
      }
    }
  }
}
```

### flat object を使用した検索

モデルパラメータを検索する場合、`flat_object` フィールド名である `Parameters` を使用できます。

```json
GET /test-index/_search
{
  "query": {
    "match": {"Parameters": "p_0001"}
  }
}
```

または、便利な完全一致検索のために標準のドットパス表記を使用することもできます。

```json
GET /test-index/_search
{
  "query": {
    "match": {"Parameters.policy.policy_id": "p_0001"}
  }
}
```

どちらの場合も、正しいドキュメントが返されます。

```json
{
  "took" : 142,
  "timed_out" : false,
  "_shards" : {
    "total" : 1,
    "successful" : 1,
    "skipped" : 0,
    "failed" : 0
  },
  "hits" : {
    "total" : {
      "value" : 1,
      "relation" : "eq"
    },
    "max_score" : 1.0601075,
    "hits" : [
      {
        "_index" : "test-index",
        "_id" : "2",
        "_score" : 1.0601075,
        "_source" : {
          "Metadata" : {
            "connector_name" : "Amazon BedRock",
            "description" : "The connector to Bedrock for the generative AI models",
            "version" : 2
          },
          "Parameters" : {
            "label" : "default_label",
            "host" : "localhost",
            "port" : 8080,
            "protocol" : "HTTP",
            "auth" : "API_Key",
            "content_type" : "application/json",
            "policy" : {
              "policy_id" : "p_0001",
              "policy_name" : "default_policy"
            }
          }
        }
      }
    ]
  }
}
```

## 今後の予定

flat object の機能と制限の詳細については、[flat object ドキュメント](https://opensearch.org/docs/latest/field-types/supported-field-types/flat-object/)を参照してください。

Painless スクリプトを使用して flat object 内のサブフィールドを検索する機能を追加しています。詳細は [GitHub issue](https://github.com/opensearch-project/OpenSearch/issues/7138) を参照してください。また、flat object に [open parameters](https://github.com/opensearch-project/OpenSearch/issues/7137) のサポートを追加しています。

本記事で言及した新しい ML Commons リモートモデル推論プロジェクトの詳細については、[Extensibility for OpenSearch Machine Learning](https://github.com/opensearch-project/ml-commons/issues/881) を参照してください。

## コントリビューター

以下のコミュニティメンバーが flat object の実装に貢献しました。

- [Mingshi Liu](https://github.com/mingshl)
- [Lukáš Vlček](https://github.com/lukas-vlcek)

貢献いただきありがとうございます！
