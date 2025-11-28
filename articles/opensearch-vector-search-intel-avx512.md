---
title: "[翻訳] Intel AVX-512 で OpenSearch ベクトル検索のパフォーマンスを向上させる"
emoji: "⚡"
type: "tech"
topics: ["opensearch", "vectorsearch", "intel", "performance", "simd"]
published: true
published_at: 2025-04-08
publication_name: "opensearch"
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/boost-opensearch-vector-search-performance-with-intel-avx512/

OpenSearch 2.18 で導入された Intel Advanced Vector Extensions 512 (Intel AVX-512) は、ベクトルワークロードのパフォーマンスを高速化できる新しい命令セットです。OpenSearch Benchmark を使用したベクトル検索ベンチマークでは、前世代の技術である AVX2 を使用した同じワークロードのパフォーマンスと比較して、インデックス作成で最大 15%、検索タスクで最大 13% のパフォーマンス向上が示されました。

アプリケーション開発者は、アプリケーションの検索品質を向上させるためにベクトル検索を使用することが増えています。この最新の技術は、コンテンツを数値表現 (ベクトル) にエンコードし、コンテンツ間の類似性を見つけるために使用します。大規模言語モデル (LLM) と生成 AI の使用が増加するにつれて、ワークロードは数百万から数十億のベクトルに増加しています。ベクトルデータサイズの増加を考慮すると、このような大規模なワークロードに対してインジェストとクエリのパフォーマンスを維持することが重要になります。

本記事では、Intel AVX-512 と AVX2 を使用したいくつかの一般的な OpenSearch ワークロードの結果を共有し、パフォーマンスを比較します。ベンチマークは [OpenSearch Benchmark](https://github.com/opensearch-project/opensearch-benchmark-workloads/tree/main/vectorsearch) を使用して実行され、Faiss ライブラリを使用した `fp32` および `fp16` 量子化において Intel AVX-512 が AVX2 よりもパフォーマンスを向上させることを示しています。ハードウェアアクセラレータは AWS で広く利用可能であり、これらのベンチマークには r7i として利用可能な第 4 世代 Intel Xeon スケーラブルプロセッサが使用されました。

## OpenSearch ベクトル検索におけるベクトル化の重要性

ベクトル検索は、コサイン類似度やユークリッド距離などの高度な技術を使用して、類似アイテムを迅速かつ効率的に見つけます。これは、従来の検索方法が遅くなる大規模データセットのコンテキストで特に有用です。さらに、ベクトル化されたデータは並列処理が可能であり、高いスケーラビリティを実現し、データセットが成長しても検索パフォーマンスが最適に維持されます。Intel AVX-512 は、より多くのベクトルを処理することで、ベクトル検索のスループットをさらに向上させることができます。

## Intel AVX-512 がより高いパフォーマンスを発揮する理由

ベクトル検索で使用される技術は計算コストが高く、Intel AVX-512 はこれらの課題に対処するのに適しています。アクセラレータは以下のいくつかの方法で直接使用できます。

- イントリンシクスを使用したネイティブコードの記述
- 自動ベクトル化などのコンパイラ最適化

アクセラレータが正しく利用されると、対応する最適化されたアセンブリ命令が生成されます。AVX2 は YMM レジスタを使用する命令を生成し、AVX-512 は ZMM レジスタを使用する命令を生成します。ZMM レジスタは 512 ビットベクトル内でクロックサイクルあたり 32 の倍精度および 64 の単精度浮動小数点演算を処理できるため、パフォーマンスが向上します。さらに、これらのレジスタは 8 つの 64 ビット整数と 16 の 32 ビット整数を処理できます。最大 2 つの 512 ビット融合積和演算 (FMA) ユニットにより、AVX-512 は Intel AVX2 YMM レジスタと比較して、データレジスタの幅、レジスタ数、FMA ユニットの幅を効果的に 2 倍にします。

これらの改善に加えて、Intel AVX-512 は並列性の向上を提供し、科学シミュレーション、分析、機械学習などの計算集約型アプリケーションでのデータ処理の高速化とパフォーマンスの向上につながります。また、複素数計算のサポートが強化され、暗号化やデータ圧縮などのタスクが高速化されます。さらに、AVX-512 には特定のアルゴリズムの効率を向上させ、消費電力を削減し、リソース利用を最適化する新しい命令が含まれており、現代のコンピューティングニーズに対応する強力なツールとなっています。

レジスタ幅を 512 ビットに倍増することで、YMM レジスタの代わりに ZMM レジスタを使用すると、データスループットと計算能力を潜在的に 2 倍にできます。AVX-512 拡張が検出されると、Faiss の距離関数とスカラー量子化関数は、AVX2 拡張のループあたり 8 ベクトルと比較して、ループあたり 16 ベクトルを処理します。

したがって、k 近傍法 (k-NN) を使用したベクトル検索では、これらの新しいハードウェア拡張の使用により、インデックス構築時間とベクトル検索パフォーマンスを向上させることができます。

## OpenSearch ベクトル検索のホットスポット

単一命令複数データ (SIMD) 処理により、AVX-512 は内積と L2 (ユークリッド) 空間タイプの両方でインデックス作成と検索中のホット関数に費やされるサイクル数を削減するのに役立ちます。これは特に FP32 エンコードのインデックス作成で顕著です。次のセクションでは、OpenSearch ベンチマーク実行中に観察されたホット関数と、AVX-512 を使用してホット関数がベクトル化されたときに観察された対応する改善について説明します。ベースラインは Faiss ライブラリの AVX2 バージョンです。**% Cycles spent** は、ベンチマーク実行中に CPU が特定の関数に費やした時間の割合を表します。

### 内積空間タイプ

- **FP32 エンコーディング:**
  - ホット関数:
    - *faiss::fvec_inner_product*
    - *faiss::fvec_inner_product_batch_4*
  - AVX-512 の利点:
    - インデックス作成: 最大 75% のサイクル削減
    - 検索: 最大 8% のサイクル削減

- **SQfp16 エンコーディング:**
  - ホット関数: *faiss::query_to_code*
  - AVX-512 の利点:
    - インデックス作成: 最大 39% のサイクル削減
    - 検索: 最大 11% のサイクル削減

以下の表は、AVX2 と AVX-512 実装を比較した、インデックス作成と検索操作の主要関数に費やされた総 CPU サイクルの割合を示しています。

| 操作 | エンコーディング | 関数 | % Cycles spent (AVX2) | % Cycles spent (AVX-512) |
|------|------------------|------|----------------------|--------------------------|
| インデックス作成 | FP32 | fvec_inner_product | 28.86 | 7.32 |
| インデックス作成 | SQfp16 | query_to_code | 17.95 | 10.94 |
| 検索 | FP32 | fvec_inner_product_batch_4 | 34.66 | 31.74 |
| 検索 | SQfp16 | query_to_code | 42.24 | 37.73 |

### L2 (ユークリッド) 空間タイプ

- **FP32 エンコーディング:**
  - ホット関数:
    - *faiss::fvec_L2sqr*
    - *faiss::fvec_L2sqrt_batch_4*
  - AVX-512 の利点:
    - インデックス作成: 最大 54% のサイクル削減
    - 検索: 最大 11% のサイクル削減

- **SQfp16 エンコーディング:**
  - ホット関数: *faiss::query_to_code*
  - AVX-512 の利点:
    - インデックス作成: 最大 17% のサイクル削減
    - 検索: 最大 6% のサイクル削減

以下の表は、AVX2 と AVX-512 実装を比較した、インデックス作成と検索操作の主要関数に費やされた総 CPU サイクルの割合を示しています。

| 操作 | エンコーディング | 関数 | % Cycles spent (AVX2) | % Cycles spent (AVX-512) |
|------|------------------|------|----------------------|--------------------------|
| インデックス作成 | FP32 | fvec_L2sqr | 36.76 | 16.75 |
| インデックス作成 | SQfp16 | query_to_code | 26.18 | 21.61 |
| 検索 | FP32 | fvec_L2sqr_batch_4 | 31.80 | 28.32 |
| 検索 | SQfp16 | query_to_code | 36.99 | 34.72 |

OpenSearch バージョン 2.18 以降、AVX-512 はデフォルトで有効になっています。2025 年 3 月時点で、OpenSearch は AWS r7i インスタンスで AVX-512 の最高のパフォーマンスを示しています。

次のセクションでは、x64 アーキテクチャ向けに出荷された Faiss ライブラリの AVX2 および AVX-512 バージョンで実行されたベンチマークの結果について説明します (詳細については、[SIMD 最適化](https://opensearch.org/docs/latest/field-types/supported-field-types/knn-methods-engines/#simd-optimization)を参照してください)。これらのベンチマークは、[OpenSearch Benchmark ベクトル検索ワークロード](https://github.com/opensearch-project/opensearch-benchmark-workloads/tree/main/vectorsearch)と以下の[ベンチマーク設定](https://github.com/opensearch-project/project-website/issues/3697#issuecomment-2771024897)を使用して実行されました。

## 結果

結果は、AVX-512 を使用すると距離計算のホット関数に費やされる時間が大幅に削減され、OpenSearch クラスターが検索とインデックス作成でより高いスループットを示すことを示しています。

Faiss ライブラリが提供する SQfp16 エンコーディングは、32 ビット浮動小数点ベクトルを 16 ビット浮動小数点形式に圧縮することで、より高速な計算と効率的なストレージをさらに支援します。メモリフットプリントが小さくなることで、同じメモリ量でより多くのベクトルを保存できます。さらに、16 ビット浮動小数点の演算は通常 32 ビット浮動小数点よりも高速であり、類似性検索の高速化につながります。

FP16 では AVX-512 と AVX2 の間でより大きなパフォーマンス改善が観察されます。これは、Faiss でのコード最適化と AVX-512 イントリンシクスの使用によるもので、AVX2 には存在しません。

すべてのベンチマークに共通する観察として、AVX-512 は[パス長](https://en.wikipedia.org/wiki/Instruction_path_length) (ワークロードを実行するために必要なマシン命令の数) の大幅な削減によりパフォーマンスを向上させます。

### COHERE-1M (FP32)

インデックス作成操作は 9% の向上を示し、検索スループットとレイテンシは AVX2 と比較してそれぞれ 7% と 6% の改善を示しています。

![COHERE-1M インデックス作成 FP32](/images/opensearch-vector-search-intel-avx512/cohere-1m-indexing-fp32.png)

![COHERE-1M 検索 QPS FP32](/images/opensearch-vector-search-intel-avx512/cohere-1m-search-qps-fp32.png)

![COHERE-1M 検索レイテンシ FP32](/images/opensearch-vector-search-intel-avx512/cohere-1m-search-latencies-fp32.png)

### COHERE-1M (SQfp16)

インデックス作成操作は 11% の向上を示し、検索操作とレイテンシは AVX2 と比較して AVX-512 を使用した場合に 10% の改善を示しています。

![COHERE-1M インデックス作成 FP16](/images/opensearch-vector-search-intel-avx512/cohere-1m-indexing-fp16.png)

![COHERE-1M 検索 QPS FP16](/images/opensearch-vector-search-intel-avx512/cohere-1m-search-qps-fp16.png)

![COHERE-1M 検索レイテンシ FP16](/images/opensearch-vector-search-intel-avx512/cohere-1m-search-latencies-fp16.png)

### GIST-1M (FP32)

インデックス作成操作は 5% の向上を示し、検索スループットとレイテンシは AVX2 と比較してそれぞれ 2% と 6% の改善を示しています。`gist-1m` データセットでの検索スループットは `cohere-1m` データセットと比較できませんが、レイテンシの向上は維持されています。

![GIST-1M インデックス作成 FP32](/images/opensearch-vector-search-intel-avx512/gist-1m-indexing-fp32.png)

![GIST-1M 検索 QPS FP32](/images/opensearch-vector-search-intel-avx512/gist-1m-search-qps-fp32.png)

![GIST-1M 検索レイテンシ FP32](/images/opensearch-vector-search-intel-avx512/gist-1m-search-latencies-fp32.png)

### GIST-1M (SQfp16)

インデックス作成操作は 15% の向上を示し、検索スループットとレイテンシは AVX2 と比較して 7% の改善を示しています。

![GIST-1M インデックス作成 FP16](/images/opensearch-vector-search-intel-avx512/gist-1m-indexing-fp16.png)

![GIST-1M 検索 QPS FP16](/images/opensearch-vector-search-intel-avx512/gist-1m-search-qps-fp16.png)

![GIST-1M 検索レイテンシ FP16](/images/opensearch-vector-search-intel-avx512/gist-1m-search-latencies-fp16.png)

### COHERE-10M (FP32)

インデックス作成操作は 8% の向上を示し、検索レイテンシは AVX2 と比較して 5% の改善を示しています。検索クライアントを 20 から 280 にスケーリングすると、AVX-512 で最大 12% の QPS 向上が見られます。

![COHERE-10M インデックス作成 FP32](/images/opensearch-vector-search-intel-avx512/cohere-10m-indexing-fp32.png)

![COHERE-10M 検索スケーリング FP32](/images/opensearch-vector-search-intel-avx512/cohere-10m-search-scaling-fp32.png)

### COHERE-10M (SQfp16)

AVX-512 を使用した SQfp16 エンコーディングは、インデックス作成で 6% のパフォーマンス向上と検索レイテンシで 5% の改善を提供します。スループット分析のために検索クライアントを 20 から 280 にスケーリングすると、AVX-512 を使用した場合に最大 13% の QPS 向上と平均 10% 低いレイテンシが見られます。

![COHERE-10M インデックス作成 FP16](/images/opensearch-vector-search-intel-avx512/cohere-10m-indexing-fp16.png)

![COHERE-10M 検索 QPS スケーリング FP16](/images/opensearch-vector-search-intel-avx512/cohere-10m-search-qps-scaling-fp16.png)

![COHERE-10M 検索レイテンシスケーリング FP16](/images/opensearch-vector-search-intel-avx512/cohere-10m-search-latencies-scaling-fp16.png)

![COHERE-10M 検索レイテンシ FP16](/images/opensearch-vector-search-intel-avx512/cohere-10m-search-latencies-fp16.png)

これらの結果は、Faiss ライブラリの Intel AVX-512 最適化が、異なる次元と空間タイプを持つ複数の OpenSearch ワークロードでベクトル検索のパフォーマンスを向上させるのにどのように役立つかを示しています。

## まとめ

本記事では、Faiss ライブラリを使用したベクトル検索中に現れるいくつかのホット関数を強調し、Intel AVX-512 アクセラレータがこれらの関数を最適化することで OpenSearch のパフォーマンスを大幅に向上させることを示しました。

実験では、前世代の AVX2 アクセラレータと比較して、OpenSearch でインデックス作成で最大 15%、ベクトル検索で最大 13% のスループット増加が示されました。複数のベクトル次元とベクトル空間タイプで改善が見られ、クエリレイテンシは平均 10% 改善されています。これらのアクセラレータは AWS を含むほとんどのクラウド環境の Intel インスタンスに存在し、OpenSearch でシームレスに使用できます。

AWS 上の OpenSearch クラスターでパフォーマンスを最大化するには、最新の AVX-512 アクセラレータを搭載した Intel [C7i、M7i、または R7i インスタンス](https://aws.amazon.com/ec2/instance-types/)の使用を検討してください。これらはベクトル検索ワークロードに最適な選択肢です。

## 今後の改善

この作業を基に、Intel 第 4 世代 Xeon スケーラブルおよびより新しいサーバープロセッサで利用可能な高度な機能を使用する予定です。主要な改善の 1 つは、スカラー量子化器に [AVX512-FP16](https://www.intel.com/content/www/us/en/content-details/669773/intel-avx-512-fp16-instruction-set-for-intel-xeon-processor-based-products-technology-guide.html) 演算を使用することです。これにより、Faiss SQfp16 (`on_disk` モードでの 2 倍圧縮) の検索レイテンシがさらに削減され、インデックス作成スループットが向上することが期待されます。

## 注意事項と免責事項

検索パフォーマンスは、使用状況、設定、その他の要因によって異なります。詳細については、[Performance Index の概要](https://edc.intel.com/content/www/us/en/products/performance/benchmarks/overview/)を参照してください。パフォーマンス結果は、設定に示された日付時点でのテストに基づいており、公開されているすべての更新を反映していない場合があります。

Intel テクノロジーには、有効化されたハードウェア、ソフトウェア、またはサービスのアクティベーションが必要な場合があります。

**注意事項:**

パフォーマンスは、データ構造、クエリパターン、インデックスなどの要因に大きく依存する可能性があることを覚えておいてください。特定のユースケースに対してパフォーマンスとコストのバランスが取れた最適なセットアップを見つけるために、異なるインスタンスタイプと設定でアプリケーションをテストすることをお勧めします。
