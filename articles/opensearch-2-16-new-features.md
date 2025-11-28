---
title: "[翻訳] OpenSearch 2.16 の紹介"
emoji: "✨"
type: "tech"
topics: ["opensearch", "search", "vectorsearch", "security", "machinelearning"]
published: false
publication_name: "opensearch"
published_at: 2024-08-07
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/introducing-opensearch-2-16/

OpenSearch 2.16 が[リリース](https://opensearch.org/downloads.html)されました。検索と生成 AI アプリケーションの構築を容易にする拡張ツールキット、パフォーマンスと効率性のさらなる向上、使いやすさを改善するアップグレードが含まれています。[OpenSearch Playground](https://playground.opensearch.org/app/home) で OpenSearch Dashboards を使用して最新バージョンを試すことができます。このリリースの新機能の詳細については[リリースノート](https://github.com/opensearch-project/opensearch-build/blob/main/release-notes/opensearch-release-notes-2.16.0.md)をご覧ください。以下は OpenSearch 2.16 で活用できる新機能と更新された機能の一部です。

## 検索と機械学習

OpenSearch 2.16 では、アプリケーション開発を加速し、生成 AI ワークロードを実現するために、OpenSearch の**検索および機械学習 (ML)** ツールキットに多くの機能が追加されました。

### バイト精度ベクトル量子化のためのベクトル圧縮自動化による効率向上

OpenSearch 2.9 では、[Lucene](https://lucene.apache.org/) k-NN エンジンを使用して構築されたインデックスに対する[バイト量子化ベクトル](https://opensearch.org/docs/latest/search-plugins/knn/knn-vector-quantization/)のサポートが追加されました。この機能は、通常有利な検索精度のトレードオフを通じて、コストを削減しクエリレイテンシを低減できます。バイトベクトル量子化は、ベクトルを次元あたり 4 バイトから 1 バイトに圧縮することで機能します。これにより、メモリ要件が実質的に 4 分の 1 になり、クラスター運用コストも削減されます。また、クエリの実行に必要な計算が少なくなるため、クエリレイテンシが低下するという利点もあります。以前は、ユーザーはクラスター外でベクトルを前処理する必要がありましたが、このリリースでは、インデックス作成タスクの一部として OpenSearch がクラスター上でフル精度ベクトルをバイト量子化するように設定できます。FAISS k-NN エンジンでのこの機能のサポートは次のリリースで予定されています。

### ソート検索と分割検索プロセッサによる柔軟な検索パイプラインの構築

OpenSearch 2.16 では、検索パイプラインツールセットに[ソート検索プロセッサと分割検索プロセッサ](https://opensearch.org/docs/latest/search-plugins/search-pipelines/search-processors/)が追加されました。ソートプロセッサは検索パイプライン内で設定して検索レスポンスをソートでき、分割プロセッサは文字列を部分文字列の配列に分割するために使用されます。これらのプロセッサは、より多くの柔軟性とユースケースをサポートするために追加されました。例えば、ML 推論検索プロセッサと組み合わせて、カスタムランキングモデルを使用して結果を再スコアリングし、ソートプロセッサを使用して再ソートするリランキング検索パイプラインを作成できるようになりました。

### バイナリベクトルサポートによるベクトル検索ワークロードのコスト削減

このリリースでは、[バイナリベクトル](https://opensearch.org/docs/latest/field-types/supported-field-types/knn-vector/#binary-k-nn-vectors)のサポートが提供され、フル精度 32 ビットベクトルで 32 倍の圧縮が可能になりました。次元あたり 1 ビットでバイナリベクトルをインデックス化および取得する機能により、バイナリベクトルを出力する最新の ML モデルを活用し、OpenSearch のベクトル検索機能の可能性を最大限に引き出すことができます。この機能は、特に大きな次元のベクトル (768 次元以上) で高い再現率パフォーマンスを提供し、大規模なデプロイメントをより経済的かつ効率的にします。OpenSearch 2.16 では、バイナリベクトルのスコアリングのためのビット単位の距離測定を可能にするハミング距離サポートも導入されました。バイナリベクトルは、ベクトル検索の近似 k-NN と完全一致 k-NN の両方で使用できます。近似 k-NN 検索は最初に FAISS エンジンで利用可能です。

### 任意の ML モデルを OpenSearch AI ネイティブ API に統合して検索フローをエンリッチ

OpenSearch 2.14 では、AI コネクタフレームワークの機能強化により、ユーザーが任意の AI/ML プロバイダーを OpenSearch にネイティブに統合できるようになりました。これらのコネクタにより、ユーザーは AI プロバイダーに接続する ML 推論インジェストプロセッサを設定することで、Ingest API を通じてインジェストタスク内で AI エンリッチメントを作成できます。OpenSearch 2.16 では、同じ AI コネクタを通じて [ML 推論検索プロセッサ](https://opensearch.org/docs/latest/search-plugins/search-pipelines/ml-inference-search-request/)を設定することで、Search API を通じて検索フロー内でも AI エンリッチメントを有効にできます。

### AI コネクタのバッチ推論サポートによる ML 機能の拡張

このリリースには、インテグレーターがコネクタに[バッチ推論サポート](https://opensearch.org/docs/latest/ml-commons-plugin/api/model-apis/batch-predict/)を追加できるようにする AI コネクタフレームワークの機能強化が含まれています。以前は、AI コネクタはリアルタイムの同期 ML 推論ワークロードに限定されていました。この機能強化により、コネクタは大規模なデータセットでより効率的に非同期バッチ推論ジョブを実行できます。ユーザーは、Amazon SageMaker などのプロバイダーへのコネクタを通じてバッチジョブを実行するためのバッチ API 呼び出しを実行できるようになります。今後のリリースでは、OpenSearch はこれらのバッチ推論ジョブを OpenSearch インジェストタスクを通じて実行できる機能を提供する予定です。

## 使いやすさ

このリリースには、OpenSearch の**使いやすさ**を向上させるために設計されたツールも含まれています。

### アプリケーションベースの設定テンプレートによるユースケースに応じたパフォーマンス最適化

OpenSearch は、テキストおよび画像検索、オブザーバビリティ、ログ分析、セキュリティなど、幅広いユースケースに対応する多用途なツールセットを提供しています。この多用途性は、新しいユースケースのために OpenSearch をセットアップする際に、アプリケーション要件に合わせてインデックスを微調整するために時間のかかる作業が必要になる可能性があることを意味します。2.16 リリースでは、アプリケーションベースの設定テンプレートの導入により、新しいアプリケーションの最適化プロセスを高速化しました。これらのテンプレートは[インデックステンプレート](https://opensearch.org/docs/latest/im-plugin/index-templates/)機能と連携して、コンピューティングおよびストレージリソースのパフォーマンス、および Index State Management (ISM) による使いやすさのためにインデックスを調整するのを簡素化するデフォルト設定を提供します。

### より多くの OpenSearch Dashboards プラグインでの複数データソースへのアクセス

OpenSearch Dashboards 全体で[複数データソース](https://opensearch.org/docs/latest/dashboards/management/multi-data-sources/)をサポートする継続的な取り組みの一環として、OpenSearch 2.14 では 9 つの外部 Dashboards プラグインのサポートが追加されました。このリリースでは、OpenSearch クラスター間でデータを管理し、可視化を単一のダッシュボードに統合するのに役立つ、さらに多くのプラグインのサポートが追加されました。2 つの外部 Dashboards プラグイン (Notebooks と Snapshot) が新たにサポートされました。すべてのプラグインで、選択から互換性のないデータソースをフィルタリングするためのバージョンデカップリングがサポートされるようになりました。

## コスト、パフォーマンス、スケール

このリリースでは、OpenSearch デプロイメントの**コスト、パフォーマンス、スケール**の改善に焦点を当てた新機能も提供されています。範囲集計のための高速フィルター最適化の追加が含まれます。

### 範囲集計パフォーマンスの最大 100 倍の向上

最近のリリースでは、日付ヒストグラム集計の特殊なケースのパフォーマンスを向上させるための高速フィルター最適化が導入されました。OpenSearch 2.16 では、これらの最適化を一般的な[範囲集計](https://opensearch.org/docs/latest/aggregations/bucket/range/)にも適用できるようになりました。これらの更新により、NOAA ワークロードの単純な範囲集計で [100 倍以上のパフォーマンス向上](https://github.com/opensearch-project/OpenSearch/pull/13865#:~:text=0%20%7C%20%20%20%20%20%20%20%20%20%20%200%20%7C%20%20%20%20%20%20%20%20%20%20%200%20%7C%20%20%20%20%20%20%25%20%7C-,noaa,-%7C%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%2050th%20percentile%20latency)が実証されています。

## 安定性、可用性、回復力

このリリースでは、OpenSearch クラスターの**安定性、可用性、回復力**を向上させるためのアップデートが導入されています。クラスター管理に関するいくつかの更新が含まれます。

### クラスターマネージャーの最適化による大規模ワークロードのスケーリング

OpenSearch ユーザーは、大規模なワークロード全体でドメインをスケーリングする際に課題に直面することがあります。多くの場合、クラスターマネージャーがボトルネックの原因となります。このリリースでは、クラスターマネージャー API のネットワーク最適化、保留中のタスク処理のコンピューティング最適化、ルーティングテーブルの増分読み取り/書き込みなど、クラスターマネージャーにいくつかの更新が加えられました。その結果、クラスターマネージャーの負荷が軽減され、クラスターマネージャーがより多くのノードとシャードをサポートできるようになりました。さらに、OpenSearch のシャード割り当てのさらなる最適化により、大規模ドメインのスケーリングと運用のオーバーヘッドが削減されました。これらの更新により、ユーザーはより多くのノードとより大量のデータにスケールアップできるようになります。

## セキュリティ分析

このリリースには、OpenSearch のセキュリティ分析機能の大幅な拡張も含まれています。

### 潜在的なセキュリティ脅威への可視性の拡大

OpenSearch [セキュリティ分析](https://opensearch.org/platform/security-analytics/index.html)は、監視対象インフラストラクチャ全体で潜在的なセキュリティ脅威を検出、調査、分析するための 3,300 以上のパッケージ済みオープンソース Sigma ルールを備えた包括的なツールキットを提供します。新しいセキュリティ脅威が継続的に出現する中、ユーザーからは悪意のある活動を見つけるために外部の脅威インテリジェンスソースを使用したいという声が寄せられています。

このリリースでは、OpenSearch はすぐに使えるセキュリティ分析ソリューションの一部として[脅威インテリジェンス](https://opensearch.org/docs/latest/security-analytics/threat-intelligence/getting-started/)機能を追加しました。この機能により、ファイルをローカルにアップロードするか Amazon S3 バケットを参照することで、カスタマイズされた Structured Threat Information Expression (STIX) 準拠の脅威インテリジェンスフィードを使用できます。サポートされている悪意のある侵害指標 (IOC) タイプには、IPv4 アドレス、IPv6 アドレス、ドメイン、ファイルハッシュが含まれます。ユーザーはこの情報をデータに適用して、脅威がエスカレートする前に潜在的な脅威を見つけることができます。Sigma ルールによる脅威検出と組み合わせることで、この機能はセキュリティ脅威へのより包括的なビューを提供し、意思決定と修復をサポートするより深い洞察を提供します。

## CentOS7 の非推奨化

2024 年 6 月 30 日にサポート終了となった CentOS Linux 7 に関して、[2.12 で非推奨通知](https://github.com/opensearch-project/opensearch-build/blob/main/release-notes/opensearch-release-notes-2.12.0.md#deprecation-notice)を発行しました。CentOS Project が発行した公式[通知](https://blog.centos.org/2023/04/end-dates-are-coming-for-centos-stream-8-and-centos-linux-7/)に従い、OpenSearch Project も 2.16 リリースで継続的インテグレーションビルドイメージおよびサポート対象オペレーティングシステムとして [CentOS Linux 7 を非推奨](https://github.com/opensearch-project/opensearch-build/issues/4379)としています。OpenSearch の互換性のあるオペレーティングシステムについては、[オペレーティングシステムの互換性](https://opensearch.org/docs/latest/install-and-configure/install-opensearch/index/#operating-system-compatibility)ページをご覧ください。

## OpenSearch 2.16 を始める

本日のリリースは[ダウンロード可能](https://www.opensearch.org/downloads.html)で、[OpenSearch Playground](https://playground.opensearch.org/app/home#/) で体験できます。このリリースの詳細については、[リリースノート](https://github.com/opensearch-project/opensearch-build/blob/main/release-notes/opensearch-release-notes-2.16.0.md)と[ドキュメントリリースノート](https://github.com/opensearch-project/documentation-website/blob/main/release-notes/opensearch-documentation-release-notes-2.16.0.md)をご確認ください。このリリースに関するフィードバックは[コミュニティフォーラム](https://forum.opensearch.org/)でお気軽にお寄せください！
