---
title: "[翻訳] OpenSearch 3.0 の Live Queries によるリアルタイムクエリモニタリング"
emoji: "🔍"
type: "tech"
topics: ["opensearch", "monitoring", "performance", "search", "observability"]
published: true
publication_name: "opensearch"
published_at: 2025-06-05
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/real-time-query-monitoring-with-live-queries-in-opensearch-3-0/

OpenSearch Query Insights は、検索クエリのパフォーマンスを理解するための重要なツールとなっており、クエリの実行方法やクラスターリソースの消費状況を可視化します。パフォーマンスのボトルネックを特定し、検索操作を最適化するための取り組みの一環として、OpenSearch 3.0 で強力な新機能である **Live Queries** を導入しました。

Top N クエリの履歴分析はトレンドや過去の問題を理解するのに役立ちますが、「今まさに何が起きているか」をリアルタイムで確認したい場面があります。特定のクエリに時間がかかりすぎていないか、リソース消費の急増が特定の検索アクティビティに関連しているか、といった疑問に Live Queries を使用することで即座に答えを得られます。

## Live Queries とは

[OpenSearch 3.0 で導入された](https://opensearch.org/blog/unveiling-opensearch-3-0/) Live Queries は、クラスターの検索ワークロードの現在の状態を調査できる機能です。Live Queries API は、クラスター全体または特定のノードで現在実行中の検索クエリのリストを取得します。この機能はクエリの動作をリアルタイムで可視化し、以下のようなタスクに特に役立ちます。

* **問題のあるクエリの特定**: 予想以上に長時間実行されているクエリを素早く発見できます。
* **リソースを大量消費するクエリのデバッグ**: 今まさに大量の CPU やメモリを消費している検索を特定できます。
* **クラスター負荷の即時把握**: クラスターに影響を与えている現在の検索アクティビティのスナップショットを取得できます。

API は各 Live Query について、クエリソース、検索タイプ、対象インデックス、実行中のノード ID、開始時刻、現在のレイテンシー、およびその時点までのリソース使用量 (コーディネーターノード上) などの主要な詳細情報を返します。

## Live Queries の仕組み

以下の REST API エンドポイントを使用して Live Query 情報にアクセスできます。

```
GET /_insights/live_queries
```

デフォルトでは、API は現在実行中の検索クエリのリストを `latency` の降順でソートして返します。

### 返される主要な情報

各 Live Query について、以下の詳細なデータが取得できます。

* `timestamp`: クエリタスクが開始された時刻 (エポックからのミリ秒)。
* `id`: 一意の検索タスク ID。
* `description`: 対象インデックス、検索タイプ、クエリソース自体 (`verbose` が true の場合) を含むクエリの詳細。
* `node_id`: クエリタスクが実行されているコーディネーターノードの ID。
* `measurements`: これまでに収集されたパフォーマンスメトリクスを含むオブジェクト。
  + `latency`: 現在の実行時間 (ナノ秒)。
  + `cpu`: これまでに消費された CPU 時間 (ナノ秒)。
  + `memory`: これまでに使用されたヒープメモリ量 (バイト)。

## Live Queries の使い方

Live Queries API の操作は簡単です。API は以下の操作をサポートしています。

### 基本的なリクエスト

レイテンシーでソートされた現在実行中のクエリのリストを取得するには、以下のリクエストを送信します。

```
GET /_insights/live_queries
```

### クエリパラメータによるカスタマイズ

以下のオプションパラメータを使用して、Live Queries API のレスポンスをカスタマイズできます。

* `verbose`: クエリソースなどの詳細なクエリ情報を含めます。
* `nodeId`: カンマ区切りのノード ID リストで結果をフィルタリングします。
* `sort`: レイテンシー、CPU 使用量、メモリ使用量などの特定のメトリクスで結果をソートします。
* `size`: 返されるクエリレコードの数を制限します。

### 例: CPU を大量消費している Live Queries の検索

現在最も CPU を消費している上位 5 つのクエリを見つけるには、以下のクエリパラメータを指定します。

```
GET /_insights/live_queries?verbose=false&sort=cpu&size=5
```

### レスポンスの理解

レスポンスの例を以下に示します ([ドキュメントの例](https://docs.opensearch.org/docs/latest/observing-your-data/query-insights/live-queries/#example-response) から抜粋、簡潔にするため 1 つのクエリのみ表示)。

```json
{
  "live_queries" : [
    {
      "timestamp" : 1745359226777,
      "id" : "troGHNGUShqDj3wK_K5ZIw:512",
      "description" : "indices[my-index-*], search_type[QUERY_THEN_FETCH], source[{\"size\":20,\"query\":{\"term\":{\"user.id\":{\"value\":\"userId\",\"boost\":1.0}}}}]",
      "node_id" : "troGHNGUShqDj3wK_K5ZIw",
      "measurements" : {
        "latency" : {
          "number" : 13959364458,
          "count" : 1,
          "aggregationType" : "NONE"
        },
        "memory" : {
          "number" : 3104,
          "count" : 1,
          "aggregationType" : "NONE"
        },
        "cpu" : {
          "number" : 405000,
          "count" : 1,
          "aggregationType" : "NONE"
        }
      }
    }
    // ... 他の Live Queries
  ]
}
```

このレスポンスから以下の情報が得られます。

* クエリはタイムスタンプ `1745359226777` に開始されました。
* ノード `troGHNGUShqDj3wK_K5ZIw` で実行されています。
* これまでに 13.9 秒以上実行されています (`latency.number` はナノ秒単位)。
* CPU 時間を `405000` ナノ秒、メモリを `3104` バイト消費しています。
* `description` (リクエストで `verbose=true` を指定したため表示) は、クエリが `my-index-*` を対象とし、実際のクエリ構造を含んでいることを示しています。

## Live Queries が重要な理由

Live Queries をモニタリングする機能には、以下のような大きなメリットがあります。

* **即時のトラブルシューティング**: ユーザーから遅延の報告があったり、ダッシュボードが高負荷を示している場合、Live Queries を使用することでアクティブな検索を即座に確認できます。これにより、特定のクエリやクエリパターンが原因かどうかを素早く特定できます。
* **プロアクティブなパフォーマンス管理**: 特にピーク時に Live Queries を定期的にチェックすることで、問題を引き起こす可能性のあるクエリを広範な影響が出る前に発見できます。
* **リソース消費の把握**: どの Live Queries が最も CPU やメモリを消費しているかを理解することで、リアルタイムのリソース評価に役立ち、必要に応じて暴走しているクエリをキャンセルするなどの即時対応の判断材料となります (キャンセル自体は別の OpenSearch Task Management API の機能です)。

## まとめ

OpenSearch 3.0 の新しい Live Queries 機能は、クラスターの現在の検索ワークロードをリアルタイムで可視化することで、クエリパフォーマンスモニタリングに重要な次元を追加します。これにより、パフォーマンスの問題をより迅速に診断・対処でき、ユーザーにとってよりスムーズで効率的な検索体験を実現できます。

Top N クエリ分析や履歴データのエクスポートなど、Query Insights の既存機能と組み合わせることで、Live Queries は OpenSearch 環境を管理・最適化するための包括的なツールキットを提供します。

Live Queries を使い始めるには、OpenSearch 3.0 にアップグレードしてください。詳細については、[Live queries](https://opensearch.org/docs/latest/observing-your-data/query-insights/live-queries/) および [Query Insights ドキュメント](https://opensearch.org/docs/latest/observing-your-data/query-insights/index/) を参照してください。

この新機能をぜひお試しいただき、[OpenSearch フォーラム](https://forum.opensearch.org/) でご意見やフィードバックをお聞かせください。
