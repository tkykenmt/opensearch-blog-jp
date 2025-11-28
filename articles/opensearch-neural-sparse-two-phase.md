---
title: "[翻訳] Neural Sparse の Two-Phase アルゴリズムの紹介"
emoji: "⚡"
type: "tech"
topics: ["opensearch", "neuralsparse", "search", "ml"]
published: true
publication_name: "opensearch"
published_at: 2024-08-13
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/introducing-a-neural-sparse-two-phase-algorithm/

Neural Sparse Search は、OpenSearch 2.11 で導入された新しい効率的なセマンティック検索手法です。Dense なセマンティックマッチングと同様に、Neural Sparse Search はセマンティック技術を使用してクエリを解釈し、従来のテキスト検索では理解できない可能性のある用語を処理できます。Dense なセマンティックモデルは意味的に類似した結果を見つけることに優れていますが、特定の用語、特に完全一致を見逃すことがあります。Neural Sparse Search は、セマンティックな類似性と特定の用語の両方を捉える Sparse 表現を導入することで、この問題に対処します。この二重の機能により、純粋なセマンティックマッチングの制限を克服し、より包括的な検索ソリューションを提供することで、テキストマッチングによる結果の説明と提示が向上します。

Neural Sparse Search は、まずテキスト (クエリまたはドキュメント) をより大きな用語セットに展開し、各用語にセマンティックな関連性に基づいた重みを付けます。次に、Lucene の効率的な用語ベクトル計算を使用して、最高スコアの結果を特定します。このアプローチにより、インデックスとメモリのコスト、および計算コストが削減されます。例えば、k-NN 検索を使用した Dense エンコーディングは検索時に RAM コストを 7.9% 増加させますが、Neural Sparse Search はネイティブの Lucene インデックスを使用するため、検索時の RAM コストの増加がありません。さらに、Neural Sparse Search は Dense エンコーディングと比較してはるかに小さいインデックスサイズになります。Document-only モデルは Dense エンコーディングインデックスのわずか 10.4% のサイズのインデックスを生成し、Bi-encoder の場合はインデックスサイズが Dense エンコーディングインデックスの 7.2% になります。

これらの利点を踏まえ、Neural Sparse 検索をさらに効率的にするための改良を続けてきました。OpenSearch 2.15 では、Two-Phase Search Pipeline という新機能が導入されました。このパイプラインは、Neural Sparse クエリの用語を 2 つのカテゴリに分割します。検索との関連性が高い高スコアトークンと、関連性が低い低スコアトークンです。最初に、アルゴリズムは高スコアトークンを使用してドキュメントを選択し、次にそれらのドキュメントのスコアを高スコアと低スコアの両方のトークンを含めて再計算します。このプロセスにより、最終的なランキングの品質を維持しながら、計算負荷が大幅に削減されます。

## Two-Phase アルゴリズム

Two-Phase Search アルゴリズムは 2 つのステージで動作します。

1. **初期フェーズ:** アルゴリズムはモデル推論を使用して、クエリからの高スコアトークンを使用して候補ドキュメントのセットを素早く選択します。これらの高スコアトークンは、トークン総数のうち小さな割合を占めますが、重要な重み (関連性) を持っているため、潜在的に関連性のあるドキュメントを迅速に特定できます。このプロセスにより、処理が必要なドキュメント数が大幅に削減され、計算コストが低下します。
2. **再計算フェーズ:** 次に、アルゴリズムは最初のフェーズで選択された候補ドキュメントのスコアを再計算します。今回は、クエリからの高スコアと低スコアの両方のトークンを含めます。低スコアトークンは個々には重みが小さいですが、包括的な評価の一部として、特にロングテール用語が全体スコアに大きく寄与する場合に、貴重な情報を提供します。これにより、アルゴリズムはより高い精度で最終的なドキュメントスコアを決定できます。

ドキュメントを段階的に処理することで、このアプローチは精度を維持しながら計算オーバーヘッドを削減します。最初のフェーズでの迅速な選択が効率を高め、2 番目のフェーズでのより詳細なスコアリングが精度を確保します。多数のロングテール用語を処理する場合でも、結果は高品質を維持し、計算効率が顕著に向上します。

## パフォーマンスメトリクス

Neural Sparse Search を使用した検索の速度と品質を測定しました。

### テスト環境

パフォーマンスは、[OpenSearch Benchmark](https://opensearch.org/docs/latest/benchmark/) を使用して、3 台の m5.4xlarge ノードを含む OpenSearch クラスターで測定しました。テストは、20 の同時クライアント、50 回のウォームアップイテレーション、200 回のテストイテレーションで実施しました。

### テストデータセット

検索品質については、複数の BEIR データセットをテストし、結果の相対的な品質を測定しました。以下の表は、これらのデータセットのパラメータ情報を示しています。

| データセット | BEIR-Name | クエリ数 | コーパス | Rel D/Q |
| --- | --- | --- | --- | --- |
| NQ | nq | 3,452 | 2.68M | 1.2 |
| HotpotQA | hotpotqa | 7,405 | 5.23M | 2 |
| DBPedia | dbpedia-entity | 400 | 4.63M | 38.2 |
| FEVER | fever | 6,666 | 5.42M | 1.2 |
| Climate-FEVER | climate-fever | 1,535 | 5.42M | 3 |

### p99 レイテンシー

Two-Phase アルゴリズムは、既存の Neural Sparse Search アルゴリズムと同じ推論時間コストを維持します。検索フェーズでの高速化をより明確に比較するために、推論はハードウェアタイプに大きく影響されるため、レイテンシー計算から推論ステップを除外しました。この記事で提供するレイテンシーベンチマークは、生のベクトル検索を使用し、推論時間による追加の影響を除外しています。

#### Doc-only モード

Doc-only モードでは、Two-Phase プロセッサーによりクエリレイテンシーが大幅に低下します。以下の図に示すとおりです。

![Doc-only モードの p99 レイテンシー](/images/opensearch-neural-sparse-two-phase/two-phase-doc-model-p99-latency-1024x612.png)

**平均レイテンシー** は以下のとおりです。

* Two-Phase アルゴリズムなし: **198 ms**
* Two-Phase アルゴリズムあり: **124 ms**

データ分布に応じて、Two-Phase プロセッサーは **1.22 倍から 1.78 倍の速度向上** を達成しました。

#### Bi-encoder モード

Bi-encoder モードでは、Two-Phase アルゴリズムによりクエリレイテンシーが大幅に低下します。以下の図に示すとおりです。

![Bi-encoder モードの p99 レイテンシー](/images/opensearch-neural-sparse-two-phase/two-phase-bi-encoder-p99-latency-1024x612.png)

**平均レイテンシー** は以下のとおりです。

* Two-Phase アルゴリズムなし: **617 ms**
* Two-Phase アルゴリズムあり: **122 ms**

データ分布に応じて、Two-Phase プロセッサーは **4.15 倍から 6.87 倍の速度向上** を達成しました。

## 試してみる

Two-Phase プロセッサーを試すには、以下の手順に従ってください。

### ステップ 1: `neural_sparse_two_phase_processor` を設定する

まず、デフォルトパラメータで `neural_sparse_two_phase_processor` を設定します。

```json
PUT /_search/pipeline/<custom-pipeline-name>
{
  "request_processors": [
    {
      "neural_sparse_two_phase_processor": {
        "tag": "neural-sparse",
        "description": "This processor creates a neural sparse two-phase processor, which can speed up neural sparse queries!"
      }
    }
  ]
}
```

### ステップ 2: デフォルトの検索パイプラインを `neural_sparse_two_phase_processor` に設定する

Neural Sparse インデックスがすでにあると仮定して、インデックスの `index.search.default_pipeline` を前のステップで作成したパイプラインに設定します。

```json
PUT /<your-index-name>/_settings 
{
  "index.search.default_pipeline" : "<custom-pipeline-name>"
}
```

## 次のステップ

Two-Phase プロセッサーの詳細については、[Neural sparse query two-phase processor](https://opensearch.org/docs/latest/search-plugins/search-pipelines/neural-sparse-query-two-phase-processor/) を参照してください。

## 参考資料

Neural Sparse Search についてさらに読む。

1. [Improving document retrieval with sparse semantic encoders](https://opensearch.org/blog/improving-document-retrieval-with-sparse-semantic-encoders)
2. [A deep dive into faster semantic sparse retrieval in OpenSearch 2.12](https://opensearch.org/blog/A-deep-dive-into-faster-semantic-sparse-retrieval-in-OS-2.12)
3. [Advancing Search Quality and Inference Speed with v2 Series Neural Sparse Models](https://opensearch.org/blog/neural-sparse-v2-models)
