---
title: "[翻訳] OpenSearch 3.5 でバルク SIMD を使用した FP16 ベクトル検索の高速化"
emoji: "🚀"
type: "tech"
topics: ["opensearch", "vectorsearch", "simd", "performance"]
publication_name: "opensearch"
published: true
published_at: 2026-03-03
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/accelerating-fp16-vector-search-performance-using-bulk-simd-in-opensearch-3-5/

OpenSearch 3.1 では、メモリに制約のある環境でベクトル検索を可能にする[メモリ最適化検索](https://docs.opensearch.org/vector-search/optimizing-storage/memory-optimized-search/)を導入しました。しかし、16 ビット浮動小数点、つまり FP16 のベクトル処理はパフォーマンスのボトルネックのままでした。その後の 2 つのリリースで、FP16 の距離計算を段階的に最適化しました。まず OpenSearch 3.4 で SIMD を導入し、次に OpenSearch 3.5 でバルク SIMD を導入することで、最大 310% のスループット向上とレイテンシの大幅な削減を達成しました。本記事では、最適化の過程と、これらのパフォーマンス向上を実現した技術の詳細を紹介します。

## FP16 パフォーマンスの最適化

FP16 のパフォーマンスは、OpenSearch 3.1 でのメモリ最適化検索の導入、3.4 での SIMD 距離計算の実装、3.5 でのバルク SIMD 処理の追加という一連の最適化を通じて改善しました。

### OpenSearch 3.1: メモリ最適化検索

OpenSearch 3.1 では、メモリ最適化検索を導入し、利用可能なメモリがインデックスサイズよりも小さいメモリ制約の厳しい環境で Faiss インデックスを使用できるようにしました。これは、Lucene の検索アルゴリズムと Faiss インデックスを組み合わせることで実現しました。Lucene の早期終了最適化のおかげで、FP16 を除くほぼすべてのベクトルタイプで、インデックスが完全にメモリにロードされたマルチセグメントシナリオにおいて検索 QPS が向上しました。

FP16 はより大きな課題を抱えていました。FP16 から FP32 への変換は Java で行われていたため、CPU がハードウェアで FP16 から FP32 への変換を処理できる場合でも、JVM はソフトウェアベースの変換に依存していました。JVM にはネイティブの FP16 サポートがないため、距離計算を行う前に FP16 ベクトルを FP32 にエンコードする必要がありました。

これが大きなパフォーマンスボトルネックとなり、FP16 を使用した検索はデフォルトの実装と比較してほぼ 2 倍遅くなりました。

### OpenSearch 3.4: SIMD FP16 距離計算

OpenSearch 3.4 では、距離計算をインターセプトして C++ SIMD に委譲することで、FP16 のパフォーマンス制限に対処しました。実装の観点からは、Faiss ライブラリが既に提供している最適化された SIMD コードを活用したため、実装が簡素化されました。

Faiss SIMD は、SIMD レジスタを使用して複数の FP16 値を FP32 にエンコードし、それらに対して同時に演算を行います。このアプローチは、クエリと単一のベクトル間で SIMD を適用し、OpenSearch 3.1 で使用されていたソフトウェアベースの計算と比較して距離計算を大幅に高速化します。

以下の図に、SIMD を使用した内積計算を示します。ループアンローリング技法を使用して、ベクトルの 4 次元を同時に処理し、計算を最適化・高速化します。

![](/images/accelerating-fp16-vector-search-performance-using/451faef55f66.png)

### OpenSearch 3.5: バルク SIMD FP16 距離計算

OpenSearch 3.4 の Faiss SIMD アプローチは既に効率的でしたが、クエリと単一のベクトル間でのみ SIMD を適用していました。つまり、ベクトル比較のたびにクエリベクトルの同じ部分をレジスタに再ロードする必要がありました。ロードされたクエリ値を可能な限り複数のベクトルに再利用することで、これを改善しました。例えば、768 次元のベクトルの場合、最初の 8 つの FP32 値が SIMD レジスタにロードされると、各ベクトル比較のたびに再ロードするのではなく、複数のベクトルに同時に適用できます。レジスタ間でバルク演算を行う方が、値を繰り返しロードして個別に処理するよりもはるかに高速であるため、このアプローチは高速です。

OpenSearch 3.5 では、バルク SIMD FP16 距離計算を導入しました。重要な知見は、評価する候補ベクトルが既に分かっている場合、クエリと各ベクトルを個別に比較するのではなく、距離計算をバルクで実行できるということです。

これがバルク SIMD の核心的なアイデアです。複数のベクトルから対応する float 値をレジスタにロードし、距離を計算して結果を一度に蓄積します。複数のレジスタを同時に活用することで、多くの演算を並列に実行でき、パフォーマンスが大幅に向上します。

これが実際にどのように機能するかを説明するために、内積計算を見てみましょう。

#### 内積の例

以下の図に、バルク SIMD が複数のベクトルにわたって内積を並列に計算する方法を示します。

![](/images/accelerating-fp16-vector-search-performance-using/8310aa26deec.png)

バルク SIMD は、ベクトル要素を 1 つずつではなく、複数同時に処理します。例えば、CPU はクエリベクトルから 4 つの要素とデータベクトルから 4 つの要素を SIMD レジスタにロードし、それらの距離を並列に計算できます。より広い SIMD アーキテクチャ (例: AVX2 や AVX-512) では、1 命令あたりさらに多くの要素を処理できます。

計算が完全にレジスタ内で行われ、データがシーケンシャルにアクセスされるため、以下のメリットがあります。

- L1 キャッシュヒット率が高い
- CPU のハードウェアプリフェッチャが後続の要素を自動的にロードできる
- メモリレイテンシが効果的に隠蔽される

このように、バルク SIMD は並列計算とキャッシュフレンドリーで効率的なメモリアクセスを組み合わせることで、スループットを向上させます。

以下の擬似コードにバルク SIMD のアプローチを示します。

```
// クエリと 4 つの候補ベクトルが既知
uint8_t* Query_Vector <- クエリベクトルを準備
uint8_t* Vector1 <- Vector1 のポインタを取得
uint8_t* Vector2 <- Vector2 のポインタを取得
uint8_t* Vector3 <- Vector3 のポインタを取得
uint8_t* Vector4 <- Vector4 のポインタを取得

// 累積用レジスタ
// FMA は融合積和演算、FMA(a, b, c) = a * b + c
FP32_Register fmpSum1
FP32_Register fmpSum2
FP32_Register fmpSum3
FP32_Register fmpSum4

// すべての値に対してバルク SIMD 内積を実行
// この例では、簡略化のため次元数は 8 の倍数と仮定
for (int i = 0 ; i < Dimension ; i += 8) {
    // 8 つの FP32 値をレジスタにロード
    FP32_Register queryFloats <- Query_Vector[i:i+8]

    // 8 つの FP16 値をレジスタにロード
    FP16_Register1 vec1Float16s <- Vector1[i:i+8]
    FP16_Register2 vec2Float16s <- Vector2[i:i+8]
    FP16_Register3 vec3Float16s <- Vector3[i:i+8]
    FP16_Register4 vec4Float16s <- Vector4[i:i+8]

    // FP16 値を FP32 に変換
    FP32_Register vec1Float32s <- ConvertToFP32(FP16_Register1)
    FP32_Register vec2Float32s <- ConvertToFP32(FP16_Register2)
    FP32_Register vec3Float32s <- ConvertToFP32(FP16_Register3)
    FP32_Register vec4Float32s <- ConvertToFP32(FP16_Register4)

    // 内積: SIMD FMA、accumulate = accumulate + q[i] * v[i]
    fmpSum1 = SIMD_FMA(fmpSum1, queryFloats, vec1Float32s)
    fmpSum2 = SIMD_FMA(fmpSum2, queryFloats, vec2Float32s)
    fmpSum3 = SIMD_FMA(fmpSum3, queryFloats, vec3Float32s)
    fmpSum4 = SIMD_FMA(fmpSum4, queryFloats, vec4Float32s)
}

// スコア値を設定
SCORE[0] = SUM(fmpSum1)
SCORE[1] = SUM(fmpSum2)
SCORE[2] = SUM(fmpSum3)
SCORE[3] = SUM(fmpSum4)
```

ARM Neon 実装の詳細については、[k-NN リポジトリ](https://github.com/opensearch-project/k-NN/blob/main/jni/src/simd/similarity_function/arm_neon_simd_similarity_function.cpp)を参照してください。

## パフォーマンスベンチマーク

以下のセクションでは、パフォーマンスベンチマークの結果を紹介します。

### ベンチマーク環境

- データセット: Cohere-10M、768 次元
- ノード: r7i.4xlarge、r7g.4xlarge
- シャード: 3 ノード、1 レプリカ
- インデックスタイプ: FP16
- セグメント数: 80

### ベンチマーク結果

以下のグラフにベンチマーク結果を示します。

![](/images/accelerating-fp16-vector-search-performance-using/af4250f4db73.png)

以下の表に、各バージョンと CPU アーキテクチャごとの詳細なスループットとレイテンシのメトリクスを示します。

| バージョン | CPU アーキテクチャ | 最大スループット | 平均レイテンシ | p90 レイテンシ | p99 レイテンシ |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 3.1 | r7i | 398.87 | 209.66 | 300 | 330 |
| 3.1 | r7g | 495.49 | 168.64 | 235 | 253 |
| 3.4 | r7i | 1025.45 | 81.42 | 124 | 136 |
| 3.4 | r7g | 1112.13 | 75.09 | 111 | 120 |
| 3.5 | r7i | 1303.76 | 63.99 | 95 | 105 |
| 3.5 | r7g | 1477.88 | 56.42 | 82 | 91 |

OpenSearch 3.1 から 3.4 へのアップグレードにより、QPS が約 230% 向上し、平均レイテンシが半減して、p99 レイテンシが約 300ms から 120ms に低下しました。3.4 から 3.5 への移行では、スループットがさらに 30% 向上し、p99 レイテンシは過去最低の 91ms にまで低下しました。

全体として、OpenSearch 3.1 と 3.5 を比較すると、パフォーマンスの総合的な進化が見られます。スループットは 310% 向上し、レイテンシは約 300% 低下しました。バルク SIMD により、約 450req/s を処理する低速なベースラインから、ほぼ瞬時のレスポンスで約 1,500req/s を処理できる高性能エンジンへと変貌しました。

## 今後の予定

実装の観点から、この最適化はバイトおよび FP32 インデックスにも適用でき、これらが主要なターゲットです。パフォーマンスをさらに最適化する機会を積極的に探っています。

ただし、バイナリインデックスについては、バルク SIMD によるパフォーマンス向上は得られません。これは、XOR 演算が JVM で既に高度に最適化されているためと考えられます。バイナリインデックスにおける SIMD 最適化の機会が生じた場合は、評価を行います。

## 試してみましょう

これらのパフォーマンス改善を体験する準備はできましたか? OpenSearch 3.5 にアップグレードし、FP16 ベクトルインデックスでメモリ最適化検索を有効にして、バルク SIMD の最適化を活用してください。結果やユースケースについて、[OpenSearch フォーラム](https://forum.opensearch.org/)でぜひお聞かせください。皆さんのフィードバックは、コミュニティのためにベクトル検索のパフォーマンスを継続的に改善する助けとなります。
