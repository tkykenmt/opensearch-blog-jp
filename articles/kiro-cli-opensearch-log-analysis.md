---
title: "[翻訳] Kiro CLI 統合: ログパターンとデータ分散分析"
emoji: "🔍"
type: "tech"
topics: ["opensearch"]
published: false
published_at: 2025-11-20
publication_name: "opensearch"
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。

**注**: 元記事では Amazon Q CLI として紹介されていますが、Amazon Q CLI は Kiro CLI に名称変更されました。本翻訳版では Kiro CLI として記載しています。
:::

https://opensearch.org/blog/amazon-q-cli-integration-log-pattern-and-data-distribution-analysis/

現代の分散システムは膨大な量のログデータを生成しますが、手動で分析するのは困難です。本記事では、Kiro CLI と OpenSearch の高度な分析ツールを統合し、複雑なログ調査を自然言語クエリに変換する方法を紹介します。Model Context Protocol (MCP) を通じて、Log Pattern Analysis Tool と Data Distribution Tool という 2 つの強力な OpenSearch エージェントツールを統合し、コマンドラインでの診断を効率化し、システムトラブルシューティングを強化する方法を実演します。

決済失敗を調査する OpenTelemetry Demo の実例を通じて、統合のセットアップ方法、必要なコンポーネントの設定方法、これらのツールを使用した自動パターン認識と統計分析の実行方法を学びます。本記事を読み終える頃には、会話形式のコマンドを使用して分散システムログの根本原因を迅速に特定し、重要な問題の解決時間を大幅に短縮する方法を理解できるでしょう。

## Log Pattern Analysis ツール

[Log Pattern Analysis ツール](https://docs.opensearch.org/latest/ml-commons-plugin/agents-tools/tools/log-pattern-analysis-tool/)は、複数の分析モードを通じてログ分析を自動化する OpenSearch エージェントツールです。ベースライン期間と問題発生期間の差分パターン分析を実行し、トレース相関を使用してログシーケンスを分析します。このツールは、ログデータからエラーパターンとキーワードを自動的に抽出してログインサイトを提供し、トラブルシューティングを加速します。

## Data Distribution ツール

[Data Distribution ツール](https://docs.opensearch.org/latest/ml-commons-plugin/agents-tools/tools/data-distribution-tool/)は、データセット内のデータ分散パターンを分析し、異なる期間の分散を比較する OpenSearch エージェントツールです。単一データセット分析と比較分析の両方をサポートし、フィールド値の分散における重要な変化を特定することで、異常、トレンド、データ品質の問題を検出します。

このツールは、値の頻度、パーセンタイル、分散メトリクスを含む統計サマリーを生成し、データ特性の理解と潜在的なデータ品質問題の特定を支援します。

## Kiro CLI 統合

Kiro CLI は、[MCP](https://opensearch.org/blog/introducing-mcp-in-opensearch/) を通じてこれらの OpenSearch 分析ツールとシームレスに統合できます。OpenSearch MCP サーバーを設定することで、Log Pattern Analysis ツールと Data Distribution ツールの両方にコマンドラインインターフェースから直接アクセスできます。

この統合により、ログ分析とデータ分散インサイトのための自然言語クエリが可能になり、複雑な診断タスクをシンプルな会話形式のコマンドでアクセスできるようになります。

### opensearch-mcp-server-py を使用した実装

この統合は、OpenSearch 用の Python ベースの MCP サーバーを提供する [opensearch-mcp-server-py](https://github.com/opensearch-project/opensearch-mcp-server-py) プロジェクトに基づいています。Log Pattern Analysis ツールと Data Distribution ツールの統合を有効にするには、このプロジェクトをクローンし、両方のツール用のカスタム統合コードを追加する必要があります。これにより、サーバーの機能が拡張され、これらの高度な分析機能がサポートされます。

### 完全な統合ワークフロー

Kiro CLI と OpenSearch MCP 統合をセットアップするには、以下の手順に従います。

1. **MCP サーバーリポジトリをクローン**:
   ```bash
   git clone https://github.com/opensearch-project/opensearch-mcp-server-py.git
   cd opensearch-mcp-server-py
   ```

2. **ツール統合コードを追加**:
   - MCP サーバーに Log Pattern Analysis ツール統合を実装
   - MCP サーバーに Data Distribution ツール統合を実装
   - MCP サーバーのツールレジストリに両方のツールを登録
   - 完全な実装例については、[opensearch-mcp-server-py/integrate-skill-tool](https://github.com/PauiC/opensearch-mcp-server-py/tree/integrate-skill-tool) のデモを参照してください

3. **MCP サーバーを起動**:
   ```bash
   OPENSEARCH_URL="<your-opensearch-cluster-endpoint>" \
   OPENSEARCH_USERNAME="<your-opensearch-username>" \
   OPENSEARCH_PASSWORD="<your-opensearch-password>" \
   python -m src.mcp_server_opensearch --transport stream --host 0.0.0.0 --port 9900
   ```
   このコマンドは、localhost:9900 で MCP サーバーを起動します。この設定を使用する場合、設定ファイルの `url` フィールドを `"http://localhost:9900/mcp"` に設定します。

4. **Kiro CLI を設定**:
   - Kiro CLI 設定ファイルを開く
   - [MCP サーバー設定](https://github.com/opensearch-project/project-website/diffs/1?base_sha=90e92bf9f9f487af1537e4564587f6cd856639f0&head_user=PauiC&name=logPatternAnalysis-dataDistribution&pull_number=3984&sha1=90e92bf9f9f487af1537e4564587f6cd856639f0&sha2=5f7db21d157c21c379ddb1f93acb2d8d021a2df0&short_path=8d145f9&unchanged=expanded&w=false#mcp-configuration-example)を追加

5. **自然言語クエリを送信**:
   - Kiro CLI を起動
   - 会話形式のコマンドを使用して OpenSearch データをクエリ

### MCP 設定例

Kiro CLI 用に OpenSearch MCP サーバーを設定するには、以下の設定を追加します。

```json
{
  "mcpServers": {
    "opensearch-mcp-server": {
      "type": "http",
      "url": "<your-mcp-server-url>",
      "env": {
        "OPENSEARCH_URL": "<your-opensearch-cluster-endpoint>",
        "OPENSEARCH_USERNAME": "<your-opensearch-username>",
        "OPENSEARCH_PASSWORD": "<your-opensearch-password>"
      }
    }
  }
}
```

**設定の注意点**:

- `url`: MCP サーバーの URL を指定 (例: `http://localhost:9900/mcp`)
- `OPENSEARCH_URL`: OpenSearch クラスターエンドポイントを指定
- `OPENSEARCH_PASSWORD`: OpenSearch パスワードを指定
- `OPENSEARCH_USERNAME`: OpenSearch ユーザー名を指定

## 実例: OpenTelemetry Demo

これらの統合ツールの実用的な応用を実演するため、OpenTelemetry Demo をシナリオ例として使用します。

OpenTelemetry は、アプリケーションからテレメトリデータ (メトリクス、ログ、トレース) を生成、収集、エクスポートするためのツール、API、SDK のコレクションを提供する可観測性フレームワークです。OpenTelemetry Demo は、カートサービス、チェックアウトサービス、決済サービス、レコメンデーションエンジンを含む複数のマイクロサービスを持つ現実的な e コマースプラットフォームをシミュレートします。

この環境では、決済処理の失敗、カート放棄エラー、レコメンデーションサービスのタイムアウト、チェックアウトワークフローの中断などの一般的な問題が発生します。これは、分散システム環境での根本原因分析の優れた機会を提供します。

### 決済失敗の調査

このシナリオでは、ユーザーがチェックアウト時に決済失敗を報告しています。これは収益と顧客体験に影響を与える重要な問題です。

OpenTelemetry Demo は、決済サービスの中断や認証問題を含むさまざまな障害条件をシミュレートできます。この問題を解決するには、ログを分析して障害パターンを特定し、問題が特定の顧客セグメント、認証問題、またはシステムレベルの設定問題に関連しているかどうかを判断する必要があります。

### Kiro CLI 調査プロセス

統合された OpenSearch ツールを使用した Kiro CLI により、自然言語クエリを通じてこの問題を調査できます。調査の流れは以下の通りです。

**初期クエリ**:

```
ユーザーがチェックアウトプロセス中に決済失敗を報告しており、2025-08-21 の午後 3 時から 4 時の間の ss4o_logs* インデックスからログを分析して、カード課金問題に関連するチェックアウトサービス障害のパターンを特定することで根本原因を調査する必要があります。
```

**Kiro CLI 分析結果**:

ツールは以下の順序で実行されました:

1. `ListIndexTool` - 利用可能なインデックスを確認
2. `IndexMappingTool` - インデックス構造を調査
3. `LogPatternAnalysisTool` - ログパターンを分析
4. `SearchIndexTool` - 特定のエラーパターンを検索
5. `CountTool` - 成功したトランザクションをカウント
6. `DataDistributionTool` - データ分散を分析

### 生のツール結果

以下のセクションでは、調査で使用された各ツールからの詳細な JSON レスポンスを提供し、分析の根拠となった特定のパターン、統計、インサイトを示します。

#### Log Pattern Analysis ツールの結果

```json
{
  "inference_results": [
    {
      "output": [
        {
          "name": "response",
          "result": {
            "logInsights": [
              {
                "pattern": "*** METRIC EVENT: Recording checkout.result=<*> status=failure error=could not charge the card: rpc error: code = Unknown desc = Payment request failed. Invalid token. app.loyalty.level=gold ***",
                "count": 63.0,
                "sampleLogs": [
                  "*** METRIC EVENT: Recording checkout.result=0, status=failure, error=could not charge the card: rpc error: code = Unknown desc = Payment request failed. Invalid token. app.loyalty.level=gold ***"
                ]
              },
              {
                "pattern": "could not charge the card: rpc error: code = Unknown desc = Payment request failed. Invalid token. app.loyalty.level=gold",
                "count": 63.0
              },
              {
                "pattern": "failed to charge card: could not charge the card: rpc error: code = Unknown desc = Payment request failed. Invalid token. app.loyalty.level=gold",
                "count": 63.0
              },
              {
                "pattern": "*** METRIC EVENT: Recording checkout.result=<*> status=failure error=failed to prepare order: failed to get product #\"<*>Z\" ***",
                "count": 19.0
              }
            ]
          }
        }
      ]
    }
  ]
}
```

#### Data Distribution ツールの結果

```json
{
  "inference_results": [
    {
      "output": [
        {
          "name": "response",
          "result": {
            "singleAnalysis": [
              {
                "field": "serviceName",
                "divergence": 0.223,
                "topChanges": [
                  {"value": "kafka", "selectionPercentage": 0.22},
                  {"value": "product-catalog", "selectionPercentage": 0.18},
                  {"value": "frontend-proxy", "selectionPercentage": 0.15},
                  {"value": "checkout", "selectionPercentage": 0.13}
                ]
              },
              {
                "field": "severityText",
                "divergence": 0.609,
                "topChanges": [
                  {"value": "INFO", "selectionPercentage": 0.61},
                  {"value": "error", "selectionPercentage": 0.01}
                ]
              }
            ]
          }
        }
      ]
    }
  ]
}
```

#### Log Pattern Analysis ツールの貢献

Log Pattern Analysis ツールは、以下の方法で決済失敗の根本原因特定に貢献しました。

**コア貢献: 自動エラーパターン認識**

Log Pattern Analysis ツールは、この決済失敗調査において重要なパターン識別の役割を果たしました:

1. **主要な障害パターンの特定** (63 件の発生):
   - 決済トークン検証失敗に関連する 3 つのパターンを自動的に特定
   - すべてのパターンが同じ根本原因を指摘: `Payment request failed. Invalid token`
   - 障害が `app.loyalty.level=gold` に関連していることを特定

2. **副次的な障害パターンの特定** (19 件の発生):
   - 製品カタログ関連の障害パターンを 2 つ特定
   - パターン: `failed to get product #"<*>Z"`
   - 特定の製品 ID 例を提供: `OLJCESPC7Z`

3. **パターンの分類と定量化**:
   - 関連するエラーメッセージを論理的な障害カテゴリに自動的にグループ化
   - 正確な発生回数の統計を提供
   - 各パターンの実際のログサンプルを検証用に提供

**提供された価値**: このツールは手動パターン認識の必要性を排除し、決済トークン検証失敗が製品カタログ問題の 3.3 倍の頻度で発生することを自動的に発見し、主要および副次的な障害モードの優先順位を明確に確立しました。

#### Data Distribution ツールの貢献

Data Distribution ツールは、以下の方法で決済失敗の根本原因特定に貢献しました。

**コア貢献: 統計分析とコンテキスト提供**

Data Distribution ツールは、調査のための重要な統計的背景とフィールド分散分析を提供しました:

1. **サービス分散分析** (divergence: 0.223):
   - `kafka`: 22% (最高ログボリュームサービス)
   - `product-catalog`: 18% (副次的障害ソース)
   - `frontend-proxy`: 15% (ユーザー向けエラー)
   - `checkout`: 13% (主要障害ポイント)

2. **重大度レベル分析** (divergence: 0.609):
   - `INFO` レベル: 合計 81%
   - `error` レベル: 1% (集中的な障害)

3. **フィールド異常検出**:
   - `droppedAttributesCount`: divergence = 1.0 (完全な異常)
   - `severityNumber`: divergence = 0.689 (高い異常)

**提供された価値**: このツールは、チェックアウトサービスが全ログの 13% しか占めていないにもかかわらず、最も高い重大な障害の集中度を持つことを明らかにしました。重大度分散は、エラーレベルのログが稀 (1%) であることを示し、63 件の決済失敗が統計的に重要であることを示しました。この定量的コンテキストは、`kafka` のような高ボリュームだが重要度の低いサービスよりもチェックアウトサービスの調査を優先するのに役立ちました。

#### 両ツールの連携

両ツールの組み合わせは、調査の効果を高める相乗効果を生み出しました:

1. **定性的 + 定量的分析**: Log Pattern Analysis ツールが特定のエラーパターンを提供し、Data Distribution ツールが統計的検証を提供
2. **優先順位のガイダンス**: 組み合わせ分析により、チェックアウトサービスがログボリュームは低いものの、不釣り合いに高い障害影響を持つことを示した
3. **根本原因の検証**: 両ツールが決済トークン検証を主要問題として確認し、製品カタログを副次的問題として確認
4. **実行可能なインサイト**: ツールが連携して特定のエラーメッセージと統計的重要性を提供し、明確な修復推奨をサポート

この調査は、Kiro CLI が複数の OpenSearch ツールをオーケストレーションする様子を示しています: データ発見のための `ListIndexTool` と `IndexMappingTool`、ターゲットクエリのための `SearchIndexTool`、フィールドパターンの統計分析のための `DataDistributionTool`、定量的評価のための `CountTool`、自動パターン抽出のための `LogPatternAnalysisTool`。

Log Pattern Analysis ツールは、正確な発生回数 (63 件の決済失敗、19 件の製品カタログ問題) を伴う精密なエラーパターン識別を提供し、Data Distribution ツールは、ログボリュームが低いにもかかわらずチェックアウトサービス障害の重要性を検証する統計的コンテキストを提供しました。この組み合わせにより、ゴールドティア顧客に影響を与える無効な決済トークンを主要問題として特定する包括的な根本原因分析が生成され、トークン検証、サービス依存関係、監視改善のための実行可能な推奨事項が提供されました。

## まとめ

Kiro CLI と OpenSearch の Log Pattern Analysis ツールおよび Data Distribution ツールの統合により、複雑なログ調査が会話形式の分析に変わります。MCP を通じて、これらのツールは自然言語クエリを介してアクセス可能になり、診断の複雑さを大幅に軽減します。

**実証された主な利点**:

1. **会話形式のインターフェース**: 自然言語クエリを通じた複雑なログ分析
2. **自動パターン認識**: 手動のログ解析やパターン識別が不要
3. **統計的検証**: 定性的な発見を支える定量的分析
4. **包括的な調査**: 単一の会話での複数ツールのオーケストレーション
5. **実行可能な結果**: 特定の推奨事項を伴う明確な根本原因の特定

これらのツールは、シンプルな会話形式のコマンドを通じて包括的な根本原因分析を提供し、従来は複数の手動クエリとドメイン専門知識を必要としていたものを、自動化されたインテリジェントな調査プロセスに変換しました。この統合により、高度なログ分析がより広い対象者にアクセス可能になり、分散システムのトラブルシューティングにおける解決時間が大幅に短縮されます。
