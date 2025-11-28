---
title: "[翻訳] 検索レイテンシモニタリングの活用"
emoji: "⏱️"
type: "tech"
topics: ["opensearch", "monitoring", "search", "performance"]
published: true
publication_name: "opensearch"
published_at: 2024-10-01
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/using-search-latency-monitoring/

検索ソリューションにおいて、レスポンスの速さは非常に重要です。検索リクエストとレスポンス間の通信遅延は、ユーザーにとって大きな問題となる可能性があります。そのため、多くの管理者は検索レイテンシ (検索リクエストが OpenSearch クラスターに送信されてからレスポンスが返されるまでの時間) を監視しています。

しかし、OpenSearch 2.11 より前のバージョンでは、検索レイテンシを監視する機能は限定的でした。[Nodes Stats API](https://opensearch.org/docs/latest/api-reference/nodes-apis/nodes-stats/) や [shard slow logs](https://opensearch.org/docs/latest/install-and-configure/configuring-opensearch/logs/#shard-slow-logs) などのツールは、シャードレベルの操作に基づくレイテンシ測定を提供しますが、コーディネーターノードレベルでの可視性は提供していませんでした。検索リクエストは複数のシャードに同時にヒットすることが多いため、単一のシャード検索フェーズで費やされた時間を測定しても、包括的なレイテンシ情報は得られません。

幸いなことに、OpenSearch 2.11 以降では、コーディネーターノードレベルでの検索レイテンシモニタリングが提供されています。本記事では、コーディネーターノードレベルの統計情報を監視するのに役立つ複数のツール (Node Stats API、`phase_took` パラメータ、検索リクエストスローログ) について説明します。

## コーディネーターノードと検索フェーズ

OpenSearch において、コーディネーターノードはクライアントとデータノード間の仲介役として、検索実行において重要な役割を果たします。検索リクエストを受信すると、コーディネーターノードは関連するシャードを含むデータノードにリクエストを分散します。検索の種類に応じて、リクエストはコーディネーターノードによって開始される一連の検索フェーズ (検索操作の種類) を経ます。これらのフェーズには以下が含まれます。

- `can_match`: クエリの書き換えに基づいて検索シャードを事前フィルタリングします。
- `dfs_pre_query`: スコアリングを 100% 正確にするために、各シャードから追加情報を収集します。
- `dfs_query`: 検索リクエスト内のすべての検索語に対して、事前に収集された分散頻度を使用して分散検索を実行します。
- `query`: クエリを実行し、各シャードからドキュメント ID、スコア、ソート基準などのマッチするドキュメントに関する情報を取得します。
- `fetch`: `query` フェーズですべてのマッチを集約した後、実際の上位マッチドキュメントを取得します。上位マッチが返されます。
- `expand`: `expand` が有効な場合、内部ヒットのフィールドを折りたたみます。

以下の図は、リクエストからレスポンスまでの検索フェーズワークフローを示しています。

![検索フェーズワークフロー](/images/opensearch-search-latency-monitoring/search_phase.png)

## フェーズモニタリングの新機能

OpenSearch 2.11 より前は、OpenSearch は `query` と `fetch` のシャード検索フェーズのみを監視しており、検索レイテンシの可視性の範囲が大幅に制限されていました。現在では、既存の API やツール内の以下の機能を活用して、コーディネーターノードレベルですべての検索フェーズのメトリクスを監視できます。

### Nodes Stats API

OpenSearch 2.11 で導入された [Nodes Stats API](https://opensearch.org/docs/latest/api-reference/nodes-apis/nodes-stats/) は、以下のコーディネーターノードレベルのメトリクスを測定できます。

| メトリクス | 説明 |
| --- | --- |
| `time_in_millis` | すべてのコーディネーター検索操作に費やされた累積時間 (ミリ秒) |
| `current` | 現在実行中のコーディネーター検索操作の累積数 |
| `total` | 完了したコーディネーター検索操作の累積数 |

以下の Nodes Stats API レスポンスは、各検索フェーズのこれらのメトリクスを示しています。

```json
GET /_nodes/stats/indices/search
{
  "_nodes": {
    "total": 6,
    "successful": 6,
    "failed": 0
  },
  "cluster_name": "113389760531:os213-2",
  "nodes": {
    "PYR526iKRq6wuuxNZJa7Zg": {
      "timestamp": 1718916559344,
      "name": "ca9a0681a452f388df882cdffc18fbfb",
      "roles": [
        "ingest",
        "master",
        "remote_cluster_client"
      ],
      "indices": {
        "search": {
          "request":  {
            "dfs_pre_query":  {
              "time_in_millis": 47,
              "current": 0,
              "total": 41
            },
            "query":  {
              "time_in_millis":  5429,
              "current":  13,
              "total":  238
            },
            "fetch":  {
              "time_in_millis":  1230,
              "current":  2,
              "total":  238
            },
            "dfs_query":  {
              "time_in_millis":  0,
              "current":  0,
              "total":  0
            },
            "expand":  {
              "time_in_millis":  304,
              "current": 1,
              "total": 238
            },
            "can_match":  {
              "time_in_millis":  0,
              "current":  0,
              "total":  0
            }
          }
        }
      }
    }
  }
}
```

### 検索フェーズ所要時間

OpenSearch 2.12 で導入された `phase_took` パラメータは、以下の例に示すように、検索レスポンスで直接フェーズの所要時間を返します。

```json
GET /my-index-000001/_search?phase_took
{
  "took" : 105,
  "phase_took" : {
    "dfs_pre_query" : 0,
    "query" : 69,
    "fetch" : 22,
    "dfs_query" : 0,
    "expand" : 4,
    "can_match" : 0
  },
  "timed_out" : false,
  "_shards" : {
    "total" : 5,
    "successful" : 5,
    "skipped" : 0,
    "failed" : 0
  },
  "hits" : {
    "total" : {
      "value" : 0,
      "relation" : "eq"
    },
    "max_score" : null,
    "hits" : [ ]
  }
}
```

### 検索リクエストスローログ

OpenSearch 2.12 で導入された検索リクエストスローログは、ユーザー定義のレイテンシしきい値を超える検索リクエストに関する統計情報を提供します。以下は `opensearch_index_search_slowlog.log` ファイルの例です。

```
[2023-10-30T15:47:42,630][TRACE][c.s.r.slowlog] [runTask-0] 
took[80.8ms], 
took_millis[80], 
phase_took_millis[{expand=0, query=39, fetch=22}], 
total_hits[4 hits], search_type[QUERY_THEN_FETCH], 
shards[{total: 10, successful: 10, skipped: 0, failed: 0}], 
source[{"query":{"match_all":{"boost":1.0}}}], 
id[]
```

スローログのしきい値の設定方法の詳細については、[Search request slow logs](https://opensearch.org/docs/latest/install-and-configure/configuring-opensearch/logs/#search-request-slow-logs) を参照してください。

## 検索レイテンシモニタリングの有効化

これらの機能を有効にするには、OpenSearch ドキュメントの [Search settings](https://opensearch.org/docs/latest/install-and-configure/configuring-opensearch/search-settings/) ページを参照するか、以下の API リクエスト例を使用してください。

:::message
検索リクエストスローログのしきい値はカスタマイズ可能です。これにより、特定の検索リクエストに対するしきい値の設定が簡素化されます。ログ作成を検索しきい値に合わせて設定できるためです。
:::

```json
PUT _cluster/settings
{
  "persistent" : {
    // コーディネーターノード統計
    "search.request_stats_enabled" : "true",
    // 検索フェーズ所要時間
    "search.phase_took_enabled" : "true",
    // 検索リクエストスローログとしきい値
    "cluster.search.request.slowlog.level" : "TRACE",
    "cluster.search.request.slowlog.threshold.warn": "10s",
    "cluster.search.request.slowlog.threshold.info": "5s",
    "cluster.search.request.slowlog.threshold.debug": "2s",
    "cluster.search.request.slowlog.threshold.trace": "10ms"
  }
}
```

## まとめ

これらの新機能は、クラスター内の検索レイテンシのエンドツーエンドの可視性を向上させるのに役立ちます。これらのツールを使用することで、リクエスト時間のスパイクをより適切にデバッグし、ボトルネックを特定し、ドメイン上で最も長時間実行されているクエリを分離できます。

OpenSearch のリリース以降の全体的なレイテンシ改善の詳細については、[An update on the OpenSearch Project's continued performance progress through version 2.11](https://opensearch.org/blog/opensearch-performance-improvements/) を参照してください。
