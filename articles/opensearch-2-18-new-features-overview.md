---
title: "[翻訳] OpenSearch 2.18 の新機能"
emoji: "🚀"
type: "tech"
topics: ["opensearch", "aws", "genai", "vectorsearch", "dashboards"]
published: true
publication_name: "opensearch"
published_at: 2024-11-06
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/get-started-with-opensearch-2-18/

今回のリリースでは、生成 AI (GenAI) アプリケーションの構築を支援する多くのアップデート、コア検索および関連ワークロードのパフォーマンス向上、そして OpenSearch Dashboards の大幅な使いやすさの改善によるチームコラボレーションの強化が含まれています。以下では、[OpenSearch 2.18](https://opensearch.org/downloads.html) で利用可能になったいくつかの注目機能の概要を紹介します。新機能の詳細については[リリースノート](https://github.com/opensearch-project/opensearch-build/blob/main/release-notes/opensearch-release-notes-2.18.0.md)をご確認ください。また、[OpenSearch Playground](https://playground.opensearch.org/app/home) で OpenSearch の可視化ツールキットをお試しいただけます。

## ベクトルデータベースと GenAI

OpenSearch 2.18 では、より柔軟で高性能な ML および GenAI アプリケーションの構築を支援するベクトルデータベースと機械学習 (ML) ツールキットのアップデートが導入されています。

### ベクトル検索アプリケーションのパフォーマンス向上

このリリースでは、ML および GenAI ワークロード向けにいくつかのパフォーマンス改善が導入されています。主なハイライトは以下の通りです。

- より効率的なメモリとキャッシュ管理。OpenSearch 2.18 では、ネイティブライブラリのメモリとキャッシュ管理の[最適化](https://github.com/opensearch-project/k-NN/pull/2182)が導入され、効率的なリソース利用が実現されています。
- インデックス作成と検索パフォーマンスの向上。Faiss エンジンへの [AVX512 SIMD](https://github.com/opensearch-project/k-NN/pull/2110) (Single Instruction, Multiple Data) サポートの統合により、高度なハードウェア機能を活用した大幅なインデックス作成と検索パフォーマンスの向上が可能になりました。
- インデックスの高速化。[ベクトルデータ構造の作成](https://github.com/opensearch-project/k-NN/issues/1942)に対する新しいアプローチにより、小さなセグメントに対して HNSW (Hierarchical Navigable Small World) インデックスをスキップしてオーバーヘッドを回避することで、インデックスの高速化が強化されています。

### 検索パイプライン出力の改善

OpenSearch 2.18 では、[ML 推論検索レスポンスプロセッサ](https://opensearch.org/docs/latest/search-plugins/search-pipelines/ml-inference-search-response/)にいくつかの改善が導入されています。ML モデルによって生成された予測を、ヒットにのみ書き込むのではなく、検索レスポンス内の `ext.ml_inference` 検索拡張に保存できるようになり、GenAI ユースケースでより柔軟な結果処理が可能になりました。リランキングのユースケースでは、ドキュメントと一緒にクエリテキストをモデル入力データセットに渡す機能が提供され、よりコンテキストを考慮した予測がサポートされています。さらに、リランクプロセッサと組み合わせることで、ML 推論検索レスポンスプロセッサは検索ヒットをランク付けし、モデルの予測に基づいてスコアを更新できるようになりました。これらの機能強化により、検索パイプラインへの ML モデルの統合が改善され、より洗練されたコンテキスト対応のドキュメントランキングと結果の拡張が可能になります。

### フィールドによるリランクで検索結果を強化

このリリースでは、OpenSearch の[リランクプロセッサ](https://opensearch.org/docs/latest/search-plugins/search-pipelines/rerank-processor/)に `ByField` という[新しいリランカータイプ](https://opensearch.org/docs/latest/search-plugins/search-pipelines/rerank-processor/#the-ml_opensearch-reranker-type)が導入されています。これにより、指定したターゲットフィールドに基づいて検索結果の二次リランクを実行できます。特に、以前のドキュメント検索結果から数値スコアを適用する場合に、より高い検索関連性を実現できます。以前の検索レスポンスプロセッサ (ML 推論プロセッサによって生成されたものなど) が検索ヒットに数値結果を追加した場合、この新しいリランクタイプを使用してそのフィールドに基づいてランキングを調整できます。また、元のスコアを保持することもできるため、調整された検索関連性が期待通りかどうかを簡単に評価できます。これにより、以前のスコアで結果をリランクし、必要に応じて最初の開始点に戻ることができます。

## 検索

このリリースでは、検索操作を強化する新機能も提供されています。

### Multi-search API を通じた検索パイプラインの定義

以前の OpenSearch バージョンでは、[Multi-search API](https://opensearch.org/docs/latest/api-reference/multi-search/) のユーザーはインデックスにデフォルトの検索パイプラインを定義する必要があり、検索パイプラインを効果的にデプロイする能力が制限されていました。OpenSearch 2.18 では、Multi-search API リクエストボディで直接 `search_pipeline` パラメータを定義できるようになり、検索操作に対するより大きな柔軟性と制御が可能になりました。以下は、Multi-search API を通じてパラメータを定義する例です。

```json
{ "index": "test"}
{ "query": { "match_all": {} }, "from": 0, "size": 10, "search_pipeline": "my_pipeline"}
{ "index": "test-1", "search_type": "dfs_query_then_fetch"}
{ "query": { "match_all": {} }, "search_pipeline": "my_pipeline1" }
```

## コスト、パフォーマンス、スケーラビリティ

このリリースには、OpenSearch クラスターのコスト、パフォーマンス、スケーラビリティの改善に役立つアップデートが含まれています。

### クラスター統計のワークロード削減と大規模環境でのトラブルシューティングの最適化

OpenSearch 2.18 では、`_cat/indices` と `_cat/shards` 用の新しい[ページネーション API](https://opensearch.org/docs/latest/api-reference/list/index) が導入されています。`_cat API` はクラスターの問題をトラブルシューティングする際に便利ですが、大規模なクラスターではスケールしにくく、リクエストを受信するノードに大きなオーバーヘッドが発生し、レスポンスサイズが大きいためにタイムアウトが発生することがあります。新しいページネーション API は `_list/indices` および `_list/shards` API としてアクセスできます。インデックス/シャードのレスポンスは一度に 1 ページずつ返され、`next` トークンを使用して追加のページをリクエストできます。インデックス/シャードの統計はリクエストされたページに対してのみ収集・集計されるため、大規模なクラスターでの API のスケーラビリティが大幅に向上します。このリリースでは、Cluster Stats API のメトリックフィルターも導入されています。この API はインデックス、シャード、ノードに関連する完全なクラスター統計を提供します。大規模なクラスターでこれらの統計を計算すると、コストのかかるオーバーヘッドが発生する可能性があります。この API では、入力でフィルターを指定してクラスター統計の特定のサブセットのみを取得するオプションが提供されるようになり、クラスターに過度の負担をかけることなく必要な統計を取得できます。

## 安定性、可用性、回復力

OpenSearch 2.18 では、OpenSearch デプロイメントの安定性、可用性、回復力の維持に役立つ機能も追加されています。

### 強化されたクエリグルーピングでリソース集約型のクエリパターンを特定

[Top N クエリ](https://opensearch.org/docs/latest/observing-your-data/query-insights/top-n-queries/)のモニタリングは、特定の時間枠内でレイテンシ、CPU、メモリ使用量などのメトリクスに基づいて、最もリソースを消費するクエリを特定するのに役立ちます。しかし、非常に負荷の高いクエリが繰り返し実行されると、Top N のスロットを独占し、他のリソース集約型クエリが見えなくなる可能性があります。これを克服するために、類似性によるクエリのグルーピングは、個々のインスタンスではなく、さまざまな高影響クエリパターンに関する洞察を提供できます。OpenSearch 2.17 では、同じクエリ構造を共有するクエリをグルーピングする[類似性によるグルーピング](https://opensearch.org/docs/latest/observing-your-data/query-insights/grouping-top-n-queries/#grouping-queries-by-similarity)が可能でした。バージョン 2.18 では、このグルーピング機能がフィールド名とデータ型も考慮するように強化され、より細かいレベルでクエリをグルーピングできるようになりました。これにより、さらに正確なクエリグルーピングが可能になり、多様なクエリタイプにわたるリソース集約型クエリパターンの特定と分析が改善されます。

## 使いやすさ

このリリースでは、OpenSearch の体験、操作、コラボレーションの方法を変革するように設計された新機能が導入されています。

### Workspace でチーム間の作成とコラボレーション

OpenSearch 2.18 では、チームコラボレーションを強化するために設計されたマルチテナント環境である [Workspace](https://opensearch.org/docs/latest/dashboards/workspace/workspace/) が導入されています。OpenSearch Dashboards でのインデックスパターン、ダッシュボード、保存されたオブジェクトのテナントレベルの「分離された」スペースの価値について、コミュニティから多くのフィードバックを受けてきました。このリリースでは、きめ細かいアクセス制御でコラボレーションを管理し、ワークスペースにコラボレーターを簡単に追加または削除し、ワークスペースレベルで権限を制御できるようになりました。ワークスペースの作成者として、ロールベースの権限を割り当てることができます。ワークスペースにアクセスしてデータの可視化を表示するだけの関係者には「読み取り専用」、保存されたオブジェクトを作成・更新する必要がある同僚には「読み取りと書き込み」、読み取り、書き込み、設定の構成、またはワークスペースの削除の完全な権限が必要な共同所有者には「管理者」を割り当てられます。さらに、5 つのワークスペースタイプがあり、それぞれ異なるユースケースに合わせて調整されています。Security Analytics、オブザーバビリティ、検索、エッセンシャル、アナリティクスの各タイプには、カスタマイズされた体験を提供する異なる利用可能な機能セットがあります。Workspace へのアクセス方法については、[ドキュメント](https://opensearch.org/docs/latest/dashboards/workspace/workspace/#enabling-the-workspace-feature)を参照してください。

### 再設計されたホームページとナビゲーション構造で効率を向上しワークフローを簡素化

OpenSearch 2.18 では、より豊かでユーザーフレンドリーな体験を提供する再設計されたホームページとナビゲーション構造がデビューしています。新しい OpenSearch ホームページは中央ハブとして機能し、ユーザーがワークスペースにアクセスして作成するための明確な経路を提供します。再設計されたナビゲーション構造は複雑なメニューから離れ、選択したワークスペースに適応し、各ユースケースに合わせたワークフローをサポートする、よりクリーンで整理されたナビゲーションバーを提供します。ワークスペースが選択されると、ユーザーは特定のタスクに適した環境が表示されます。各ワークスペースタイプは、チームがより効率的に作業できるように、専用のツール、ビュー、ナビゲーションパスを提供します。合理化された「はじめに」ガイドは、新規ユーザーのプロセスを簡素化し、ニーズに基づいて主要な機能に誘導します。セキュリティインシデントの管理、データ分析の実施、インフラストラクチャの監視など、ユーザーはより少ないクリックで必要なツールにアクセスできます。これらのアップデートは、チーム間のデータ管理、分析、コラボレーションを合理化し、複雑さを軽減して生産性を向上させることを目的としています。

### 更新された Discover インターフェースでデータをクエリし洞察を効率化

新しい実験的な [Discover](https://opensearch.org/docs/latest/dashboards/discover/index-discover/) インターフェースは、クエリ体験を強化し、より多くのカスタマイズオプションを提供します。このインターフェースにより、アナリストは未使用のセクションを折りたたんでワークスペースを合理化できます。過去 1 年間、Log Explorer (オブザーバビリティ用) の Piped Processing Language (PPL) や Query Workbench の SQL など、OpenSearch のクエリインターフェース全体でユーザーから貴重なフィードバックを収集してきました。これに応えて、Dashboards Query Language (DQL) と Lucene に加えて、PPL と SQL を Discover のクエリオプションとして追加し、アナリストが好みのクエリ言語を使用できるようにしています。また、データセレクターを改善し、非常に要望の多かったオートコンプリート機能を追加しました。新しい体験はフィーチャーフラグの背後で利用可能で、**Dashboards Management** に移動し、**Advanced Settings** を選択し、「Enable query enhancements」を ON に切り替えることで有効にできます。[この機能に関するフィードバック](https://github.com/opensearch-project/OpenSearch-Dashboards/issues/8813)をお待ちしており、新しい Discover 体験が一般提供されるバージョン 2.21 までコミュニティの意見を収集します。さらに、Vega ベースの可視化用に VisBuilder に新しい円グラフの可視化を導入しました。試すには、**Advanced Settings** で「Enable vega transformation in visbuilder」を有効にしてください。

## OpenSearch 2.18 を探索する

本日のリリースは[ダウンロード可能](https://www.opensearch.org/downloads.html)で、[OpenSearch Playground](https://playground.opensearch.org/app/home#/) で探索できます。このリリースの詳細については、[リリースノート](https://github.com/opensearch-project/opensearch-build/blob/main/release-notes/opensearch-release-notes-2.18.0.md)および[ドキュメントリリースノート](https://github.com/opensearch-project/documentation-website/blob/main/release-notes/opensearch-documentation-release-notes-2.18.0.md)をご確認ください。いつものように、[コミュニティフォーラム](https://forum.opensearch.org/)または [OpenSearch Slack ワークスペース](https://opensearch.org/slack.html)でこのリリースに関するフィードバックをお寄せください。
