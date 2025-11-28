---
title: "[翻訳] OpenSearch Benchmark: 最新アップデート"
emoji: "📊"
type: "tech"
topics: ["opensearch", "benchmark", "performance", "testing"]
published: false
publication_name: "opensearch"
published_at: 2025-05-12
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/opensearch-benchmark-an-update/

[OpenSearch](https://opensearch.org/) のユーザーやコントリビューターであれば、OpenSearch のパフォーマンスベンチマークツールである [OpenSearch Benchmark](https://opensearch.org/docs/latest/benchmark/) をご存知かもしれません。OpenSearch Benchmark は、さまざまな状況で OpenSearch のパフォーマンスを測定、追跡、改善するために、開発者や組織で広く使用されています。本記事では、プロジェクトの現状と、今後予定されている機能強化や新機能についてご紹介します。

## OpenSearch Benchmark プロジェクト

OpenSearch が Elasticsearch からフォークされたのと同時期に、OpenSearch Benchmark は Rally のフォークとして公開されました。約 2 年前から多くの改善が加えられ、バグが修正され、定期的なリリースサイクルが確立されました。それ以来、このツールは大幅に堅牢性、信頼性、使いやすさが向上しています。また、検索パフォーマンスを比較するための [`big5`](https://github.com/opensearch-project/opensearch-benchmark-workloads/tree/main/big5) や、生成 AI や機械学習アプリケーションに関連する[ベクトル検索](https://github.com/opensearch-project/opensearch-benchmark-workloads/tree/main/vectorsearch)や[ニューラル検索](https://github.com/opensearch-project/opensearch-benchmark-workloads/tree/main/neural_search)などの分野における新しいワークロードも追加されています。

OpenSearch Benchmark チームは、コミュニティが OpenSearch のパフォーマンスを追跡するために依存している[公式ベンチマーク結果](https://benchmarks.opensearch.org/)の公開も担当しています。

### OpenSearch Benchmark を使う理由

OpenSearch Benchmark は、OpenSearch のパフォーマンステストに最適な選択肢です。OpenSearch 本体を開発しているチームと同じメンバーによって作られているためです。OpenSearch のデプロイメントを運用している場合、エンドツーエンドのシステムテストを実行する最も簡単で迅速な方法は、OpenSearch Benchmark のワークロードを実行することです。

OpenSearch Benchmark は、基本的なテスト、概念実証、さらには本番環境でも使用できます。検索、ログ、ベクトルワークロードのテストに最適です。集計、日付ヒストグラム、Neural プラグインを使用した AI 搭載検索、k-NN アルゴリズムなどのクエリで OpenSearch のパフォーマンスをテストできます。ある意味で、OpenSearch Benchmark はスイスアーミーナイフのような機能を持つアプリケーションです。クラスターのサイジング、適切なシャード数のチューニング、新しいバージョンへのアップグレードでパフォーマンスが低下しないことの確認、さらには本番ワークロードのカプセル化にも使用できます。

[Trail of Bits](https://www.trailofbits.com/) などの独立したサードパーティは、[OpenSearch と Elasticsearch の比較パフォーマンステスト](https://blog.trailofbits.com/2025/03/06/benchmarking-opensearch-and-elasticsearch/)を実行するための推奨ベンチマークツールとして OpenSearch Benchmark を使用しています。

### OpenSearch Benchmark の使い方

OpenSearch Benchmark を始める最も簡単な方法は、[クイックスタート](https://docs.opensearch.org/docs/latest/benchmark/quickstart/)ガイドに従うことです。より深く学びたい場合は、OpenSearch Benchmark の[ユーザーガイド](https://docs.opensearch.org/docs/latest/benchmark/user-guide/index/)と[リファレンス](https://docs.opensearch.org/docs/latest/benchmark/reference/index/)セクションをご覧ください。

OpenSearch Benchmark のドキュメントに対するフィードバックや機能強化の提案がある場合は、[Issue を作成](https://github.com/opensearch-project/documentation-website/)してください。

### 今後の機能強化と新機能

プロジェクトのロードマップには、多くの新しい機能強化と機能が予定されています。

* 新しい生成 AI ワークロード
* 本番ワークロードを代表的なカスタム OpenSearch Benchmark ワークロードにカプセル化する機能
* データストリーミングによる大規模データコーパスのサポート
* 特定のビジネスユースケースをテストするための合成データ生成機能
* 段階的なランプアップを含むレッドラインテストなど、大規模な OpenSearch の負荷テストを容易にする機能
* 長期耐久テストとカオステスト

新しい開発情報を把握する最良の方法は、プロジェクトに関連する [RFC と GitHub Issue](https://github.com/opensearch-project/opensearch-benchmark/issues) を追跡し、定期的に [OpenSearch Benchmark ロードマップ](https://github.com/orgs/opensearch-project/projects/219)を確認することです。

### コントリビューションに興味がありますか？

OpenSearch Benchmark プロジェクトは過去 2 年間で大きな進歩を遂げましたが、皆さんの協力が必要です！開発者、ユーザー、レビュアー、メンテナーなど、誰もが OpenSearch Benchmark を最高のベンチマークアプリケーションにするために貢献できます。コントリビューションに興味がある方は、OpenSearch Benchmark の[コントリビューションガイド](https://github.com/opensearch-project/opensearch-benchmark/blob/main/CONTRIBUTING.md)をご覧いただくか、[OpenSearch Benchmark コミュニティミートアップ](https://www.meetup.com/opensearch/events/307446531/?eventOrigin=group_upcoming_events)にご参加ください。
