---
title: "[翻訳] Concurrent Segment Search でベクトル検索を高速化する"
emoji: "🚀"
type: "tech"
topics: ["opensearch", "vector", "search", "performance"]
published: true
publication_name: "opensearch"
published_at: 2024-08-27
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/boost-vector-search-with-css/

OpenSearch では、データはシャードに格納され、シャードはさらにセグメントに分割されます。検索クエリを実行すると、クエリに関係する各シャードのすべてのセグメントに対して順次実行されます。セグメント数が増加すると、この順次実行によって *クエリレイテンシー* (結果を取得するまでの時間) が増加する可能性があります。これは、クエリが次のセグメントに移る前に、各セグメントの実行完了を待つ必要があるためです。この遅延は、一部のセグメントの処理に他のセグメントより時間がかかる場合に特に顕著になります。

OpenSearch バージョン 2.12 で導入された *Concurrent Segment Search* は、シャード内の複数のセグメントに対してクエリを並列実行することで、この問題に対処します。利用可能なコンピューティングリソースを活用することで、この機能は特に多くのセグメントを持つ大規模なデータセットに対して、全体的なクエリレイテンシーを削減します。Concurrent Segment Search は、より一貫性のある予測可能なレイテンシーを提供するように設計されています。セグメントのパフォーマンスやセグメント数の変動がクエリ実行時間に与える影響を軽減することで、この一貫性を実現しています。

この記事では、ベクトル検索ワークロードに対する Concurrent Segment Search の影響を探ります。

## Concurrent Segment Search の有効化

デフォルトでは、OpenSearch で Concurrent Segment Search は無効になっています。実験では、以下の動的クラスター設定を使用して、クラスター内のすべてのインデックスに対して有効にしました。

```json
PUT _cluster/settings
{
   "persistent": {
      "search.concurrent_segment_search.enabled": true
   }
}
```

Concurrent Segment Search を実現するために、OpenSearch は各シャード内のセグメントを複数のスライスに分割し、各スライスは別々のスレッドで並列処理されます。スライス数は OpenSearch が提供できる並列度を決定します。Lucene のデフォルトのスライシングメカニズムを使用するか、最大スライス数を手動で設定できます。スライス数の更新に関する詳細な手順については、[Slicing mechanisms](https://opensearch.org/docs/latest/search-plugins/concurrent-segment-search/#slicing-mechanisms) を参照してください。

## パフォーマンス結果

OpenSearch Benchmark の [vector search workload](https://github.com/opensearch-project/opensearch-benchmark-workloads/tree/main/vectorsearch) を使用して、[OpenSearch 2.15](https://opensearch.org/versions/opensearch-2-15-0.html) クラスターでテストを実施しました。Cohere データセットを 2 つの異なる構成で使用し、Concurrent Segment Search を無効にした場合、デフォルト設定で有効にした場合、および異なる最大スライス数で有効にした場合のベクトル検索クエリのパフォーマンス改善を評価しました。

### クラスター構成

* データノード 3 台 (r5.4xlarge: 128 GB RAM、16 vCPU、250 GB ディスク容量)
* クラスターマネージャーノード 3 台 (r5.xlarge: 32 GB RAM、4 vCPU、50 GB ディスク容量)
* OpenSearch ワークロードクライアント 1 台 (c5.4xlarge: 32 GB RAM、16 vCPU)
* 検索クライアント 1 台および 4 台
* `index_searcher` スレッドプールサイズ: 32

#### インデックス設定

| `m` | `ef_construction` | `ef_search` | シャード数 | レプリカ数 | Space type |
| --- | --- | --- | --- | --- | --- |
| 16 | 100 | 100 | 6 | 1 | inner product |

#### 構成

| 次元数 | ベクトル数 | 検索クエリ数 | リフレッシュ間隔 |
| --- | --- | --- | --- |
| 768 | 10M | 10K | 1s (デフォルト) |

### サービス時間の比較

以下の実験を実施しました。

1. Concurrent Search 無効
2. Concurrent Search 有効:
   * 最大スライス数 = 0 (デフォルト)
   * 最大スライス数 = 2
   * 最大スライス数 = 4
   * 最大スライス数 = 8

### 結果の比較

簡潔にするため、単一の検索クライアントでの p90 メトリクスに焦点を当てます。このメトリクスは、長時間実行されるベクトル検索クエリのパフォーマンスを捉えています。

#### サービス時間の比較 (p90)

| k-NN エンジン | CS 無効 | CS 有効 (Lucene デフォルトスライス数) | 改善率 | CS 有効 (最大スライス数=2) | 改善率 | CS 有効 (最大スライス数=4) | 改善率 | CS 有効 (最大スライス数=8) | 改善率 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Lucene | 37 | 15 | 59.5% | 16 | 56.8% | 15.9 | 57% | 16 | 56.8% |
| NMSLIB | 35 | 14 | 60% | 23 | 34.3% | 15 | 57.1% | 12 | 65.7% |
| Faiss | 37 | 14 | 62.2% | 22 | 40.5% | 15 | 59.5% | 16 | 56.8% |

#### CPU 使用率の比較

| k-NN エンジン | CS 無効 | CS 有効 (Lucene デフォルトスライス数) | 追加 CPU 使用率 | CS 有効 (最大スライス数=2) | 追加 CPU 使用率 | CS 有効 (最大スライス数=4) | 追加 CPU 使用率 | CS 有効 (最大スライス数=8) | 追加 CPU 使用率 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Lucene | 11 | 47 | 36 | 41 | 30 | 49 | 38 | 43 | 32 |
| NMSLIB | 10 | 38 | 28 | 16 | 6 | 29 | 19 | 41 | 31 |
| Faiss | 10 | 34 | 24 | 19 | 9 | 30 | 20 | 44 | 34 |

パフォーマンスベンチマークが示すように、デフォルトのスライス数で Concurrent Segment Search を有効にすると、ベクトル検索のサービス時間が **60% 以上改善** され、必要な追加 CPU は **25〜35%** のみです。この CPU 使用率の増加は、Concurrent Segment Search がより多くの CPU スレッド (CPU コア数の 2 倍のスレッド数) で実行されるため、予想通りの結果です。

複数の同時検索クライアントを使用した場合も、同様のサービス時間の改善が観察されました。ただし、同時に実行されるアクティブな検索スレッド数の増加により、最大 CPU 使用率も予想通り 2 倍になりました。

## まとめ

実験結果から、デフォルトのスライス数で Concurrent Segment Search を有効にすると、CPU 使用率が高くなる代わりに、ベクトル検索クエリのパフォーマンスが向上することが明確に示されました。スライス数を増やすことで得られる追加の並列化が、追加の処理オーバーヘッドを上回るかどうかを判断するために、ワークロードをテストすることをお勧めします。

Concurrent Segment Search を実行する前に、より良いパフォーマンスを達成するために、セグメントを単一のセグメントに force-merge することをお勧めします。このアプローチの主な欠点は、セグメントが大きくなるにつれて force-merge に必要な時間が増加することです。そのため、ユースケースに応じてセグメント数を削減することをお勧めします。

ベクトル検索と Concurrent Segment Search を組み合わせることで、クエリパフォーマンスを向上させ、検索操作を最適化できます。Concurrent Segment Search を始めるには、[ドキュメント](https://opensearch.org/docs/latest/search-plugins/concurrent-segment-search/) を参照してください。
