---
title: "[翻訳] OpenSearch Agent Health: AI エージェントのためのオープンソースオブザーバビリティと評価"
emoji: "🔍"
type: "tech"
topics: ["opensearch", "ai", "observability", "agent", "llm"]
publication_name: "opensearch"
published: true
published_at: 2026-03-05
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

@[card](https://opensearch.org/blog/opensearch-agent-health-open-source-observability-and-evaluation-for-ai-agents/)

あなたはエージェント型 AI アプリケーションを構築しました。再帰的なループと自律的なツール呼び出しを使ってデータを処理する、洗練されたアプリケーションです。ローカルテストに合格したので、本番環境にデプロイしました。

そしてログを確認します。

あるユーザーが注文状況の更新を問い合わせました。エージェントは誤ったコンテキストを取得し、製品マニュアルを推論する必要があると判断し、コストの高い無関係なツール呼び出しを連続して実行しました。数秒と予想外の推論コストの後、自信に満ちた、しかし役に立たない回答を返しました。ダッシュボードには正常なクラスターと成功を示す 200 OK が表示されていますが、エージェントはサイレントに失敗していたのです。

## エージェントがサイレントに失敗する理由

AI エージェントがプロトタイプから本番環境へ移行するにつれて、組織は無視できない重大な課題に直面しています。エージェントは自律的に意思決定を行い、ツールを呼び出し、結果を返していますが、それを構築するチームは可視性のないまま運用していることが多いのです。これにより、3 つの重大な課題が生じます。

- **推論のギャップ**: エージェントが返す最終的な回答は見えますが、その回答に至るまでにエージェントが行ったハルシネーションを含むステップは見えません。間違った API を呼び出したのか? ユーザーの意図を誤解したのか? 失敗した操作を成功するまで 3 回リトライしたのか? 推論チェーンの可視性がなければ、デバッグは推測に頼ることになります。
- **コストとレイテンシーの悪循環**: エージェント型ワークフローは本質的に再帰的です。1 つのユーザークエリが、コストが高く時間のかかるサブタスクの連鎖を引き起こす可能性があります。リアルタイムの運用オブザーバビリティがなければ、どの特定のツールやサブエージェントが予算を消費しているのかわかりません。パフォーマンスの問題は請求書が届いてから初めて発見されます。
- **評価のパラドックス**: エージェントのパフォーマンスを大規模に体系的に評価する方法がなければ、チームは手動のスポットチェックに戻ることになります。最新のプロンプト変更が精度を 5% 向上させたのか、それともサイレントに 10% 低下させたのか、どうすればわかるでしょうか? 体系的な評価がなければ、チームは自信を持ってエージェントを本番環境にデプロイできません。

## Agent Health はどのように役立つのか

数か月にわたるデプロイサイクルから毎週のデプロイへの移行は、手動の QA プロセスを排除することにかかっています。プロンプトを調整したり、エージェントに新しいツールやスキルを追加するたびに、考えられるすべてのシナリオを手動でテストすることは大規模には実現不可能です。Agent Health は、このテストプロセスを自動化された AI ジャッジベースのワークフローに変換することで開発を加速します。開発フェーズ (および CI/CD パイプライン) でリグレッションを早期に検出し、エージェントが失敗または逸脱した正確なポイントをリアルタイムのビジュアルトレースで提供することで、チームはログのレビューや顧客のインシデントレポートの待機に費やしていたエンジニアリング時間を取り戻せます。問題を数分でデバッグし、体系的にテストし、より自信を持ってデプロイできます。以下の図に、従来のエージェント開発と Agent Health ワークフローの違いを示します。

![](/images/opensearch-agent-health-open-source-observability/3600c43fce0a.png)

## OpenSearch Agent Health の紹介

開始するには、1 つのコマンドを実行するだけで Agent Health の完全なインターフェースを起動できます。

```
npx @opensearch-project/agent-health
# ✓ Server running at http://localhost:4001
# ✓ Demo data loaded
```

これだけです。インストールは不要です。トレース、ベンチマーク、評価、比較を含む完全な Agent Health インターフェースが利用可能になります。

OpenSearch Agent Health は、AI エージェントのためのオープンソースのオブザーバビリティおよび評価ソリューションです。インストール不要の NPX ツールとして提供され、軽量 (約 4 MB) なパッケージで **3 つのコア機能** を提供します。

**1. 推論のギャップの解決: OpenTelemetry ネイティブのトレースオブザーバビリティ**

Agent Health は、エージェントが各ステップで何を行っているかを正確に示すタイムラインとフローのビジュアライゼーションを提供します。呼び出しているツール、意思決定のシーケンス、コンポーネント間を流れるデータ、障害が発生する場所などです。すべてのトレースは OpenTelemetry 標準に準拠しているため、計装はポータブルであり、既存のオブザーバビリティツールと連携して動作します。

**2. コストとレイテンシーの悪循環の解決: 構造化されたベンチマーク**

Agent Health は、テストスイート全体でエージェント構成の体系的な A/B 比較を可能にします。異なるプロンプト、モデル、構成をサイドバイサイドでテストし、結果を時系列で追跡できます。すべてのベンチマークと結果を OpenSearch に保存することで、Agent Health はすべての評価実行の永続的でクエリ可能な履歴を提供し、リグレッションを本番環境に到達する前に (到達した後ではなく) 検出できます。

**3. 評価のパラドックスの解決: リアルタイムのエージェント評価**

Agent Health は、エージェントのパフォーマンスを評価するために *ゴールデンパス* のトラジェクトリ比較を使用します。このアプローチでは、エージェントが従うべき理想的なステップ、ツール呼び出し、結果のシーケンスをゴールデンパスとして定義します。LLM ジャッジがエージェントの実際の動作をその期待されるトラジェクトリと照合してスコアリングし、エラーやリグレッションを示す逸脱をフラグ付けします。Agent Health はこれらの基準に対するエージェントのパフォーマンスを測定し、好みの LLM プロバイダーをジャッジとして使用することで、ニーズと予算に合った評価モデルを柔軟に選択できます。

## 開発者ワークフロー向けに構築

Agent Health はローカルマシン上で動作し、Web UI (`localhost:4001`) とヘッドレス CLI の両方を提供して、AI エージェント開発者と ML エンジニアがエージェントの構築、観察、継続的な改善という開発サイクル全体をサポートします。

- **CLI の使用**: JSON でベンチマークを定義し、コマンドラインから評価を実行し、結果を CI/CD パイプラインに統合して自動品質ゲーティングを行います。
- **Web UI の使用**: 結果をビジュアルに探索し、ゴールデンデータセットを設計し、構成間の A/B テストを実行し、レポートやさらなる分析のために結果をエクスポートします。

## 試してみましょう

Agent Health の動作を確認する準備はできましたか? プリロードされたサンプルデータで探索するか、独自のエージェントを接続して評価を開始するか、お好みのパスを選択してください。

### クイックスタート: サンプルデータで探索する (エージェント不要)

Agent Health を体験する最も速い方法は、組み込みのサンプルデータを使用することです。1 つのコマンドを実行するだけで、すぐに探索できるモックトレース、ベンチマーク、評価結果が用意されます。

```
npx @opensearch-project/agent-health
# ✓ Server running at http://localhost:4001
# ✓ Demo data loaded
```

**Traces** に移動してプリロードされたエージェント実行データを探索し、**Benchmarks** に移動して `Travel Planning Accuracy - Demo` を実行して LLM ジャッジ評価の動作を確認し、**Compare** にアクセスしてサイドバイサイドの実行比較を確認します。

### 独自のエージェントを評価する

このウォークスルーでは、エージェントの計装、ベンチマークの作成、評価結果に基づくイテレーションの方法を示します。

#### ステップ 1: Agent Health を起動する

ツールを起動し、接続を構成します。

```
npx @opensearch-project/agent-health
# ✓ Server running at http://localhost:4001
```

Agent Health は、評価データ (テストケース、ベンチマーク、結果) とオブザーバビリティデータ (エージェントトレース) のために OpenSearch クラスターが必要です。既存のホスト型 OpenSearch クラスターを使用するか、[OpenSearch Observability Stack](https://github.com/opensearch-project/observability-stack?tab=readme-ov-file#-quickstart) を使用してローカルで起動できます。

```bash
curl -fsSL https://raw.githubusercontent.com/opensearch-project/observability-stack/main/install.sh | bash
```

ローカルスタックは 2 つのコンポーネントを起動します。

- **ポート 9200 の OpenSearch クラスター** — Agent Health の Settings で評価ストレージとオブザーバビリティストレージの両方のエンドポイントとして使用します。
- **ポート 4317 の OTEL コレクター** — 計装済みエージェントのトレースをここに送信します。Agent Health はトレース収集に OpenTelemetry を使用します。エージェントにトレースを追加するには、お使いの言語の [OpenTelemetry 計装ガイド](https://opentelemetry.io/docs/instrumentation/)を参照してください。

既存のクラスターを使用する場合は、**Settings** でクラスターエンドポイントを両方のストレージエンドポイントとして直接追加します。

**Settings** では、エージェントエンドポイント (名前、URL、コネクタタイプ) の構成と、環境変数を使用した独自の LLM ジャッジの構成が可能です。

#### ステップ 2: ベンチマークを作成する

JSON 形式でテストケースを定義します。以下は旅行プランナーエージェントの例 (`travel-agent-benchmark.json`) です。

```json
[
  {
    "name": "Check hotel availability",
    "description": "User wants to find hotels in New York for specific dates",
    "labels": ["category:Travel", "difficulty:Easy"],
    "initialPrompt": "Are there any hotels available in Manhattan for next weekend?",
    "expectedOutcomes": [
      "Agent should call search_hotels tool with location and date range",
      "Agent should present available hotels with prices and amenities"
    ]
  },
  {
    "name": "Complete booking with confirmation",
    "description": "User wants to book a specific flight and hotel",
    "labels": ["category:Travel", "difficulty:Medium"],
    "initialPrompt": "Book the morning flight to New York and the Hilton hotel for 2 nights",
    "context": [
      {
        "description": "Previous search results showing available flights and hotels",
        "value": "{\"flights\":[{\"id\":\"AA123\",\"time\":\"8:00 AM\",\"price\":\"$350\"}],\"hotels\":[{\"id\":\"hilton-manhattan\",\"name\":\"Hilton Manhattan\",\"price\":\"$200/night\"}]}"
      }
    ],
    "expectedOutcomes": [
      "Agent should call book_flight tool with the correct flight ID",
      "Agent should call book_hotel tool with hotel ID and number of nights",
      "Agent should confirm both bookings with confirmation numbers and total cost"
    ]
  }
]
```

#### ステップ 3: 実行と分析

ベンチマークを実行して分析するには、Agent Health の CLI モードまたは Agent Health の UI を使用します。

**オプション A: CLI モードの使用**

CLI モードを使用するには、以下のコマンドを実行します。

```bash
npx @opensearch-project/agent-health benchmark \
  -f travel-agent-benchmark.json \
  -a travel-agent \
  --export baseline-results.json \
  -v
```

このコマンドはベンチマークをインポートし、作成し、エージェントに対して実行し、結果をエクスポートします。

**オプション B: UI の使用**

**Benchmarks** に移動し、**Import JSON** でファイルを選択します。**Run** を選択してエージェントとジャッジモデルを構成します。各テストケースが実行される様子をリアルタイムで確認できます。

#### ステップ 4: 結果を確認する

UI を通じて結果にアクセスし、全体の合格率、テストケースごとの LLM ジャッジの推論を含む結果、優先度順にランク付けされた改善戦略を確認できます。結果にアクセスするには、**Benchmarks** に移動し、**Latest Run** を選択します。**Traces** に移動して、タイムラインビュー、フロービュー、スパン詳細を含む詳細な実行ビジュアライゼーションを確認します。または、JSON エクスポートを分析します。

```bash
cat baseline-results.json | jq '.runs[0].reports[] | select(.passFailStatus == "failed") | {
  testCase: .testCaseId,
  reasoning: .llmJudgeReasoning,
  strategies: .improvementStrategies
}'
```

#### ステップ 5: イテレーションと改善

優先度の高い推奨事項に基づいてエージェントを更新し、ベンチマークを再実行して結果を比較します。**Compare from Benchmarks** に移動し、2 つの実行を選択して、合格率、レイテンシー、コスト、失敗したテストなどのメトリクス全体の改善をビジュアライズします。以下の画像にその例を示します。

![](/images/opensearch-agent-health-open-source-observability/5a4382af7ae4.png)

## 今後の予定

Agent Health は、エージェントが本番環境に到達する前に構築、テスト、イテレーションを支援する開発フェーズのコンパニオンとして設計されています。これは実験的なリリースであり、Agent Health の今後の改善を積極的に検討しています。AI エージェントプラットフォームが成熟し標準が確立されるにつれて、実際の使用状況に基づいてツールを進化させ続け、Agent Health の評価およびオブザーバビリティ機能を本番規模のデプロイメントに拡張する方法を探求していきます。

Agent Health をインストールし、ベンチマークを実行し、結果を共有してください。[リポジトリ](https://github.com/opensearch-project/agent-health)で Issue を作成するか、[RFC](https://github.com/opensearch-project/agent-health/issues/42) のディスカッションに参加するか、[OpenSearch フォーラム](https://forum.opensearch.org/)でコミュニティと体験を共有してください。皆さんのフィードバックが、機能の優先順位付けと開発者体験の改善に直接影響します。

*OpenSearch エコシステム上にネイティブに構築された LLM 評価プラットフォームに興味がありますか? [Agentic AI Eval Platform RFC](https://github.com/opensearch-project/dashboards-observability/issues/2588) を参照してください。*
