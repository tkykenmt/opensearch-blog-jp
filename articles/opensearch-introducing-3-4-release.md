---
title: "[翻訳] OpenSearch 3.4 のご紹介"
emoji: "🚀"
type: "tech"
topics: ["opensearch", "search", "analytics", "ppl", "grpc"]
published: true
publication_name: "opensearch"
published_at: 2025-12-17
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/introducing-opensearch-3-4/

OpenSearch 3.4 がダウンロード可能になりました。さまざまなユースケースに対応する新機能や更新機能に加え、一般的なワークロードのパフォーマンスを向上させる機能強化が含まれています。主なアップグレードは以下の通りです。

- エージェント検索のための全く新しいユーザーエクスペリエンス
- 検索関連性を向上させる新しいツール群
- 分析およびオブザーバビリティのユースケース向けに拡張された [Piped Processing Language](https://docs.opensearch.org/latest/search-plugins/sql/ppl/index/) (PPL) コマンド
- 集計ワークロードの大幅なパフォーマンス向上

[最新バージョンはこちらからダウンロード](https://opensearch.org/downloads/)するか、[Playground](https://playground.opensearch.org/app/home) で OpenSearch をお試しください。新機能の詳細については、[リリースノート](https://github.com/opensearch-project/opensearch-build/blob/main/release-notes/opensearch-release-notes-3.4.0.md)を参照してください。

## 検索

OpenSearch 3.4 では、エージェント検索の実装を簡素化し、検索結果の関連性を向上させる新機能が組み込まれています。

### ノーコードのユーザーエクスペリエンスでエージェント検索を強化

OpenSearch 3.4 では、エージェントの構築と[エージェント検索](https://docs.opensearch.org/latest/vector-search/ai-search/agentic-search/index/)の実行のための、再設計されたノーコードのユーザーエクスペリエンスが導入されました。エージェント作成 UI は、外部 Model Context Protocol (MCP) 統合、検索テンプレート統合、会話メモリ、単一モデルサポートなど、最新のエージェント機能を完全にサポートするようになりました。エージェント検索を実行する際、ユーザーはインデックスとエージェントをシームレスに切り替え、会話検索を有効にし、履歴をクリアし、クエリを停止して新しいクエリを再実行できます。エージェントサマリービューでは、使用されたステップとツールのシーケンスを確認できます。また、視覚的なインデックスを備えた強化されたドキュメント結果により、クエリの関連性と結果の精度を簡単に検証できます。エージェント設定パネルは折りたたみ可能になり、ユーザーは検索体験に集中できます。最後に、「Export」ボタンを使用して、エージェント検索をダウンストリームアプリケーションにエクスポートして適用する方法に関する関連リソースとステップバイステップのガイダンスにアクセスできるようになりました。

### 新しいワークベンチツールで検索関連性のチューニングを強化・簡素化

このリリースでは、[Search Relevance Workbench](https://docs.opensearch.org/latest/search-plugins/search-relevance/using-search-relevance-workbench/) にいくつかの新しいツールと UX の強化が加わりました。強力な新機能の 1 つはスケジュール実験です。UI から直接実験をスケジュールで実行するように設定できるようになり、継続的な関連性チューニングに役立ちます。毎晩、毎週、毎月テストを実行して、時間の経過に伴う検索品質の理解を深めることができます。単一クエリ比較ツールは、[エージェント検索](https://docs.opensearch.org/latest/vector-search/ai-search/agentic-search/index/)クエリのネイティブサポートで強化され、エージェント生成クエリ、エージェントサマリー、会話検索機能を検索結果と同時に表示できるようになりました。もう 1 つの改善点は、グローバル一意識別子 (GUID) フィルタリングです。実験、検索設定、クエリセット、判定リストを ID で検索できます。これにより、Search Relevance Workbench を長期間使用して多くのアセットが蓄積された場合でも、ナビゲーションが簡素化されます。

## オブザーバビリティ、ログ分析、セキュリティ分析

[OpenSearch 3.3](https://opensearch.org/blog/explore-opensearch-3-3/) では、データからインサイトを得るための多数の新しい PPL コマンドと関数を含む、オブザーバビリティツールキットへのいくつかの追加が導入されました。このリリースでは、OpenSearch の PPL 機能がさらに拡張され、便利な新機能が追加されています。

### 新しい PPL 関数とコマンドでデータを探索

OpenSearch 3.4 では、PPL 用の `chart` コマンドが導入され、柔軟なグループ化オプションを備えた統計集計を通じて、クエリ結果を可視化可能なデータに変換できます。このコマンドは、標準的な集計のための単一フィールドグループ化と、`OVER...BY` 構文を使用した二重フィールドグループ化をサポートしています。後者では、最初のフィールドが行を定義し、2 番目のフィールドが 2 次元の可視化のために列にピボットできるカテゴリを定義します。chart コマンドは、ダッシュボードや可視化ツールでの使用に適した形式で結果を出力します。さらに、新しい `streamstats` コマンドは、定義されたウィンドウ上でデータを増分的に集計し、各イベントが到着するたびに累計やカウントなどのメトリクスを生成します。このコマンドは、ウィンドウ境界内でデータを段階的に評価することで、PPL クエリ内で直接シーケンシャルおよびトレンドに敏感な分析を実行できます。

このリリースには、複数の検索サブサーチからの結果を単一の統合結果セットに結合できる新しい `multisearch` コマンドと、指定されたフィールド内のテキストパターンを置換できる `replace` コマンドも含まれています。新しい `appendpipe` コマンドは、サブパイプラインの結果を検索結果に追加します。サブサーチとは異なり、サブパイプラインは最初に実行されるのではなく、検索が `appendpipe` コマンドに到達したときに実行されます。また、2 つの新しい関数もリリースに含まれています。`mvindex` 関数は、開始インデックス値とオプションの終了インデックス値を使用して、多値配列のサブセットを返します。`mvdedup` eval 関数は、多値配列から重複値を削除できます。

## コスト、パフォーマンス、スケーラビリティ

このリリースには、OpenSearch クラスターのコスト効率、パフォーマンス、スケーラビリティを向上させるための更新が含まれています。

### Lucene バルクコレクション API で集計ワークロードを高速化

OpenSearch は、[集計](https://docs.opensearch.org/latest/aggregations/)用の Lucene の新しいバルクコレクション API を統合し、カーディナリティ、ヒストグラム、一連の統計集計を含むいくつかの主要な分析操作で 5% から 40% のパフォーマンス向上を実現しました。バルクコレクション API は、ドキュメントごとのコレクションオーバーヘッドを削減することで集計実行を最適化します。以前は、各ドキュメントのコレクションに仮想メソッド呼び出しが必要で、不要な計算オーバーヘッドが発生していました。新しいバルクコレクションアプローチは、操作をバッチ処理することでドキュメントをより効率的に処理し、集計実行中のこれらの仮想呼び出しのパフォーマンスへの影響を分散させます。コミュニティからの貢献とフィードバックを歓迎します。ディスカッションに参加するには、[メタ Issue](https://github.com/opensearch-project/OpenSearch/issues/20031) を参照してください。

### パーセンタイルと matrix stats 集計のレイテンシを改善

このリリースには、[集計](https://docs.opensearch.org/latest/aggregations/)ワークロードの追加のパフォーマンス最適化が含まれています。これには、パーセンタイル集計の変更が含まれます。以前の `AVLTreeDigest` 実装を `MergingDigest` 実装に置き換えることで、パーセンタイル集計は高カーディナリティフィールドで約 2 倍のパフォーマンス向上が見られ、低カーディナリティフィールドでは最大 30 倍の改善が見られる場合があります。さらに、`matrix_stats` 集計の簡素化により、最大 5 倍のパフォーマンス向上が実現しました。

### 拡張されたクエリサポートとバルクリクエストの改善で gRPC をデプロイ

[gRPC](https://docs.opensearch.org/latest/api-reference/grpc-apis/index/) Search API は、OpenSearch 3.4 で追加機能を獲得し、`ConstantScoreQuery`、`FuzzyQuery`、`MatchBoolPrefixQuery`、`MatchPhrasePrefix`、`PrefixQuery`、`MatchQuery` の新しいクエリタイプのサポートが追加されました。このリリースには、CBOR/SMILE/YAML ドキュメント形式のサポートを含む gRPC バルクリクエストの改善も含まれています。

## はじめに

最新バージョンは[ダウンロードページ](https://opensearch.org/downloads/)で入手するか、[OpenSearch Playground](https://playground.opensearch.org/app/home#/) で可視化ツールをお試しください。詳細については、[リリースノート](https://github.com/opensearch-project/opensearch-build/blob/main/release-notes/opensearch-release-notes-3.4.0.md)、[ドキュメントリリースノート](https://github.com/opensearch-project/documentation-website/blob/main/release-notes/opensearch-documentation-release-notes-3.4.0.md)、[更新されたドキュメント](https://docs.opensearch.org/latest/)を参照してください。また、[コミュニティフォーラム](https://forum.opensearch.org/)でこのリリースに関するフィードバックを共有したり、[Slack インスタンス](https://opensearch.org/slack/)で他の OpenSearch ユーザーとつながることもできます。

2026 年には OpenSearch 3.5 やその他の新しいリリースで、OpenSearch デプロイメントのパフォーマンスと機能をさらに向上させる予定です。それまで、OpenSearch コミュニティの皆様に新年のご多幸をお祈りいたします！
