---
title: "[翻訳] OpenSearch 3.6 のご紹介"
emoji: "🔍"
type: "tech"
topics: ["opensearch", "検索", "オブザーバビリティ", "AI", "ベクトル検索"]
publication_name: "opensearch"
published: true
published_at: 2026-04-07
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/introducing-opensearch-3-6/

## エージェント駆動の検索とオブザーバビリティで開発とディスカバリーを効率化

[最新バージョンの OpenSearch](https://opensearch.org/downloads/) には、ビルド、デプロイ、結果の提供を高速化するためのエージェント駆動ツールが多数含まれています。本番環境対応の検索アプリケーションの開発でも、完全なオープンソースのオブザーバビリティスタックの立ち上げでも、OpenSearch 3.6 を使えば数分で実現できます。OpenSearch 3.6 でサポートされる新機能は以下のとおりです。

- エージェントガイドのワークフローによる検索アプリケーション開発の自動化
- 1 つのコマンドでフルスタックオブザーバビリティソリューションを起動
- 自然言語インターフェースによる検索関連性チューニングの自動化
- 分散アプリケーション向けのリアルタイム Application Performance Monitoring と根本原因分析のデプロイ

これらの機能や OpenSearch 3.6 のその他の進化について詳しくは以下をお読みください。新機能の包括的な一覧については[リリースノート](https://github.com/opensearch-project/opensearch-build/blob/main/release-notes/opensearch-release-notes-3.6.0.md)を参照してください。

## 検索のモダナイゼーション

### OpenSearch の専門知識がなくても、数分で完全な検索アプリケーションを構築

[OpenSearch Launchpad](https://opensearch.org/blog/introducing-opensearch-launchpad-from-requirements-to-a-running-search-application-in-minutes/) を使えば、検索ソリューション構築の複雑な作業を、ガイド付きの AI 駆動エクスペリエンスにより数時間〜数日から数分に短縮できます。従来、検索アプリケーションの開発には、適切な検索戦略の選択、インフラストラクチャのプロビジョニング、機械学習 (ML) モデルとパイプラインの設定、使いやすいインターフェースの作成など、複数の領域にわたる深い専門知識が必要でした。これらはすべて設計を検証する前に行う必要がありました。OpenSearch Launchpad は、サンプルドキュメントを分析し、会話を通じて好みを収集し、最適なアーキテクチャと動作する UI を備えた完全なローカルセットアップを自動的にプロビジョニングするインテリジェントエージェントにより、この障壁を取り除きます。Launchpad はセマンティックエンコーディングからクラスター設定まで、あらゆる技術的な判断を処理するため、差別化された検索エクスペリエンスの創出に集中できます。

OpenSearch Launchpad は [OpenSearch Agent Skills](https://github.com/opensearch-project/opensearch-agent-skills/) で利用可能な最初のスキルであり、今後数週間でさらに多くのスキルがリリースされる予定です。Model Context Protocol (MCP) ツールを通じて Claude Code、Cursor、Kiro などの IDE にネイティブに統合されるこれらのスキルにより、使い慣れたインターフェースとワークフローから OpenSearch を活用したアプリケーションを素早く構築・デプロイできます。

### エージェント駆動の関連性チューニングで検索品質を自動化

3.6 リリースで実験的ツールとして導入された [OpenSearch Relevance Agent](https://docs.opensearch.org/latest/search-plugins/search-relevance/relevance-agent/) を使えば、検索関連性チューニングを集中的な専門家主導のプロセスから、あらゆる開発者がアクセスできる自動化されたワークフローに変換できます。OpenSearch Dashboards に統合された高度なマルチエージェントシステムを通じて、Relevance Agent はユーザー行動シグナルを継続的に分析し、データ駆動の仮説を生成し、厳密なオフライン評価を通じて改善を検証します。これらはすべて自然言語の会話で行えます。このツールは 3 つの専門サブエージェント (User Behavior Analysis、Hypothesis Generator、Evaluator) を適用し、関連性のギャップの診断から検索フィールドの改善やブースト関数のチューニングなどの DSL レベルの最適化の実行まで、検索改善サイクル全体をオーケストレーションします。人間によるコントロールを維持しながら、最適化サイクルを数週間から数時間に短縮します。

[OpenSearch Relevance Agent](https://docs.opensearch.org/latest/search-plugins/search-relevance/relevance-agent/) は、新しい [OpenSearch Agent Server](https://github.com/opensearch-project/opensearch-agent-server) によってサポートされています。これは実験的なマルチエージェントオーケストレーションプラットフォームであり、OpenSearch および OpenSearch Dashboards と連携する特化型 AI エージェントを開発者が構築できるようにします。

### エージェント作成の簡素化と入力の標準化

OpenSearch 3.6 は AI エージェントの構築方法を効率化します。実験的な[統合エージェント登録 API](https://docs.opensearch.org/latest/ml-commons-plugin/api/agent-apis/register-agent/#unified-agent-registration) は、コネクタの作成、モデルの登録、エージェントの設定、パラメータのマッピングという 4 つの手動ステップを、シンプルなモデルブロックからコネクタとモデルの作成を自動的に処理する単一の API コールに統合します。実験的な [conversational_v2](https://docs.opensearch.org/latest/ml-commons-plugin/agents-tools/agents/conversational/) エージェントタイプは、プレーンテキスト、マルチモーダルコンテンツブロック (画像、動画、ドキュメント)、完全なメッセージベースの会話履歴をサポートする標準化された入力インターフェースを導入します。カスタムコネクタの設定は不要です。レスポンスはトークン使用量メトリクスを含む標準化された出力フォーマットに従います。この標準は今後のリリースですべてのエージェントタイプに拡張される予定です。

### より堅牢なエージェント型検索アプリケーションの構築

OpenSearch 3.6 には、以下を含むいくつかの[エージェント型検索](https://docs.opensearch.org/latest/vector-search/ai-search/agentic-search/index/)の機能強化が含まれています。

- **エイリアスサポート** – より柔軟なクエリ設定のために、特定のインデックス名に加えてインデックスエイリアスを参照できます。
- **埋め込みモデル設定** – 実行時にニューラルクエリを有効にするために、エージェント型クエリトランスレータプロセッサを通じて埋め込みモデル ID を直接設定できます。
- **フォールバッククエリ** – プライマリのエージェント型クエリが失敗した場合や結果が返されない場合のバックアップクエリを設定できます。
- **リランキング** – リランキングモデルを使用して取得結果を並べ替え、関連性と精度を向上させます。
- **エージェントメモリ** – 以前のインタラクションのコンテキストを保持し、会話型でコンテキストを考慮した検索エクスペリエンスを実現します。

### 1 ビットスカラー量子化でベクトル検索のパフォーマンスを向上し、ストレージ効率を最大化

OpenSearch 3.6 は [Faiss](https://docs.opensearch.org/latest/vector-search/optimizing-storage/faiss-scalar-quantization/) と [Lucene](https://docs.opensearch.org/latest/vector-search/optimizing-storage/lucene-scalar-quantization/) の両エンジンで 1 ビットスカラー量子化 (SQ) を確立し、パフォーマンスを犠牲にすることなく最大のストレージ効率を必要とするユーザー向けにストレージリソースを最適化します。このアップデートにより、Faiss での 1 ビットスカラー量子化が 32 倍圧縮のデフォルトとして確立され、既存のバイナリ方式と比較して 24% 高いリコールと 15% 低いレイテンシーを実現します。Lucene では、1 ビット SQ により初めて 32 倍圧縮が可能になり、量子化されたベクトル上で近似および正確な k-NN 検索の両方を直接実行できます。これはメタデータの多いユースケースに特に効果的で、複雑なフィルターが適用された場合でも高速かつ低メモリのスコアリングが可能です。

### Faiss 量子化の最適化でレイテンシーを 40% 削減

OpenSearch 3.6 は Faiss 量子化インデックスの最適化を導入し、グラフファイルから量子化されたフラットベクトルを直接活用することで検索オーバーヘッドを大幅に削減します。以前は FP32 フラットベクトルを使用すると「量子化税」が発生していました。これは検索プロセス中にベクトルを量子化するために必要な追加の計算ステップです。グラフファイル内にすでに保存されている事前量子化されたベクトルを利用することで、この冗長なステップが排除され、量子化インデックス検索のレイテンシーが 40% 削減されます。

### ベクトルインデックスのメタデータ圧縮でストレージを削減

このリリースでは、ベクトルと並行して [Zstandard (zstd) 圧縮](https://docs.opensearch.org/latest/im-plugin/index-codecs/)を導入し、大幅なストレージ最適化を実現します。メタデータ圧縮をターゲットにすることで、補助データの全体的なディスクフットプリントを削減し、検索と取得に必要な高速アクセスを損なうことなく、同じハードウェアでより多くのメタデータリッチなベクトルを保存できます。

### プリフェッチでベクトル検索のレイテンシーを半減

スループットをさらに向上させるため、このリリースでは ANN (近似最近傍) と正確な検索の両方のユースケースにプリフェッチ機能を導入します。プリフェッチは、CPU が必要とする前に距離計算に必要な特定のベクトルをメモリにプロアクティブにロードします。これにより、ディスクやより低速なメモリ階層からのデータ待ちに費やされるアイドルサイクルが最小化され、CPU 使用率が向上し、メモリ制約のある環境で最大 2 倍の検索レイテンシー改善を実現します。

### Search Relevance Workbench の改善で関連性チューニングを効率化

[Search Relevance Workbench](https://docs.opensearch.org/latest/search-plugins/search-relevance/using-search-relevance-workbench/) は OpenSearch 3.6 で多くの使いやすさの向上を実現しています。複数のデータソースに対して実験を実行できるようになり、オプションの名前と説明フィールドの追加により実験の整理が容易になりました。プレーンテキスト、キーバリュー、NDJSON フォーマットを使用して UI 上で直接クエリセットを作成でき、外部でのクエリセットのエクスポートや編集が不要になりました。新しいフライアウトとツールチップによりナビゲーションも強化されています。3 つの新しいメトリクスにより、さまざまな検索シナリオでの品質をより適切に評価できます。Recall@K、Mean Reciprocal Rank (MRR)、Discounted Cumulative Gain (DCG@K) に加え、Precision@K などの既存のバイナリ評価での非バイナリ評価の処理も改善されています。

## オブザーバビリティと分析

### 1 つのコマンドでフルスタックオブザーバビリティをデプロイ

[OpenSearch Observability Stack](https://opensearch.org/platform/observability-stack/) は、マイクロサービス、Web アプリケーション、AI エージェントを監視するためのオープンソースの OpenTelemetry ネイティブオブザーバビリティプラットフォームです。OpenTelemetry Collector、Data Prepper、OpenSearch、Prometheus、OpenSearch Dashboards を単一の事前設定済みデプロイメントにバンドルし、docker compose またはインタラクティブインストーラーで 1 つのコマンドで起動できます。このスタックは、自動生成されたサービスマップと RED メトリクスによる分散トレーシング、ログ分析、PromQL サポート付きの Prometheus 互換メトリクス、そして OpenTelemetry GenAI セマンティック規約を使用した実行グラフの可視化、LLM コールの追跡、トークン使用量の監視を含むファーストクラスの AI エージェントオブザーバビリティを提供します。このスタックには、マルチエージェントトラベルプランナーなどのサンプルサービスが含まれており、ユーザーはすぐに機能を探索できます。

OpenSearch Observability Stack には [Claude Code プラグイン](https://observability.opensearch.org/docs/claude-code/)も含まれており、開発者はターミナルや IDE から自然言語を使用してトレース、ログ、メトリクスを直接クエリおよび調査できます。PPL クエリ、PromQL メトリクス、クロスシグナル相関、モニタリングのための事前構築済みスキルが用意されています。

### Application Performance Monitoring で分散アプリケーションを追跡・分析

OpenSearch 3.6 は [Application Performance Monitoring](https://docs.opensearch.org/latest/observing-your-data/apm/) (APM) を導入します。これは分散アプリケーションのリアルタイム監視のための新しいオブザーバビリティ機能です。APM は、OpenTelemetry と Data Prepper パイプラインを活用した RED メトリクス (Rate、Errors、Duration) と自動生成されたサービストポロジーマップを組み合わせます。主な機能には、オペレーションごとおよび依存関係のパフォーマンスブレークダウンを備えた一元化されたサービスカタログ、サービスメトリクスから関連するトレースやログにドリルダウンして根本原因を分析するためのコンテキスト内相関が含まれます。これらはすべて OpenSearch Dashboards の Observability ワークスペースからアクセスできます。インタラクティブなアプリケーショントポロジーマップは、トレースデータから有向グラフを自動生成し、サービスをヘルスコード付きノードとして表示し、通信パターンを示す方向付きエッジを表示します。

![Application monitoring services catalog showing service list with RED metrics](/images/introducing-opensearch-3-6/697fbdb3b62e.png)
*RED メトリクス付きのサービスリストを表示するアプリケーション監視サービスカタログ*

リソース属性 (SDK 言語やチームなど) でサービスをグループ化したり、エラー率やフォールト率のしきい値でフィルタリングしたり、任意のノードを選択してリクエスト、レイテンシー、エラーの詳細な時系列チャートを表示したりできます。関連するトレースやログへの直接ナビゲーションにより、根本原因の調査が可能です。

### Agent Traces で生成 AI アプリケーションを監視

OpenSearch 3.6 は生成 AI アプリケーションを監視するための [Agent Traces](https://docs.opensearch.org/latest/observing-your-data/agent-traces/agent-tracing/) を導入します。OpenTelemetry ベースのインストルメンテーションを使用して、AI スタック全体のエージェント呼び出し、LLM コール、ツール実行、取得操作をトレースします。Python SDK は、OpenAI、Anthropic、Amazon Bedrock、LangChain、LlamaIndex を含むさまざまなプロバイダー向けのデコレータ、エンリッチメント関数、自動インストルメンテーションを提供し、Strands Agents、LangGraph、CrewAI などのフレームワークの組み込みサポートも備えています。OpenSearch Dashboards では、Agent Traces プラグインが実行フローをインタラクティブな DAG グラフ、階層的なトレースツリー、ガントスタイルのタイムラインとして描画し、同期ビュー、トークン使用量の追跡、スパンレベルの詳細を提供して、本番環境での AI エージェントのデバッグと最適化を支援します。

![Agent trace map showing path of an agent and its subsequent API and LLM calls](/images/introducing-opensearch-3-6/279f32093e33.png)
*エージェントとその後続の API および LLM コールのパスを示すエージェントトレースマップ*

### 新しい PPL コマンドと機能強化でクエリを強化

OpenSearch 3.6 は、より強力な PPL クエリ機能のためのさまざまなアップデートを提供します。

- **外部統合** – 新しい統合クエリライブラリにより、Apache Spark、CLI ツール、カスタマーアプリケーションなどのサードパーティツールが、OpenSearch プラグインランタイムに依存せずに SQL および PPL クエリを Calcite 論理プランにパースできます。新しい文法バンドルはバージョン対応の ANTLR メタデータを提供し、サーバーコールなしでダウンストリームのクライアントサイドオートコンプリートを可能にします。
- **ハイライトサポート** – 検索結果のハイライトにより、設定可能な pre_tags と post_tags を持つ新しい highlight API パラメータを通じて、datarows と並んでトップレベルの highlights 配列でマッチを返すことができます。この実装はシンプルな配列フォーマットと OpenSearch Dashboards のワークフローをサポートします。
- **spath の自動抽出モード** – 明示的なフィールド名なしで JSON や構造化データからフィールドを自動的に検出・抽出し、半構造化ログデータの分析を簡素化します。このコマンドは、柔軟なデータエンリッチメントパイプラインのために appendcol、appendpipe、multisearch とも統合されます。
- **graphlookup コマンド** – 幅優先探索を使用した再帰的なグラフ走査を複数の走査モードで実行できるようになりました。開始ノードが既知の場合、先行する source コマンドなしでトップレベルコマンドとして使用できます。
- **クエリのキャンセルとタイムアウト** – Tasks API を通じて実行中のクエリをキャンセルし、自動タイムアウトを設定して暴走クエリによるクラスターリソースの枯渇を防止し、システムの安定性を向上させます。

## スケーラビリティとレジリエンシー

### ユーザーおよびチームベースのアクセス制御でクエリデバッグを強化

新しい search.insights.top_queries.filter_by_mode により、マルチテナント環境でデータプライバシーを維持しながら、管理者権限を必要とせずにセルフサービスのクエリデバッグが可能になります。この新しい設定は、ユーザー ID またはチームメンバーシップに基づいて[クエリインサイト](https://docs.opensearch.org/latest/observing-your-data/query-insights/index/)の可視性を決定します。username モードではユーザーは自分のクエリのみを表示でき、backend_roles モードでは少なくとも 1 つのバックエンドロールを共有するユーザーのクエリを表示できます。フィルタリングはインメモリデータと履歴データの両方に適用され、all_access ロールを持つ管理者は常に完全な可視性を保持します。

### 自動推奨によるクエリインサイトの改善

新しい[クエリインサイト](https://docs.opensearch.org/latest/observing-your-data/query-insights/index/)推奨エンジンは、上位 N クエリを分析し、問題を特定してソリューションを提案できます。このエンジンはクエリ構造とインデックスメタデータを検査してアンチパターンを検出し、レイテンシー、CPU、メモリ、正確性の各次元への推定影響と信頼度スコアを含む具体的な推奨事項を生成します。推奨事項は検索パスの外で非同期に生成されるため、クエリパフォーマンスへの影響はありません。特定のワークロード向けのカスタムルールもサポートされています。

### キャッシュレイヤーで短命なクエリを観測

[クエリインサイト](https://docs.opensearch.org/latest/observing-your-data/query-insights/index/)は、Live Queries API 向けの完了済みクエリキャッシュレイヤーをサポートするようになりました。これにより、アクティブなクエリと並んで最近完了したクエリを取得でき、通常は見逃されてしまう短命なクエリの観測に最適です。この API は 2 つの新しいクエリパラメータを導入します。Workload Management グループでフィルタリングするための wlmGroupId と、最近完了したクエリを含めるための use_finished_cache です。キャッシュはオンデマンドでアクティブ化され、設定可能なアイドル期間後に自動的に非アクティブ化される動的ライフサイクルモデルに従い、リソースを節約します。再構成されたレスポンスモデルは、トップレベルのサマリー、コーディネータータスク、詳細なシャードタスクのブレークダウンを含む階層ビューを提供し、リアルタイムと履歴のインサイト間の相関のために ID の継続性と Top Queries データへのリンクを備えています。

### 上位 N クエリのリモートストレージアクセス

クエリインサイトでは、リモートリポジトリエクスポーターを通じて[上位 N クエリ](https://docs.opensearch.org/latest/observing-your-data/query-insights/top-n-queries/)データをリモート Blob ストアリポジトリに移動できるようになりました。これにより、既存のローカルインデックスエクスポーターとは独立した、コスト効率の高い長期ストレージオプションが提供されます。エクスポートされたデータはタイムスタンプで整理された JSON ファイルとして書き込まれ、データ保持は OpenSearch ではなくバケット設定で管理されます。リモートエクスポーターは現在 Amazon S3 リポジトリをサポートしています。セットアップについては[ドキュメント](https://docs.opensearch.org/latest/observing-your-data/query-insights/top-n-queries/)を参照してください。

### 上位 N クエリにビジュアライゼーションを追加

[上位 N クエリ](https://docs.opensearch.org/latest/observing-your-data/query-insights/top-n-queries/)ページに Stats & Visualizations パネルが追加され、メトリクスごとの P90 および P99 パーセンタイル統計が表示されるようになりました。インタラクティブな円グラフとテーブルを通じてクエリ分布の属性を探索できます。新しい Performance Analysis セクションでは、最小値、最大値、平均値のメトリクス値を含む折れ線グラフとヒートマップビューが表示され、時間の経過に伴うトレンドや異常を発見するのに役立ちます。これらのビジュアライゼーションにより、パフォーマンスのボトルネックの特定、クエリの分布の理解、パフォーマンス最適化のためのアクションの実行が容易になります。

## はじめに

OpenSearch 3.6 は、お好みのディストリビューションで[ダウンロード](https://opensearch.org/downloads/)するか、ダウンロード不要の [OpenSearch Playground](https://playground.opensearch.org/app/home) で探索できます。詳細については、[リリースノート](https://github.com/opensearch-project/opensearch-build/blob/main/release-notes/opensearch-release-notes-3.6.0.md)、[ドキュメントリリースノート](https://github.com/opensearch-project/documentation-website/blob/main/release-notes/opensearch-documentation-release-notes-3.6.0.md)、および更新された[ドキュメント](https://docs.opensearch.org/latest/)を参照してください。このリリースを実現した数百人のコントリビューターの皆さまに心より感謝いたします。最新のツールがより強力で高性能なアプリケーションの推進にどのように役立っているか、[コミュニティフォーラム](https://forum.opensearch.org/)、[プロジェクト GitHub](https://github.com/opensearch-project)、または [Slack](https://opensearch.org/slack/) でお聞かせください。
