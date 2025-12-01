---
title: "[翻訳] OpenSearch Observability TAG 発表: オープンソースオブザーバビリティの未来を共に形作る"
emoji: "🔭"
type: "tech"
topics: ["opensearch", "observability", "opentelemetry", "opensource"]
published: true
publication_name: "opensearch"
published_at: 2025-09-16
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/announcing-opensearch-observability-tag-shaping-open-source-observability-together/

## OpenSearch Observability TAG でオープンソースオブザーバビリティの未来を形作る

OpenSearch は、開発者がアプリケーションやインフラストラクチャに対する可視性を得られるよう支援し、システムの監視、デバッグ、最適化を容易にしています。強力な検索機能と柔軟な設計により、ログ、メトリクス、トレースなどのオブザーバビリティデータを扱うための有力な選択肢となっています。この成功は、活発なオープンソースコミュニティと、50 社以上のソリューションプロバイダーやパートナーからなる急速に拡大するエコシステムに支えられています。

プラットフォームの成長指標は、この広範な採用とコミュニティの関与を反映しています。プロジェクトは 10 億回以上のダウンロードを達成し、30 以上の組織から 1,000 人以上の開発者が貢献し、140 以上の GitHub リポジトリに拡大しています。検索、セキュリティ、AI/ML ワークフローなど、オブザーバビリティ以外のユースケースにも対応する OpenSearch スタックのコンポーネントが増加する中、スタック全体にわたるオブザーバビリティのエンドツーエンドの技術的視点が求められるようになりました。これは、拡大するエコシステムとネイティブに統合し、OpenTelemetry などの進化する標準に準拠した、統一されたコスト効率の高いオブザーバビリティソリューションを導くためです。

この勢いとコミュニティの高まるニーズを受けて、OpenSearch Project は [Observability Technical Advisory Group (TAG)](https://github.com/opensearch-project/technical-steering/tree/main/technical-advisory-groups/observability-tag) の設立を発表します。[Technical Steering Committee](https://github.com/opensearch-project/technical-steering) の下に設立されたこの新しいグループは、OpenSearch エコシステム内のオブザーバビリティソリューションをさらに強化するための戦略的方向性と技術的ガイダンスを提供します。Observability TAG は 2025 年 9 月 2 日に初回ミーティングを開催し、AWS、SAP、Apple、Hilti からの参加者が集まりました。また、Uber や Paessler など他の組織からのメンバーも含まれており、オブザーバビリティコミュニティの幅広い層を代表しています。

Observability TAG の目的は、さまざまなテレメトリシグナルの取り込み、保存、可視化に OpenSearch を効果的に実装するためのベストプラクティスを定義、提唱、普及させることです。このグループは、オブザーバビリティ関連のイニシアチブについて Technical Steering Committee に助言し、OpenSearch がオープンスタンダード、相互運用性、業界トレンド、コミュニティのニーズに沿うようにします。[TAG の完全なチャーターはこちら](https://github.com/opensearch-project/technical-steering/blob/main/technical-advisory-groups/observability-tag/charter.md)で確認できます。

### Observability TAG は以下の主要な領域に注力します。

- OpenSearch を使用したオブザーバビリティアプリケーションの技術的ガイダンスを提供します。これには、メトリクス、ログ、トレース、プロファイルのストレージ、取り込みパイプライン、可視化、ダッシュボード、アラートや異常検知などのプラグインが含まれます。
- OpenSearch のオブザーバビリティイニシアチブを業界トレンド、[CNCF オブザーバビリティガイドライン](https://github.com/cncf/tag-observability)、相互運用性標準に沿わせるため、OpenTelemetry、Prometheus、Jaeger、Fluent Bit などの外部プロジェクトと連携します。
- 取り込みパイプライン、アラート、可視化、運用監視を含む OpenSearch オブザーバビリティデプロイメントのベストプラクティスを確立し、コミュニティの成長と採用を促進します。

### メンバーシップと参加

Observability TAG の初期[メンバー](https://github.com/opensearch-project/technical-steering/blob/main/technical-advisory-groups/observability-tag/README.md)は、Orcun Berkem (Amazon)、Michael Froh (Uber)、Yupeng Fu (Uber)、Shenoy Pratik Gurudatt (Amazon)、Dotan Horovits (Amazon)、Jonah Kowall (Paessler)、Karsten Schnitter (SAP)、Mikhail Stepura (Apple)、Jürgen Walter (SAP)、Shuyi Zhang (Uber) です。

TAG への参加はコミュニティに開かれており、ミーティングは公開されています。興味のある方は誰でもミーティングに参加して、視点やアイデアを共有できます。TAG のメンバーでなくても、貢献や支援は可能です。メンバーになることに興味がある場合は、[参加方法はこちら](https://github.com/opensearch-project/technical-steering/blob/main/technical-advisory-groups/observability-tag/charter.md#eligibility)を参照してください。

すべての参加者は、敬意を持った包括的な環境を維持するため、OpenSearch Software Foundation の行動規範と TAG の運用ガイドラインを遵守することが求められます。

### 参加方法

Observability TAG はコミュニティの取り組みであり、皆さんの参加を歓迎します。

- TAG の[ガバナンスチャーター](https://github.com/opensearch-project/technical-steering/tree/main/technical-advisory-groups/observability-tag)を確認する
- [OpenSearch Slack](https://opensearch.org/slack/) に参加し、`#observability` チャンネルで議論に参加する
- [Observability TAG ミーティング](https://zoom-lfx.platform.linuxfoundation.org/meetings/os-tag-observability)に参加して意見を共有する
- OpenSearch フォーラムの `observability` カテゴリに参加する

私たちはオープンソースオブザーバビリティに情熱を持っており、コミュニティと共に前進することを楽しみにしています。Observability TAG からの最新情報をお待ちください。ぜひご参加ください。
