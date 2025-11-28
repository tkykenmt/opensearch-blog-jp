---
title: "[翻訳] OpenSearch と OpenTelemetry で分散マイクロサービスを深く理解する"
emoji: "🔭"
type: "tech"
topics: ["opensearch", "opentelemetry", "observability", "microservices", "tracing"]
published: true
publication_name: "opensearch"
published_at: 2025-08-12
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/diving-deep-into-distributed-microservices-with-opensearch-and-opentelemetry/

現代の分散システムでは、マイクロサービス間のインタラクションを理解することが、パフォーマンスのボトルネックを特定し、障害を診断するために不可欠です。本記事では、[OpenSearch バージョン 3.1](https://opensearch.org/blog/get-started-with-opensearch-3-1/) の Trace Analytics プラグインで導入された新機能 (強化されたサービスマップの可視化、高度なスパングルーピング、レイテンシ分布チャートなど) を紹介します。また、OpenTelemetry (OTel) Collector と OpenSearch Data Prepper を使用してテレメトリデータを計装、収集、OpenSearch に取り込む方法も説明します。その後、OpenSearch Dashboards を使用してオブザーバビリティ調査ワークフローを探索、可視化、分析する方法を順を追って説明します。

## デモのセットアップ

複数のマイクロサービスで構成された e コマースサイトである OpenTelemetry Astronomy Shop を使用します。このデモは [opentelemetry-demo](https://github.com/opensearch-project/opentelemetry-demo) で利用できます。Docker Compose セットアップにより、Astronomy Shop サービスと以下のコンポーネントが起動します。

* **OpenSearch Data Prepper**: ログとトレースを OpenSearch に取り込みます。
* **OpenSearch**: テレメトリデータを保存し、検索エンジンとして機能します。
* **OpenSearch Dashboards**: ログ、メトリクス、トレースの統合 UI を提供します。

デモのアーキテクチャを以下の図に示します。

![Astronomy Shop デモのアーキテクチャ図](/images/opensearch-opentelemetry-microservices/os-observability-architecture.png)

### OpenTelemetry Astronomy Shop

Astronomy Shop には、以下の画像に示すように、Frontend、Cart、Ad、Accounting、Currency、Payment、Checkout などのサービスが含まれています。各サービスは異なる言語で実装されており、OTel SDK を使用してスパンとメトリクスを出力します。

![Astronomy Shop のサービス](/images/opensearch-opentelemetry-microservices/otel-demo-astronomy-shop-1.gif)

### OTel デモのフィーチャーフラグ

デモには、以下の画像に示すように、`adServiceHighCpu`、`cartServiceFailure`、`productCatalogFailure`、`paymentServiceFailure` などの障害をシミュレートするフィーチャーフラグサービスが含まれています。このウォークスルーでは、Ad サービスに焦点を当て、高エラー率シナリオをトリガーして、障害を検出・診断する方法を説明します。

![フィーチャーフラグサービス](/images/opensearch-opentelemetry-microservices/otel-demo-feature-flag-scaled.png)

### OpenSearch Dashboards

OpenSearch Dashboards にはいくつかのオブザーバビリティプラグインが含まれています。このデモでは、以下のプラグインを有効にします。

1. **Workspaces**: 関連するダッシュボードとクエリを整理します。
2. **Query Enhancements**: オートコンプリート、シンタックスハイライト、AI 駆動の提案を追加します。
3. **Query Assist**: 自然言語と AI 駆動のクエリ生成を可能にします。

デモでは、以下のプラグインも設定しました。

* **Services**: Rate、Errors、Duration (RED) メトリクス、サービスマップ、ログとトレースへのリンクを表示します。
* **Traces**: 個々のトレース、トレースグループ、スパンの探索を可能にし、ガントチャート、累積サービスタイミング、トレースペイロードを表示します。
* **Discover**: Piped Processing Language (PPL)、SQL、Lucene、または Dashboards Query Language (DQL) を使用したログとメトリクスのアドホッククエリを提供します。

### 相関ログインデックスのセットアップ

OpenSearch 3.1 では、Trace Analytics プラグインで、以下の画像に示すように、トレースとサービスマップのインデックスに加えて、非 OTel ログスキーマをサポートするカスタムフィールドマッピングを持つ相関ログインデックスをセットアップできるようになりました。

![Trace Analytics プラグインのアニメーション](/images/opensearch-opentelemetry-microservices/correlations-setup.gif)

### 自然言語機能

以下の AI 駆動機能により、調査が効率化されます。

1. **Text-to-PPL**: 平易な言語の質問を PPL クエリに変換します。
2. **データ要約**: クエリ結果とログフィールドの簡潔な要約を提供します。

OpenSearch Dashboards の AI 機能の詳細については、[OpenSearch Assistant for OpenSearch Dashboards](https://docs.opensearch.org/docs/latest/dashboards/dashboards-assistant/index/) を参照してください。

## オブザーバビリティワークフロー

本番環境でサービスを監視する際、問題を特定して解決するための体系的なアプローチが重要です。このウォークスルーでは、OpenSearch オブザーバビリティツールを使用してサービスエラーを迅速に特定し、調査する方法を示します。

### ステップ 1: 問題のあるサービスを特定

**Services** ページでは、以下の画像に示すように、すべてのサービスとその健全性ステータスの概要を確認できます。

![Services ページのスクリーンショット](/images/opensearch-opentelemetry-microservices/opensearch-services-scaled.png)

問題のあるサービスを素早く特定するには、エラー率でソートして最も高い障害率のサービスを特定します。または、以下の画像に示すように、**Errors** タブを選択したサービスマップを表示して、どのサービスが問題を経験しているか、それらがどのように相互接続されているかを可視化できます。

![サービスマップのエラー表示](/images/opensearch-opentelemetry-microservices/ad-service-correlated-traces-scaled.png)

### ステップ 2: 問題のあるサービスに移動

Ad サービスのエラー率が高いことを特定した後、それを選択して専用のサービスページに移動します。このページでは、以下の画像に示すように、問題のあるサービスのより焦点を絞ったビューが提供されます。

![サービスページのスクリーンショット](/images/opensearch-opentelemetry-microservices/highlighted-ad-service-scaled.png)

### ステップ 3: サービス概要の分析

Ad サービスページでは、以下の画像に示すように、高レベルのパフォーマンス指標、時間経過に伴うエラー率の傾向、サービスの健全性パターン、主要なパフォーマンスメトリクスなど、包括的な概要メトリクスを確認できます。トレンドセクションは、これが最近の問題なのか継続的な問題なのかを理解するのに役立ちます。

![Ad サービスの詳細](/images/opensearch-opentelemetry-microservices/highlighted-ad-service-scaled.png)

### ステップ 4: 個々のトレースを調査

根本原因をより深く掘り下げるには、**Traces** アイコンを選択して、このサービスがフィルターとして適用された **Traces** ページにリダイレクトします (以下の画像参照)。

![Traces ページのスクリーンショット](/images/opensearch-opentelemetry-microservices/ad-service-correlated-traces-scaled.png)

ここで個々のリクエストとその実行パスを調べることができます。**Traces** ページで、エラーでソートして問題のあるリクエストを分離します。これにより、以下の画像に示すように、エラーを含む 2 つのスパンが明らかになります。

![エラートレースの選択](/images/opensearch-opentelemetry-microservices/opensearch-services-demo-2.gif)

### ステップ 5: トレースタイムラインの分析

特定のトレース ID を選択して **Trace details** ページにリダイレクトします。このページでは、以下の画像に示すように、その特定のリクエストの詳細な実行フローを調べることができます。

![選択されたエラートレース](/images/opensearch-opentelemetry-microservices/selected-error-trace-scaled.png)

Trace Details ページには、各サービス呼び出しのタイミング情報、エラーの場所、サービスの依存関係と呼び出しパターンを含む、サービス間の完全なリクエストフローを示すガントチャートが表示されます。以下の画像では、ad サービスのスパンに焦点を当て、それを選択して特定のエラーに関するより詳細な情報を表示します。

![トレース詳細ページ](/images/opensearch-opentelemetry-microservices/trace-details-page.gif)

### ステップ 6: エラーログの調査

根本原因を理解するには、以下の画像に示すように、エラースパンに関連するすべてのログエントリを表示する **Logs** ページに移動します。

![エラーページのスクリーンショット](/images/opensearch-opentelemetry-microservices/correlated-logs-from-spans-scaled.png)

`body` フィールドを選択することで、以下の画像に示すように、障害につながった特定のエラーメッセージとコンテキストを素早く確認できます。

![相関ログ](/images/opensearch-opentelemetry-microservices/correlated-logs-scaled.png)

### ステップ 7: 自然言語クエリの使用

より高度な調査には、自然言語機能を使用してデータをクエリできます。「Show me the logs for span id '475dc023cbf02058' and summarize the body field」のようなプロンプトを使用すると、以下の画像に示すように、システムが適切なクエリを生成し、調査結果の要約を提供します。これにより、手動でクエリを書くことなく、複雑なエラーパターンを理解しやすくなります。

![自然言語クエリと要約](/images/opensearch-opentelemetry-microservices/nlqg-summary-ad-service-1.gif)

## このワークフローからの主な学び

この体系的なアプローチは以下のメリットを提供します。

* サービスレベルのメトリクスへのアクセスによる*迅速な問題特定*
* 分散トレーシングを使用した*正確なエラー位置の特定*
* 詳細なログ調査による*根本原因分析*
* 自然言語クエリを使用した*効率的な調査*

このワークフローに従うことで、サービスの問題の検出から根本原因の理解まで迅速に移行でき、より速い解決とシステム信頼性の向上を実現できます。

## 次のステップ

オブザーバビリティの実践をさらに進める準備はできましたか？以下の次のステップをご覧ください。

* [**OTel デモを自分で試す**](https://github.com/opensearch-project/opentelemetry-demo): Astronomy Shop デモをセットアップし、サービスエラー、トレーシング、ログ相関を実験してください。
* **自然言語機能を探索**: 自然言語クエリやデータ要約などの AI 駆動機能をより深く掘り下げてください。
* **独自のサービスと統合**: マイクロサービスを OTel SDK で計装し、OpenSearch に接続してより深い洞察を得てください。

OpenSearch 3.1 のトレースとサービスの更新に関するリソースとドキュメントの詳細については、[Trace Analytics plugin for OpenSearch Dashboards](https://docs.opensearch.org/latest/observing-your-data/trace/ta-dashboards/) と [Trace analytics](https://docs.opensearch.org/latest/data-prepper/common-use-cases/trace-analytics/) を参照してください。
