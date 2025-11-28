---
title: "[翻訳] OpenSearch Benchmark 2.0 の紹介"
emoji: "🚀"
type: "tech"
topics: ["opensearch", "benchmark", "performance"]
published: true
publication_name: "opensearch"
published_at: 2025-08-21
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/introducing-opensearch-benchmark-2-0/

OpenSearch Benchmark は、OpenSearch エコシステムにおけるパフォーマンステストのリファレンスアプリケーションとして、OpenSearch の誕生当初から存在してきました。開発者や組織が OpenSearch デプロイメントのパフォーマンスを測定、追跡、最適化するために広く採用されています。本日、OpenSearch Benchmark 2.0 のリリースを発表できることを嬉しく思います。これは、多くの改善を含み、ベンチマーク機能を複数の面で拡張した、より大胆で優れたバージョンです。

OpenSearch Benchmark は、OpenSearch がフォークされたのとほぼ同時期に登場しました。2023 年 5 月の最初のメジャーリリース以来、パフォーマンステストと新しい OpenSearch 機能の評価に広く使用されてきました。以下の実績が示すように、OpenSearch の決定版ベンチマークツールとしての地位を確立しています。

- PyPi で 15 のマイナーバージョンにわたり 265,000 回以上のダウンロード
- ブログ記事で引用されるほぼすべての OpenSearch パフォーマンス指標に使用
- クエリのリグレッション発見と OpenSearch の最適な設定の特定に不可欠なソリューション
- 負荷テスト、ストレステスト、サーバーレスオファリングに対するベンチマーク、本番ワークロードのシミュレーションなどの新機能
- 広く使用されている包括的な検索ワークロード ([Big5](https://github.com/IanHoang/opensearch-benchmark-workloads/tree/main/big5)) と 4 つの生成 AI ワークロード ([ベクトル検索](https://github.com/opensearch-project/opensearch-benchmark-workloads/tree/main/vectorsearch)や[ニューラル検索](https://github.com/opensearch-project/opensearch-benchmark-workloads/tree/main/neural_search)など) によるワークロードカバレッジの拡大
- コミュニティエンゲージメントの成長: メンテナー数が 3 倍、コントリビューター数が 5 倍に増加し、定期的なコミュニティミーティングとオフィスアワーを開催

プロジェクトの影響力はツール自体を超えて広がっています。OpenSearch Benchmark チームは、コミュニティが OpenSearch の進歩を追跡するために依存する[ベンチマーク結果を定期的に公開](https://opensearch.org/benchmarks/)しています。また、以下のテックトークに見られるように、カンファレンスでパフォーマンスツールの知見と専門知識を共有しています。

- [Unleash Your Cluster's Potential with OpenSearch Benchmark at OpenSearchCon EU 2024 in Berlin](https://www.youtube.com/watch?v=IKkZ0cQuMLI)
- [Maximizing OpenSearch Cluster Performance: A Comprehensive Benchmarking Approach at OpenSearchCon EU 2025 in Amsterdam](https://www.youtube.com/watch?v=yMIOeXuFN6U)
- [Recreating Workload Behavior is an Art, Not a Science at OpenSearchCon EU 2025 in Amsterdam](https://www.youtube.com/watch?v=vMeaAklGFwg)

OpenSearch Benchmark 2.0 は、この強固な基盤の上に構築され、ユーザーエクスペリエンスを向上させ、待望の機能を追加しています。

## OpenSearch Benchmark 2.0 の新機能

OpenSearch Benchmark 2.0 には以下の機能強化が含まれています。

### 合成データ生成

OpenSearch Benchmark には、一般的な OpenSearch ユースケースをカバーするクエリを含む汎用データコーパスを持つ 17 のワークロードがパッケージされています。これらのパッケージ済みワークロードはベースラインのパフォーマンス比較や OpenSearch バージョン間のパフォーマンス改善の追跡に適していますが、従来のベンチマークツールと同様に、実際の本番環境の固有の特性や動作を捉えることができないという共通の制限があります。

OpenSearch Benchmark は、合成データ生成によってこの制限に対処します。2.0 からは、OpenSearch インデックスマッピングを提供するだけで、プライバシーに準拠したデータセットを大規模に作成できます。この強力な機能はあらゆる複雑さのワークロードをサポートし、機密データを公開することなく本番シナリオを模倣できます。

### ストリーミングインジェスト

大量のデータを使用した負荷テストとスケールテストは、ベンチマークにおけるもう一つの課題でした。OpenSearch Benchmark の制限の一つは、パッケージ済みワークロードに含まれるデータコーパスのサイズが比較的小さいことでした。従来のクラスターでもサーバーレスオファリングでも、より大規模なデプロイメントに移行するユーザーは、スケールでのパフォーマンスを評価したいと考えています。合成データ生成はこれに役立ちますが、大規模なデータセットの管理は煩雑になる可能性があります。そのようなコーパスのダウンロード、解凍、パーティショニングには数時間かかることがあり、負荷生成ホストのディスク容量が不足する可能性もあります。

OpenSearch Benchmark 2.0 はストリーミングインジェストを搭載しており、データストリームから高速でドキュメントを継続的にインジェストできます。この機能は、ローカルに保存された静的コーパスに依存することなく、単一の負荷生成ホストを使用して 1 日あたり数テラバイトまでスケールします。これにより、前述の制約を克服し、OpenSearch デプロイメントで本番規模のパフォーマンステストを実施できます。合成データ生成と組み合わせることで、あらゆるビジネスシナリオのスケールテストを実施するための統合ソリューションが得られます。

### クラウドプロバイダー非依存

OpenSearch Benchmark 2.0 は、クラウドプロバイダーのロジックをプライマリワークフローから分離し、真にクラウド非依存なツールになりました。これにより、コミュニティは AWS、Google Cloud、Microsoft Azure などのさまざまなクラウドプロバイダーのサポートを追加でき、ベンチマークがより柔軟になります。

### ビジュアルレポート

OpenSearch Benchmark 2.0 はビジュアルレポート機能を導入し、生のテスト結果を共有可能な UI 生成レポートに変換できます。これにより、パフォーマンストレンドの分析と組織間での結果共有が容易になります。

### 改善された CLI

OpenSearch Benchmark 2.0 は、バージョン 1.X よりもはるかに直感的な CLI を提供し、ベンチマーク分野で一般的なシンプルな用語を使用しています。これにより、パフォーマンステスト用のより読みやすいスクリプトを作成できます。

| 1.X の用語 | 2.X の用語 |
| --- | --- |
| execute-test, test-execution-id, TestExecution | run, test-run, TestRun |
| results_publishing, results_publisher | reporting, publisher |
| provision-configs, provision-config-instances | cluster-configs, cluster-config-instances |
| load-worker-coordinator-hosts | worker-ips |

これらの新機能と変更により、OpenSearch Benchmark はシンプルで制約のあるベンチマークツールから、包括的なパフォーマンステストスイートへと変貌しました。従来のベンチマークの実行、クラスターの限界点の特定、合成データストリームのスケールテストなど、OpenSearch Benchmark 2.0 は OpenSearch デプロイメントを最適化し、ビジネス要件を満たすために必要な重要なツールを提供します。

## 今後の予定

OpenSearch Benchmark 2.0 には多くの新しいアップデートが含まれていますが、さらに多くの機能強化が予定されています。新しい開発を追跡し、将来のバージョンで何が予定されているかを確認するには、[OpenSearch Benchmark ロードマップ](https://github.com/orgs/opensearch-project/projects/219)を定期的に確認し、プロジェクトリポジトリの [RFC と GitHub Issues](https://github.com/opensearch-project/opensearch-benchmark/issues) を追跡することをお勧めします。

## 入手方法

OpenSearch Benchmark 2.0 は [PyPi](https://pypi.org/project/opensearch-benchmark/)、[Docker Hub](https://hub.docker.com/r/opensearchproject/opensearch-benchmark)、[Amazon Elastic Container Registry (Amazon ECR)](https://gallery.ecr.aws/opensearchproject/opensearch-benchmark) で利用可能です。

## コントリビューション

パフォーマンステストとイノベーションの世界では、常にやるべきことがあります。コントリビューションに興味がある方は、OpenSearch Benchmark の[コントリビューションガイド](https://github.com/opensearch-project/opensearch-benchmark/blob/main/CONTRIBUTING.md)を参照するか、[OpenSearch Benchmark コミュニティミートアップ](https://www.meetup.com/opensearch/events/307446531/?eventOrigin=group_upcoming_events)に参加してください。
