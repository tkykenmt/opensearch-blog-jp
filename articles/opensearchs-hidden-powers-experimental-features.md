---
title: "[翻訳] OpenSearch の隠れた力: 実験的機能"
emoji: "🔍"
type: "tech"
topics: ["opensearch", "experimental", "observability", "grpc", "dashboards"]
publication_name: "opensearch"
published: true
published_at: 2026-02-19
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

@[card](https://opensearch.org/blog/opensearchs-hidden-powers-experimental-features/)

私は最近、最新の実験的機能である Apache Arrow と Arrow Flight の実装について[記事を書きました](https://opensearch.org/blog/opensearch-and-apache-arrow-a-tour-of-the-archery-range/)が、その際に、技術的には「実験的」でありながら十分な注目を集めていない他の OpenSearch の機能についても考えました。

OpenSearch Project がイノベーションに真剣に取り組み、問題をより小さく消化しやすいステップに分解する新しい方法を模索していることを学びました。そのためには、ある程度の実験が必要になることもあります。OpenSearch には、明日のイノベーションを今日試せるように実験的とマークされた多くの機能があります。もちろんそれらはクールでエキサイティングですが、実験的な形態ではリスクを伴う可能性もあります。安定性とリスクの境界線こそがイノベーションの生まれる場所です。これらの機能を最前線に持ってくるために、皆さんの協力が必要です。

## 実験的機能とは

実験的機能は、まだ本番環境向けの準備が完全には整っていませんが、重要なイノベーションを表しています。開発環境での使用に最適であり、すべての機能が本番環境で完全に使用可能と見なされるほど十分な開発期間を経ているわけではありません。

## まだ完成していないものを試す理由

まず、イノベーションへの早期アクセスが得られます。新しいアルゴリズム、UI の変更、パフォーマンスの最適化、最先端の機械学習機能などは、フィーチャーフラグの背後に隠される傾向があるイノベーションの例です。また、コミュニティのフィードバックが OpenSearch の将来を直接形作る領域でもあります。これらの機能のテストへの貢献が、開発とイノベーションを前進させます。電球はろうそくの継続的な改良から生まれたわけではありません。

## これらの機能にアクセスする方法

フィーチャーフラグの背後に隠された実験的機能は、`opensearch.yml` または `opensearch_dashboards.yml` の設定オプションを通じてアクセスできます。いくつかの例を見てみましょう。

## OpenSearch Dashboards の Workspace

以下の画像に示す **OpenSearch Dashboards の Workspace** は、実装するユースケースに特化した方法で画面上の要素をカスタマイズできるように UI を再構成します。オブザーバビリティのユースケースでは、ログやメトリクスを通じてヘルスとパフォーマンスを可視化することに大きく依存します。

![OpenSearch Dashboards の Workspace](/images/opensearchs-hidden-powers-experimental-features/003e1c09120c.png)

この機能を有効にするには、`opensearch_dashboards.yml` ファイルに以下の数行を追加します。

```yaml
workspace.enabled: true
uiSettings:
    overrides:
        "home:useNewHomePage": true
```

クラスターに Security プラグインがインストールされている場合は、マルチテナンシーを無効にする必要があります。設定に以下も追加してください。

```yaml
opensearch_security.multitenancy.enabled: false
```

## 分散トレーシング

分散トレーシング機能はバージョン 2.10 から実験的機能として提供されており、アプリケーショントレーシングのユースケースに最適です。この機能を有効にするには、いくつかの編集が必要です。

- `opensearch.yml` ファイルに `opensearch.experimental.feature.telemetry.enabled=true` を追加します。
- さらに `telemetry.feature.tracer.enabled=true` と `telemetry.tracer.enabled=true` を追加します。

最後に、OpenSearch OpenTelemetry プラグイン (`telemetry-otel`) をインストールします。詳細については、[分散トレーシングのドキュメント](https://docs.opensearch.org/latest/observing-your-data/trace/distributed-tracing/)を参照してください。

## 他にもあるのか

OpenSearch にはいくつかの実験的機能があります。ドキュメントには「これは実験的機能であり、本番環境での使用は推奨されません」と明確に記載されています。

そのような実験的機能の 1 つが[インデックスコンテキスト](https://docs.opensearch.org/latest/im-plugin/index-context/)で、インデックスのユースケースを宣言します。これにより、OpenSearch は事前設定された一連の設定とマッピングを適用できます。

また、[セキュリティ設定のバージョニングとロールバック API](https://docs.opensearch.org/latest/security/configuration/versioning/) も実験的に利用可能です。これはセキュリティ設定のバージョン管理手段を提供します。変更が追跡され、監査証跡が作成され、必要に応じて以前の設定を復元できます。

私のお気に入りの実験的機能の 1 つは、[gRPC 経由の Search API](https://docs.opensearch.org/latest/api-reference/grpc-apis/search/) です。これにより、トランスポートの目的で Protocol Buffers を利用しながら gRPC 経由でクエリを実行でき、データをクエリする非常にパフォーマンスの高い方法となります。

また、Pull ベースのインジェスト API にも非常に期待しています。クライアントや小さなサイドカーアプリがデータを OpenSearch にプッシュする代わりに、OpenSearch が自らデータを取得しに行き、許容可能なレートでデータが取得されることを保証し、ドキュメントの取り込みが速すぎてクラスターに悪影響を与えないようにします。現在、Apache Kafka 用と Amazon Kinesis 用の 2 つのインジェストプラグインのみが存在します。Pull ベースのインジェストの詳細については[こちら](https://docs.opensearch.org/latest/api-reference/document-apis/pull-based-ingestion/)を参照してください。

## 責任を持って実験しましょう

実験的機能は予告なく変更される可能性があるため、本番環境では使用しないでください。実験は開発環境、テストクラスター、概念実証、学習と探索に限定してください。実験的機能を有効にした後はクラスターを注意深く監視してください。顕著なパフォーマンスの変化、予期しないクラッシュ、リソース消費の増加、互換性の問題が発生する可能性があります。

## さあ、試してみましょう

OpenSearch Project は、検索、分析、オブザーバビリティのニーズに応えるために継続的にイノベーションを行っています。皆さんのフィードバックはこのプロセスにとって非常に貴重です。[コミュニティフォーラム](https://forum.opensearch.org/)でフィードバックを共有したり、プロジェクトの [Slack インスタンス](https://opensearch.org/slack/)で他の OpenSearch ユーザーとつながったりしてください。
