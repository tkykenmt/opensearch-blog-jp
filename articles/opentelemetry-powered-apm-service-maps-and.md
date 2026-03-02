---
title: "[翻訳] Data Prepper 2.14: OTel ベースの APM サービスマップと Prometheus サポート"
emoji: "🔍"
type: "tech"
topics: ["opensearch", "opentelemetry", "prometheus", "dataprepper", "observability"]
publication_name: "opensearch"
published: true
published_at: 2026-02-25
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/opentelemetry-powered-apm-service-maps-and-production-ready-prometheus-support/

OpenSearch Data Prepper のメンテナーは、Data Prepper 2.14 のリリースを発表しました。このバージョンでは、新しいアプリケーションパフォーマンスモニタリング (APM) サービスマップと改善された Prometheus サポートにより、オブザーバビリティのユースケースへの対応が拡充されています。

## APM サービスマップ

`otel_apm_service_map` プロセッサーは、OpenTelemetry のトレーススパンを分析して APM サービスマップの関係性とメトリクスを自動生成します。サービス間の通信方法やパフォーマンス特性を示すサービストポロジーグラフとして可視化できる構造化イベントを作成します。

主な機能は以下のとおりです。

- **サービス関係の自動検出:** OpenTelemetry スパンからサービス間のインタラクションを特定します。
- **APM メトリクスの生成:** スライディングタイムウィンドウによる 3 ウィンドウ処理を使用して、サービスインタラクションのレイテンシー、スループット、エラーレートのメトリクスを生成し、完全なトレースコンテキストを確保します。
- **環境認識:** 既存のスパン属性から新しい属性を導出し、サービス環境のグルーピングとカスタム属性をサポートします。Amazon Elastic Compute Cloud (Amazon EC2)、Amazon Elastic Container Service (Amazon ECS)、Amazon Elastic Kubernetes Service (Amazon EKS)、AWS Lambda、Amazon API Gateway の環境検出機能を備えており、他のクラウドプロバイダーへの拡張も可能です。
- **サービスマップスナップショット:** カスタマイズ可能なリソース属性フィルタリングにより、特定の期間のサービス接続を表示できます。

## Prometheus シンクサポートの改善

Prometheus シンクは、統合されたソートおよび重複排除ロジックにより、リモートライト要件への準拠を確保するようになりました。受信イベントを時系列に整理し、同一シリーズ/タイムスタンプの重複サンプルを送信前に除去することで、ブローカー側での拒否を防止します。

データ取り込みの課題にさらに対応するため、新しい `out_of_order_time_window` オプションにより、遅延データに対する猶予期間を設定できます。このウィンドウにより、シンクは順序どおりに到着しなかったサンプルを受け入れて再ソートできるため、完全な順序での配信が困難な分散環境でのパイプラインの耐障害性が大幅に向上します。

## AWS Lambda ストリーミング

AWS Lambda の機能の 1 つとして、[レスポンスストリーミング](https://docs.aws.amazon.com/lambda/latest/dg/configuration-response-streaming.html)があります。これにより、関数からクライアントへデータをストリーミングでき、最初のレスポンスのレイテンシーが削減され、最大 200 MB のより大きなペイロードをサポートします。

Data Prepper 2.14 では、`aws_lambda` プロセッサーでストリーミング呼び出しを使用するように設定できるようになりました。これにより、6 MB を超えるレスポンスを受信できるため、出力データが入力データのサイズを超える場合に特に有用です。

## クロスリージョン S3 シンク

Data Prepper の `s3` シンクが、複数の AWS リージョンにまたがる Amazon Simple Storage Service (Amazon S3) バケットへの書き込みをサポートするようになりました。

以前は、単一の `s3` シンクは 1 つのリージョンのバケットにしか書き込めなかったため、主要な機能の 1 つである動的バケット名の活用が制限されていました。

この機能強化により、異なるリージョンに対応する動的バケット名を指定できます。たとえば、`myorganization-${/aws/region}` のようなバケットを定義すると、Data Prepper は `myorganization-us-east-2` や `myorganization-eu-central-1` などのバケットに書き込みます。

## forward_to パイプライン

特定のワークフローでは、特定の順序でシンクにデータを送信したり、あるシンクの出力を別のシンクの入力として使用したりする必要がある場合があります。

`opensearch` シンクが `forward_to` 設定をサポートするようになりました。これにより、OpenSearch への書き込み後にイベントを受信するターゲットパイプラインを定義できます。転送されたイベントにはドキュメント ID フィールドが含まれます。

## ARM アーキテクチャサポート

Data Prepper は、ARM と x86 の両方をサポートするマルチアーキテクチャ Docker イメージを提供するようになりました。

多くの組織がコンピューティングコストの削減のために ARM を採用する中、この変更により、エミュレーションに頼ることなく ARM システムで Data Prepper イメージを直接プルできます。

さらに、Data Prepper は ARM アーカイブファイルも提供しており、Docker を使用しない ARM システムでの実行が容易になります。

## その他の主な変更点

- Data Prepper の Docker イメージが 46% 小さくなり、レイヤー数も削減されたため、Docker プル時間が改善されました。
- AWS Lambda プロセッサーで改善されたタイムアウト設定がサポートされるようになりました。
- aggregate プロセッサーでエンドツーエンドの確認応答のサポートが強化され、確認応答を無効にする設定が追加されました。
- Data Prepper はパイプラインの健全性を監視するためのいくつかの新しいメトリクスを提供します。

## はじめに

- Data Prepper をダウンロードするには、[Download & Get Started](https://opensearch.org/downloads.html) ページを参照してください。
- Data Prepper の使い方については、[Getting started with OpenSearch Data Prepper](https://opensearch.org/docs/latest/data-prepper/getting-started/) を参照してください。
- Data Prepper 2.15 やその他のリリースの進行中の作業については、[Data Prepper Project Roadmap](https://github.com/orgs/opensearch-project/projects/221) を参照してください。

## コントリビューターの皆さんに感謝します!

このリリースに貢献してくださった以下のコミュニティメンバーに感謝します!

- [ashrao94](https://github.com/ashrao94)
- [chenqi0805](https://github.com/chenqi0805) — Qi Chen
- [chrisale000](https://github.com/chrisale000)
- [cwperks](https://github.com/cwperks) — Craig Perkins
- [divbok](https://github.com/divbok) — Divyansh Bokadia
- [dlvenable](https://github.com/dlvenable) — David Venable
- [eatulban](https://github.com/eatulban)
- [graytaylor0](https://github.com/graytaylor0) — Taylor Gray
- [joelmarty](https://github.com/joelmarty) — Joël Marty
- [kennedy-onyia](https://github.com/kennedy-onyia) — Kennedy Onyia
- [kkondaka](https://github.com/kkondaka) — Krishna Kondaka
- [LeilaMoussa](https://github.com/LeilaMoussa) — Leila Moussa
- [mananrajotia](https://github.com/mananrajotia) — Manan Rajotia
- [peterzhuamazon](https://github.com/peterzhuamazon) — Peter Zhu
- [sabarinathan590](https://github.com/sabarinathan590) — Sabarinathan Subramanian
- [san81](https://github.com/san81) — Santhosh Gandhe
- [sb2k16](https://github.com/sb2k16) — Souvik Bose
- [stelucz](https://github.com/stelucz) — Stehlík Lukáš
- [Subrahmanyam-Gollapalli](https://github.com/Subrahmanyam-Gollapalli) — Subrahmanyam-Gollapalli
- [TomasLongo](https://github.com/TomasLongo) — Tomas
- [Utkarsh-Aga](https://github.com/Utkarsh-Aga) — Utkarsh Agarwal
- [vamsimanohar](https://github.com/vamsimanohar) — Vamsi Manohar
- [vecheka](https://github.com/vecheka) — Vecheka
- [wandna-amazon](https://github.com/wandna-amazon) — Nathan Wand
- [wjyao0316](https://github.com/wjyao0316)
- [Zhangxunmt](https://github.com/Zhangxunmt) — Xun Zhang
