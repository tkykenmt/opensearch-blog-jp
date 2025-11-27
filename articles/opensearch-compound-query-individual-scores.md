---
publication_name: "opensearch"
title: "OpenSearch の複雑なクエリにおいて、各クエリごとの個別スコアを取得する方法"
emoji: "🔍"
type: "tech"
topics: ["opensearch"]
published: true
published_at: 2025-11-26
---

## はじめに

OpenSearch で複数のクエリを組み合わせた複合クエリ(bool クエリや hybrid クエリ)を実行する際、最終的なスコアだけでなく「どのクエリがどれだけ貢献したか」を知りたいケースがあります。

個別に確認したいクエリとしては、ハイブリッド検索における正規化前のキーワードとベクトルそれぞれの検索スコア、bool クエリにおける各検索条件ごとのスコア、nested query におけるネストされた各ドキュメントごとのスコアなどが挙げられます。

こうした個別のスコアを確認することで、チューニングすべきクエリが見えてきます。OpenSearch にはスコアの詳細な計算過程を検索結果と合わせて返却する explain オプションが存在しますが、explain を有効化するとレイテンシに影響するため、本番での常用は望ましくありません。

本記事では、explain オプションを使用せず、個々のクエリやネストされたドキュメントごとのスコアを取得する方法について解説します。

:::message
**対象バージョン**: 本記事内のクエリは OpenSearch 3.0 以降で動作を確認しています。
:::

## テスト環境のセットアップ

### インデックス作成

k-NN ベクトルを含む nested フィールドを持つインデックスを作成します。

```json
PUT my-knn-index-1
{
  "settings": {
    "index.knn": true,
    "index.knn.memory_optimized_search": true,
    "number_of_replicas": 0,
    "number_of_shards": 1
  },
  "mappings": {
    "properties": {
      "metadata.label": {
        "type": "text"
      },
      "metadata.version": {
        "type": "short"
      },
      "nested_field": {
        "type": "nested",
        "properties": {
          "my_vector": {
            "type": "knn_vector",
            "dimension": 3,
            "space_type": "l2",
            "data_type": "float",
            "mode": "in_memory"
          },
          "my_text": {
            "type": "text"
          }
        }
      }
    }
  }
}
```

### テストデータ投入

```json
POST _bulk?refresh=true
{ "index": { "_index": "my-knn-index-1", "_id": "1" } }
{"nested_field":[{"my_vector":[1,1,1], "my_text": "blue racoon"},{"my_vector":[2,2,2], "my_text": "yellow racoon"},{"my_vector":[3,3,3], "my_text": "white racoon"}], "metadata": {"label": "racoon", "version": 2}}
{ "index": { "_index": "my-knn-index-1", "_id": "2" } }
{"nested_field":[{"my_vector":[10,10,10], "my_text": "red cat"},{"my_vector":[20,20,20], "my_text": "green cat"},{"my_vector":[30,30,30], "my_text": "black cat"}],"metadata": {"label": "cat", "version": 15}}
{ "index": { "_index": "my-knn-index-1", "_id": "3" } }
{"nested_field":[{"my_vector":[100,100,100], "my_text": "brown lion"},{"my_vector":[200,200,200], "my_text": "purple lion"},{"my_vector":[300,300,300], "my_text": "gray lion"}],"metadata": {"label": "lion", "version": 1}}
{ "index": { "_index": "my-knn-index-1", "_id": "4" } }
{"nested_field":[{"my_vector":[1000,1000,1000], "my_text": "silver stray cat"},{"my_vector":[2000,2000,2000], "my_text": "maroon stray cat"},{"my_vector":[3000,3000,3000], "my_text": "black stray cat"}], "metadata": {"label": "stray cat", "version": 20}}
{ "index": { "_index": "my-knn-index-1", "_id": "5" } }
{"nested_field":[{"my_vector":[10000,10000,10000], "my_text": "golden racoon dog"},{"my_vector":[20000,20000,20000], "my_text": "red racoon dog"},{"my_vector":[30000,30000,30000], "my_text": "black racoon dog"}],"metadata": {"label":"racoon dog", "version": 9}}
```

---

## bool クエリでの個別スコア取得

bool クエリの各クエリ `_name` を付与し、`include_named_queries_score=true` で検索します。

このパラメーターは Named Query と呼ばれるものです。検索結果でどのクエリにマッチしたかを `matched_queries` フィールドで確認することができます。

`include_named_queries_score=true` パラメータを Search API に追加することで、**各 Named Query の個別スコア**を取得可能です。

:::message
**パフォーマンスへの影響**: `include_named_queries_score=true` は `explain` オプションと比較してオーバーヘッドが小さく、本番環境でも利用可能です。ただし、多数の Named Query を設定した場合はレスポンスサイズが増加するため、必要なクエリにのみ `_name` を付与することを推奨します。
:::

```json
GET my-knn-index-1/_search?include_named_queries_score=true
{
  "query": {
    "bool": {
      "should": [
        {
          "match": {
            "metadata.label": {
              "query": "cat",
              "_name": "match.metadata.label"
            }
          }
        },
        {
          "match": {
            "metadata.label": {
              "query": "stray",
              "_name": "match.metadata.label2"
            }
          }
        }
      ]
    }
  }
}
```

:::details 実行結果

```json
{
  "hits": {
    "hits": [
      {
        "_id": "4",
        "_score": 0.874715,
        "matched_queries": {
          "match.metadata.label": 0.33857906,
          "match.metadata.label2": 0.5361359
        }
      },
      {
        "_id": "2",
        "_score": 0.45060888,
        "matched_queries": {
          "match.metadata.label": 0.45060888
        }
      }
    ]
  }
}
```

:::

### 結果の読み方

| ドキュメント        | 最終スコア | cat クエリ | stray クエリ |
| ------------------- | ---------- | ---------- | ------------ |
| \_id: 4 (stray cat) | 0.874715   | 0.338      | 0.536        |
| \_id: 2 (cat)       | 0.450      | 0.450      | -            |

- `_id: 4` は両方のクエリにマッチし、スコアが合算されている
- `_id: 2` は "cat" のみにマッチ
- `matched_queries` にはマッチしたクエリのみが含まれる

---

## nested + k-NN クエリでの個別スコア取得

Named query の適用範囲は広く、ベクトル検索にも利用可能です。以下は nested されたベクトルに対して Named query を使用した例です。

```json
GET my-knn-index-1/_search?include_named_queries_score=true
{
  "query": {
    "nested": {
      "path": "nested_field",
      "query": {
        "knn": {
          "nested_field.my_vector": {
            "vector": [1.4, 1.4, 1.4],
            "k": 5
          }
        }
      },
      "score_mode": "max",
      "_name": "nested_knn"
    }
  }
}
```

:::details 実行結果(抜粋)

```json
{
  "hits": [
    {
      "_id": "1",
      "_score": 0.67567575,
      "matched_queries": {
        "nested_knn": 0.67567575
      }
    },
    {
      "_id": "2",
      "_score": 0.0044867187,
      "matched_queries": {
        "nested_knn": 0.0044867187
      }
    },
    {
      "_id": "3",
      "_score": 0.000034285466,
      "matched_queries": {
        "nested_knn": 0.000034285466
      }
    },
    {
      "_id": "4",
      "_score": 3.3426852e-7,
      "matched_queries": {
        "nested_knn": 3.3426852e-7
      }
    },
    {
      "_id": "5",
      "_score": 3.3342673e-9,
      "matched_queries": {
        "nested_knn": 3.3342673e-9
      }
    }
  ]
}
```

:::

上記のクエリでは `score_mode` に `max` を指定していますが、これは最も高いスコアの nested ドキュメントのスコアが親ドキュメントのスコアとするためです。

## inner hits によるドキュメントごとのスコア取得

inner_hits オプションを使用することで、ネストされたドキュメントごとのスコアを確認することができます。

:::message alert
**注意**: `inner_hits` を使用すると、ネストされたドキュメントの情報がレスポンスに含まれるため、レスポンスサイズが大幅に増加する可能性があります。大量の nested ドキュメントがある場合は、`size` パラメータで返却数を制限することを推奨します(例: `"inner_hits": { "size": 3 }`)。
:::

```json
GET my-knn-index-1/_search?include_named_queries_score=true
{
  "query": {
    "nested": {
      "path": "nested_field",
      "query": {
        "knn": {
          "nested_field.my_vector": {
            "vector": [1.4,1.4,1.4],
            "k": 5,
            "expand_nested_docs": true
          }
        }
      },
      "inner_hits": {},
      "score_mode": "max",
      "_name": "nested_knn"
    }
  }
}
```

:::details 実行結果(抜粋)

```json
{
  "hits": [
    {
      "_id": "1",
      "_score": 0.67567575,
      "matched_queries": {
        "nested_knn": 0.67567575
      },
      "inner_hits": {
        "nested_field": {
          "hits": {
            "total": {
              "value": 3,
              "relation": "eq"
            },
            "max_score": 0.67567575,
            "hits": [
              {
                "_index": "my-knn-index-1",
                "_id": "1",
                "_nested": {
                  "field": "nested_field",
                  "offset": 0
                },
                "_score": 0.67567575,
                "_source": {
                  "my_text": "blue racoon",
                  "my_vector": [1, 1, 1]
                }
              },
              {
                "_index": "my-knn-index-1",
                "_id": "1",
                "_nested": {
                  "field": "nested_field",
                  "offset": 1
                },
                "_score": 0.48076925,
                "_source": {
                  "my_text": "yellow racoon",
                  "my_vector": [2, 2, 2]
                }
              },
              {
                "_index": "my-knn-index-1",
                "_id": "1",
                "_nested": {
                  "field": "nested_field",
                  "offset": 2
                },
                "_score": 0.11520737,
                "_source": {
                  "my_text": "white racoon",
                  "my_vector": [3, 3, 3]
                }
              }
            ]
          }
        }
      }
    }
  ]
}
```

:::

## hybrid クエリでの個別スコア取得

OpenSearch のハイブリッド検索では、キーワード検索とベクトル検索を組み合わせて実行できます。各サブクエリに Named Queries を設定することで、正規化前の個別スコアを確認できます。

:::message
**重要**: `matched_queries` で返されるスコアは **正規化前の生スコア** です。最終的な `_score` は `normalization-processor` による正規化後の値となるため、`matched_queries` の値を単純に合算しても `_score` とは一致しません。
:::

inner_hits を複数個所で指定する場合は、name プロパティを付与することで各クエリごとに、ドキュメント単位のスコアを表示することが可能です。

```json
GET my-knn-index-1/_search?include_named_queries_score=true&phase_took
{
 "query": {
   "hybrid": {
     "queries": [
       {
         "bool": {
           "should": [
             {
               "match": {
                 "metadata.label": {
                   "query": "cat",
                   "_name": "match.metadata.label"
                 }
               }
             },
             {
               "match": {
                 "metadata.label": {
                   "query": "stray",
                   "_name": "match.metadata.label2"
                 }
               }
             }
           ]
         }
       },
       {
         "nested": {
           "path": "nested_field",
           "query": {
             "knn": {
               "nested_field.my_vector": {
                 "vector": [1.4, 1.4, 1.4],
                 "k": 5,
                 "expand_nested_docs": true
               }
             }
           },
           "inner_hits": { "name": "nested_knn" },
           "score_mode": "max",
           "_name": "nested_knn"
         }
       },
       {
         "nested": {
           "path": "nested_field",
           "query": {
             "match": {
               "nested_field.my_text": "blue"
             }
           },
           "inner_hits": { "name": "nested_match" },
           "score_mode": "max",
           "_name": "nested_match"
         }
       }
     ]
   }
 },
 "search_pipeline": {
   "phase_results_processors": [
     {
       "normalization-processor": {
         "normalization": { "technique": "z_score" }
       }
     }
   ]
 }
}
```

:::details 実行結果(フルバージョン。長いです)

```json
{
  "took": 5,
  "phase_took": {
    "dfs_pre_query": 0,
    "query": 5,
    "fetch": 0,
    "dfs_query": 0,
    "expand": 0,
    "can_match": 0
  },
  "timed_out": false,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": {
      "value": 5,
      "relation": "eq"
    },
    "max_score": 0.98117065,
    "hits": [
      {
        "_index": "my-knn-index-1",
        "_id": "1",
        "_score": 0.98117065,
        "_source": {
          "nested_field": [
            {
              "my_vector": [1, 1, 1],
              "my_text": "blue racoon"
            },
            {
              "my_vector": [2, 2, 2],
              "my_text": "yellow racoon"
            },
            {
              "my_vector": [3, 3, 3],
              "my_text": "white racoon"
            }
          ],
          "metadata": {
            "label": "racoon",
            "version": 2
          }
        },
        "matched_queries": {
          "nested_match": 1.1546944,
          "nested_knn": 0.67567575
        },
        "inner_hits": {
          "nested_match": {
            "hits": {
              "total": {
                "value": 1,
                "relation": "eq"
              },
              "max_score": 1.1546944,
              "hits": [
                {
                  "_index": "my-knn-index-1",
                  "_id": "1",
                  "_nested": {
                    "field": "nested_field",
                    "offset": 0
                  },
                  "_score": 1.1546944,
                  "_source": {
                    "my_text": "blue racoon",
                    "my_vector": [1, 1, 1]
                  }
                }
              ]
            }
          },
          "nested_knn": {
            "hits": {
              "total": {
                "value": 3,
                "relation": "eq"
              },
              "max_score": 0.67567575,
              "hits": [
                {
                  "_index": "my-knn-index-1",
                  "_id": "1",
                  "_nested": {
                    "field": "nested_field",
                    "offset": 0
                  },
                  "_score": 0.67567575,
                  "_source": {
                    "my_text": "blue racoon",
                    "my_vector": [1, 1, 1]
                  }
                },
                {
                  "_index": "my-knn-index-1",
                  "_id": "1",
                  "_nested": {
                    "field": "nested_field",
                    "offset": 1
                  },
                  "_score": 0.48076925,
                  "_source": {
                    "my_text": "yellow racoon",
                    "my_vector": [2, 2, 2]
                  }
                },
                {
                  "_index": "my-knn-index-1",
                  "_id": "1",
                  "_nested": {
                    "field": "nested_field",
                    "offset": 2
                  },
                  "_score": 0.11520737,
                  "_source": {
                    "my_text": "white racoon",
                    "my_vector": [3, 3, 3]
                  }
                }
              ]
            }
          }
        }
      },
      {
        "_index": "my-knn-index-1",
        "_id": "4",
        "_score": 0.2360356,
        "_source": {
          "nested_field": [
            {
              "my_vector": [1000, 1000, 1000],
              "my_text": "silver stray cat"
            },
            {
              "my_vector": [2000, 2000, 2000],
              "my_text": "maroon stray cat"
            },
            {
              "my_vector": [3000, 3000, 3000],
              "my_text": "black stray cat"
            }
          ],
          "metadata": {
            "label": "stray cat",
            "version": 20
          }
        },
        "matched_queries": {
          "match.metadata.label": 0.33857906,
          "match.metadata.label2": 0.5361359,
          "nested_knn": 3.3426852e-7
        },
        "inner_hits": {
          "nested_match": {
            "hits": {
              "total": {
                "value": 0,
                "relation": "eq"
              },
              "max_score": null,
              "hits": []
            }
          },
          "nested_knn": {
            "hits": {
              "total": {
                "value": 3,
                "relation": "eq"
              },
              "max_score": 3.3426852e-7,
              "hits": [
                {
                  "_index": "my-knn-index-1",
                  "_id": "4",
                  "_nested": {
                    "field": "nested_field",
                    "offset": 0
                  },
                  "_score": 3.3426852e-7,
                  "_source": {
                    "my_text": "silver stray cat",
                    "my_vector": [1000, 1000, 1000]
                  }
                },
                {
                  "_index": "my-knn-index-1",
                  "_id": "4",
                  "_nested": {
                    "field": "nested_field",
                    "offset": 1
                  },
                  "_score": 8.3450125e-8,
                  "_source": {
                    "my_text": "maroon stray cat",
                    "my_vector": [2000, 2000, 2000]
                  }
                },
                {
                  "_index": "my-knn-index-1",
                  "_id": "4",
                  "_nested": {
                    "field": "nested_field",
                    "offset": 2
                  },
                  "_score": 3.7071626e-8,
                  "_source": {
                    "my_text": "black stray cat",
                    "my_vector": [3000, 3000, 3000]
                  }
                }
              ]
            }
          }
        }
      },
      {
        "_index": "my-knn-index-1",
        "_id": "2",
        "_score": 0.0006666667,
        "_source": {
          "nested_field": [
            {
              "my_vector": [10, 10, 10],
              "my_text": "red cat"
            },
            {
              "my_vector": [20, 20, 20],
              "my_text": "green cat"
            },
            {
              "my_vector": [30, 30, 30],
              "my_text": "black cat"
            }
          ],
          "metadata": {
            "label": "cat",
            "version": 15
          }
        },
        "matched_queries": {
          "match.metadata.label": 0.45060888,
          "nested_knn": 0.0044867187
        },
        "inner_hits": {
          "nested_match": {
            "hits": {
              "total": {
                "value": 0,
                "relation": "eq"
              },
              "max_score": null,
              "hits": []
            }
          },
          "nested_knn": {
            "hits": {
              "total": {
                "value": 3,
                "relation": "eq"
              },
              "max_score": 0.0044867187,
              "hits": [
                {
                  "_index": "my-knn-index-1",
                  "_id": "2",
                  "_nested": {
                    "field": "nested_field",
                    "offset": 0
                  },
                  "_score": 0.0044867187,
                  "_source": {
                    "my_text": "red cat",
                    "my_vector": [10, 10, 10]
                  }
                },
                {
                  "_index": "my-knn-index-1",
                  "_id": "2",
                  "_nested": {
                    "field": "nested_field",
                    "offset": 1
                  },
                  "_score": 0.0009625751,
                  "_source": {
                    "my_text": "green cat",
                    "my_vector": [20, 20, 20]
                  }
                },
                {
                  "_index": "my-knn-index-1",
                  "_id": "2",
                  "_nested": {
                    "field": "nested_field",
                    "offset": 2
                  },
                  "_score": 0.00040735188,
                  "_source": {
                    "my_text": "black cat",
                    "my_vector": [30, 30, 30]
                  }
                }
              ]
            }
          }
        }
      },
      {
        "_index": "my-knn-index-1",
        "_id": "5",
        "_score": 0.00033333336,
        "_source": {
          "nested_field": [
            {
              "my_vector": [10000, 10000, 10000],
              "my_text": "golden racoon dog"
            },
            {
              "my_vector": [20000, 20000, 20000],
              "my_text": "red racoon dog"
            },
            {
              "my_vector": [30000, 30000, 30000],
              "my_text": "black racoon dog"
            }
          ],
          "metadata": {
            "label": "racoon dog",
            "version": 9
          }
        },
        "matched_queries": {
          "nested_knn": 3.3342673e-9
        },
        "inner_hits": {
          "nested_match": {
            "hits": {
              "total": {
                "value": 0,
                "relation": "eq"
              },
              "max_score": null,
              "hits": []
            }
          },
          "nested_knn": {
            "hits": {
              "total": {
                "value": 3,
                "relation": "eq"
              },
              "max_score": 3.3342673e-9,
              "hits": [
                {
                  "_index": "my-knn-index-1",
                  "_id": "5",
                  "_nested": {
                    "field": "nested_field",
                    "offset": 0
                  },
                  "_score": 3.3342673e-9,
                  "_source": {
                    "my_text": "golden racoon dog",
                    "my_vector": [10000, 10000, 10000]
                  }
                },
                {
                  "_index": "my-knn-index-1",
                  "_id": "5",
                  "_nested": {
                    "field": "nested_field",
                    "offset": 1
                  },
                  "_score": 8.334501e-10,
                  "_source": {
                    "my_text": "red racoon dog",
                    "my_vector": [20000, 20000, 20000]
                  }
                },
                {
                  "_index": "my-knn-index-1",
                  "_id": "5",
                  "_nested": {
                    "field": "nested_field",
                    "offset": 2
                  },
                  "_score": 3.7040496e-10,
                  "_source": {
                    "my_text": "black racoon dog",
                    "my_vector": [30000, 30000, 30000]
                  }
                }
              ]
            }
          }
        }
      },
      {
        "_index": "my-knn-index-1",
        "_id": "3",
        "_score": 0.00033333336,
        "_source": {
          "nested_field": [
            {
              "my_vector": [100, 100, 100],
              "my_text": "brown lion"
            },
            {
              "my_vector": [200, 200, 200],
              "my_text": "purple lion"
            },
            {
              "my_vector": [300, 300, 300],
              "my_text": "gray lion"
            }
          ],
          "metadata": {
            "label": "lion",
            "version": 1
          }
        },
        "matched_queries": {
          "nested_knn": 0.000034285466
        },
        "inner_hits": {
          "nested_match": {
            "hits": {
              "total": {
                "value": 0,
                "relation": "eq"
              },
              "max_score": null,
              "hits": []
            }
          },
          "nested_knn": {
            "hits": {
              "total": {
                "value": 3,
                "relation": "eq"
              },
              "max_score": 0.000034285466,
              "hits": [
                {
                  "_index": "my-knn-index-1",
                  "_id": "3",
                  "_nested": {
                    "field": "nested_field",
                    "offset": 0
                  },
                  "_score": 0.000034285466,
                  "_source": {
                    "my_text": "brown lion",
                    "my_vector": [100, 100, 100]
                  }
                },
                {
                  "_index": "my-knn-index-1",
                  "_id": "3",
                  "_nested": {
                    "field": "nested_field",
                    "offset": 1
                  },
                  "_score": 0.000008451165,
                  "_source": {
                    "my_text": "purple lion",
                    "my_vector": [200, 200, 200]
                  }
                },
                {
                  "_index": "my-knn-index-1",
                  "_id": "3",
                  "_nested": {
                    "field": "nested_field",
                    "offset": 2
                  },
                  "_score": 0.0000037385012,
                  "_source": {
                    "my_text": "gray lion",
                    "my_vector": [300, 300, 300]
                  }
                }
              ]
            }
          }
        }
      }
    ]
  }
}
```

:::

## まとめと補足

本記事では OpenSearch のハイブリッドクエリやネストクエリにおける個別スコアの取得方法について解説しました。

### ポイントまとめ

| 機能                     | 用途                                | パラメータ                                   |
| ------------------------ | ----------------------------------- | -------------------------------------------- |
| Named Query              | 各クエリの個別スコア取得            | `_name` + `include_named_queries_score=true` |
| inner_hits               | nested ドキュメントごとのスコア取得 | `"inner_hits": {}`                           |
| hybrid_score_explanation | hybrid query の詳細な explain       | response_processors に追加                   |

### explain との使い分け

- **開発・デバッグ時**: `explain=true` で詳細なスコア計算過程を確認
- **本番環境でのモニタリング**: `include_named_queries_score=true` で軽量に個別スコアを取得

より詳細なスコア計算過程が必要な場合は、explain も合わせて利用していきましょう。

なお、hybrid query の explain を取得する場合は、別途 `hybrid_score_explanation` プロセッサが必要となります。

```json
GET my-knn-index-1/_search?include_named_queries_score=true&explain=true&phase_took
{
  "query": {
    "hybrid": {
      "queries": [
       {
          "nested": {
            "path": "nested_field",
            "query": {
              "knn": {
                "nested_field.my_vector": {
                  "vector": [1.4,1.4,1.4],
                  "k": 5,
                  "expand_nested_docs": true
                }
              }
            },
            "inner_hits": {
              "name": "nested_knn"
            },
            "score_mode": "max",
            "_name": "nested_knn"
          }
        },
        {
          "nested": {
            "path": "nested_field",
            "query": {
              "match": {
                "nested_field.my_text": "blue"
              }
            },
            "inner_hits": {
              "name": "nested_match"
            },
            "score_mode": "max",
            "_name": "nested_match"
          }
        }
      ]
    }
  },
  "search_pipeline" : {
    "phase_results_processors": [
      {
        "normalization-processor": {
          "normalization": {
            "technique": "z_score"
          }
        }
      }
    ],
    "response_processors": [
      {
          "hybrid_score_explanation": {}
      }
    ]
  }
}
```

:::details explain 実行結果(抜粋)

```json
"_explanation": {
  "value": 1.4717745,
  "description": "arithmetic_mean combination of:",
  "details": [
    {
      "value": 1.7888174,
      "description": "z_score normalization of:",
      "details": [
        {
          "value": 1.1546944379806519,
          "description": "combined score of:",
          "details": [
            {
              "value": 0.67567575,
              "description": "Score based on 3 child docs in range from 0 to 2, using score mode Max",
              "details": [
                {
                  "value": 0.67567575,
                  "description": "sum of:",
                  "details": [
                    {
                      "value": 0.67567575,
                      "description": "the type of knn search executed was Disk-based and the first pass k was 100 with vector dimension of 3, over sampling factor of 5.0, shard level rescoring enabled",
                      "details": [
                        {
                          "value": 0.67567575,
                          "description": "the type of knn search executed at leaf was Approximate-NN with vectorDataType = FLOAT, spaceType = l2",
                          "details": []
                        }
                      ]
                    },
                    {
                      "value": 0,
                      "description": "match on required clause, product of:",
                      "details": [
                        {
                          "value": 0,
                          "description": "# clause",
                          "details": []
                        },
                        {
                          "value": 1,
                          "description": "_nested_path:nested_field",
                          "details": []
                        }
                      ]
                    }
                  ]
                }
              ]
            },
            {
              "value": 1.1546944,
              "description": "Score based on 1 child docs in range from 0 to 2, using score mode Max",
              "details": [
                {
                  "value": 1.1546944,
                  "description": "weight(nested_field.my_text:blue in 0) [PerFieldSimilarity], result of:",
                  "details": [
                    {
                      "value": 1.1546944,
                      "description": "score(freq=1.0), computed as boost * idf * tf from:",
                      "details": [
                        {
                          "value": 2.3671236,
                          "description": "idf, computed as log(1 + (N - n + 0.5) / (n + 0.5)) from:",
                          "details": [
                            {
                              "value": 1,
                              "description": "n, number of documents containing term",
                              "details": []
                            },
                            {
                              "value": 15,
                              "description": "N, total number of documents with field",
                              "details": []
                            }
                          ]
                        },
                        {
                          "value": 0.4878049,
                          "description": "tf, computed as freq / (freq + k1 * (1 - b + b * dl / avgdl)) from:",
                          "details": [
                            {
                              "value": 1,
                              "description": "freq, occurrences of term within document",
                              "details": []
                            },
                            {
                              "value": 1.2,
                              "description": "k1, term saturation parameter",
                              "details": []
                            },
                            {
                              "value": 0.75,
                              "description": "b, length normalization parameter",
                              "details": []
                            },
                            {
                              "value": 2,
                              "description": "dl, length of field",
                              "details": []
                            },
                            {
                              "value": 2.4,
                              "description": "avgdl, average length of field",
                              "details": []
                            }
                          ]
                        }
                      ]
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
},
```

:::

## 参考リンク

https://docs.opensearch.org/latest/api-reference/search-apis/search/

https://docs.opensearch.org/latest/search-plugins/searching-data/inner-hits/

https://docs.opensearch.org/latest/vector-search/ai-search/hybrid-search/inner-hits/
