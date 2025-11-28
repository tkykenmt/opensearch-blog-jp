---
title: "[翻訳] OpenSearch Query Insights の新機能: 高度なグルーピング、ダッシュボード、履歴分析"
emoji: "🔍"
type: "tech"
topics: ["opensearch", "monitoring", "observability", "performance", "dashboard"]
published: true
published_at: 2025-04-22
publication_name: "opensearch"
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/whats-new-in-opensearch-query-insights-advanced-grouping-dashboards-and-historical-analysis/

OpenSearch Query Insights は、検索クエリのパフォーマンスを可視化し、クエリの実行状況やクラスターリソースの使用状況を把握するための重要な機能です。[Query Insights](https://opensearch.org/blog/query-insights/) の導入以来、パフォーマンスのボトルネックを特定し、クエリを最適化するためのツールを提供することで、ユーザーの検索体験を向上させることを目指してきました。クエリを効果的に分析することは、高速で効率的な検索運用を維持するための鍵となります。

この基盤をもとに、皆様からのフィードバックを反映しながら Query Insights の開発を続けてきました。本記事では、高度なクエリグルーピングによる深い分析機能、専用ダッシュボードによる使いやすさの向上、エクスポートオプションを使用した履歴分析、Query Insights システムの運用監視の改善など、いくつかの新機能を紹介します。

## 類似クエリのグルーピングによる分析の改善

レイテンシ、CPU 使用率、メモリ使用量でランク付けされた Top N クエリリストを確認する際、構造的には類似しているものの、リテラルパラメータ値のみが異なるクエリが多数含まれていることに気づくかもしれません。このような繰り返しパターンがあると、注意が必要な他のユニークでリソース集約型のクエリを見つけにくくなります。

この問題に対処するため、Query Insights は**類似性によるクエリグルーピング**をサポートするようになりました。この機能により、検索語句やフィルターなどの特定の値の違いを無視し、クエリのコア構造に基づいてグルーピングできます。

**仕組み**: 有効にすると、Query Insights は受信クエリを分析してコア構造を抽出します。例えば、以下の 2 つのクエリは同じフィールドを対象としていますが、異なる値を使用しています。

```json
// Query 1
{ "query": { "term": { "user_id": "valueA" } } }

// Query 2
{ "query": { "term": { "user_id": "valueB" } } }
```

類似性グルーピングを有効にすると、両方のクエリは `query → term → user_id` という構造で定義される同じグループに配置されます。Query Insights は、平均レイテンシ、総実行回数、合計リソース使用量などのグループの集計メトリクスと、代表的なクエリ例を表示します。

**有効化の方法**: クラスター設定を更新することで類似性グルーピングを有効にできます。デフォルト値 (`none`) ではグルーピングは無効です。

```json
PUT _cluster/settings
{
  "persistent" : {
    "search.insights.top_queries.group_by" : "similarity"
  }
}
```

フィールド名や型が類似性構造に影響するかどうかを設定することで、グルーピングの動作を微調整することもできます。詳細については、[Top N クエリのグルーピング](https://opensearch.org/docs/latest/observing-your-data/query-insights/grouping-top-n-queries/)を参照してください。

**重要な理由**: この機能により、個々のクエリから共有クエリパターンへと焦点が移ります。影響の大きいクエリ構造をより効果的に見つけて改善でき、根本原因の分析とパフォーマンスチューニングが容易になります。

## ビジュアルダッシュボードでクエリインサイトを探索

Query Insights API はパフォーマンスデータへの直接アクセスを提供しますが、ビジュアルインターフェースを使用するとパターンの発見や設定の微調整が容易になります。そのため、**OpenSearch Dashboards に Query Insights を追加**しました。これは Dashboards インターフェースに組み込まれた専用の機能です。

このインターフェースには以下の主要機能が含まれています。

- **Top N クエリビュー**: レイテンシ、CPU 使用率、メモリなどのメトリクスでランク付けされた Top N クエリまたはクエリグループのソート・フィルタリング可能なリストを表示します。時間範囲、インデックス、検索タイプ、コーディネーターノード ID でフィルタリングできます。主要なパフォーマンスデータは、以下の画像のように明確なテーブルレイアウトで表示されます。

![Top N クエリの概要](/images/opensearch-query-insights-grouping-dashboards/top-queries-overview-scaled.png)

- **クエリ詳細ページ**: クエリ ID を選択すると詳細情報を表示できます。個々のクエリの場合、完全なクエリ本文、実行タイムスタンプ、CPU とメモリ使用量、フェーズレベルのレイテンシ、インデックス、ノード、シャードなどのメタデータが表示されます。グループ化されたクエリの場合、以下の画像のように、平均レイテンシや総カウントなどの集計メトリクスと代表的なクエリ例が表示されます。

![クエリ詳細](/images/opensearch-query-insights-grouping-dashboards/top-queries-details-scaled.png)

- **設定インターフェース**: API を使用する代わりに、ダッシュボードから直接設定を調整できます。特定のメトリクスの監視の有効化/無効化、監視ウィンドウ (`window_size`) の設定、追跡するクエリ数 (`top_n_size`) の制御、グルーピング戦略 (`group_by`) の選択、エクスポート設定の構成など、すべてシンプルでインタラクティブなコントロールで行えます。

![設定インターフェース](/images/opensearch-query-insights-grouping-dashboards/query-insights-dashboards-config-scaled.png)

**重要な理由**: OpenSearch Dashboards の Query Insights により、検索パフォーマンスの監視が容易になります。クエリパフォーマンスを監視する管理者でも、特定のクエリの問題を調査する開発者でも、データを素早く可視化し、個々のクエリを探索し、API を操作することなく設定を調整できます。セットアップ手順と使用方法のヒントについては、[Query Insights ダッシュボード](https://opensearch.org/docs/latest/observing-your-data/query-insights/query-insights-dashboard/)を参照してください。

## ローカルインデックスエクスポーターを使用した履歴トレンドの分析

リアルタイム監視はパフォーマンスの問題にリアルタイムで対処するのに役立ちます。しかし、長期的なトレンドを理解したり、過去のインシデントを調査したりするには、履歴データへのアクセスが必要です。**ローカルインデックスエクスポーター**がこれを実現します。

履歴データを永続化するように設定すると、Query Insights は Top N クエリレコード (個々のクエリまたはグループ化されたもの) をクラスター内の専用 OpenSearch インデックスに保存します。

**仕組み**: クラスター設定でエクスポータータイプを `local_index` に設定します。OpenSearch は `top_queries-YYYY.MM.dd-hashcode` のような標準化された命名形式を使用して、毎日新しいインデックスを作成します。`delete_after_days` 設定を使用してデータ保持を制御でき、定義された日数 (デフォルトは `7`) 後に古いインデックスを削除します。例えば、レイテンシデータを保存するようにローカルインデックスエクスポーターを設定するには、以下のリクエストを使用します。オプションで、保持期間をカスタム値 (この例では 30 日) に設定できます。

```json
PUT _cluster/settings
{
  "persistent" : {
    "search.insights.top_queries.exporter.type" : "local_index",
    "search.insights.top_queries.exporter.delete_after_days" : 30
  }
}
```

**重要な理由**: データをローカルに保存することで、同じ `/_insights/top_queries` API を通じて履歴 Top N データをクエリできます。`from` と `to` のタイムスタンプパラメータを追加するだけです。例えば、2024 年 11 月 5 日の午前 10 時から午後 12 時 (UTC) までのレイテンシ関連クエリを取得するには、以下のリクエストを実行します。

```
GET /_insights/top_queries?type=latency&from=2024-11-05T10:00:00.000Z&to=2024-11-05T12:00:00.000Z
```

これにより、時間の経過に伴うパフォーマンスの追跡、インシデント後のレビュー、スケーリングとキャパシティプランニングに関するデータ駆動型の意思決定が容易になります。詳細については、[Top N クエリデータのエクスポート](https://opensearch.org/docs/latest/observing-your-data/query-insights/top-n-queries/#exporting-top-n-query-data)を参照してください。

## プラグインの健全性とリソース使用量の監視

クエリ監視機能は Query Insights プラグインによって提供されます。Query Insights がデータを収集、集計、エクスポートする際、当然ながらクラスターリソースを使用します。内部の健全性を監視し、問題を早期に特定できるよう、Query Insights には専用の監視機能が含まれるようになりました。

1. **Health Stats API**: `GET /_insights/health_stats` エンドポイントを使用して、プラグインを実行している各ノードから運用メトリクスを取得します。これには以下が含まれます。
   - 内部スレッドプール (`query_insights_executor`) のステータスと設定
   - 受信クエリレコードをバッファリングするキューの現在のサイズ (`QueryRecordsQueueSize`)
   - クエリグルーピング中に使用される `FieldTypeCacheStats` などのキャッシュパフォーマンス統計
   - Top N クエリコレクターのリソース使用量

2. **OpenTelemetry エラーメトリクス**: クラスターで OpenTelemetry が有効になっている場合、Query Insights はプラグイン固有のエラーカウンターを報告します。これらのメトリクスは、以下のようなプラグイン内の運用障害を追跡します。
   - `LOCAL_INDEX_READER_PARSING_EXCEPTIONS`
   - `DATA_INGEST_EXCEPTIONS`
   - `LOCAL_INDEX_EXPORTER_BULK_FAILURES`
   - `QUERY_CATEGORIZE_EXCEPTIONS`

**重要な理由**: これらの監視ツールは、プラグインの動作とリソースへの影響を可視化します。インサイトデータの欠落、レポートの遅延に気づいた場合や、Query Insights がクラスター全体のパフォーマンスに影響を与えている可能性がある場合に特に役立ちます。

利用可能なすべてのメトリクスとフィールドについては、[Query Insights プラグインの健全性](https://opensearch.org/docs/latest/observing-your-data/query-insights/health/)を参照してください。

## まとめ: より統合されたクエリ分析ワークフロー

Query Insights は、検索クエリのパフォーマンスに対する実用的な可視性を提供するという明確な目標のもと、進化を続けています。最新の機能強化である**類似性によるクエリグルーピング**、**OpenSearch Dashboards の Query Insights**、**ローカルインデックスエクスポーター**、**プラグイン健全性監視**は、その目標に向けた大きな前進です。

これらの機能は連携して動作するように設計されており、より統合された効果的なワークフローを実現します。ダッシュボードは、Top N クエリまたはクエリグループを可視化し、数クリックで監視設定を構成できる中心的な場所を提供します。ローカルインデックスエクスポーターは履歴分析を可能にし、永続化されたデータを通じてトレンドを探索したり、過去の問題を調査したりできます。このプロセス全体を通じて、健全性監視ツールは Query Insights システムが効果的に動作していることを確認できます。

これらの改善により、クエリの動作を理解し最適化するための、より完全でユーザーフレンドリーなワークフローが提供されます。履歴データを使用してレイテンシスパイクを調査する場合でも、グルーピングを使用して非効率なクエリの繰り返しパターンを特定する場合でも、OpenSearch Dashboards で監視パラメータを設定する場合でも、Query Insights により検索のチューニングがより簡単で直感的になりました。

開始するには、最新の Query Insights および Query Insights Dashboards プラグインを提供する最新の OpenSearch バージョンに更新してください。セットアップガイド、API リファレンス、例については、[Query Insights ドキュメント](https://opensearch.org/docs/latest/observing-your-data/query-insights/index/)を参照してください。

いつものように、皆様のフィードバックは OpenSearch のオブザーバビリティの改善に役立ちます。この新機能を探索し、[OpenSearch フォーラム](https://forum.opensearch.org/)でご意見をお聞かせください。
