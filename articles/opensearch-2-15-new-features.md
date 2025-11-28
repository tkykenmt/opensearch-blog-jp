---
title: "[翻訳] OpenSearch 2.15 の新機能を探る"
emoji: "🚀"
type: "tech"
topics: ["opensearch", "search", "vectorsearch", "machinelearning", "analytics"]
published: true
publication_name: "opensearch"
published_at: 2024-06-25
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/diving-into-opensearch-2-15/

OpenSearch 2.15 が[リリース](https://opensearch.org/downloads.html)されました。パフォーマンスと効率性の向上、安定性・可用性・回復力の強化、検索アプリケーションの機能拡張に加え、新しい機械学習 (ML) 機能と使いやすさの改善が含まれています。[OpenSearch Playground](https://playground.opensearch.org/app/home#/) で OpenSearch Dashboards を使用して最新のアップデートを試すことができます。新機能の詳細については[リリースノート](https://github.com/opensearch-project/opensearch-build/blob/main/release-notes/opensearch-release-notes-2.15.0.md)をご確認ください。以下は OpenSearch 2.15 で使用できる新しいツールの一部です。

## コスト、パフォーマンス、スケール

このリリースでは、OpenSearch デプロイメントの**コスト、パフォーマンス、スケール**の改善に焦点を当てた多くの機能が提供されています。

### 並列インジェストによるドキュメント処理の高速化

多くの最新アプリケーションでは、インジェスト時に大量のデータ処理が必要です。例えば、ニューラル検索では、インジェストされたドキュメントを ML サービス (通常はリモート) によってベクトル空間に埋め込む必要があります。インジェスト処理を高速化し、最新のプロセッサやリモートサービスが提供する並列性を活用するため、OpenSearch 2.15 では[並列インジェスト処理](https://opensearch.org/docs/latest/ingest-pipelines/processors/index-processors/#batch-enabled-processors)が有効になりました。また、ドキュメントをバッチで処理する機能も導入され、リモートサービスへの API 呼び出し回数を削減してより効率的な処理が可能になりました。

### 並列処理によるハイブリッド検索の高速化

このリリースでは、ハイブリッド検索にも並列処理が導入され、大幅なパフォーマンス向上が実現しました。OpenSearch 2.10 で導入された[ハイブリッド検索](https://opensearch.org/blog/hybrid-search/)は、字句検索 (BM25) またはニューラルスパース検索とセマンティックベクトル検索を組み合わせることで、どちらか一方の手法のみを使用する場合よりも高品質な結果を提供します。これはテキスト検索のベストプラクティスです。OpenSearch 2.15 では、プロセスの様々な段階で 2 つの[サブ検索を並列実行](https://opensearch.org/docs/latest/search-plugins/neural-sparse-search/#step-5-create-and-enable-the-two-phase-processor-optional)することでハイブリッド検索のレイテンシを低減します。その結果、最大 25% のレイテンシ削減が実現しました。

### 完全一致検索の SIMD サポートによる検索パフォーマンスの向上

OpenSearch 2.12 では JDK21 のサポートが導入され、ユーザーは最新の Java バージョンで OpenSearch クラスターを実行できるようになりました。このアップグレードを基に、OpenSearch 2.15 では完全一致検索クエリに対する Single Instruction, Multiple Data (SIMD) 命令セットのサポートが追加され、パフォーマンスがさらに向上しました。以前のバージョンでは、近似最近傍検索クエリに対して SIMD がサポートされていました。完全一致検索への SIMD 統合は追加の設定手順を必要とせず、シームレスなパフォーマンス向上を実現します。ユーザーはクエリレイテンシの大幅な削減と、より効率的でレスポンシブな検索体験を期待でき、非 SIMD 実装と比較して約 1.5 倍高速なパフォーマンスが得られます。

### ベクトル検索のストレージ容量の節約

OpenSearch 2.15 では、Lucene エンジンを使用したベクトル検索で `k-nn` フィールドのドキュメント値を無効にする機能が導入されました。これは k-NN 検索機能に影響を与えません。例えば、以前のバージョンの OpenSearch と同様に、Lucene エンジンで近似最近傍検索と完全一致検索の両方を引き続き実行できます。テストでは、ドキュメント値を無効にした後、シャードサイズが約 16% 削減されることが確認されました。今後のリリースでは、この最適化を NMSLIB および Faiss エンジンにも拡張する予定です。

### ワイルドカードフィールドによる特定データの効率的なクエリ

標準の `text` フィールドはテキストをトークンに分割し、トークンインデックスを構築して検索を非常に効率的にします。しかし、多くのアプリケーションでは、トークン境界に関係なく任意の部分文字列を検索する必要があり、これはトークンインデックスでは十分にサポートされていません。OpenSearch 2.15 では [`wildcard` フィールドタイプ](https://opensearch.org/docs/latest/field-types/supported-field-types/wildcard/)が導入されました。このフィールドタイプは、特定のログのように自然なトークン構造を持たないフィールドや、個別のトークン数が非常に多い場合に、より効率的な検索を提供するインデックスを構築するオプションを提供します。

### 派生フィールドによるドキュメントフィールドの操作と効率化

OpenSearch 2.15 では[派生フィールド](https://opensearch.org/docs/latest/field-types/supported-field-types/derived/) (計算フィールド、生成フィールド、仮想フィールドとも呼ばれます) が導入されました。派生フィールドの値はクエリ時に計算されるため、フィールドを個別にインデックス化または保存する必要なく、`_source` ドキュメントに対してスクリプトをリアルタイムで実行することで、既にインデックス化されたフィールドを追加または操作できます。これにより、クエリはインジェスト時に使用されたフィールド名から独立し、異なる方法でインジェストされたデータに対して同じクエリを使用でき、動的なデータ変換とエンリッチメントが可能になります。動的フィールドは直接インデックス化を回避することでストレージ要件を削減でき、フィルタリングやレポート用の追加フィールドの計算にも使用できます。

### 単一カーディナリティ集計のパフォーマンス向上

カーディナリティ集計は、特定のフィールド内のユニーク値の概算カウントを提供する一般的なメトリクス集計手法です。使用例としては、サービスへの訪問者数のカウントや、ユニーク IP アドレスやイベントタイプ全体での異常検出などがあります。OpenSearch 2.15 では、[動的プルーニング](https://opensearch.org/docs/latest/install-and-configure/configuring-opensearch/search-settings/)と呼ばれる新しい最適化が導入され、特に低カーディナリティのフィールドで単一カーディナリティ集計のパフォーマンスが大幅に向上します。[Big5 ワークロード](https://github.com/opensearch-project/opensearch-benchmark-workloads/tree/main/big5)からの観測に基づくと、この最適化によりこれらの集計を実行する際のレイテンシが最大 100 倍改善される可能性があります。Big5 ベンチマークテストの包括的な結果は、この[プルリクエスト](https://github.com/opensearch-project/OpenSearch/pull/13821)で提供されています。

## 安定性、可用性、回復力

2.15 リリースには、OpenSearch クラスターの**安定性、可用性、回復力**をサポートするアップデートも含まれています。

### ローリングアップグレードによるリモートバックストレージへの移行

リモートバックストレージは、すべてのインデックストランザクションのバックアップを自動的に作成し、リモートストレージに送信することで、データ損失から保護する新しい方法を提供します。OpenSearch 2.14 で実験的機能として導入された[リモートバックストレージへの移行](https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/remote-store/migrating-to-remote/)は、OpenSearch 2.15 で本番環境対応の機能として有効になりました。ローリングアップグレードメカニズムを通じて、ドキュメントレプリケーションベースのクラスターをリモートバックストレージに移行できるようになりました。ローリングアップグレード (ノード置換アップグレードとも呼ばれます) は、実質的にダウンタイムなしで実行中のクラスターで実行できます。ノードは個別に停止してその場で移行するか、または、ノードを停止してリモートバックホストで 1 つずつ置き換えることができます。このプロセス中も、クラスターデータのインデックス作成とクエリを継続できます。

### クラスター状態公開のオーバーヘッド削減 (実験的機能)

OpenSearch 2.15 では、リモートバックストレージを通じてクラスター状態の公開を有効にする実験的機能が追加されました。従来、クラスターマネージャーノードはクラスター状態の更新を処理し、更新されたクラスター状態をローカルトランスポート層を通じてすべてのフォロワーノードに公開していました。[リモートバック状態公開](https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/remote-store/remote-cluster-state/)を有効にすると、クラスター状態は状態更新のたびにリモートストアにバックアップされます。これにより、フォロワーノードはリモートストアから直接更新された状態を取得でき、公開のためのクラスターマネージャーノードのメモリと通信オーバーヘッドが削減されます。

### Top N クエリによる検索クエリパフォーマンスの可視性向上

OpenSearch 2.15 では、[Top N クエリ](https://opensearch.org/docs/latest/observing-your-data/query-insights/top-n-queries/)のいくつかの高度な機能が導入され、クエリパフォーマンス分析とモニタリングが強化されました。レイテンシによる Top N クエリに加えて、ユーザーは CPU とメモリ使用量に基づいて Top N クエリを設定および取得できるようになりました。このリリースでは、クエリインサイトをローカルインデックスなどの宛先にエクスポートすることも可能になり、パフォーマンス分析と問題のあるクエリの特定のために履歴 Top N クエリデータを保存できます。Top N クエリ結果には、タスクレベルのリソース使用量や Top N クエリのソース追跡用の `x-opaque-id` など、追加のメトリクスと情報も含まれるようになりました。これらの機能により、ユーザーはクエリパフォーマンスへの可視性が拡張され、より効果的な最適化とトラブルシューティングが可能になります。

## 検索と ML

OpenSearch 2.15 には、ML を活用したアプリケーションと統合をより柔軟で構築しやすくするために設計された、OpenSearch **検索および ML** ツールキットへのいくつかの追加が含まれています。

### 既存の字句インデックスからのベクトル検索の有効化

[フローフレームワーク](https://opensearch.org/docs/latest/automating-configurations/api/index/)を使用して、ユーザーはテンプレートを実行し、既存の字句インデックスをそのテキストフィールドからのベクトルフィールドで拡張できるようになりました。この[再インデックスワークフロー](https://opensearch.org/docs/latest/automating-configurations/workflow-steps/)機能により、ソースインデックスの再インデックス化に時間とリソースを費やすことなく、既存のインデックスでベクトル検索とハイブリッド検索を簡単に有効にできます。

### モデルの有害性に対するガードレールとしての統合 AI サービスの使用

以前は、OpenSearch ユーザーは OpenSearch [モデル](https://opensearch.org/docs/latest/ml-commons-plugin/api/model-apis/index/)からの有害な入出力を検出するために、正規表現ベースのガードレールのみを作成できました。OpenSearch 2.15 では、リモートモデルを[ガードレール](https://opensearch.org/docs/latest/ml-commons-plugin/remote-models/guardrails/)として設定できるようになりました。これにより、ユーザーは最先端の AI サービスやモデルを使用して、より正確に有害性を検出する強力なガードレールを作成できます。

### ML 推論処理のためのローカルモデルの有効化

[ML 推論プロセッサ](https://opensearch.org/docs/latest/ingest-pipelines/processors/ml-inference/)により、ユーザーは統合された ML モデルからの推論を使用してインジェストパイプラインをエンリッチできます。以前は、プロセッサは Amazon SageMaker、OpenAI、Cohere、Amazon Bedrock などのモデルプロバイダー API に接続するリモートモデルのみをサポートしていました。OpenSearch 2.15 では、プロセッサは検索クラスターのインフラストラクチャでホストされるモデルであるローカルモデルと互換性があります。

## 使いやすさ

このリリースには、OpenSearch の**使いやすさ**を向上させるツールも含まれています。

### より多くの OpenSearch Dashboards プラグインでの複数データソースへのアクセス

OpenSearch Dashboards 全体で[複数データソース](https://opensearch.org/docs/latest/dashboards/management/multi-data-sources/)をサポートする継続的な取り組みの一環として、OpenSearch 2.14 では 9 つの外部 Dashboards プラグインのサポートが追加されました。このリリースでは、OpenSearch クラスター間でデータを管理し、可視化を単一のダッシュボードに統合するのに役立つ、さらにいくつかのプラグインのサポートが追加されました。4 つの外部 Dashboards プラグイン (Metrics Analytics、Security Analytics、Dashboards Assistant、Alerting) が新たにサポートされました。1 つのコアプラグイン (Timeline) もこのリリースの一部として追加されました。さらに、OpenSearch 2.9 で導入された可視化用のモニターと検出器を構築する機能も、複数の OpenSearch クラスターの使用をサポートするようになりました。

## OpenSearch 2.15 を始める

最新バージョンの OpenSearch は[こちら](https://www.opensearch.org/downloads.html)からダウンロードでき、[OpenSearch Playground](https://playground.opensearch.org/app/home#/) で OpenSearch Dashboards をライブで体験できます。このリリースの詳細については、[リリースノート](https://github.com/opensearch-project/opensearch-build/blob/main/release-notes/opensearch-release-notes-2.15.0.md)と[ドキュメントリリースノート](https://github.com/opensearch-project/documentation-website/blob/main/release-notes/opensearch-documentation-release-notes-2.15.0.md)をご覧ください。このリリースに関するフィードバックは[コミュニティフォーラム](https://forum.opensearch.org/)でお待ちしています！
