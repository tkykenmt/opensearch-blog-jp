---
title: "[翻訳] ギャップを埋める: OpenSearch 長期サポート (LTS) ローンチの振り返り"
emoji: "🏛️"
type: "tech"
topics: ["opensearch", "lts", "foundation", "opensource"]
publication_name: "opensearch"
published: true
published_at: 2026-04-24
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/bridging-the-gap-recapping-the-launch-of-opensearch-long-term-support-lts/

先週、プラハで開催された [OpenSearchCon Europe](https://www.youtube.com/watch?v=0xefDLNWxKs&list=PLzgr9zSpws14VJOiJ-CC9cl8Hm7G2V61p) で、OpenSearch Project は多くの人が決定的な転換点と呼ぶマイルストーンに到達しました。このイベントでは、[CERN の Foundation への参加](https://opensearch.org/blog/cern-joins-the-opensearch-software-foundation/) から [OpenSearch 3.6](https://opensearch.org/blog/introducing-opensearch-3-6/) のリリースまで、多くのニュースが発表されました。なかでもエコシステム全体で話題を集め続けているのが、[長期サポート (LTS) プログラム](https://opensearch.org/long-term-support/) の正式ローンチです。

発表の興奮が一段落した今、なぜこの動きがコミュニティにとってこれほど画期的なのか、そしてプロジェクトの将来にとって何を意味するのかを振り返ります。

### なぜ LTS なのか。エンタープライズの現実への対応

OpenSearch Software Foundation のエグゼクティブディレクターである Bianca Lewis 氏が発表時に語ったように、LTS ローンチの決断は、大規模な採用の波とコミュニティからの直接的なフィードバックによって動機づけられました。

組織はオープンソースソフトウェアがもたらすイノベーションとデータ主権を求めていますが、ミッションクリティカルなワークロードに関しては、しばしば社内のハードルに直面します。セキュリティチームは文書化された SLA を必要とし、エンジニアリングチームは安定した予測可能なアップグレードパスを必要とします。LTS プログラムはこうした「論理的なステップ」に対応し、オープンソースの原則を犠牲にすることなく、企業が自信を持って OpenSearch を採用しやすくします。

### LTS プログラムの柱

LTS プログラムは、オープンソースの完全な自由を維持しながら、通常はプロプライエタリベンダーに関連付けられる安定性を提供するように設計されています。先週の発表の主なハイライトは以下のとおりです。

- **明確な 18 か月のサポートライフサイクル**: プロジェクトの途中でバージョンのサポートが切れるリスクを排除するため、LTS バージョンには最低 18 か月のサポートが提供されます。プログラムは OpenSearch 2.19 および 3.6 からスタートします。
- **SBOM に裏付けられたコンプライアンス**: 152 の OpenSearch リポジトリすべてをスキャンし、Software Bill of Materials (SBOM) のライブラリを作成しています。これにより、CRA のような現代の規制基準において重要な要件である、デプロイメントの出所とセキュリティ体制を組織が実証できるようになります。
- **透明性の高いセキュリティ体制**: プログラムでは、セキュリティ脆弱性の早期通知と、中および高重大度の脆弱性を開示から 60 日以内に対処するというコミットメントを導入しています。
- **認定ベンダーの選択**: [BigData Boutique](https://opensearch.org/solutions-providers/bigdataboutique)、[Eliatra](https://opensearch.org/solutions-providers/eliatra/)、[Resolve Technology](https://opensearch.org/solutions-providers/resolve-technology-ltd/)、[Seacom](https://opensearch.org/solutions-providers/seacom/) を含むプロフェッショナルプロバイダーの初期グループを審査・認定し、Foundation 認定の商用サポートを提供しています。

### 統一されたコードベース。「no-fork」コミットメント

このプログラムの重要な柱の 1 つが「no-fork」ポリシーです。LTS バージョン向けに開発されたすべてのバグ修正とセキュリティパッチは、アップストリームに還元する必要があります。これにより、コミュニティ全体がエンタープライズ主導の改善の恩恵を受けられ、ユーザーが単一のプロバイダーにロックインされることがなくなります。誰もが共有する統一されたオープンなコードベースに対する Foundation のコミットメントを改めて強化する取り組みです。

### 今後の予定

最初の LTS 指定リリースである [**OpenSearch 3.6**](https://opensearch.org/blog/introducing-opensearch-3-6/) は、安定性とイノベーションが出会ったときに何が可能になるかをすでに示しています。[**OpenSearch Observability Stack**](https://opensearch.org/platform/observability-stack/) と、[**OpenSearch Relevance Agent**](https://docs.opensearch.org/latest/search-plugins/search-relevance/relevance-agent/) のような AI 搭載ツールを統合することで、OpenSearch がエンタープライズにとって単一のインテリジェントな運用レイヤーとして機能する未来へと進んでいます。

今後 1 年を見据えると、LTS プログラムの成功は、より多くの企業がベンダーロックインから脱却し、より健全で革新的なオープンソースエコシステムに貢献できるよう支援することで促進される成長によって測られます。

プラハで一緒にこのマイルストーンを祝福してくださった皆さん、ありがとうございました。コミュニティがこの新しい基盤を活用してどのようにイノベーションを起こしていくのか、楽しみにしています。

### LTS プログラムの詳細

組織が OpenSearch の [**長期サポート (LTS) プログラム**](https://opensearch.org/long-term-support/) をどのように活用できるかについて参照してください。

https://www.youtube.com/watch?v=gdvEcu5-R2M
