---
publication_name: "opensearch"
title: "OpenSearch の複雑なクエリにおいて、各クエリごとの個別スコアを取得する方法"
emoji: "🔍"
type: "tech"
topics: ["opensearch"]
published: true
---

## はじめに

OpenSearch で複数のクエリを組み合わせた複合クエリ（bool クエリや hybrid クエリ）を実行する際、最終的なスコアだけでなく「どのクエリがどれだけ貢献したか」を知りたいケースがあります。

個別に確認したいクエリとしては、ハイブリッド検索における正規化前のキーワードとベクトルそれぞれの検索スコア、bool クエリにおける各検索条件ごとのスコア、nested query におけるネストされた各ドキュメントごとのスコアなどが挙げられます。

こうした個別のスコアを確認することで、チューニングすべきクエリが見えてきます。OpenSearch にはスコアの詳細な計算過程を検索結果と合わせて返却する explain オプションが存在しますが、explain を有効化するとレイテンシに影響するため、本番での常用は望ましくありません。

本記事では、explain オプションを使用せず、個々のクエリやネストされたドキュメントごとのスコアを取得する方法について解説します。

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
PUT bulk?refresh=true
{ "index": { "index": "my-knn-index-1", "_id": "1" } }
{"nested_field":[{"my_vector":[1,1,1], "my_text": "blue racoon"},{"my_vector":[2,2,2], "my_text": "yellow racoon"},{"my_
vector":[3,3,3], "my_text": "whie racoon"}], "metadata": {"label": "racoon", "version": 2}}
{ "index": { "_index": "my-knn-index-1", "_id": "2" } }
{"nested_field":[{"my_vector":[10,10,10], "my_text": "red cat"},{"my_vector":[20,20,20], "my_text": "green cat"},{"my_
vector":[30,30,30], "my_text": "black cat"}],"metadata": {"label": "cat", "version": 15}}
{ "index": { "_index": "my-knn-index-1", "_id": "3" } }
{"nested_field":[{"my_vector":[100,100,100], "my_text": "brown lion"},{"my_vector":[200,200,200], "my_text": "purple
lion"},{"my_vector":[300,300,300], "my_text": "gray lion"}],"metadata": {"label": "lion", "version": 1}}
{ "index": { "_index": "my-knn-index-1", "_id": "4" } }
{"nested_field":[{"my_vector":[1000,1000,1000], "my_text": "silver stray cat"},{"my_vector":[2000,2000,2000], "my_text":
"maroon stray cat"},{"my_vector":[3000,3000,3000], "my_text": "black stray cat"}], "metadata": {"label": "stray cat",
"version": 20}}
{ "index": { "_index": "my-knn-index-1", "_id": "5" } }
{"nested_field":[{"my_vector":[10000,10000,10000], "my_text": "golden racoon dog"},{"my_vector":[20000,20000,20000], "my
_text": "red racoon dog"},{"my_vector":[30000,30000,30000], "my_text": "black racoon dog"}],"metadata": {"label":
"racoon dog", "version": 9}}
```

---

## bool クエリでの個別スコア取得

bool クエリの各クエリ `_name` を付与し、`include_named_queries_score=true` で検索します。

このパラメーターは Named Query と呼ばれるものです。検索結果でどのクエリにマッチしたかを `matched_queries` フィールドで確認することができます。

`include_named_queries_score=true` パラメータを Search API に追加することで、**各 Named Query の個別スコア**を取得可能です。

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

| ドキュメント | 最終スコア | cat クエリ | stray クエリ |
|-------------|-----------|-----------|-------------|
| _id: 4 (stray cat) | 0.874715 | 0.338 | 0.536 |
| _id: 2 (cat) | 0.450 | 0.450 | - |

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

:::details 実行結果（抜粋）

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
                    "my_vector": [
                      1,
                      1,
                      1
                    ]
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
                    "my_vector": [
                      2,
                      2,
                      2
                    ]
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
                    "my_text": "whie racoon",
                    "my_vector": [
                      3,
                      3,
                      3
                    ]
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
              "my_vector": [
                1,
                1,
                1
              ],
              "my_text": "blue racoon"
            },
            {
              "my_vector": [
                2,
                2,
                2
              ],
              "my_text": "yellow racoon"
            },
            {
              "my_vector": [
                3,
                3,
                3
              ],
              "my_text": "whie racoon"
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
                    "my_vector": [
                      1,
                      1,
                      1
                    ]
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
                    "my_vector": [
                      1,
                      1,
                      1
                    ]
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
                    "my_vector": [
                      2,
                      2,
                      2
                    ]
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
                    "my_text": "whie racoon",
                    "my_vector": [
                      3,
                      3,
                      3
                    ]
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
              "my_vector": [
                1000,
                1000,
                1000
              ],
              "my_text": "silver stray cat"
            },
            {
              "my_vector": [
                2000,
                2000,
                2000
              ],
              "my_text": "maroon stray cat"
            },
            {
              "my_vector": [
                3000,
                3000,
                3000
              ],
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
                    "my_vector": [
                      1000,
                      1000,
                      1000
                    ]
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
                    "my_vector": [
                      2000,
                      2000,
                      2000
                    ]
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
                    "my_vector": [
                      3000,
                      3000,
                      3000
                    ]
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
              "my_vector": [
                10,
                10,
                10
              ],
              "my_text": "red cat"
            },
            {
              "my_vector": [
                20,
                20,
                20
              ],
              "my_text": "green cat"
            },
            {
              "my_vector": [
                30,
                30,
                30
              ],
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
                    "my_vector": [
                      10,
                      10,
                      10
                    ]
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
                    "my_vector": [
                      20,
                      20,
                      20
                    ]
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
                    "my_vector": [
                      30,
                      30,
                      30
                    ]
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
              "my_vector": [
                10000,
                10000,
                10000
              ],
              "my_text": "golden racoon dog"
            },
            {
              "my_vector": [
                20000,
                20000,
                20000
              ],
              "my_text": "red racoon dog"
            },
            {
              "my_vector": [
                30000,
                30000,
                30000
              ],
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
                    "my_vector": [
                      10000,
                      10000,
                      10000
                    ]
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
                    "my_vector": [
                      20000,
                      20000,
                      20000
                    ]
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
                    "my_vector": [
                      30000,
                      30000,
                      30000
                    ]
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
              "my_vector": [
                100,
                100,
                100
              ],
              "my_text": "brown lion"
            },
            {
              "my_vector": [
                200,
                200,
                200
              ],
              "my_text": "purple lion"
            },
            {
              "my_vector": [
                300,
                300,
                300
              ],
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
                    "my_vector": [
                      100,
                      100,
                      100
                    ]
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
                    "my_vector": [
                      200,
                      200,
                      200
                    ]
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
                    "my_vector": [
                      300,
                      300,
                      300
                    ]
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

## まとめ
本記事では OpenSearch のハイブリッドクエリやネストクエリにおける個別スコアの取得方法について解説しました。より詳細なスコア計算過程が必要な場合は、explain も合わせて利用していきましょう。


## 参考リンク

https://docs.opensearch.org/latest/api-reference/search-apis/search/

https://docs.opensearch.org/latest/search-plugins/searching-data/inner-hits/

https://docs.opensearch.org/latest/vector-search/ai-search/hybrid-search/inner-hits/