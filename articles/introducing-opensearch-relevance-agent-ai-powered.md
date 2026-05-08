---
title: "[翻訳] OpenSearch Relevance Agent の紹介: AI を活用した検索チューニング"
emoji: "🔍"
type: "tech"
topics: ["opensearch", "ai", "search", "relevance", "llm"]
publication_name: "opensearch"
published: true
published_at: 2026-05-05
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/introducing-opensearch-relevance-agent-ai-powered-search-tuning/

検索の関連性 (Relevance) 向上は、継続的な取り組みを必要とするプロセスです。ユーザーが尋ねる質問と、実際に求めているものとのバランスを取る必要があります。誰かが「apple」と検索したとき、その人が探しているのはスナックでしょうか、新しい携帯電話でしょうか、それとも株価でしょうか。

ほとんどのチームにとって、検索関連性の向上は 3 つの大きなハードルを越えることを意味します。

- **意図のギャップ**: 曖昧なクエリを解釈し、precision (関連する結果のみを返す) と recall (十分な数の結果を返す) のバランスを取ること。
- **データとの格闘**: 「ノイズの多い」メタデータや、情報が疎で不完全なニッチなデータセットへの対応。
- **スケールの問題**: 小さなテスト環境でうまく動くものが、本番トラフィックの混沌とした大量のリアリティの下ではしばしば失敗します。

**TL;DR**

- OpenSearch Dashboards の自然言語インターフェースを通じて検索関連性チューニングを自動化する AI 搭載エージェント
- 3 つのエージェントがクエリパターンを分析し、チューニング戦略を生成し、改善を自動的に検証
- 関連性の診断を数日から数時間に短縮。検索の深い専門知識は不要
- Human-in-the-loop: ユーザーが方向を決め、エージェントが実行
- OpenSearch 3.6 の実験的機能として [Agent Server リポジトリ](https://github.com/opensearch-project/opensearch-agent-server) 経由で利用可能

## 手動チューニングの問題

従来、関連性のチューニングはマラソンでした。「完璧な」設定を見つけるために、検索の専門家による数か月にわたる手動の調整が必要になることが多かったのです。しかし、現代のエンタープライズではデータは静止していません。季節的なトレンドや進化する商品カタログは、人間が適応できるよりも速く検索空間を拡大します。

これにより、組織は事後対応型チューニングのサイクルに陥り、何百万ものユニークなクエリにわたって高品質な結果を維持するのに苦労しています。

## 検索品質の自動化

このサイクルを断ち切るために、OpenSearch Project は検索体験を最適化するより速く、よりスマートな方法を導入します。**OpenSearch Relevance Agent** は複雑なチューニングタスクを自動化するように設計されており、直感に基づくチューニングからデータ駆動型の精度へと、わずかな時間で移行できます。OpenSearch Relevance Agent は、ユーザー行動のシグナルとクエリパターンを継続的に分析し、データに基づいた仮説を生成し、厳密なオフライン評価を通じて改善を検証します。

OpenSearch Dashboards の会話型インターフェースを通じて、関連性の問題を対話的に特定し、ガイド付きのチューニング推奨を受け取り、自然言語を使用して複雑なワークフローを実行します。これにより、高度な関連性最適化があらゆるチームにとって利用しやすくなります。

OpenSearch Relevance Agent は、あらゆる環境で即座に価値を提供します。利用可能な場合は User Behavior Insights (UBI) データを使用してより深い最適化を行うように設計されていますが、関連性ワークフローの変革を始めるにあたって UBI は必須ではありません。今後のリリースでは、追加のデータソースへのサポートが追加される予定です。

Search Relevance Workbench の完全な機能を活用することで、OpenSearch Relevance Agent はエンドツーエンドの実験を可能にします。クエリセットと判定リストの作成から、制御されたテストの実行、標準的な関連性メトリクスを使用した影響の定量化まで対応します。このシステムは、関連性エンジニアリングの複雑さを抽象化する、体系的で自動化されたチューニングワークフローをオーケストレーションします。[OpenSearch 3.6](https://opensearch.org/blog/introducing-opensearch-3-6/) では、検索フィールドの洗練、ウェイトの調整、ブースト関数のチューニングといった、実用的なクエリ DSL レベルの最適化を通じて即座に効果をもたらします。

OpenSearch Relevance Agent は、バージョン 3.6 で実験的リリースとして OpenSearch Agent Server でサポートされるエージェントの 1 つです。[OpenSearch Agent Server](https://github.com/opensearch-project/opensearch-agent-server) は、OpenSearch 内で連携する特化した AI エージェントを構築できるマルチエージェントオーケストレーションプラットフォームです。

## チームがより良い検索をより速く提供できるようにする

OpenSearch Relevance Agent は、検索最適化へのアプローチを変革するいくつかの主要なメリットを提供します。

- **開発者の速度の加速**: 関連性の問題の*診断と修正にかかる時間*を、数日または数週間から数時間に短縮します。OpenSearch Relevance Agent は根本原因分析とチューニングワークフローを自動化し、迅速な反復とリリースサイクルの加速を可能にします。
- **関連性エンジニアリングの民主化**: 希少な検索関連性の専門家への依存を排除します。OpenSearch Relevance Agent は、ガイド付きのエージェント駆動ワークフローを通じて、あらゆる開発者や製品チームが自信を持って検索品質をチューニングできるようにし、組織全体での参入障壁を下げます。
- **エビデンスに基づく信頼**: 直感に基づくチューニングを**自動化された評価および検証ループ**に置き換えます。OpenSearch Relevance Agent は、実際のクエリとデータセットに対して継続的に変更をテストし、改善が測定可能かつ説明可能であり、意図しないリグレッションを伴わないことを保証します。
- **Human-in-the-loop の制御**: 協調的なアプローチを使用して、最適化プロセスの完全な監視を維持できます。OpenSearch Relevance Agent が複雑なタスクを自動化する一方で、ユーザーは究極の意思決定者であり続け、エージェントの方向を導き、重要なドメイン固有のコンテキストを提供し、推奨事項を洗練してユニークなビジネス要件や専門家の直感に完全に合致させます。

## 仕組み。OpenSearch 向けに構築されたマルチエージェントシステム

OpenSearch Relevance Agent を使用すると、検索改善サイクルの任意の段階で会話に参加できます。診断チェックから始める場合でも、即座に検証するための特定の仮説を持ち込む場合でも可能です。すべてを実行しようとする単一のボットではなく、Relevance Agent は、3 つのエージェントのワークフローで 3 人の専門家を管理する**オーケストレーター**が率いる特化したタスクフォースである**マルチエージェントシステム**を使用します。

1. **User Behavior Analysis Agent** は、UBI データ (利用可能な場合) またはクエリパターンを分析して関連性のギャップを特定します。
2. **Hypothesis Generator Agent** は、結果を解釈してデータに基づいたチューニング戦略を作成します。
3. **Evaluator Agent** は、Search Relevance Workbench 内のオフライン評価セットに対して自動テストを実行して戦略を検証します。

## 技術アーキテクチャ。OpenSearch プラットフォーム向けに構築

OpenSearch Relevance Agent は単なるスタンドアロンツールではありません。以下の図に示すように、既存の OpenSearch 環境に直接統合されます。

![](/images/introducing-opensearch-relevance-agent-ai-powered/8994828fef5f.png)

OpenSearch Relevance Agent のアーキテクチャは、次の主要コンポーネントで構成されています。

- **シームレスな統合**: **Strands SDK** 上に構築されたエージェントは、[**AG-UI 標準**](https://github.com/ag-ui-protocol/ag-ui) を通じて OpenSearch Dashboards のチャットに直接統合されます。
- **MCP サーバー**: すべてのエージェントは、[**OpenSearch Model Context Protocol (MCP) サーバー**](https://github.com/opensearch-project/opensearch-mcp-server-py/) を通じてのみ検索エンジンと通信します。この抽象化レイヤーは AI と検索エンジンの間の安全な翻訳者として機能し、OpenSearch Relevance Agent が標準化されたツールを通じて Search Relevance Workbench のフルパワーを活用できるようにします。
- **直感ではなく事実を**: システムは、エージェント環境内の特化したツールを使用して複雑なメトリック計算を処理します。これらの計算を大規模言語モデル (LLM) から決定論的ツールにオフロードすることで、OpenSearch Relevance Agent はハルシネーションや数学的な推定のリスクを大幅に減らし、報告される主要業績評価指標 (KPI) や関連性メトリクスのすべてが厳密でエラーのない分析に基づいていることを保証します。

## OpenSearch Relevance Agent を始める

OpenSearch Relevance Agent を数分で設定する手順で行います。

### 前提条件

クイックスタートスクリプトでは、Java 21+、Node.js 20+、Python 3.12+、[`uv`](https://astral.sh/uv)、yarn、`jq`、`curl` がインストールされている必要があります。また、Amazon Bedrock でホストされている LLM へのアクセスも必要です (追加のモデルプロバイダーは将来サポートされる予定です)。

**1. リポジトリをクローン**

まず、OpenSearch Agent Server のリポジトリをクローンし、プロジェクトフォルダに移動します。

```
git clone https://github.com/opensearch-project/opensearch-agent-server.git
```

**2. 環境変数を設定**

提供されているテンプレートからローカルの環境ファイルを作成します。

```
cp .env.example .env
```

お好みのエディタで `.env` ファイルを開き、Amazon Bedrock の認証情報と設定を追加します。

```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
BEDROCK_INFERENCE_PROFILE_ARN=arn:aws:bedrock:...
```

**注意事項:** AWS IAM ユーザーに Amazon Bedrock モデル呼び出しに必要な権限があることを確認してください。

**3. クイックスタートスクリプトの起動**

自動セットアップスクリプトを実行します。このスクリプトは、OpenSearch、OpenSearch Dashboards、OpenSearch Agent Server を含むすべての必要なコンポーネントをダウンロード、設定、起動します。

```
./scripts/quickstart.sh
```

通常、このプロセスには数分かかります。ブラウザに「OpenSearch Dashboards did not load properly」というエラーが表示された場合は、バックエンドサービスが完全に初期化されるまでさらに 2 〜 3 分待ってください。

**4. チューニングを開始**

セットアップが完了したら、[http://localhost:5601](http://localhost:5601) で OpenSearch Dashboards に移動します。

- OpenSearch Dashboards は事前設定された **Search Workspace** を自動的に開きます。
- 右上隅にある **「Ask AI」** ボタンを選択して、**OpenSearch Relevance Agent** インターフェースを開きます。
- 以下の動画に示すように、`What are "underperforming" queries of the past two years?` (過去 2 年間にパフォーマンスが低かったクエリは何か) というプロンプトを試してください。

https://www.youtube.com/watch?v=N5BL_iaKpJQ

エージェントはすぐに、クイックスタートスクリプトでインデックスされたサンプル UBI データの分析を開始し、発見の詳細なサマリーを提供します。

## 今後の予定

OpenSearch 3.6 は検索品質の合理化における大きな飛躍を示していますが、これは自律型関連性最適化というより広範なビジョンの始まりに過ぎません。関連性エンジニアリングをよりダイナミックで包括的、そしてますます自律的なものにするための将来の強化を計画しています。

### オンラインテストでループを閉じる

現在、OpenSearch Relevance Agent は履歴データを使用したオフライン評価に優れています。次の大きなマイルストーンは、改善サイクルを**オンライン本番環境**に拡張することです。OpenSearch Relevance Agent が**インターリービング**テスト、つまり異なるチューニング戦略の結果をリアルタイムで組み合わせる手法をオーケストレーションできるようにする計画です。ライブ環境でのユーザーのクリックパターンを分析することで、OpenSearch Relevance Agent は従来の A/B テストよりも速くユーザーフィードバックを捉えることができるようになり、さらに迅速で精密な反復が可能になります。

### 最適化対象の拡大

現在のバージョンの OpenSearch Relevance Agent は、強力なクエリ DSL レベルの調整に焦点を当てています。エージェントのツールボックスを拡張し、**複雑なインデックスレベルの操作**と**高度な最適化手法**を含めることを計画しています。

- **スキーマ進化**: サブフィールドの追加やトークナイザーの変更など、マッピングへの変更を推奨および実行します。
- **ベクトル検索とハイブリッド検索のチューニング**: k-NN パラメーターの最適化、およびハイブリッド検索アーキテクチャにおけるレキシカルとセマンティックの重みのバランス調整を行います。
- **自動化された Learning to Rank (LTR)**: 機械学習を使用して数百の特徴を同時に重み付けする高度なランキングモデルのトレーニングとデプロイ。OpenSearch Relevance Agent は、特徴エンジニアリングとモデルトレーニングのライフサイクルの自動化を支援し、手動のブースト関数を超えて完全に最適化されたランキング体験へと進みます。

### MCP を使用したユニバーサルデータ接続

OpenSearch Relevance Agent は OpenSearch のネイティブ UBI 機能を活用するように最適化されていますが、各組織には固有のデータプラットフォームがあることも認識しています。私たちのビジョンは、**MCP サーバー**を活用して外部シグナルと接続し、**Google Analytics**、**Matomo**、**Snowflake**、**BigQuery** のようなプラットフォームをモジュラーなデータソースとして扱うことで、OpenSearch Relevance Agent を真にデータに依存しないエンジンにすることです。これにより、OpenSearch Relevance Agent は、ユーザーの成功を追跡するために使用されるあらゆる信頼できる情報源に基づいて推奨事項を提供できるようになり、特化したプラグインから普遍的な関連性オーケストレーターへと変貌を遂げます。

## 貢献する方法

OpenSearch Relevance Agent は、OpenSearch Project プラットフォームの一部であるオープンソースプロジェクトであり、コミュニティの貢献によって成長します。新しい関連性機能のサポートを追加したい場合でも、relevance agent を改善したい場合でも、単に経験からのフィードバックを共有したい場合でも、皆さんの声をお聞きしたいと思います。[リポジトリをクローン](https://github.com/opensearch-project/opensearch-agent-server) し、ご自身のデータで試して、結果をコミュニティと共有してください。

⭐ **GitHub の [OpenSearch Agent Server リポジトリ](https://github.com/opensearch-project/opensearch-agent-server) にスターを付けて参加してください**

質問がある場合は、OpenSearch の [コミュニティフォーラム](https://forum.opensearch.org/) と Slack で会話に参加してください。

### 謝辞

このプロジェクトへの貴重な貢献をしてくださった以下のコントリビューターに心からの感謝を表します。

- [Sean Zheng](https://github.com/sean-zheng-amazon)
- [Janelle Arita](https://github.com/janellearita)
- [Mingshi Liu](https://github.com/mingshl)
- [Jiaping Zeng](https://github.com/jiapingzeng)
- [Eric Pugh](https://github.com/epugh)
- [David Mackey](https://github.com/davidshq)
- [Andreas Wagenmann](https://github.com/awagen)
- [Craig Perkins](https://github.com/cwperks)

皆さんの献身、専門知識、協調の精神は、このプロジェクトを成功に導く上で不可欠でした。時間と貢献をいただきありがとうございました。
