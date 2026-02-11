---
title: "[翻訳] OpenSearch 3.5 がリリースされました！"
emoji: "🔍"
type: "tech"
topics: ["opensearch", "検索", "オブザーバビリティ", "GenAI", "ベクトル検索"]
publication_name: "opensearch"
published: true
published_at: 2026-02-10
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/opensearch-3-5-is-live/

# OpenSearch 3.5 がリリースされました！

OpenSearch 3.5 が[ダウンロード可能](https://opensearch.org/downloads/)になりました。オブザーバビリティワークロードと検索ユースケースの大幅なアップグレード、より強力なエージェントアプリケーションを構築するための新しいツール、運用の最適化に役立つ多数の機能強化が含まれています。本リリースの新機能は以下の通りです。

- Prometheus サポートの拡張によるメトリクスデータのより深い洞察
- Search Relevance Workbench による検索最適化の強化
- 自己学習アプリケーション向けのエージェントメモリサポート
- クエリパフォーマンスと効率に対する制御の向上

以下では最新バージョンのハイライトをご紹介します。OpenSearch 3.5 の新機能の完全なまとめについては、[リリースノート](https://github.com/opensearch-project/opensearch-build/blob/main/release-notes/opensearch-release-notes-3.5.0.md)を参照してください。

### 強力なベクトル検索と GenAI アプリケーションの構築

#### 会話メモリによるよりスマートなエージェントアプリケーションの作成

[エージェント会話メモリ](https://docs.opensearch.org/latest/ml-commons-plugin/api/agent-apis/execute-agent/)は、AI エージェントに OpenSearch 内で直接、永続的で構造化されたメモリを提供します。会話のコンテキスト、中間的なツール推論、最終的な応答を一箇所に記録するため、エージェントはより一貫性のあるフォローアップ回答を提供できます。リクエスト間でセッションを継続し、必要に応じてメモリコンテキストを切り替え、より明確なトレーサビリティで動作のトラブルシューティングを行うことができます。組み込みのバリデーションにより、本番ワークロードのより安全なロールアウトのために設定ミスを早期に検出できます。

#### フックベースのコンテキスト管理によるエージェントパフォーマンスの向上

[コンテキスト管理](https://docs.opensearch.org/latest/ml-commons-plugin/context-management)により、OpenSearch エージェントは大規模言語モデル (LLM) にリクエストを送信する前にコンテキストを動的に最適化できます。これにより、コンテキストウィンドウのオーバーフローを回避し、トークン使用量を削減し、会話履歴とツールのインタラクションをインテリジェントに管理することで長時間実行されるエージェントを強化します。コンテキストマネージャーは、自動切り詰め、要約、スライディングウィンドウ戦略をサポートしています。フックベースのシステムはエージェント実行の異なるステージでアクティブ化でき、特定のユースケースに合わせた設定の柔軟性を提供します。

#### 結果を犠牲にせずにベクトル検索スループットを向上

本リリースでは、OpenSearch のベクトル検索エンジンにパフォーマンスの改善と機能強化がもたらされました。[効率的なフィルター](https://github.com/opensearch-project/k-NN/issues/3047)と、より高速な FP16 ベクトル演算のための[バルク SIMD 実装](https://github.com/opensearch-project/k-NN/issues/2875)、Lucene エンジンの ef_search パラメータの強化、ソースインデキシングにおけるフィールド除外の改善、ネストされた k-NN クエリのより良い処理が含まれています。メモリ最適化検索を備えたバルク SIMD 実装は、マルチセグメントシナリオで FP16 ベクトルに対して 58% のスループット向上を実現し、94% のリコールを維持しながら、シングルセグメントシナリオでは 28% のパフォーマンス向上を達成しています。

#### 外部 REST API とのより強力な接続の構築

OpenSearch 3.5 では、ML Commons の[コネクタフレームワーク](https://docs.opensearch.org/latest/ml-commons-plugin/remote-models/connectors/)が強化され、カスタム名付きアクションと追加の HTTP メソッド (PUT および DELETE) のサポートが追加されました。これにより、外部 REST API との統合のためのより柔軟で強力なコネクタ設定が可能になります。コネクタアクション定義の新しいオプションの name フィールドにより、アクションを一意に識別でき、単一のコネクタ内で同じタイプの複数のアクションを有効にできます。例えば、コネクタは EXECUTE アクションタイプを使用して、書き込み、検索、更新、削除の各操作を個別に定義できるようになりました。拡張された HTTP メソッドサポートと組み合わせることで、単一のコネクタ設定で包括的な CRUD 操作が可能になります。

#### フロントエンドアプリケーションにリアルタイム会話 AI を直接導入

3.5 で実験的機能として追加された [Agent-User Interaction](https://docs.opensearch.org/latest/ml-commons-plugin/agents-tools/agents/ag-ui/) (AG-UI) プロトコルのサポートは、ML Commons エージェントフレームワークにおいて、AI エージェントがユーザー向けアプリケーションに接続する方法を標準化します。イベントベースのストリーミングインタラクションを通じて、リアルタイムの会話 AI をユーザーインターフェースに直接導入し、OpenSearch Dashboards やその他のフロントエンドアプリケーションでレスポンシブでインタラクティブな体験を実現します。例えば、この機能により、OpenSearch プラットフォーム内で完全にエンドツーエンドのコンテキスト対応チャットボットのようなアプリケーションを構築できます。

### テレメトリシグナルからのより深い洞察の獲得

#### 新しい Discover 体験で Prometheus メトリクスデータを探索・チャート化

[Prometheus](https://prometheus.io/) は、クラウドネイティブ環境におけるメトリクス収集のデファクトスタンダードとなっており、Kubernetes デプロイメントや最新のインフラストラクチャスタック全体で広く採用されています。OpenSearch 3.5 では、[OpenSearch Dashboards](https://opensearch.org/platform/opensearch-dashboards/) の新しい [Discover](https://docs.opensearch.org/latest/dashboards/discover/index-discover/) 体験により Prometheus サポートが拡張され、Prometheus データソースからのメトリクスデータをログやトレースと並べて直接クエリおよび可視化できるようになりました (以下の画像参照)。これにより、統合されたオブザーバビリティビューのために複数のツール間でコンテキストを切り替える必要がなくなります。本リリースでは、複雑なクエリの迅速な開発を促進する PromQL (Prometheus Query Language) のオートコンプリートと、CPU 使用率やメモリ使用量などの変動する値をより簡単に監視するためのゲージメトリクスタイプのサポートも導入されています。セルフホストの Prometheus または Amazon Managed Service for Prometheus のいずれを使用している場合でも、この統合は OpenSearch 内でのネイティブなログ、メトリクス、トレースの包括的なサポートに向けた重要なステップであり、単一プラットフォーム内でオブザーバビリティワークフローを効率化します。Discover でメトリクスデータを操作するには、設定の詳細について[ドキュメント](https://docs.opensearch.org/latest/observing-your-data/exploring-observability-data/discover-metrics/)を参照してください。

![ローカル Prometheus インスタンスからの CPU 使用率メトリクスを示すマルチシリーズ折れ線グラフ](/images/opensearch-3-5-is-live/653453f68a7b.png)
*ローカル Prometheus インスタンスからの CPU 使用率メトリクスを示すマルチシリーズ折れ線グラフ。*

#### 高度な PPL ツールでデータをクエリ・変換

本リリースでは、多数の新しい [Piped Processing Language](https://docs.opensearch.org/latest/sql-and-ppl/ppl/index/) (PPL) 関数とコマンドが追加され、オブザーバビリティデータを価値ある発見に変換するためのより多くの方法が提供されます。mvcombine コマンドは、複数のフィールド値が共通の値を共有する場合に、マルチバリューフィールドを統合してより簡単な分析を可能にします。mvzip 関数では、2 つのマルチバリューフィールドの値を結合してつなぎ合わせることができます。mvfind 関数は、マルチバリュー配列を検索し、指定された値の最初の一致のインデックス位置を返します。mvmap は、マルチバリュー配列の各値を反復処理し、指定された式を適用して、変換された結果を含む新しい配列を返します。さらに、新しい addtotals コマンドは各行のすべての列の合計を新しい列として表示し、オプションで各列のすべての行の合計を新しい行として表示します。新しい streamstats コマンドは、データセットのスキャン後に最終的な集計を計算するのではなく、イベントが処理される際に累積的な統計計算を実行します。

### 検索の関連性向上とより良い結果のためのチューニング

#### LLM を活用した評価で検索結果を最適化

[Search Relevance Workbench](https://docs.opensearch.org/latest/search-plugins/search-relevance/using-search-relevance-workbench/) に、関連性のチューニングをより簡単かつ強力にするエキサイティングな新機能が追加されました。LLM-as-judge の導入により、テストを強化できます。LLM を使用してカスタマイズ可能なプロンプトで検索結果を自動的に評価し、手動の判断を超えて進む準備ができたら関連性テストをスケールアップできます。

#### 時間を節約する検索関連性ツールの活用

Search Relevance Workbench には、使いやすさのためのいくつかの機能強化も追加されました。シンプルなクエリ比較 UI で検索設定を再利用し、異なるアプローチ間の比較を効率化できるようになりました。検索設定の新しい説明フィールドにより、各設定の内容をドキュメント化しやすくなり、新しい検索エンドポイントにはスマートフィルタリングオプションが付属して、探しているものをより速く見つけることができます。また、検索品質のベースラインを確立するための夜間または週次のスケジュール評価のサポートと、以下の画像に示すような [User Behavior Insights](https://docs.opensearch.org/latest/search-plugins/ubi/index/) 用の新しいサンプルデータセットとダッシュボードも追加されています。

![日次スケジュールの Search Relevance Workbench 実験](/images/opensearch-3-5-is-live/feff9613701f.png)
*Mean Average Precision (mAP)、Normalized Discounted Cumulative Gain (NDCG)、精度の検索品質メトリクスで測定された結果を含む、日次スケジュールの Search Relevance Workbench 実験。*

### クエリパフォーマンスと効率の最適化

#### コストの高いクエリの背後にあるものを把握

[クエリインサイト](https://docs.opensearch.org/latest/observing-your-data/query-insights/index/)に、[上位 N クエリ結果](https://docs.opensearch.org/latest/observing-your-data/query-insights/top-n-queries/)のすべてのクエリに対する自動的なユーザー名とユーザーロールのキャプチャが含まれるようになりました。これにより、共有環境でのクエリ所有権の可視性が向上し、より良い運用インテリジェンスが実現します。新しい username および user_roles フィールドが、すべてのクエリレコードのレイテンシ、CPU、メモリメトリクスと並んで表示されます。このコンテキストにより、どのチームやロールがリソース集約型のクエリを生成しているかを特定し、クエリの最適化とリソース割り当てについて情報に基づいた意思決定を行い、異常な動作が検出された際に適切な担当者に迅速に連絡できます。

#### 分離されたデプロイメント向けのクエリインサイト設定のセキュア化

新しいラッパー REST API エンドポイントにより、マルチテナント環境での[クエリインサイト設定](https://docs.opensearch.org/latest/observing-your-data/query-insights/query-insights-dashboard/)をより細かく制御できます。新しい /_insights/settings エンドポイントは、メトリクス設定 (レイテンシ、CPU、メモリ)、グルーピングパラメータ、エクスポーター設定を含むクエリインサイトクラスター設定への狭い目的別のアクセスを提供します。これにより、管理者はより広範なクラスター設定機能を公開することなく、きめ細かいアクセス制御を実装し、本番デプロイメントのセキュリティを強化できます。

#### 複雑なクエリのストレージ最適化

クエリソースフィールドの保存に対する新しいアプローチにより、データの整合性を維持しながらストレージ効率が大幅に向上しました。クエリソースは、複雑なオブジェクトとしてではなく、ローカルインデックスに文字列として保存されるようになり、クエリの複雑さや長さに関係なく信頼性の高いクエリインサイトの収集が可能になりました。本番規模のワークロードを使用したベンチマークでは、平均的なクエリで 58% の削減、大規模なクエリで 49% の削減が示されており、設定可能な切り詰めにより、完全なクエリソースが不要な場合にさらなるストレージ最適化が可能です。

#### クエリパフォーマンスとワークロード管理ポリシーの関係を探索

[ワークロード管理](https://docs.opensearch.org/latest/tuning-your-cluster/availability-and-recovery/workload-management/wlm-feature-overview/)のグループ割り当てが、クエリインサイトダッシュボードに直接統合されました。上位クエリテーブルの新しいワークロード管理グループ列はフィルタリングとソートをサポートし、単一のビューでクエリパフォーマンスとリソース割り当てポリシーを迅速に相関させることができます。

### インフラストラクチャとアーキテクチャの更新

#### Node.js 20 の非推奨化と 22 への更新、Webpack 4 から Rspack への置き換え

OpenSearch Dashboards は、バージョン 3.5.0 で Node.js 20 のサポートを非推奨とします。これは、バージョン 20 が 2026 年 4 月にサポート終了となるためです ([nodejs.org](http://nodejs.org) からの[こちらの通知](https://nodejs.org/en/blog/announcements/node-18-eol-support)を参照)。同様に、プロジェクトは Webpack 4 を [Rspack](https://github.com/web-infra-dev/rspack) に置き換えました。Rspack は webpack の API と互換性のある高速な Rust ベースの JavaScript バンドラーで、GitHub の[こちらの公開 RFC](https://github.com/opensearch-project/OpenSearch-Dashboards/issues/11125) で議論されています。アップグレードプロセスにおいて、顧客向け API に関連する破壊的変更は確認されていません。

#### 実験的な HTTP/3 サポート

OpenSearch 3.5 では、サーバーサイドでの [HTTP/3 プロトコル](https://datatracker.ietf.org/doc/html/rfc9114#name-http-3-protocol-overview)の実験的サポートが導入されました。その他のメリットとして、HTTP/3 は UDP 上の QUIC トランスポートプロトコルを使用しており、HTTP/2 で使用される TCP プロトコルと比較して、ネットワークパフォーマンスと回復力の面で大きなメリットがあります。サーバーサイド HTTP/3 を有効にする方法については、[ネットワーク設定ドキュメント](https://docs.opensearch.org/latest/install-and-configure/configuring-opensearch/network-settings/)を参照してください。

### はじめに

OpenSearch 3.5 は、[ダウンロードページ](https://opensearch.org/downloads/)でさまざまなディストリビューションで利用可能です。また、[OpenSearch Playground](https://playground.opensearch.org/app/home#/) で OpenSearch の可視化ツールを試すことができます。詳細については、[リリースノート](https://github.com/opensearch-project/opensearch-build/blob/main/release-notes/opensearch-release-notes-3.5.0.md)、[ドキュメントリリースノート](https://github.com/opensearch-project/documentation-website/blob/main/release-notes/opensearch-documentation-release-notes-3.5.0.md)、および更新された[ドキュメント](https://docs.opensearch.org/latest/)を参照してください。[コミュニティフォーラム](https://forum.opensearch.org/)でフィードバックをお寄せいただき、プロジェクトの [Slack インスタンス](https://opensearch.org/slack/)で他の OpenSearch ユーザーとつながることをお勧めします。
