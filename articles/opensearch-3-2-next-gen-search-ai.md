---
title: "[翻訳] OpenSearch 3.2 の紹介: AI 機能が強化された次世代の検索と分析"
emoji: "🚀"
type: "tech"
topics: ["opensearch", "release", "ai", "search"]
published: true
publication_name: "opensearch"
published_at: 2025-08-19
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/introducing-opensearch-3-2-next-generation-search-and-anayltics-with-enchanced-ai-capabilities/

OpenSearch 3.2 がリリースされました。検索、オブザーバビリティ、生成 AI のユースケースを強化・拡張する多くの機能が含まれています。

このリリースでは、3.x 系で導入された新しいイノベーションの拡張に焦点を当てています。

- GPU サポートの拡張
- 近似フレームワークの大幅な改善
- OpenSearch における Protobuf の GA

多くの機能強化は、より効率的なインデックス作成とクエリ機能によるワークロードのスケーリングを支援することに焦点を当てています。ハイライトをご紹介します!

## 検索

検索は、パフォーマンス、スケーラビリティ、機能拡張に焦点を当てた多くの変更が行われました。

### 近似フレームワークの大幅な改善

OpenSearch 3.2 では、[近似フレームワーク](https://opensearch.org/blog/opensearch-approximation-framework/)が 2 つの異なる領域で拡張されました。

まず、3.2 で `search_after` クエリがサポートされるようになり、これらのクエリが以前はデフォルトの Lucene トラバーサルにフォールバックしていた重大なパフォーマンスギャップに対処しました。この機能強化により、`search_after` パラメータが適切な範囲クエリの境界に変換されます。ASC ソートでは `search_after` を下限として、DESC ソートでは上限として使用し、デフォルトの Lucene にフォールバックする代わりに `ApproximatePointRange` クエリの最適化された BKD トラバーサルを継続して使用できます。この最適化により、時系列および数値ワークロードのページネーションパフォーマンスが大幅に向上します。ベンチマークテストでは、Big5 データセットで `search_after` を使用した ASC と DESC の両方のタイムスタンプソートで p90 レイテンシが 185 ms から 8 ms に削減されました。`http_logs` データセットでも同様の改善が達成され、DESC ソートのレイテンシが 397 ms から 7 ms に低下しました。これにより、ページネーションされた検索結果、リアルタイムダッシュボード、大規模な時系列または数値データセットを通じた深いページネーションを必要とするアプリケーションの応答性が向上します。

次に、OpenSearch 3.2 では、近似クエリ機能が LONG フィールドタイプだけでなく、すべての数値フィールドタイプに拡張されました。この機能強化には、`HALF_FLOAT`、`FLOAT`、`DOUBLE`、`INTEGER`、`BYTE`、`SHORT`、`UNSIGNED_LONG` フィールドが含まれます。http_logs と nyc_taxis データセットでのベンチマークテストでは、p90 レイテンシが最大 80% 削減されるなど、大幅なパフォーマンス向上が実証されています。この最適化は、分析ワークロード、時系列データ分析、多様な数値フィールドタイプにわたる高速な数値フィルタリング/ソート操作を必要とするアプリケーションに最も有益です。

### より高性能な API として gRPC/Protobuf を試す

3.2 では、[gRPC トランスポート](https://docs.opensearch.org/latest/api-reference/grpc-apis/index/)レイヤーが一般提供 (GA) に達し、バルクドキュメント取り込みと k-NN クエリ機能の高性能サポートを提供します。これは、OpenSearch ユーザーにとってパフォーマンス、効率性、拡張性における重要な前進を示しています。ネイティブ REST API を使用する代わりに、gRPC モジュールは Protocol Buffers (Protobufs) を使用して通信します。これは、OpenSearch API 仕様から自動生成されるコンパクトで構造化された強く型付けされたバイナリ形式です。この形式により、ペイロードサイズが削減され、特にバルク取り込みや k-NN クエリを使用したベクトル検索などのプリミティブタイプのデータに対する高スループット操作で全体的なパフォーマンスが向上します。GA リリースの追加のハイライトには、拡張された検索 API 機能と転送中の暗号化が含まれます。gRPC トランスポートレイヤーは、パフォーマンスが重要なワークロードをサポートし、将来的に効率的なクライアント統合を構築するためのエキサイティングな可能性を開きます。この機能の実現に向けてリーダーシップとコラボレーションを発揮してくれた OpenSearch Software Foundation のプレミアメンバーである Uber に特別な感謝を申し上げます。

### 新しい skip_list 機能でクエリパフォーマンスを向上

OpenSearch 3.2 で導入された `skip_list` パラメータは、範囲クエリや集計で頻繁に使用されるフィールドに特に有益です。`skip_list` を使用すると、クエリエンジンがクエリ条件に一致しないドキュメント範囲をスキップできるため、パフォーマンスが向上します。このパラメータの使用方法の詳細については、[フィールドタイプのドキュメント](https://docs.opensearch.org/latest/field-types/supported-field-types/index/)を参照してください。

### star-tree を使用した検索の新機能

[star-tree を使用した検索](https://docs.opensearch.org/latest/search-plugins/star-tree-index/)で、`IP` フィールドに対するクエリを含む集計もサポートされるようになりました。また、star-tree を使用して解決されたクエリに関する基本的なメトリクスが、インデックス/ノード/シャード統計の一部として含まれるようになりました。表示オプションには、star-tree を使用して解決されたクエリの総数、star-tree を使用して現在実行中のクエリ、star-tree を使用してクエリを解決するのに費やした合計時間が含まれます。この機能の紹介については、[関連記事](https://opensearch.org/blog/the-power-of-star-tree-indexes-supercharging-opensearch-aggregations/)を参照してください。

### ストリーミング集計でリソース分散を改善

3.2 で実験的機能として、ストリーミングトランスポート上に構築されたストリーミング[集計](https://docs.opensearch.org/latest/aggregations/)機能が導入されました。これにより、シャードごとに単一のレスポンスを返す代わりに、セグメントレベルの部分集計レスポンスをコーディネーターノードにストリーミングバックできます。このアプローチにより、コーディネーターをスケールする単一のポイントにすることで、リソース分散が改善されます。オプトイン使用のために、`stream=true` クエリパラメータを使用して `term` 集計検索を実行できます。このアーキテクチャの変更により、メモリ集約型の reduce ロジックがデータノードからコーディネーターに移動し、高カーディナリティ集計のスケーラビリティが向上します。

### Search Relevance Workbench で品質を評価

Search Relevance Workbench がバージョン 3.2 で GA になりました。これにより、検索クエリの問題を調査・診断することで、実験を通じて検索関連性を改善・微調整できます。検索評価とグローバルハイブリッド最適化の詳細な調査を容易にするために、個々のクエリ品質の可視化を備えたダッシュボードが作成されました。この新しいツールの使い方については、[検索関連性](https://opensearch.org/blog/taking-your-first-steps-towards-search-relevance/)の入門記事が参考になります。

## ベクトルデータベースと生成 AI

OpenSearch 3.2 では、GPU サポートのより多くのベクトルタイプへの拡張、ベクトル検索品質の改善、Neural Search プラグインの更新など、パフォーマンスとスケールに関連するいくつかの改善が導入されています。

### 拡張された GPU サポートで新しいベクトルタイプを使用

OpenSearch の GPU インデックス作成で、以前の FP32 サポートに加えて、`FP16`、`byte`、`binary` ベクトルタイプがサポートされるようになりました。これらの追加の表現は `FP32` ベクトルよりもメモリ使用量が少なく、メモリにより多くのストレージを確保し、GPU と CPU 間のデータ転送を削減できます。最終的な結果は、リソースのより効率的でスケーラブルな使用と、[GPU アクセラレーションインデックス作成](https://docs.opensearch.org/latest/vector-search/remote-index-build/)を使用して構築されるより広範なアプリケーションの可能性です。

### オンディスクベクトル検索の再現率を向上

OpenSearch 3.2 では、バイナリ量子化インデックスの検索品質を向上させる [2 つの強力な技術](https://github.com/opensearch-project/k-NN/issues/2714)が導入されています。非対称距離計算 (ADC) は、圧縮されたドキュメントベクトルと比較しながらフルプレシジョンのクエリベクトルを維持し、メモリオーバーヘッドなしで重要な検索情報を保持します。ランダム回転 (RR) は、32 倍の圧縮プロセス中の情報損失を防ぐために、ベクトル次元全体に分散を再分配します。ADC は 1 ビット量子化をサポートし、RR は 1、2、4 ビット構成で動作します。これらのオプトイン機能を組み合わせることで、SIFT のような困難なデータセットで再現率を最大 80% 向上させることができ、適度なレイテンシのトレードオフがあり、精度が重要なアプリケーションでバイナリ量子化を実用的にします。

### 特定のデータ、パフォーマンス、関連性のニーズに合わせてセマンティック検索を最適化

OpenSearch 3.2 では、[Neural Search](https://docs.opensearch.org/latest/vector-search/api/neural/) プラグインのセマンティックフィールドに、高度なセマンティック検索シナリオをより良くサポートするための新しい設定可能性が追加されました。ユーザーは、密な埋め込みフィールドパラメータ (例: `engine`、`mode`、`compression_level`、`method`) を微調整し、複数のアルゴリズム/設定でテキストチャンキングをカスタマイズし、プルーニング戦略と比率でスパース埋め込み生成を設定できるようになりました。新しいバッチサイズオプションによりインデックス作成スループットが向上し、埋め込み再利用設定によりコンテンツが変更されていない場合の冗長な処理が削減されます。これらの機能強化により、セマンティック検索がより柔軟で効率的かつ適応性が高くなり、特定のデータ、パフォーマンス、関連性のニーズに合わせた最適化オプションが作成されます。

### Plan-Execute-Reflect エージェントが GA に

計画と振り返りによって複雑なタスクを自律的に解決できる Plan-Execute-Reflect エージェントが 3.2 で一般提供になり、パフォーマンスを向上させるプロンプト、メッセージ履歴を制御するパラメータの公開、プロンプトに日付と時刻を含める機能が強化されました。[ML Commons プラグイン](https://docs.opensearch.org/latest/ml-commons-plugin/)で利用可能な Plan-Execute-Reflect エージェントは、複雑な質問を管理可能なステップに分解し、実行に適したツールを選択し、振り返りを通じて戦略を反復的に改善します。

### エージェント検索を使用して自然言語の質問を OpenSearch DSL に変換

バージョン 3.2 で実験的機能として導入された[エージェント検索](https://docs.opensearch.org/latest/vector-search/ai-search/agentic-search)は、クエリの理解、計画、実行のための[エージェント駆動ワークフロー](https://github.com/opensearch-project/ml-commons/blob/main/docs/tutorials/agentic_search/agentic_search_llm_generated_type.md)をトリガーする OpenSearch で提案された新しいクエリタイプです。DSL を手作業で作成する代わりに、自然言語の質問とエージェント ID を提供します。エージェントは[クエリ計画ツール](https://docs.opensearch.org/latest/ml-commons-plugin/agents-tools/tools/query-planning-tool/)を実行して OpenSearch DSL を生成し、エージェントクエリ句を介して実行し、検索結果を返します。

### 過去のインタラクションから学習する AI エージェントを作成

OpenSearch 3.2 で実験的機能として導入された[エージェントメモリ](https://docs.opensearch.org/latest/ml-commons-plugin/api/agentic-memory-apis/index/)により、AI エージェントは単純な会話履歴を超えた永続的なメモリを維持できます。この機能は会話から重要な事実を抽出して保存し、エージェントが過去のインタラクションから学習し、セッション間でよりパーソナライズされた支援を提供できるようにします。開発者は、[セマンティック検索を活用する AI エージェント](https://github.com/opensearch-project/ml-commons/blob/main/docs/tutorials/agentic_memory/agentic_memory_with_strands_agent.md)を構築して、以前のインタラクションから関連するコンテキストを呼び出し、将来のセッションの品質を向上させることができます。

## オブザーバビリティ、ログ分析、セキュリティ分析

OpenSearch 3.2 では、クエリパフォーマンスの改善、Trace Analytics プラグインの新しい分析手段などが導入されています。

### 新しい OpenTelemetry 互換性とサービスマップコントロールでトレース分析を改善

[Trace Analytics プラグイン](https://docs.opensearch.org/latest/observing-your-data/trace/ta-dashboards/)は、Data Prepper 2.11 での取り込みから OpenSearch 3.2 でのトレース分析の可視化まで、OpenTelemetry (OTel) に準拠したトレースの分析をサポートするようになりました。`output_format: otel` で OTel ソースを設定し、スパンを OpenSearch に送信して標準の OTel フィールドとメタデータを保持することで、OpenTelemetry ツールとのスムーズな統合とシンプルなパイプラインが可能になります。ユーザーは、サービスマップに表示される最大ノード数とエッジ数を設定できるようになり、大規模な環境での視覚的な複雑さをより細かく制御できます。

### PPL Calcite の更新でクエリパフォーマンスと使いやすさを向上

OpenSearch 3.2 では、Piped Processing Language (PPL) に大幅なパフォーマンスとクエリの柔軟性の改善が提供されています。新しい Calcite 行式ベースのスクリプトエンジンにより、集計関数、フィルター関数のプッシュダウン、スパンのプッシュダウン、関連性クエリのプッシュダウン、ソートマージ結合のプッシュダウン、IP 比較のプッシュダウンが可能になります。引数の強制変換、改善された日付処理、`QUERY_SIZE_LIMIT` の適用のための新しい関数が追加されました。これらの更新により、以下の画像に示すように、OpenSearch データソース全体の複雑なクエリのパフォーマンス、正確性、使いやすさが総合的に向上します。

![OpenSearch PPL](/images/opensearch-3-2-next-gen-search-ai/ppl-execution-time.png)
*画像: PPL 実行時間の改善: 2.x vs. 3.x*

### OpenSearch Prometheus エクスポーター

Prometheus エクスポータープラグインが OpenSearch プロジェクトに移行され、OpenSearch 3.2 と並行してリリースされています。このプラグインはコアビルドにバンドルされておらず、別途インストールする必要があります。ただし、パッケージングとリリースサイクルは OpenSearch プロジェクトのリリーススケジュールに合わせて更新されました。既存の Prometheus スクレイピングワークフローは互換性を維持しており、メトリクスは引き続き `/_prometheus/metrics` で公開されます。移行の管理と支援をしてくれた Aiven に特別な感謝を申し上げます。

## はじめに

OpenSearch の最新バージョンは[ダウンロードページ](https://opensearch.org/downloads/)で入手するか、[OpenSearch Playground](https://playground.opensearch.org/app/home#/) で可視化ツールをお試しください。詳細については、[リリースノート](https://github.com/opensearch-project/opensearch-build/blob/main/release-notes/opensearch-release-notes-3.2.0.md)、[ドキュメントリリースノート](https://github.com/opensearch-project/documentation-website/blob/main/release-notes/opensearch-documentation-release-notes-3.2.0.md)、[更新されたドキュメント](https://docs.opensearch.org/docs/latest/)をご覧ください。他のソフトウェアプロバイダーから OpenSearch への移行を検討している場合は、このプロセスを支援するために設計されたツールとドキュメントを[こちら](https://docs.opensearch.org/docs/latest/migration-assistant/)で提供しています。

このリリースに関する貴重なフィードバックを共有し、[Slack インスタンス](https://opensearch.org/slack/)で他の OpenSearch ユーザーとつながるために、コミュニティフォーラムにぜひお越しください。
