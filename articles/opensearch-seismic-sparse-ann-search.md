---
title: "[翻訳] 近似検索によるニューラルスパース検索の数十億ベクトル規模へのスケーリング"
emoji: "🔍"
type: "tech"
topics: ["opensearch", "sparsesearch", "vectorsearch", "ann"]
published: true
publication_name: "opensearch"
published_at: 2025-10-23
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/scaling-neural-sparse-search-to-billions-of-vectors-with-approximate-search/

ニューラルスパース検索は、ニューラルモデルの意味理解能力とスパースベクトル表現の効率性を組み合わせた手法です。この技術は、従来の語彙検索の利点を維持しながら意味的な検索を実現し、テキストマッチングによる結果の説明性と表示性に優れています。スパース埋め込みの普及に伴い、インデックスサイズの増大がスケーラビリティの課題となっています。

従来の検索手法では、コレクションの増大に伴いクエリレイテンシが増加します。このクエリスループットの低下は、ユーザー体験に大きな影響を与える可能性があります。OpenSearch 2.15 では、この課題に対処する重要な第一歩として [2 フェーズ検索プロセッサ](https://opensearch.org/blog/introducing-a-neural-sparse-two-phase-algorithm/)を導入しました。重みが無視できるほど小さいトークンを動的に枝刈りすることで、検索精度を維持しながら計算負荷を削減するアプローチです。

効率性と高品質な検索という同じ目標に向けて、私たちは最近、[SEISMIC](https://dl.acm.org/doi/10.1145/3626772.3657769) (**S**pilled Clust**e**ring of **I**nverted Lists with **S**ummaries for **M**aximum **I**nner Produ**c**t Search) 近似検索アルゴリズムに基づくスパース近似最近傍 (ANN) 検索を導入しました。このアルゴリズムは、大規模検索の可能性を根本的に変えるものです。本日、SEISMIC アルゴリズムが OpenSearch 3.3 で利用可能になったことをお知らせします。このアルゴリズムは、ニューラルスパースモデルの意味理解能力を維持しながら、従来の BM25 よりも高速なクエリレイテンシを実現し、検索パフォーマンスの常識を覆します。

## SEISMIC アルゴリズム

SEISMIC インデックスは、転置インデックスと順方向インデックスの 2 つのコンポーネントで構成されます。順方向インデックスは、各ドキュメント ID をそのスパース埋め込みにマッピングします。各埋め込みコンポーネントは、トークン ID とその対応する重みを表します。一方、転置インデックスは、効率性の最適化とストレージ削減のために複数の枝刈り技術を適用します。

1. **クラスタ化ポスティングリスト**: 転置インデックスの各タームについて、SEISMIC アルゴリズムはドキュメントをトークンの重みでソートし、上位のドキュメントのみを保持し、類似したドキュメントをグループ化するためにクラスタリングを適用します。
2. **スパースベクトル要約**: 各クラスタは、最も重みの高いトークンのみを含む要約ベクトルを保持し、クエリ時の効率的な枝刈りを可能にします。
3. **クエリ時枝刈り**: クエリ実行時に、SEISMIC アルゴリズムはトークンレベルとクラスタレベルの枝刈りを行い、スコアリングが必要なドキュメント数を大幅に削減します。

順方向インデックスと転置インデックスのデータ構成を以下の図に示します。

![SEISMIC のデータ構成](/images/opensearch-seismic-sparse-ann-search/seismic.png)

## 試してみよう

SEISMIC ベースの ANN スパース検索を試すには、以下の手順に従ってください。

### ステップ 1: インデックスの作成

`index.sparse` を `true` に設定し、インデックスマッピングで `sparse_vector` フィールドを定義してスパースインデックスを作成します。

```json
PUT sparse-vector-index
{
  "settings": {
    "index": {
      "sparse": true
    }
  },
  "mappings": {
    "properties": {
      "sparse_embedding": {
        "type": "sparse_vector",
        "method": {
          "name": "seismic",
          "parameters": {
            "approximate_threshold": 1
          }
        }
      }
    }
  }
}
```

### ステップ 2: インデックスへのデータ投入

`sparse_vector` フィールドを含む 3 つのドキュメントをインデックスに投入します。

```json
PUT sparse-vector-index/_doc/1
{
  "sparse_embedding": {
    "1000": 0.1
  }
}
```

```json
PUT sparse-vector-index/_doc/2
{
  "sparse_embedding": {
    "2000": 0.2
  }
}
```

```json
PUT sparse-vector-index/_doc/3
{
  "sparse_embedding": {
    "3000": 0.3
  }
}
```

### ステップ 3: インデックスの検索

スパースインデックスに対して、生のベクトルまたは自然言語を使用して [neural sparse クエリ](https://docs.opensearch.org/latest/query-dsl/specialized/neural-sparse/)でクエリを実行できます。

#### 生のベクトルを使用したクエリ

生のベクトルを使用してクエリするには、`query_tokens` パラメータを指定します。

```json
GET sparse-vector-index/_search
{
  "query": {
    "neural_sparse": {
      "sparse_embedding": {
        "query_tokens": {
          "1000": 5.5
        },
        "method_parameters": {
          "heap_factor": 1.0,
          "top_n": 10,
          "k": 10
        }
      }
    }
  }
}
```

#### 自然言語を使用したクエリ

自然言語を使用してクエリするには、`query_text` と `model_id` パラメータを指定します。

```json
GET sparse-vector-index/_search
{
  "query": {
    "neural_sparse": {
      "sparse_embedding": {
        "query_text": "<入力テキスト>",
        "model_id": "<モデル ID>",
        "method_parameters": {
          "k": 10,
          "top_n": 10,
          "heap_factor": 1.0
        }
      }
    }
  }
}
```

## ベンチマーク実験: SEISMIC と従来手法の比較

SEISMIC アルゴリズムと従来の検索手法 (BM25、ニューラルスパース検索、2 フェーズ検索) のパフォーマンスを比較するため、数十億規模のベンチマークを実施しました。

### 実験環境

- **コーパスセット**: [Dolma](https://huggingface.co/datasets/allenai/dolma) の C4 データセット。前処理後、データセットは 1,285,526,507 件 (約 12.9 億件) のドキュメントにチャンク化されました。
- **クエリセット**: MS MARCO v1 dev セット (6,980 クエリ)
- **スパース埋め込みモデル**: doc-only モードで以下の 2 つのモデルを使用
  - コーパスエンコーディング: `amazon/neural-sparse/opensearch-neural-sparse-encoding-doc-v3-gte`
  - クエリエンコーディング: `amazon/neural-sparse/opensearch-neural-sparse-tokenizer-v1`
- **OpenSearch クラスタ**: OpenSearch バージョン 3.3 を実行するクラスタ
  - クラスタマネージャーノード: m7g.4xlarge インスタンス 3 台
  - データノード: r7g.12xlarge インスタンス 15 台

### ベンチマーク結果

数十億規模のベンチマークでは、データセットを 10 パーティションに均等に分割しました。各パーティションの投入後、force merge を実行して新しい SEISMIC セグメントを構築しました。このアプローチにより、データノードあたり 10 個の SEISMIC セグメントが作成され、各セグメントには約 850 万件のドキュメントが含まれます。

[Big ANN](https://big-ann-benchmarks.com/neurips23.html) ベンチマークに従い、recall@10 が 90% に達した時点でのクエリパフォーマンスに注目しました。シングルスレッドとマルチスレッドの 2 つの実験設定を検討しました。シングルスレッド設定では、Python スクリプトを使用してメトリクスを収集しました。レイテンシは OpenSearch クエリが返す `took` 時間を使用して測定しました。マルチスレッド設定では、合計 4 スレッドで `opensearch-benchmark` を使用してスループットメトリクスを測定しました。ベンチマーク結果を以下の表に示します。

**表 I: ニューラルスパース、BM25、SEISMIC クエリの比較**

| カテゴリ         | メトリクス              | ニューラルスパース | ニューラルスパース 2 フェーズ | BM25   | SEISMIC    |
| ---------------- | ----------------------- | ------------------ | ----------------------------- | ------ | ---------- |
| -                | Recall@10 (%)           | 100                | 90.483                        | N/A    | **90.209** |
| シングルスレッド | 平均レイテンシ (ms)     | 125.12             | 45.62                         | 41.52  | **11.77**  |
| シングルスレッド | P50 レイテンシ (ms)     | 109                | 34                            | 28     | **11**     |
| シングルスレッド | P90 レイテンシ (ms)     | 226                | 100                           | 90     | **16**     |
| シングルスレッド | P99 レイテンシ (ms)     | 397.21             | 200.21                        | 200.21 | **27**     |
| シングルスレッド | P99.9 レイテンシ (ms)   | 551.15             | 296.53                        | 346.06 | **50.02**  |
| マルチスレッド   | 平均スループット (op/s) | 26.35              | 82.05                         | 85.86  | **158.7**  |

90% の recall において、**SEISMIC アルゴリズムは平均クエリ時間わずか 11.77 ms を達成しました**。これは BM25 (41.52 ms) の約 **4 倍**、標準的なニューラルスパース検索 (125.12 ms) の **10 倍以上**高速です。マルチスレッド設定では、SEISMIC は毎秒 158.7 オペレーションを処理し、BM25 のスループット (85.86 op/s) のほぼ 2 倍という大きなスループット優位性を示しながら、2 フェーズアプローチと同等の recall を維持しました。

force merge の合計時間は 2 時間 58 分 30 秒でした。平均して、SEISMIC データの保存にはデータノードあたり約 53 GB のメモリを消費しました。

## ベストプラクティス

ベンチマーク結果に基づき、SEISMIC アルゴリズムを使用する際のベストプラクティスを以下に示します。

1. **推奨セグメントサイズ**: approximate threshold を 500 万ドキュメントに設定し、最適なパフォーマンスのためにセグメントを 500 万〜1,000 万ドキュメントに force merge してください。
2. **メモリ計画**: クラスタのサイジングと適切なインスタンスタイプの選択時に、100 万ドキュメントあたり約 1 GB のメモリを計画してください。

これらの結果は、SEISMIC アルゴリズムが数十億規模の検索アプリケーションに対して前例のないパフォーマンスを提供し、ニューラルスパースモデルの意味理解能力を維持しながら従来の BM25 をも上回ることを示しています。

## まとめ

OpenSearch 3.3 では、スパースベクトル向けの近似検索アルゴリズムを導入しています。このアルゴリズムは、ニューラルスパースモデルの意味理解能力を維持しながら、BM25 よりも高速なクエリ時間を実現します。数十億規模の検索アプリケーションにおいて、クエリレイテンシを劇的に削減することで主要なスケーラビリティの障壁を取り除き、より少ないノードでより高いパフォーマンスを達成できます。

12 ms 未満のレイテンシで数十億のドキュメントを検索できる能力は、情報検索の可能性を大きく広げます。この技術を使用して次世代のセマンティック検索アプリケーションを構築されることを楽しみにしています。いつものように、皆様のフィードバックをお待ちしています。[OpenSearch フォーラム](https://forum.opensearch.org/)で会話に参加し、体験を共有してください。

## 参考資料

1. [SEISMIC 論文](https://dl.acm.org/doi/10.1145/3626772.3657769)
2. [スパースセマンティックエンコーダによるドキュメント検索の改善](https://opensearch.org/blog/improving-document-retrieval-with-sparse-semantic-encoders/)
3. [ニューラルスパース 2 フェーズアルゴリズムの紹介](https://opensearch.org/blog/introducing-a-neural-sparse-two-phase-algorithm/)
