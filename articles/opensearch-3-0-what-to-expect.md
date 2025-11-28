---
title: "[翻訳] OpenSearch 3.0: 何が変わるのか"
emoji: "🚀"
type: "tech"
topics: ["opensearch", "lucene", "java", "elasticsearch", "検索エンジン"]
published: true
publication_name: "opensearch"
published_at: 2025-04-25
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/opensearch-3-0-what-to-expect/

OpenSearch 2.0 のリリースから 3 年、OpenSearch は Apache Lucene 10 のリリースを機に新しいメジャーバージョンの開発に着手しました。

なぜ新しいメジャーバージョンが必要なのでしょうか。[Lucene の v10 へのアップグレード](https://github.com/opensearch-project/OpenSearch/issues/11415)と [JVM の v21 へのアップグレード](https://github.com/opensearch-project/OpenSearch/issues/14011)は、OpenSearch のコアだけでなく、プラグインや OpenSearch Dashboards などのエコシステム全体に影響を与える破壊的変更を伴うためです。

また、JavaScript 3.0 クライアントでは Node.js 14 未満が非推奨となりました。OpenSearch のメンテナーによれば、これらの変更はプロジェクトをより将来性のあるものにするためのものです。

## 破壊的変更

このセクションでは、OpenSearch 3.0 における主要な破壊的変更について説明します。Apache Lucene 10 と JVM 21、そして Java Security Manager の削除です。

### Apache Lucene 10 と JVM 21

Apache Lucene が v10 にアップグレードされます。これに伴い、JVM は最低 v21 が必要となり、OpenSearch にいくつかの破壊的変更が発生します。これが 3.0 リリースの理由です。

JavaScript クライアントにも大きな変更があり、厳格なパラメータ命名規則 (キャメルケースは使用不可) や、互換性の問題を引き起こす可能性のある型システムの導入などが含まれます。

しかし、これらの破壊的変更は強力な新機能ももたらします。

Apache Lucene では、I/O と検索の並列処理の両方が改善されています。I/O については、データの非同期フェッチを可能にする API コールが追加されました。検索については、以前のセグメントグループ化による並列検索の方法から、セグメント内の論理パーティションを使用する方式に変更されました。

JVM が最低 21 に更新されることで、仮想スレッド、`switch` 文のパターンマッチング、シーケンスコレクションなど、[多くの利点](https://www.oracle.com/java/technologies/javase/21-relnote-issues.html)がもたらされます。

### Java Security Manager の削除

もう一つの大きな破壊的変更は、Java Security Manager の置き換えです。[JVM 24 以降で無効化される](https://openjdk.org/projects/jdk/24/)ため、OpenSearch のメンテナーはバージョン 3.0 で置き換えることを決定しました。

進捗を追跡する GitHub のメタイシューがあります。[GitHub メタイシュー](https://github.com/opensearch-project/OpenSearch/issues/16913)では、Java Security Manager を置き換える必要がある理由と、検討されたさまざまなオプションについての情報が提供されています。

変更内容については、[このメタイシュー](https://github.com/opensearch-project/OpenSearch/issues/17181)をご確認ください。

## 主要な新機能

このアップデートには多くの主要な新機能があります。このセクションでは、そのいくつかを詳しく説明します。

### Apache Lucene 10

Apache Lucene 10 へのアップグレードの理由は、パフォーマンスに大きく関係しています。Lucene 10 は、OpenSearch 2.x の前バージョンと比較して[多くのカテゴリでより高いパフォーマンス](https://github.com/opensearch-project/OpenSearch/issues/16934)を発揮します。前述のように、I/O パフォーマンスと並列タスク実行のパフォーマンスに大きな変更がありました。しかし、Lucene 10 には他にも変更があります。

- **スパースインデックス**: プライマリキーインデックスとも呼ばれ、スパースインデックスはデータをブロックに整理し、最小値と最大値を記録します。これにより、クエリ時に関連のないブロックをより効率的にスキップでき、CPU/ストレージの効率が向上します。これは、前述の I/O 並列処理の改善によって可能になりました。
- **k-NN/ニューラル検索の改善**: 並列検索の改善により、Lucene 10 では k-NN およびニューラル検索の並列実行が向上しました。また、ベクトルインデックスの改善も追加されています。I/O の並列化が改善されたことで、ベクトルの保存方法の最適化が真価を発揮し、よりスケーラブルなニューラル検索エンジンが実現しました。

Lucene 10 の改善点の詳細については、[変更履歴](https://lucene.apache.org/core/10_0_0/changes/Changes.html#v10.0.0)を参照してください。

### その他のパフォーマンス改善

Lucene 10 のアップグレードによる改善だけでなく、OpenSearch コミュニティは Big5 ベンチマークでのパフォーマンス向上に取り組んできました。3.0 は 2.x と比較して全体的にはるかに高いパフォーマンスを示しており、集計処理では OpenSearch 1.3 と比較して 8.4 倍ものパフォーマンス向上を達成しています。

### JavaScript 3.0 クライアント

OpenSearch JavaScript 3.0 クライアントはすでにリリースされており、TypeScript を公式にサポートしています。これは以前の非公式な方法よりもはるかに優れています。唯一の欠点は、新しいパラメータ名の強制と Node.js v14.x 未満の非推奨化です。これらは OpenSearch ワークロードに波及効果をもたらす可能性があります。また、[OpenSearch プロジェクトとの整合性を高める](https://github.com/opensearch-project/opensearch-js/issues/803)ために、内部アーキテクチャの全面的な見直しも行われました。

### OpenSearch Dashboards

![OpenSearch Dashboards](/images/opensearch-3-0-what-to-expect/dashboards.jpg)

OpenSearch Dashboards のコードも多くの内部的な見直しが行われました。多くの不要なコードが削除され、OpenSearch プロジェクトの他の部分とより密接に連携するようにいくつかの動作が変更されました。UI の変更もあり、上のスクリーンショットに示すように、Discovery ツールは完全に作り直され、更新されました。

### SQL プラグインの変更

最後に、SQL プラグインが更新されました。クエリの DSL 形式は非推奨となり、SQL での `DELETE` 文はサポートされなくなりました。DSL 形式を好む方には、多くの柔軟な代替手段があります。

- SQL
- Piped Processing Language (PPL): パイプラインベースのクエリ言語
- REST API に対するアプリケーションの作成
- 多数のクライアントライブラリの使用

SparkSQL コネクタも削除され、その統合を使用しているプロジェクトに影響があります。代わりに JDBC 接続を使用するか、Spark のリクエストライブラリを使用して OpenSearch の REST API と連携できます。

## OpenSearch 3.0 へのアップグレード

プロジェクトのメンテナーは、バージョン 3.0 がインプレースアップグレードとなるよう懸命に取り組んでおり、ローリングアップデートやブルーグリーンデプロイメントが可能です。ただし、プラグインのアップグレードは、それらのプラグインに波及した破壊的変更のため、少し難しいかもしれません。とはいえ、[このメタイシュー](https://github.com/opensearch-project/opensearch-build/issues/5243)では、2.x から 3.0 への破壊的変更ガイドが提供されています。

## まとめ

OpenSearch 3.0 は、セマンティックバージョニングに忠実に、アプリケーションに破壊的変更をもたらします。

OpenSearch 3.0 がロールアウトされる際には、プラグインとコードを監査して、新しいバージョンでも動作することを確認する必要があります。[新しくリリースされた 3.0.0-alpha1 でテスト](https://github.com/opensearch-project/opensearch-build/issues/3747)することもできます。待っている間に OpenSearch 2.x クラスターを立ち上げたい場合は、[Instaclustr](https://www.instaclustr.com/) がホスト型 OpenSearch サービスの[無料トライアル](https://console2.instaclustr.com/signup)を提供しています。最後に、OpenSearch 3.0 の変更点についてより深く掘り下げる今後の記事にご期待ください。
