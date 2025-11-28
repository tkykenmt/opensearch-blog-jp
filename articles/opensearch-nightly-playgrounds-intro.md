---
title: "[翻訳] OpenSearch Nightly Playgrounds の紹介"
emoji: "🎮"
type: "tech"
topics: ["opensearch", "aws", "cdk", "devops", "oss"]
published: true
publication_name: "opensearch"
published_at: 2024-11-07
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/introducing-the-nightly-playgrounds/

[Nightly Playgrounds](https://playground.nightly.opensearch.org/) を紹介します。これは、完全にデプロイされたディストリビューションクラスターで、OpenSearch と OpenSearch Dashboards の今後のバージョンを探索できる動的な環境です。このライブデモ環境は、最新の検証済みナイトリービルドアーティファクトを実行するクラスターをホストしており、[OpenSearch](https://build.ci.opensearch.org/view/Build/job/distribution-build-opensearch/) と [OpenSearch Dashboards](https://build.ci.opensearch.org/view/Build/job/distribution-build-opensearch-dashboards/) の 2.x および 3.x バージョンの最新機能へのプレビューアクセスを提供します。

Nightly Playgrounds の目標は、開発中の新機能を試し、早期にフィードバックを提供し、ディストリビューションに統合される改善を確認できるようにすることです。

## Nightly Playgrounds でできること

現在の [OpenSearch Playground](https://playground.opensearch.org/app/home) と同様に、Nightly Playgrounds では匿名の読み取り専用アクセスで新機能を試し、事前設定されたサンプルデータを探索できます。

### 新機能のプレビュー

OpenSearch や OpenSearch Dashboards のインストールや設定なしで、サンプルダッシュボード、可視化、データソースを操作できます。一晩で構築された新機能を探索し、最終リリースに貢献するフィードバックを提供できます。

### デバッグの高速化

Nightly Playgrounds は 2.16 リリース中に価値を証明し、Alerting Dashboards プラグインの問題を迅速に発見するのに役立ちました。これらのクラスターは、リリースサイクル中を含め、日常的なデバッグにいつでも使用できます。

### ドキュメント作成のサポート

OpenSearch のテクニカルライターは、[ドキュメントリポジトリ](https://opensearch.org/docs/latest/)に提出された新しいドキュメントの技術的な側面を検証するために Nightly Playgrounds を使用しています。これには、今後の機能、機能強化、修正に関するドキュメントが含まれます。OpenID Connect (OIDC) プロバイダーとしての GitHub 統合により、ドキュメントチームはアクセスが改善され、検証用の別々のクラスターが不要になり、ドキュメント開発が効率化されています。

## Nightly Playgrounds のセットアップ方法

Nightly Playgrounds は、AWS Cloud Development Kit (AWS CDK) を通じて管理される Amazon Elastic Compute Cloud (Amazon EC2) インスタンスに、OpenSearch と OpenSearch Dashboards の x64 Linux tarball を使用して毎日デプロイされます。GitHub Actions がデプロイを自動化し、クラウドインフラストラクチャとのスムーズな統合を確保しています。デフォルト設定に加えて、セキュリティ設定により GitHub が OIDC プロバイダーとして有効になり、制御されたアクセスが可能になります。Nightly Playgrounds は、高度にカスタマイズ可能なクラスターをデプロイするために [opensearch-cluster-cdk](https://github.com/opensearch-project/opensearch-cluster-cdk) に依存しています。

## FAQ

### Nightly Playgrounds にはどこからアクセスできますか？

Nightly Playgrounds は [Nightly Playground ウェブサイト](https://playground.nightly.opensearch.org/)で利用可能で、現在、今後の 2.x および 3.x リリースをサポートしています。探索したいバージョンを選択できます。

### デプロイされたディストリビューションのビルドに使用されたコミットを確認するには？

すべてのユーザーはこれらのクラスターへの読み取り専用アクセスを持っています。コンポーネント名、リポジトリ、GitHub リファレンス、コミット ID などの詳細を含むディストリビューションマニフェストは、クラスターに自動的にインデックスされます。取得するには、以下の手順を使用します。

1. 選択した Nightly Playground バージョンの OpenSearch Dashboards のトップメニューバーで、**Management > Dev Tools** に移動します。
2. マニフェストを取得するには、以下のコマンドを実行します。
   - OpenSearch コンポーネントの場合: `GET opensearch/_doc/1`
   - OpenSearch Dashboards コンポーネントの場合: `GET opensearch-dashboards/_doc/1`

レスポンスには、デプロイされたクラスター内のコンポーネントがコミット ID とアーティファクトの場所とともに表示されます。

### 特定のコンポーネントやプラグインが欠落しているのはなぜですか？

コンポーネントがディストリビューションから欠落している場合、ビルドに失敗した可能性があります。ナイトリービルドは、一部のコンポーネントで問題が発生しても継続され、個々のコンポーネントの失敗によって全体のビルドプロセスが影響を受けず、中断のない進行が可能になります。コンポーネントのビルドエラーを確認するには、コンポーネントのリポジトリにアクセスし、[こちら](https://github.com/opensearch-project/security-analytics/issues/904)のようなビルド失敗の autocut issue を検索してください。

### これらのクラスターにデータを追加するには？

GitHub [issue](https://github.com/opensearch-project/opensearch-devops/issues) を開くか、必要なデータを含むプルリクエストを送信できます。メンテナーは、クラスターにインデックスする前に、セキュリティと機密情報についてデータをレビューします。

### テストに追加の権限が必要な場合は？

最近、Nightly Playgrounds を OIDC プロバイダーとして GitHub と統合しました。現在、ログインしたすべてのユーザーはクラスターへの読み取り専用アクセスを持っています。将来的には、GitHub ハンドルをサポートすることでこれらの権限を強化する予定です。追加の権限をリクエストするには、GitHub [issue](https://github.com/opensearch-project/opensearch-devops/issues) を作成し、リクエストに GitHub ハンドルを含めてください。

## まとめ

コミュニティと開発者にとってさらに便利になるよう、Nightly Playgrounds を継続的に強化しており、新機能が利用可能になり次第探索できるようにしています。[GitHub](https://github.com/opensearch-project/opensearch-devops/tree/main/nightly-playground) で Infrastructure as Code を確認し、詳細については [meta issue](https://github.com/opensearch-project/opensearch-devops/issues/129) をフォローしてください。

フィードバックの共有、機能のリクエスト、Nightly Playgrounds をさらに価値あるものにするための貢献をいつでも歓迎します。皆様のご参加とサポートに感謝します！
