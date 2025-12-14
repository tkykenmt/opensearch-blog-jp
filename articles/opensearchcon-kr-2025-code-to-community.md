---
title: "OpenSearchCon Korea 2025: コードからコミュニティへ"
emoji: "🌐"
type: "tech"
topics: ["opensearch", "opensource", "community", "linuxfoundation"]
published: false
---

:::message
本記事は [OpenSearch Project YouTube チャンネル](https://www.youtube.com/@OpenSearchProject) で公開されているセッション動画の内容を日本語で書き起こしたものです。
:::

**イベント**: [OpenSearchCon Korea 2025](https://www.youtube.com/playlist?list=PLzgr9zSpws16DPeI08ZXYQI2zz-EuJfyA)
**プレゼンター**: Andrew Ross, Principal Engineer, AWS

https://www.youtube.com/watch?v=FdVvrNUkvAk

※ 本記事は動画の自動字幕を基に作成しています。誤字脱字や誤った内容が含まれる可能性があります。

## はじめに

このセッションでは、OpenSearch が Linux Foundation に参加してからの 13 ヶ月間の変化と、コミュニティ主導のイノベーションについて解説します。オープンガバナンス、オープンコラボレーション、そしてイノベーションの加速という 3 つの主要なテーマを中心に、具体的な貢献事例を紹介します。

## 本編

[![Thumbnail](/images/opensearchcon-kr-2025-code-to-community/thumbnail_5.jpg)](https://www.youtube.com/watch?v=FdVvrNUkvAk&t=5)

### 自己紹介と本日のテーマ

皆さん、本日 OpenSearchCon にご参加いただきありがとうございます。私は Andrew Ross です。AWS のプリンシパルエンジニアで、日々の業務の多くをコア OpenSearch リポジトリのメンテナー作業に費やしています。また、今年 OpenSearch Technical Steering Committee（TSC）の議長に選出されたことを光栄に思っています。

本日は、Linux Foundation に参加してからの OpenSearch についてお話しします。しかし、本当にお伝えしたいのは、コミュニティ主導のイノベーションについてです。

[![Thumbnail](/images/opensearchcon-kr-2025-code-to-community/thumbnail_60.jpg)](https://www.youtube.com/watch?v=FdVvrNUkvAk&t=60)

### Linux Foundation 参加後の変化

OpenSearch が 13 ヶ月前に Linux Foundation に参加したとき、多くのことが変わりました。プロジェクトとそのソフトウェアをサポートする非営利組織として、OpenSearch Software Foundation を立ち上げました。

これにより、プロジェクト管理においてベンダーニュートラルなアプローチが実現し、持続可能な長期的成長のための基盤が提供されました。また、12 社以上の企業が Foundation に参加しました。

ベンダーニュートラルでコミュニティ主導のアプローチにより、オープンソースプロジェクトへの貢献の場が急速に平等化され、すぐに成果が見え始めました。

[![Thumbnail](/images/opensearchcon-kr-2025-code-to-community/thumbnail_180.jpg)](https://www.youtube.com/watch?v=FdVvrNUkvAk&t=180)

### 3 つの主要なメリット

Linux Foundation に参加することで、3 つの主要なメリットがありました。

1. **オープンガバナンスへの移行**: 意思決定が透明で包括的なモデルを意味します
2. **オープンコラボレーション**: 一緒に、公開で作業することで、プロジェクトを成功裏に構築・成長させます
3. **イノベーションの加速**: 最初の 2 つの結果として、より多くの組織からより多くの貢献者が OpenSearch に賭けるようになると、イノベーションが加速し、長期的に複利効果を生みます

### オープンガバナンス

オープンガバナンスとは、コミュニティ主導、コミュニティリード、そして独立を意味します。具体的な例として、Governing Board と Technical Steering Committee について説明します。

**Governing Board**: Foundation を導く選出された理事会です。理事会は、Foundation を財政的に支援することを約束した組織から構成されており、OpenSearch の成長やこのようなイベントの開催を支援しています。AWS、Aiven、DataStax、SAP、Uber のステークホルダーと協力して Foundation の活動を監督できることを光栄に思います。

**Technical Steering Committee (TSC)**: プロジェクトの技術的方向性をリードするために設立されており、重要な役割を果たしています。TSC のメンバーシップは、技術的リーダーシップと貢献を認めるように設計されており、実績に基づいて毎年選挙が行われます。各メンバーは 2 年の任期を務め、毎年半数が改選されます。

実際、1 周年を迎えた際に最初の選挙を完了し、その結果、これまでで最も多様な委員会となりました。15 名のメンバーが 11 の異なる組織を代表しています。

[![Thumbnail](/images/opensearchcon-kr-2025-code-to-community/thumbnail_360.jpg)](https://www.youtube.com/watch?v=FdVvrNUkvAk&t=360)

### Technical Advisory Groups (TAGs)

TSC の一部として、Technical Advisory Groups（TAGs）を紹介したいと思います。TAGs は、OpenSearch 内の特定の技術ドメインに焦点を当てた専門グループです。各 TAG は、貢献者、メンテナー、ユーザー、そして特定のドメインに専門知識を持つあらゆる専門家を集めます。

TAGs の目的は、ドメイン固有の課題についての深い議論を可能にすることです。各 TAG は公開で運営され、公開ミーティングを開催し、独自のロードマップを維持し、決定を透明に文書化します。

TAGs は TSC がガバナンスをスケールするための重要なメカニズムです。すべての議論が TSC レベルで行われる必要はなく、TSC がすべてのドメインに専門知識を持っているわけではありません。

現在、2 つの TAG があります：
- **Build TAG**: OpenSearch インフラストラクチャの健全性と 120 以上のリポジトリ全体でのプロジェクト標準の整合に焦点を当てています
- **Observability TAG**: OpenSearch エコシステム内のオブザーバビリティソリューションの戦略的方向性と技術的ガイダンスを推進しています

さらに、Security TAG と Search TAG の 2 つが提案されています。

[![Thumbnail](/images/opensearchcon-kr-2025-code-to-community/thumbnail_540.jpg)](https://www.youtube.com/watch?v=FdVvrNUkvAk&t=540)

### オープンコラボレーションの成果

オープンコラボレーションは OpenSearch の原動力であり、数字にそれが表れています。強調したい大きな数字は、OpenSearch が貢献者数でランク付けされた Linux Foundation プロジェクトの中で、70 位からトップ 20 内（現在 19 位）に上昇したことです。

これらの数字は、成長する活気あるオープンソースエコシステムを示しています。

### 具体的な貢献事例

過去 1 年間の具体的な貢献事例をいくつか紹介します。これらには共通点があります：ある企業が OpenSearch に何かをより良くしてほしい、または以前はできなかったことをしてほしいと思い、それを実装し、オープンソースなのでプロジェクトに還元され、コミュニティ全体が恩恵を受けるということです。

[![Thumbnail](/images/opensearchcon-kr-2025-code-to-community/thumbnail_720.jpg)](https://www.youtube.com/watch?v=FdVvrNUkvAk&t=720)

#### Uber: ネイティブ gRPC API

Uber は OpenSearch Software Foundation に早期に参加し、すぐに貢献を始めました。最初に取り組んだ大きな課題の 1 つは、OpenSearch にネイティブ gRPC API を実装することでした。

Uber はミッションクリティカルなサービスを支える大規模な検索インフラストラクチャを運用しており、毎秒数千のクエリを処理しています。既存の HTTP JSON ベースのプロトコルにいくつかの課題がありました：

- テキストベースのプロトコルの非効率性（特に大きなペイロードの場合）
- スケールが拡大し続ける中でのデータ伝送効率の向上の必要性
- Uber 内の既存サービスで使用されている gRPC の成熟したエコシステムとの統合

Uber は OpenSearch をその既存のエコシステムに適合させたいと考え、gRPC サポートを実装しました。

[![Thumbnail](/images/opensearchcon-kr-2025-code-to-community/thumbnail_900.jpg)](https://www.youtube.com/watch?v=FdVvrNUkvAk&t=900)

#### SAP: Star Tree インデックス

SAP は、集計クエリのパフォーマンスを大幅に向上させる Star Tree インデックスを貢献しました。これは、事前に集計されたデータを特殊なインデックス構造に格納することで、複雑な集計クエリを高速化する機能です。

#### Atlassian: Kubernetes オペレーター

Atlassian は、Kubernetes 上での OpenSearch のデプロイと管理を簡素化する Kubernetes オペレーターを貢献しました。これにより、クラウドネイティブ環境での OpenSearch の運用が大幅に容易になりました。

[![Thumbnail](/images/opensearchcon-kr-2025-code-to-community/thumbnail_1080.jpg)](https://www.youtube.com/watch?v=FdVvrNUkvAk&t=1080)

### イノベーションの加速

コミュニティ主導のアプローチにより、イノベーションが加速しています。主要な技術的進歩には以下が含まれます：

- **ベクトル検索の強化**: AI/ML ワークロードをサポートするための継続的な改善
- **パフォーマンスの最適化**: 検索レイテンシーとスループットの向上
- **オブザーバビリティ機能**: Query Insights やライブクエリモニタリングなどの新機能
- **セキュリティの強化**: エンタープライズグレードのセキュリティ機能

[![Thumbnail](/images/opensearchcon-kr-2025-code-to-community/thumbnail_1260.jpg)](https://www.youtube.com/watch?v=FdVvrNUkvAk&t=1260)

### コミュニティへの参加方法

OpenSearch コミュニティに参加する方法はたくさんあります：

1. **GitHub での貢献**: コードの貢献、バグ報告、機能リクエスト
2. **TAG への参加**: 専門分野での議論に参加
3. **フォーラムでの活動**: 質問への回答、知識の共有
4. **イベントへの参加**: OpenSearchCon などのイベントでのネットワーキング

[![Thumbnail](/images/opensearchcon-kr-2025-code-to-community/thumbnail_1440.jpg)](https://www.youtube.com/watch?v=FdVvrNUkvAk&t=1440)

## まとめ

OpenSearch が Linux Foundation に参加してからの 13 ヶ月間で、オープンガバナンス、オープンコラボレーション、イノベーションの加速という 3 つの主要な成果を達成しました。

ベンダーニュートラルでコミュニティ主導のアプローチにより、Uber、SAP、Atlassian などの企業からの重要な貢献が実現し、プロジェクト全体が恩恵を受けています。

Technical Steering Committee と Technical Advisory Groups を通じて、透明で包括的なガバナンスモデルが確立され、コミュニティ全体がプロジェクトの方向性に参加できるようになりました。

OpenSearch の未来は、コミュニティの皆さんの手にあります。ぜひ参加して、一緒にプロジェクトを成長させましょう。

詳細については、以下のリソースを参照してください：
- [OpenSearch Software Foundation](https://opensearch.org/foundation)
- [Technical Steering Committee GitHub](https://github.com/opensearch-project/tsc)
