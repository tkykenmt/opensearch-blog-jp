---
title: "[翻訳] FP16 量子化で OpenSearch を最適化する"
emoji: "⚡"
type: "tech"
topics: ["opensearch", "ベクトル検索", "量子化", "メモリ最適化", "knn"]
published: true
publication_name: "opensearch"
published_at: 2024-06-27
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/optimizing-opensearch-with-fp16-quantization/

大規模言語モデル (LLM) と生成 AI の台頭により、自然言語処理能力の新時代が到来しました。ベクトルデータベースは、LLM が生成する埋め込みを効率的にインデックス化、保存、検索できる外部データベースとして、この分野で重要なコンポーネントとなっています。しかし、LLM の規模と複雑さが増し続けるにつれて、ベクトルデータベースのワークロードも大幅に増加しています。数十億のベクトルを取り込みクエリすることは、計算リソースに負担をかけ、メモリ要件の増加と運用コストの上昇につながります。Faiss スカラー量子化を使用すると、ベクトル埋め込みを低精度で保存でき、メモリ消費を削減し、結果としてコストを削減できます。

## Faiss スカラー量子化を使用する理由

[OpenSearch 2.13](https://github.com/opensearch-project/opensearch-build/blob/main/release-notes/opensearch-release-notes-2.13.0.md) 以降のバージョンでベクトルをインデックス化する際、k-NN インデックスに*スカラー量子化*を適用するよう設定できます。スカラー量子化は、ベクトルの各次元を 32 ビット浮動小数点 (`fp32`) から 16 ビット浮動小数点 (`fp16`) 表現に変換します。k-NN プラグインに統合された Faiss スカラー量子化器 (SQfp16) を使用すると、再現率の低下を最小限に抑えながら約 50% のメモリを節約できます (ベンチマーク結果を参照)。[SIMD 最適化](https://opensearch.org/docs/latest/search-plugins/knn/knn-index#simd-optimization-for-the-faiss-engine)と組み合わせると、SQfp16 量子化は検索レイテンシを大幅に削減し、インデックス作成スループットを向上させることもできます。

## Faiss スカラー量子化の使用方法

Faiss スカラー量子化を使用するには、k-NN インデックスを作成する際に k-NN ベクトルフィールドの `method.parameters.encoder.name` を `sq` に設定します。

```json
PUT /test-index
{
  "settings": {
    "index": {
      "knn": true
    }
  },
  "mappings": {
    "properties": {
      "my_vector1": {
        "type": "knn_vector",
        "dimension": 8,
        "method": {
          "name": "hnsw",
          "engine": "faiss",
          "space_type": "l2",
          "parameters": {
            "encoder": {
              "name": "sq",
              "parameters": {
                "type": "fp16",
                "clip": true
              }
            },
            "ef_construction": 256,
            "m": 8
          }
        }
      }
    }
  }
}
```

SQ パラメータの詳細については、[k-NN ドキュメント](https://opensearch.org/docs/latest/search-plugins/knn/knn-index/#sq-parameters)を参照してください。

`fp16` エンコーダーは 32 ビットベクトルを 16 ビットに変換します。このエンコーダータイプでは、ベクトル値は **[-65504.0, 65504.0]** の範囲内である必要があります。

上記の `clip` パラメータは、範囲外の値をどのように処理するかを指定します。

- デフォルトでは `clip` は `false` で、範囲外の値を含むベクトルは拒否されます。
- `clip` を `true` に設定すると、範囲外のベクトル値はサポートされる範囲内に切り上げまたは切り下げられます。例えば、元の 32 ビットベクトルが `[65510.82, -65504.1]` の場合、ベクトルは `[65504.0, -65504.0]` の範囲でインデックス化されます。

**注意**: `clip` を `true` に設定するのは、サポート範囲外の要素がごくわずかな場合のみ推奨されます。値を丸めると再現率が低下する可能性があります。

取り込み時には、ベクトルの各次元がサポート範囲 ([-65504.0, 65504.0]) 内であることを確認してください。

```json
PUT test-index/_doc/1
{
  "my_vector1": [-65504.0, 65503.845, 55.82, -65300.456, 34.67, -1278.23, 90.62, 8.36]
}
```

クエリ時には、クエリベクトルに範囲制限はありません。

```json
GET test-index/_search
{
  "size": 2,
  "query": {
    "knn": {
      "my_vector1": {
        "vector": [265436.876, -120906.256, 99.84, 89.45, 100000.45, 9.23, -70.17, 6.93],
        "k": 2
      }
    }
  }
}
```

## fp16 での HNSW メモリ見積もり

HNSW に必要なメモリは `1.1 * (2 * dimension + 8 * M)` バイト/ベクトルと見積もられます。

例として、次元 256、M が 16 の 100 万ベクトルがあると仮定します。メモリ要件は以下のように見積もることができます。

`1.1 * (2 * 256 + 8 * 16) * 1,000,000 ~= 0.656 GB`

IVF (Inverted File) アルゴリズムでのスカラー量子化のメモリ見積もりについては、[こちらのドキュメント](https://opensearch.org/docs/latest/search-plugins/knn/knn-vector-quantization/#memory-estimation-1)を参照してください。

## ベンチマーク結果

[opensearch-benchmark](https://github.com/opensearch-project/opensearch-benchmark-workloads/tree/main/vectorsearch) ツールを使用して、いくつかの一般的なデータセットでベンチマークテストを実行し、Faiss スカラー量子化のインデックス作成、検索パフォーマンス、検索結果の品質を比較しました。Faiss スカラー量子化 (FP16) と、エンコーディングなしの Faiss float ベクトル (FP32) を比較しました。すべてのテストは、x86 アーキテクチャで AVX2 最適化を有効にした [SIMD](https://opensearch.org/docs/latest/search-plugins/knn/knn-index/#simd-optimization-for-the-faiss-engine) (Single Instruction Multiple Data) で実行されました。

**注意**: SIMD 最適化 (AVX2 または NEON) なし、または AVX2 が無効 (x86 アーキテクチャ) の場合、量子化プロセスで追加のオーバーヘッドが発生し、レイテンシが増加します。AVX2 をサポートするプロセッサについては、[CPUs with AVX2](https://en.wikipedia.org/wiki/Advanced_Vector_Extensions#CPUs_with_AVX2) を参照してください。AWS 環境では、[HVM](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/virtualization_types.html) をサポートするすべてのコミュニティ Amazon Machine Images (AMI) が x86 アーキテクチャの AVX2 最適化をサポートしています。

### 小規模ワークロードでのベンチマーク結果

以下のテストは、レプリカなしの単一ノードクラスターで実行しました。

#### 設定

| m | ef\_construction | ef\_search | replica |
| --- | --- | --- | --- |
| 16 | 100 | 100 | 0 |

#### 再現率とメモリ結果

| データセット ID | Faiss hnsw recall@100 | Faiss hnsw-sqfp16 recall@100 | Faiss hnsw メモリ使用量 (gb) | Faiss hnsw-sqfp16 メモリ使用量 (gb) | メモリ削減率 |
| --- | --- | --- | --- | --- | --- |
| Dataset 1 | 0.91 | 0.91 | 3.72 | 1.93 | 48% |
| Dataset 2 | 0.99 | 0.99 | 0.18 | 0.10 | 44% |
| Dataset 3 | 0.95 | 0.95 | 1.43 | 0.75 | 48% |
| Dataset 4 | 0.94 | 0.94 | 3.00 | 1.57 | 48% |
| Dataset 5 | 0.99 | 0.99 | 0.62 | 0.38 | 39% |

#### 分析

ベンチマーク結果を比較すると、以下のことがわかります。

- Faiss HNSW SQfp16 で得られる再現率は、Faiss HNSW と一致します (無視できる程度の差異)。
- SQfp16 を使用すると、**最大 48% のメモリ使用量削減**があり、ディスク使用量もわずかに削減されます。これらの結果は、ベクトル次元が大きいほどメモリ削減が大きくなることを示しています。
- SQfp16 を使用した場合、パフォーマンス指標は `fp32` ベクトルと同様です。

### 大規模ワークロードでのベンチマーク結果

パフォーマンス指標とメモリ節約を比較するために、768 次元の大規模 [Laion](https://laion.ai/about/) 1 億データセットで、Faiss HNSW SQfp16 と Faiss HNSW の両方を使用してテストを実行しました。

#### 設定

|  | Faiss HNSW SQfp16 | Faiss HNSW |
| --- | --- | --- |
| OpenSearch バージョン | 2.13 | 2.13 |
| ベクトル次元 | 768 | 768 |
| 取り込みベクトル数 | 1 億 | 1 億 |
| データノード数 | 4 | 8 |
| データノードインスタンスタイプ | r5.4xlarge | r5.4xlarge |

Faiss HNSW SQfp16 は 4 つのデータノードを必要とし、Faiss HNSW (8 ノード) の半分です。これは、SQfp16 がメモリ要件を 50% 削減することを示しています。

#### 再現率とメモリ結果

| 実験 ID | hnsw-recall@1000 | hnsw-sqfp16-recall@1000 | hnsw メモリ使用量 (gb) | hnsw-sqfp16 メモリ使用量 (gb) | メモリ削減率 |
| --- | --- | --- | --- | --- | --- |
| hnsw 1 | 0.94 | 0.94 | 300.28 | 157.23 | 47.64% |
| hnsw 2 | 0.96 | 0.96 | 300.28 | 157.23 | 47.64% |
| hnsw 3 | 0.98 | 0.98 | 300.28 | 157.23 | 47.64% |

#### 分析

- k=1000 の場合、Faiss HNSW と SQfp16 を使用した Faiss HNSW の再現率は同一です。
- SQfp16 を使用した Faiss HNSW は、Faiss HNSW の約半分のメモリを必要とします (必要なデータノード数で測定)。[k-NN stats API メトリクス](https://opensearch.org/docs/latest/search-plugins/knn/api/#stats)によると、SQfp16 を使用することでメモリ使用量が 47.64% 削減されました。
- ほとんどの場合、SQfp16 は `fp32` ベクトルと比較してより良いインデックス作成スループットを示しました。

## 結論

Faiss SQfp16 スカラー量子化は、フル精度ベクトルと同様の高い再現率パフォーマンスを維持しながら、大幅なメモリ節約を提供する強力な技術です。ベクトルを 16 ビット浮動小数点表現に変換することで、メモリ要件を最大 50% 削減できます。SIMD 最適化と組み合わせると、SQfp16 スカラー量子化はインデックス作成スループットを向上させ、検索レイテンシを削減し、全体的なパフォーマンスの向上につながります。この方法は、メモリ効率と精度の間で優れたバランスを取り、大規模な類似検索アプリケーションにとって価値あるツールとなっています。

## 今後の展望

さらなるメモリ効率を達成するために、[Faiss スカラー量子化器](https://github.com/opensearch-project/k-NN/issues/1723)と [Lucene スカラー量子化器](https://github.com/opensearch-project/k-NN/issues/1277)を使用した `int8` 量子化サポートの導入を計画しています。この技術により、フル精度ベクトルと比較して 75% のメモリ要件削減、つまり 4 倍の圧縮が可能になり、再現率の低下は最小限に抑えられると予想しています。

さらに、バイナリベクトルサポートのリリースを目指しており、前例のない 32 倍の圧縮率を実現します。このアプローチにより、メモリ消費がさらに削減されます。また、検索レイテンシのさらなる削減に貢献する AVX-512 最適化の組み込みも計画しています。

OpenSearch の継続的な分析とチューニングにより、リソース要件を最小化しコスト効率を最大化しながら、大規模な類似検索に対応できます。

## 付録: メモリとデータノード要件の見積もり

1 億件、768 次元の大規模ワークロードベンチマークテストに必要なメモリ量とデータノード数の見積もりは以下の通りです。

```
// Faiss HNSW SQfp16 メモリ見積もり
1.1 * (2 * dimension + 8 * M) * num_of_vectors * (1 + num_of_replicas) バイト

m = 16、num_replicas = 0 とすると

1.1 * (2 * 768 + 8 * 16) * 100000000 * (1 + 0) = 170.47 gb = 171 gb

インスタンス r5.4xlarge は 128 gb のメモリを持ち、そのうち 32 gb は JVM に使用されます。
サーキットブレーカー制限を 0.5 と仮定します。

利用可能な総メモリ = (データノードインスタンスメモリ - JVM メモリ) * サーキットブレーカー制限
利用可能な総メモリ = (128 - 32) * 0.5 = 48gb

データノード数 -> 171/48 = 3.56 = 4
```

```
// Faiss HNSW メモリ見積もり
1.1 * (4 * dimension + 8 * M) * num_of_vectors * (1 + num_of_replicas) バイト

m = 16、num_replicas = 0 とすると

1.1 * (4 * 768 + 8 * 16) * 100000000 * (1 + 0) = 327.83 gb = 328 gb

インスタンス r5.4xlarge は 128 gb のメモリを持ち、そのうち 32 gb は JVM に使用されます。
サーキットブレーカー制限を 0.5 と仮定します。

利用可能な総メモリ = (データノードインスタンスメモリ - JVM メモリ) * サーキットブレーカー制限
利用可能な総メモリ = (128 - 32) * 0.5 = 48gb

データノード数 -> 328/48 = 6.83 = 7 + 1 (安定性のため) = 8
```
