---
title: "[翻訳] OpenSearch Data Prepper 2.12 のご紹介: データ取り込みのための新しいソースとシンク"
emoji: "🔍"
type: "tech"
topics: ["opensearch", "dataprepper", "opentelemetry", "aws", "observability"]
publication_name: "opensearch"
published: true
published_at: 2025-07-01
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

@[card](https://opensearch.org/blog/announcing-opensearch-data-prepper-2-12-additional-source-and-sinks-for-your-data-ingestion-needs/)

OpenSearch Data Prepper 2.12 がダウンロード可能になりました！このリリースでは、OpenTelemetry (OTel) データを取り込む新しい方法と、2 つの新しいシンクが含まれています。

## 統合 OTLP ソース

[Data Prepper](https://docs.opensearch.org/docs/latest/data-prepper/) に、統合 OpenTelemetry Protocol (OTLP) ソースが追加されました。これにより、単一の統合された設定でテレメトリデータの取り込みを効率化できます。このソースは複数のプロトコルをサポートし、gRPC と HTTP (proto エンコーディング) の両方のエンドポイントをシームレスに処理します。公開された OTLP エンドポイントを通じて OTel のログ、トレース、メトリクスの取り込みが可能になり、設定管理が簡素化され、データ処理パイプラインの効率が向上します。

さらに、OTel が提供するさまざまなシグナルタイプの処理を支援するために、Data Prepper に `getEventType()` 関数が追加されました。この機能により、パイプライン内でイベントの動的な分類と条件付きルーティングが可能になり、より柔軟でインテリジェントな処理を実現します。特に `otlp` ソースでは、この関数を使用して異なるタイプを異なるパイプラインにルーティングできます。

以下のサンプルパイプラインは、ログ、メトリクス、トレースを 3 つの異なるパイプラインにルーティングする基本的な `otlp` ソースの設定を示します。

```yaml
source:
  otlp:
  route:
    - logs: 'getEventType() == "LOG"'
    - traces: 'getEventType() == "TRACE"'
    - metrics: 'getEventType() == "METRIC"'
```

## Amazon SQS シンク

Data Prepper で [Amazon Simple Queue Service (Amazon SQS)](https://aws.amazon.com/sqs/) が出力シンクとしてサポートされるようになりました。Amazon SQS は、分散システムにおけるプロデューサーとコンシューマーの分離を目的として広く採用されているメッセージキューイングサービスです。タイムリーな配信と信頼性の高い処理が求められる軽量で構造化されたメッセージに特に適しています。

Data Prepper の出力を SQS に送信することで、データのプロデューサーとコンシューマー間のシームレスな通信が可能になります。SQS にデータを直接送信する方法は、Amazon Simple Storage Service (Amazon S3) バケットに出力を送信してそのバケットに SQS 通知を設定するといった従来のアプローチと比較して、大幅に高速かつ効率的です。新しい SQS シンクにより、Data Prepper は S3 への書き込みや間接的な SQS トリガーのオーバーヘッドを回避し、レイテンシーを削減してレスポンスを向上させます。S3 イベント通知の設定、中間ファイルの書き込み、バケットライフサイクルルールの管理が不要になります。処理からキューイングまで、クリーンで最小限の設定で直接実行できるようになりました。

SQS シンクの使い方は以下のとおりです。

```yaml
sink:
  - sqs:
        queue_url: <queue-url>
        codec:
          json:
        aws:
          region: <region>
          sts_role_arn: <role>
```

## AWS X-Ray 向け OTLP シンク

Data Prepper の新しい OTLP シンクプラグインを使用して、処理済みのトレースデータを [AWS X-Ray](https://aws.amazon.com/xray/) にシームレスにエクスポートすることで、オブザーバビリティパイプラインの相互運用性を強化できるようになりました。この統合により、OTel 標準への準拠を維持しながら Data Prepper の強力な変換・エンリッチメント機能を活用し、OTLP 形式で AWS X-Ray にデータを直接送信できます。OTLP シンクは現在、AWS X-Ray エンドポイントへのスパンのエクスポートをサポートしており、将来のバージョンでは任意の OTLP protobuf 互換エンドポイントへのスパン、メトリクス、ログの送信をサポートする予定です。このプラグインは高パフォーマンス向けに設計されており、最小限のシステムリソースで最大 3,500 トランザクション/秒を維持し、p99 レイテンシーは 150ms 未満です。本番環境の信頼性を考慮して構築されており、指数バックオフ付きの設定可能なリトライロジック、効率的なデータ転送のための gzip 圧縮、パイプラインの健全性を監視するための包括的なメトリクスを備えています。AWS X-Ray 向け OTLP シンクの使い方は以下のとおりです。

```yaml
source:
  otel_trace_source:
sink:
  - otlp:
      endpoint: "https://xray.{region}.amazonaws.com/v1/traces"
      aws: { }
```

## Maven リリース

多くのコミュニティメンバーが、さまざまな Data Prepper の機能をライブラリとして使用することに関心を示しています。より広いコミュニティをサポートするために、Data Prepper チームはすべての Data Prepper ライブラリを Maven Central に公開するようになりました。

以下の Maven グループがコミュニティに提供されています。

- `org.opensearch.dataprepper` — プラグイン作成者がプラグインを作成するために使用する `data-prepper-api` ライブラリを含みます。
- `org.opensearch.dataprepper.test` — Data Prepper に対する開発時の一般的なテストシナリオをサポートするテストライブラリです。
- `org.opensearch.dataprepper.plugins` — Data Prepper とともにデプロイされるプラグインです。各プラグインは独自の jar を持つか、密接に関連するプラグインと組み合わされています。
- `org.opensearch.dataprepper.core` — プラグインフレームワーク、イベント、式、パイプラインとしての実行など、Data Prepper のコア機能です。

## その他の機能と改善

- Data Prepper の式で剰余演算子 (`%`) がサポートされるようになりました。
- Data Prepper で API トークンを使用して OpenSearch に認証できるようになりました。新しいパラメーター `api_token` はベアラートークンを設定し、JWT を使用して OpenSearch にアクセスできます。
- すべてを有効/無効にするのではなく、特定の実験的プラグインを個別に有効にできるようになりました。
- 特定の Data Prepper メトリクスのレポートを無効にできるようになりました。これにより、監視が不要なメトリクスがある場合に、メトリクスの全体量を削減できます。

## はじめに

- Data Prepper をダウンロードするには、[OpenSearch のダウンロード](https://opensearch.org/downloads.html)ページにアクセスしてください。
- Data Prepper の使い方については、[Data Prepper 入門](https://opensearch.org/docs/latest/data-prepper/getting-started/)を参照してください。
- Data Prepper 2.13 およびその他のリリースの進行中の作業については、[Data Prepper ロードマップ](https://github.com/orgs/opensearch-project/projects/221)を参照してください。

## コントリビューターの皆さんに感謝します！

このリリースに貢献してくださった以下のコミュニティメンバーに感謝します！

- [alparish](https://github.com/alparish)
- [chenqi0805](https://github.com/chenqi0805) — Qi Chen
- [Davidding4718](https://github.com/Davidding4718) — Siqi Ding
- [derek-ho](https://github.com/derek-ho) — Derek Ho
- [divbok](https://github.com/divbok) — Divyansh Bokadia
- [dlvenable](https://github.com/dlvenable) — David Venable
- [gaiksaya](https://github.com/gaiksaya) — Sayali Gaikawad
- [graytaylor0](https://github.com/graytaylor0) — Taylor Gray
- [huypham612](https://github.com/huypham612) — huyPham
- [jeffreyAaron](https://github.com/jeffreyAaron) — Jeffrey Aaron Jeyasingh
- [KarstenSchnitter](https://github.com/KarstenSchnitter) — Karsten Schnitter
- [kkondaka](https://github.com/kkondaka) — Krishna Kondaka
- [MohammedAghil](https://github.com/MohammedAghil) — Mohammed Aghil Puthiyottil
- [nsgupta1](https://github.com/nsgupta1) — Neha Gupta
- [oeyh](https://github.com/oeyh) — Hai Yan
- [ps48](https://github.com/ps48) — Shenoy Pratik
- [saketh-pallempati](https://github.com/saketh-pallempati) — Saketh Pallempati
- [san81](https://github.com/san81) — Santhosh Gandhe
- [savit-aluri](https://github.com/savit-aluri) — Savit Aluri
- [sb2k16](https://github.com/sb2k16) — Souvik Bose
- [shenkw1](https://github.com/shenkw1) — Katherine Shen
- [Zhangxunmt](https://github.com/Zhangxunmt) — Xun Zhang
