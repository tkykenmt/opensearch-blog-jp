---
title: "[翻訳] OpenSearch 2.19 の新機能を探る"
emoji: "🚀"
type: "tech"
topics: ["opensearch", "search", "vectorsearch", "observability", "ai"]
published: true
published_at: 2025-02-11
publication_name: "opensearch"
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/explore-opensearch-2-19/

OpenSearch の最新バージョンは、検索とオブザーバビリティのユースケースの機能を拡張し、パフォーマンスと使いやすさを向上させ、機械学習 (ML) と生成 AI アプリケーション向けの多数の進歩を導入しています。OpenSearch 2.19 で利用可能なエキサイティングな機能のいくつかを確認しましょう。新機能の詳細については、[リリースノート](https://github.com/opensearch-project/opensearch-build/blob/main/release-notes/opensearch-release-notes-2.19.0.md) を参照してください。お好みの [OpenSearch ディストリビューションはこちら](https://opensearch.org/downloads.html) からダウンロードするか、[OpenSearch Playground](https://playground.opensearch.org/app/home) でデータ可視化ツールキットを使用して最新機能を探索できます。

## ベクトルデータベースと生成 AI

OpenSearch 2.19 には、より柔軟で高機能な ML 搭載および生成 AI アプリケーションを構築するための、OpenSearch のベクトルデータベースと ML ツールキットの更新が含まれています。

### 実験的な derived source for vectors でストレージを最大 60% 節約

このリリースでは、k-NN ベクトル用の derived source の実験的サポートが導入されています。`source` フィールドはドキュメントの JSON 表現にほぼ相当し、検索時の値の取得や再インデックスなどの操作に使用されます。derived source 機能は、これらのベクトルを JSON ソースから削除し、必要に応じて動的に注入します。2.19 では、この機能はフラットベクトルマッピング、オブジェクトフィールド、単一レベルのネストフィールドで動作し、最大 60% のストレージ節約を実証しています。ぜひ試して、[RFC](https://github.com/opensearch-project/k-NN/issues/2377) でフィードバックを共有してください。

### ベクトルワークロード用のプラガブルストレージの実装

OpenSearch 2.18 では、ベクトルデータ構造を読み取るための[プラガブルストア](https://opensearch.org/blog/enable-pluggable-storage-in-opensearch-vectordb/)を使用する機能が導入されました。このバージョンでは、ユーザーはこのサポートを拡張して、プラガブルストレージからの読み取りと書き込みの両方の操作を実行できるようになりました。`RemoteStore` ベースのディレクトリ実装を使用する OpenSearch ディストリビューションは、ベクトルワークロードと完全に互換性があります。詳細については、[この GitHub issue](https://github.com/opensearch-project/k-NN/issues/2033) を参照してください。

### Lucene エンジン用のバイナリベクトルでメモリとストレージ要件を削減

[バイナリベクトル](https://opensearch.org/docs/latest/field-types/supported-field-types/knn-vector/#binary-vectors)は FP32 ベクトルの効率的な代替手段を提供し、小規模なハードウェア構成で強力なパフォーマンスを維持しながら、メモリフットプリントとストレージ使用量を [90% 以上](https://github.com/opensearch-project/k-NN/issues/1857#issuecomment-2598998408) 削減できます。このリリースでは、既存の Faiss エンジンのバイナリベクトルサポートを補完する [Lucene バイナリベクトル](https://opensearch.org/docs/latest/search-plugins/knn/knn-index/#binary-vectors)が追加され、ベクトル検索アプリケーションにより大きな柔軟性を提供します。

### Faiss ベクトルエンジンでコサインベースの類似検索を適用

OpenSearch k-NN プラグインは、k-NN およびラジアル検索用の Faiss エンジンで[コサイン類似度](https://opensearch.org/docs/latest/search-plugins/knn/approximate-knn/)のサポートを導入し、コサイン距離に基づく類似検索を実行する OpenSearch の機能を強化しました。この改善により、ユーザーは手動でデータを正規化する必要なくコサイン類似検索を実行でき、プロセスを合理化してパフォーマンスを向上させます。この機能は、レコメンデーションシステム、不正検出、コンテンツベースの検索アプリケーションなど、さまざまなユースケースに利点を提供します。詳細と実装ガイドラインについては、[この GitHub issue](https://github.com/opensearch-project/k-NN/issues/2242) を参照してください。

### OpenSearch Dashboards でインジェストと検索パイプラインを使用してアプリケーションを構築

OpenSearch 2.19 の新機能として、[OpenSearch Flow](https://opensearch.org/docs/latest/automating-configurations/workflow-builder/) は、最新の AI 技術を活用したフローを作成することで、開発者がより速くイノベーションを起こすのを支援します。カスタムフローは、RAG やベクトル検索アプリケーションなど、さまざまなユースケースをサポートするために、より少ないコードで構成できます。OpenSearch Dashboards の OpenSearch Flow を使用すると、検索とインジェストパイプラインを反復的に構築でき、[OpenSearch Flow Framework プラグイン](https://opensearch.org/docs/latest/automating-configurations/index/)がバックグラウンドで構成とリソース管理の自動化を提供します。構築したソリューションに満足したら、[ワークフローテンプレート](https://opensearch.org/docs/latest/automating-configurations/workflow-templates/)をエクスポートして、異なるクラスターやデータソース間でリソースを再作成できます。

### ハイブリッド検索でのページネーションサポートで検索関連性を向上

[ハイブリッド検索](https://opensearch.org/docs/latest/search-plugins/hybrid-search/)は、キーワード検索やニューラル検索など、複数のクエリタイプを組み合わせて検索の関連性を向上させます。OpenSearch 2.19 では、ハイブリッド検索機能がいくつかの重要な改善で強化されました。新しい `pagination_depth` パラメータにより、大きな結果セットをより適切に管理でき、サブクエリごとに各シャードから取得される結果の最大数を指定することで、結果セットを小さなサブセットに分割できます。

### ML 推論検索でクエリを強化

OpenSearch 2.19 では、ML 推論検索リクエスト拡張が導入されています。この機能は、検索クエリの一部ではない追加の入力フィールドをユーザーが渡せるようにすることで、検索中に ML モデル予測を適用する際の制限に対処します。新しい `ml_inference` 検索拡張は、任意の検索クエリと一緒に使用でき、検索リクエストをさまざまなモデルに適応させるさまざまなモデル入力形式を含む柔軟なオブジェクトを提供します。

### Reciprocal Rank Fusion でハイブリッド検索結果を強化

このリリースでは、[Reciprocal Rank Fusion](https://opensearch.org/docs/latest/search-plugins/search-pipelines/score-ranker-processor/) (RRF) が追加されました。これは、結果の組み合わせに対する代替アプローチを提供する新しいランクベースの検索プロセッサです。RRF プロセッサは、スコアではなくドキュメントの位置に焦点を当て、より堅牢で偏りのないランキングを提供します。この機能は、異なるサブクエリからのスケーリングされたスコアを組み合わせる際に発生する可能性のあるバイアスを軽減することを目的としています。各クエリに対するドキュメントのランクの逆数に基づいて各ドキュメントをスコアリングすることでこれを達成します。これらの逆数ランクが合計されて最終的な統一ランキングが作成され、よりバランスの取れた効果的な結果セットが保証されます。

### ハイブリッド検索のデバッグとトラブルシューティングを改善

[ハイブリッド検索](https://opensearch.org/docs/latest/search-plugins/hybrid-search/)では、スコアの正規化と組み合わせのプロセスが実際のクエリ実行とスコア収集から分離され、検索パイプラインプロセッサで実行されるため、`explain` パラメータなどのデバッグおよびトラブルシューティングツールの使用が複雑になります。OpenSearch 2.19 では、`hybrid_score_explanation` レスポンスプロセッサのサポートが追加されました。これにより、正規化と組み合わせの結果が返される検索レスポンスに追加され、スコアとランクの正規化プロセスを理解するためのデバッグツールが提供されます。

## 検索

このリリースでは、検索操作を強化する新機能も提供されています。

### 新しい `template` クエリタイプで検索操作を改善

OpenSearch 2.19 では、プレースホルダー変数を含む検索クエリを作成するための[テンプレートクエリ](https://opensearch.org/docs/latest/query-dsl/specialized/template/)を使用できます。検索リクエストを送信すると、これらのプレースホルダーは検索リクエストプロセッサが値を割り当てるまで未解決のままです。このアプローチは、初期検索リクエストに検索プロセッサを使用して実行時に変換または生成する必要があるデータが含まれている場合に特に有用です。検索プロセッサの機能を活用することで、テンプレートクエリはより柔軟で効率的かつ安全な検索操作を可能にします。

### 実験的な star-tree アグリゲーションでクエリパフォーマンスを向上しキャッシュ使用率を削減

このリリースの実験的機能である [Star-tree アグリゲーション](https://opensearch.org/docs/latest/search-plugins/star-tree-index/)は、メトリクスアグリゲーションとメトリクスアグリゲーションを伴う日付ヒストグラムのサポートにより、検索パフォーマンスに大幅な向上を提供します。ユーザーは、キーワードフィールドと数値フィールド (unsigned long と scaled float フィールドを除く) で `term`、`terms`、`range` クエリを使用して、アグリゲーション結果をフィルタリングする検索クエリを適用できます。このリリースには、star-tree 検索パフォーマンスを向上させるためのクエリ内の複数の terms に対するバイナリ検索の最適化も含まれています。これらの更新により、[最大 100 倍のクエリ削減と 30 倍のキャッシュ使用率低下](https://github.com/opensearch-project/OpenSearch/pull/16674#issuecomment-2643981712)を実証する印象的なパフォーマンス改善が提供されます。

## オブザーバビリティとログ分析

このリリースでは、オブザーバビリティとログ分析のユースケースに対する OpenSearch の機能が拡張されています。

### 新しい機能基準で異常検出を微調整

OpenSearch 2.19 では、[異常](https://opensearch.org/docs/latest/observing-your-data/ad/index/)と見なされる動作を定義する際に、より多くの基準を追加するオプションが提供されます。各検出器機能を、その機能のデータパターンのスパイクまたはディップのいずれかを識別するように構成できるようになりました。例えば、フリート全体の CPU データを監視している場合、通常の使用率の低下を無視しながら、実際の値が予想値よりも高い潜在的な問題を示す可能性のある CPU 使用率の異常なスパイクの検出にのみ焦点を当てるように機能を構成できるようになりました。

### より豊富なダッシュボード可視化のために異常検出値を変換

OpenSearch の[異常検出](https://opensearch.org/docs/latest/observing-your-data/ad/index/)では、多くの値がフラット化されていないため、ダッシュボードで表示するのが困難です。例えば、エンティティ値はネストされたオブジェクトであり、機能は配列です。異常検出の使いやすさを向上させるために、[フラット化された結果](https://opensearch.org/docs/latest/observing-your-data/ad/result-mapping/)を格納するための別のインデックスが導入されました。このインデックスは、ネストされたエンティティ値と機能配列を構造化された形式に変換するスクリプトプロセッサを持つインジェストパイプラインを使用して入力されます。このアーキテクチャの強化により、機能を名前で参照でき、カテゴリフィールドが `terms` アグリゲーションを適切にサポートするようになり、クエリ効率が大幅に向上し、ダッシュボードの可視化が改善されます。

## 使いやすさ

このリリースでは、OpenSearch Dashboards を使用して構成、管理、インサイトの発見方法を強化するために設計された新機能も導入されています。

### クエリインサイトダッシュボードで検索パフォーマンス監視を改善

OpenSearch 2.19 では、[クエリインサイトダッシュボード](https://opensearch.org/docs/latest/observing-your-data/query-insights/query-insights-dashboard/)が導入されました。これは、Query Insights プラグインによって収集された[トップ N クエリ](https://opensearch.org/docs/latest/observing-your-data/query-insights/top-n-queries/)を監視および分析できる新しいビジュアルインターフェースです。トップクエリをリストし、履歴データを統合する概要ページ、詳細分析のためのドリルダウンビュー、構成と管理を合理化する構成ビューを提供します。新しい可視化機能をサポートするために、クエリインサイトキャッシュパフォーマンスを監視するための Health API のフィールドタイプキャッシュ統計、UI クエリ取得を合理化するための ID によるトップクエリ取得用の新しい API、構成可能なデータ有効期限を持つトップ N クエリ保持管理など、いくつかの新しいバックエンド強化が含まれています。これらの機能を組み合わせることで、OpenSearch のクエリオブザーバビリティが強化され、検索パフォーマンス監視がよりスケーラブルで効率的になります。

### Discover の実験的ビューの強化を探る

[OpenSearch 2.18](https://opensearch.org/blog/get-started-with-opensearch-2-18/) では、クエリエクスペリエンスを強化しカスタマイズを向上させるために設計された新しいルックアンドフィールを含む、[Discover](https://opensearch.org/docs/latest/dashboards/discover/index-discover/) の実験的ビューが導入されました。このインターフェースにより、アナリストは未使用のセクションを折りたたんでワークスペースを合理化できます。過去 1 年間、Log Explorer の Piped Processing Language (PPL) (オブザーバビリティアプリケーション用) や Query Workbench の SQL など、OpenSearch のクエリインターフェース全体でユーザーから貴重なフィードバックを収集してきました。これに応えて、Dashboards Query Language (DQL) と Lucene に加えて、PPL と SQL をクエリオプションとして Discover に追加し、アナリストが好みのクエリ言語を使用できるようにしています。また、データセレクターを改善し、非常に要望の多かったオートコンプリート機能を追加しました。新しいエクスペリエンスは機能フラグの背後で利用可能であり、**Dashboards Management** に移動し、**Advanced Settings** を選択し、**Enable query enhancements** を ON に切り替えることで有効にできます。新しい Discover エクスペリエンスがデフォルトになる 3.0 だけでなく、2.21 まで既存の Discover エクスペリエンスを引き続きサポートします。このインターフェースを一般提供する前に、コミュニティの入力を収集し続けているため、[この機能に関するフィードバック](https://github.com/opensearch-project/OpenSearch-Dashboards/issues/8813)を歓迎します。

## セキュリティ

OpenSearch 2.19 には、OpenSearch クラスターのセキュリティを強化する更新が含まれています。

### 新しいプラグインセキュリティアプローチでシステムインデックス保護を強化

このリリースでは、プラグインが OpenSearch システムインデックスに格納されたメタデータにアクセスできるようにする新しいメカニズムが導入されています。OpenSearch は、さまざまなユースケースをサポートするためにコア機能を拡張する豊富なプラグインの選択肢を提供しています。時折、これらのプラグインは、データを永続化するためにシステムインデックスへの読み取りと書き込みなど、通常のユーザーには禁止されている特権操作を実行する必要があります。現在のメカニズムは低レベル API の呼び出しを含み、プラグイン開発者がリクエスト処理中にセキュリティ情報がどのように転送されるかを理解する必要があります。[この issue](https://github.com/opensearch-project/security/issues/4439) で詳述されている新しいアプローチは、プラグインにランタイムに必要な情報を提供するための、より安全で直感的な方法を提供します。

## コスト、パフォーマンス、スケーラビリティ

このリリースでは、OpenSearch デプロイメントのコスト、パフォーマンス、スケーラビリティを向上させるために設計されたいくつかの新機能も導入されています。

### 権限評価パフォーマンスの改善

このリリースでは、OpenSearch Security は、現在線形時間で実行されている権限評価を定数時間で実行できるようにする新しいデータ構造を導入し、クラスター内のロールとインデックスの数を増やしています。この最適化により、OpenSearch Security は権限評価時のルックアップに最適化された事前計算されたデータ構造を活用します。このリリースには、[フィールドレベルセキュリティ](https://opensearch.org/docs/latest/security/access-control/field-level-security/)、[ドキュメントレベルセキュリティ](https://opensearch.org/docs/latest/security/access-control/document-level-security/)、または[フィールドマスキング](https://opensearch.org/docs/latest/security/access-control/field-masking/)に関連する改善は含まれておらず、これらは将来のリリースで計画されています。OpenSearch ソリューションプロバイダーの [Eliatra](https://opensearch.org/solutionsProviders/eliatra.html) は、これらのパフォーマンス改善を[こちら](https://eliatra.com/blog/performance-improvements-for-the-access-control-layer-of-opensearch/)と[こちら](https://eliatra.com/blog/performance-improvements-for-the-access-control-layer-of-opensearch-2/)の記事で詳述しています。

### ビットマップフィルタリングでクエリ効率を最適化しコストを削減

バージョン 2.17 で導入された[ビットマップフィルタリング](https://opensearch.org/docs/latest/query-dsl/term/terms/#bitmap-filtering)は、ビットマップを使用してクエリ対象の terms を表すことで、数値フィールドの効率的なフィルタリングを可能にします。このリリースでは、より良いパフォーマンスのために数値フィールドのインデックス構造を使用する新しいビットマップクエリを通じて、この機能が改善されています。さらに、このリリースではコストベースのクエリ最適化も導入されています。ビットマップフィルタリングが Boolean クエリ内で使用される場合、OpenSearch は各アプローチのコストのリアルタイム推定に基づいて、新しいインデックスベースのクエリまたは既存のドキュメント値ベースのクエリを自動的に選択します。

### 実験的なディスク階層リクエストキャッシュのパフォーマンスを向上

OpenSearch 2.19 では、実験的な[ディスク階層リクエストキャッシュ](https://opensearch.org/docs/latest/search-plugins/caching/tiered-cache/)を複数のパーティションに分割することで、パフォーマンスが改善されています。各パーティションは独自の読み取り/書き込みロックで保護されています。これにより、複数の同時リーダーが競合なしにデータにアクセスでき、複数のライターが同時に操作できるため、書き込みスループットが向上します。デフォルトでは、パーティション数は利用可能な CPU コアに基づいて決定されますが、ユーザーがカスタマイズすることもできます。

## 非推奨のお知らせ

### Ubuntu Linux 20.04 のサポート非推奨

OpenSearch と OpenSearch Dashboards は、Ubuntu Linux 20.04 が 2025 年 4 月に標準サポートの終了を迎えるため (Canonical Ubuntu からの[このお知らせ](https://ubuntu.com/blog/ubuntu-20-04-lts-end-of-life-standard-support-is-coming-to-an-end-heres-how-to-prepare)を参照)、今後のバージョンで継続的インテグレーションビルドイメージおよびサポート対象オペレーティングシステムとしての Ubuntu Linux 20.04 のサポートを非推奨にすることにご注意ください。互換性のあるオペレーティングシステムのリストについては、[こちら](https://opensearch.org/docs/latest/install-and-configure/os-comp/)を参照してください。

### OpenSearch Dashboards での Amazon Linux 2 のサポート非推奨

OpenSearch Dashboards は、Node.js 18 が 2025 年 4 月にサポート終了を迎え (nodejs.org からの[このお知らせ](https://nodejs.org/en/blog/announcements/v18-release-announce)を参照)、新しいバージョンの Node.js LTS バージョン (20+) が Amazon Linux 2 でのランタイムをサポートしないため、今後のバージョンで継続的インテグレーションビルドイメージおよびサポート対象オペレーティングシステムとしての Amazon Linux 2 のサポートを非推奨にすることにご注意ください。互換性のあるオペレーティングシステムのリストについては、[こちら](https://opensearch.org/docs/latest/install-and-configure/os-comp/)を参照してください。

### OpenSearch 3.0.0 での機能とプラグインのサポート非推奨

OpenSearch と OpenSearch Dashboards は、[OpenSearch 3.0.0](https://github.com/opensearch-project/opensearch-build/issues/3747) で以下の機能とプラグインのサポートを非推奨にすることにご注意ください。

* [Performance-Analyzer-Rca](https://github.com/opensearch-project/performance-analyzer-rca/issues/591): [Telemetry プラグイン](https://github.com/opensearch-project/performance-analyzer/issues/585)に置き換えられます。
* [Dashboards-Visualizations](https://github.com/opensearch-project/dashboards-visualizations/issues/430) (ganttCharts): プラグインは OpenSearch Dashboards バンドルアーティファクトの一部として削除されます。
* [Dashboards-Observability](https://github.com/opensearch-project/dashboards-observability/issues/2311): オブザーバビリティインデックスからのレガシーノートブックのサポートが削除されます。
* [SQL](https://github.com/opensearch-project/sql/issues/3248): OpenSearch 3.0.0 では、OpenSearch DSL 形式といくつかの設定が非推奨になり、SparkSQL コネクタが削除され、SQL での DELETE ステートメントサポートが削除されます。
* [k-NN](https://github.com/opensearch-project/k-NN/issues/2396): OpenSearch 3.0.0 では NMSLIB エンジンが非推奨になります。ユーザーは代わりに Faiss または Lucene エンジンを使用することをお勧めします。

バージョン 3.0.0 での破壊的変更と非推奨/削除された機能の詳細については、[メタ issue](https://github.com/opensearch-project/opensearch-build/issues/5243) の詳細を参照してください。

### OpenSearch 2.19 を始める

OpenSearch の最新バージョンは[こちら](https://www.opensearch.org/downloads.html)からダウンロードでき、[OpenSearch Playground](https://playground.opensearch.org/app/home#/) で OpenSearch Dashboards をライブで探索できます。このリリースの詳細については、[リリースノート](https://github.com/opensearch-project/opensearch-build/blob/main/release-notes/opensearch-release-notes-2.19.0.md)と[ドキュメントリリースノート](https://github.com/opensearch-project/documentation-website/blob/main/release-notes/opensearch-documentation-release-notes-2.19.0.md)をご確認ください。このリリースに関するフィードバックをお待ちしています。[コミュニティフォーラム](https://forum.opensearch.org/)でご意見をお聞かせください。
