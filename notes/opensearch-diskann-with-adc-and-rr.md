# Disk-based Vector Search 完全フロー（RR + ADC 対応）

## 概要

OpenSearch の Disk-based Vector Search は、バイナリ量子化を使用してメモリフットプリントを削減しながら高い Recall を維持する機能です。v3.1.0 で導入された Random Rotation (RR) と Asymmetric Distance Calculation (ADC) により、さらに Recall を向上させることができます。

## 全体アーキテクチャ

### インデックス作成時

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              インデックス作成時                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐             │
│  │ 元のベクトル     │ → │ 回転行列 M 適用  │ → │ バイナリ量子化   │             │
│  │ (float32)       │    │ (RR 有効時)     │    │ (0/1 に変換)    │             │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘             │
│                                                                                 │
│  保存されるもの (QuantizationState):                                             │
│  - meanThresholds[] (量子化閾値)                                                │
│  - rotationMatrix[][] (RR 有効時)                                               │
│  - belowThresholdMeans[] / aboveThresholdMeans[] (ADC 用)                       │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 検索時のフロー

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           第 1 フェーズ (ANN Search)                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  クエリベクトル                                                                  │
│       │                                                                         │
│       ▼                                                                         │
│  RR 有効? → YES → rotationMatrix を適用してクエリを回転                         │
│       │                                                                         │
│       ▼                                                                         │
│  ADC 有効?                                                                      │
│    YES → クエリを ADC 変換 → 設定 space type で ADC 計算                        │
│    NO  → クエリを量子化 → HAMMING 距離                                          │
│       │                                                                         │
│       ▼                                                                         │
│  HNSW グラフ検索 → firstPassK 件の候補を取得                                    │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           第 2 フェーズ (Rescore)                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ディスクからフル精度ベクトルを読み込み                                           │
│  元のクエリベクトル vs フル精度ドキュメントベクトル                                │
│  設定された space type (L2/COSINE/INNER_PRODUCT) で正確な距離計算                │
│       │                                                                         │
│       ▼                                                                         │
│  上位 K 件を返却                                                                │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 設定パターン別の動作

| 設定            | 第 1 フェーズ (ANN)                          | 第 2 フェーズ (Rescore)    |
| --------------- | -------------------------------------------- | -------------------------- |
| RR=OFF, ADC=OFF | クエリ量子化 → HAMMING                       | フル精度 → 設定 space type |
| RR=ON, ADC=OFF  | クエリ回転 → 量子化 → HAMMING                | フル精度 → 設定 space type |
| RR=OFF, ADC=ON  | クエリ ADC 変換 → 設定 space type (ADC)      | フル精度 → 設定 space type |
| RR=ON, ADC=ON   | クエリ回転 →ADC 変換 → 設定 space type (ADC) | フル精度 → 設定 space type |

## Random Rotation (RR)

### 概要

Random Rotation は、バイナリ量子化の効果を向上させるための技術です。バイナリ量子化は各次元を等しく扱いますが、実際のデータでは次元ごとに分散が異なることがあります。回転を適用することで、分散の偏りを各次元に均等に分散させます。

### 回転行列の生成方法

1. 行列の各エントリを標準正規分布からサンプリング
2. Gram-Schmidt 法で直交正規化

結果の行列 `M` は `norm(Mx) = norm(x)` を満たします（ベクトルの長さが保存される）。

## Asymmetric Distance Calculation (ADC)

### 概要

ADC は、検索時にクエリベクトルを量子化せず、フル精度のまま使用することで精度を向上させる技術です。

バイナリ量子化では 2 段階で誤差が発生します：

1. ドキュメントベクトルの量子化時（インデックス作成時）- 必須
2. クエリベクトルの量子化時（検索時）- ADC で回避可能

### 変換式

各クエリベクトルのエントリ `q_d` を以下で変換：

```
q_d = (q_d - x_d) / (y_d - x_d)
```

- `x_d`: 次元 d で `0` に量子化された全ドキュメントエントリの平均（below threshold mean）
- `y_d`: 次元 d で `1` に量子化された全ドキュメントエントリの平均（above threshold mean）

## ベンチマーク結果（ADC + RR 併用時）

| データセット         | Space Type | Recall (Baseline) | Recall (Enhanced) | 改善幅 |
| -------------------- | ---------- | ----------------- | ----------------- | ------ |
| sift-128             | l2         | 0.39              | 0.70              | +0.31  |
| gist-960             | l2         | 0.12              | 0.36              | +0.24  |
| glove-200            | cosine     | 0.42              | 0.57              | +0.15  |
| flickr-image-queries | l2         | 0.81              | 0.93              | +0.12  |
| e5_embeddings        | l2         | 0.80              | 0.88              | +0.08  |

### レイテンシへの影響

- 平均検索レイテンシ増加: 約 17.6%

## 使用方法

```json
PUT vector-index
{
  "mappings": {
    "properties": {
      "vector_field": {
        "type": "knn_vector",
        "dimension": 768,
        "method": {
          "name": "hnsw",
          "engine": "faiss",
          "space_type": "l2",
          "parameters": {
            "encoder": {
              "name": "binary",
              "parameters": {
                "random_rotation": true,
                "enable_adc": true
              }
            }
          }
        }
      }
    }
  }
}
```

## 関連コード URL

### インデックス作成時

| 処理                                     | ファイル                                                                                                                                                                                             |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 回転行列生成・適用                       | [QuantizerHelper.java](https://github.com/opensearch-project/k-NN/blob/main/src/main/java/org/opensearch/knn/quantization/quantizer/QuantizerHelper.java)                                            |
| 量子化状態の保存 (RR/ADC パラメータ含む) | [OneBitScalarQuantizationState.java](https://github.com/opensearch-project/k-NN/blob/main/src/main/java/org/opensearch/knn/quantization/models/quantizationState/OneBitScalarQuantizationState.java) |

### 検索時 - 第 1 フェーズ

| 処理                        | ファイル                                                                                                                                                                      |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ANN 検索のエントリポイント  | [KNNWeight.java](https://github.com/opensearch-project/k-NN/blob/main/src/main/java/org/opensearch/knn/index/query/KNNWeight.java)                                            |
| クエリの量子化/ADC 変換判定 | [KNNWeight.java#maybeQuantizeVector / maybeTransformVector](https://github.com/opensearch-project/k-NN/blob/main/src/main/java/org/opensearch/knn/index/query/KNNWeight.java) |

### 検索時 - 第 2 フェーズ (Rescore)

| 処理                   | ファイル                                                                                                                                                                                 |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Rescore 処理の呼び出し | [NativeEngineKnnVectorQuery.java#doRescore](https://github.com/opensearch-project/k-NN/blob/main/src/main/java/org/opensearch/knn/index/query/nativelib/NativeEngineKnnVectorQuery.java) |
| Exact Search 実行      | [ExactSearcher.java](https://github.com/opensearch-project/k-NN/blob/main/src/main/java/org/opensearch/knn/index/query/ExactSearcher.java)                                               |
| スコア計算 (ADC 含む)  | [VectorIdsKNNIterator.java](https://github.com/opensearch-project/k-NN/blob/main/src/main/java/org/opensearch/knn/index/query/iterators/VectorIdsKNNIterator.java)                       |

### Space Type 定義

| 処理                    | ファイル                                                                                                                     |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Space Type とスコア変換 | [SpaceType.java](https://github.com/opensearch-project/k-NN/blob/main/src/main/java/org/opensearch/knn/index/SpaceType.java) |

## 主要コードスニペット

### RR 適用 (QuantizerHelper.java)

```java
if (trainingRequest.isEnableRandomRotation()) {
    rotationMatrix = RandomGaussianRotation.generateRotationMatrix(dim);
}
Pair<float[], float[]> meanStd = calculateMeanAndStdDev(trainingRequest, sampledIndices, rotationMatrix);
```

### ADC/量子化の判定 (KNNWeight.java)

```java
byte[] quantizedVector = maybeQuantizeVector(segmentLevelQuantizationInfo);
float[] transformedVector = maybeTransformVector(segmentLevelQuantizationInfo, spaceType);
```

### ADC スコア計算 (VectorIdsKNNIterator.java)

```java
protected float scoreWithADC(float[] queryVector, byte[] documentVector, SpaceType spaceType) {
    if (spaceType.equals(SpaceType.L2)) {
        return SpaceType.L2.scoreTranslation(KNNScoringUtil.l2SquaredADC(queryVector, documentVector));
    } else if (spaceType.equals(SpaceType.INNER_PRODUCT)) {
        return SpaceType.INNER_PRODUCT.scoreTranslation((-1 * KNNScoringUtil.innerProductADC(...)));
    } else if (spaceType.equals(SpaceType.COSINESIMIL)) {
        return SpaceType.COSINESIMIL.scoreTranslation(1 - KNNScoringUtil.innerProductADC(...));
    }
}
```

### Rescore 時のフル精度検索 (NativeEngineKnnVectorQuery.java)

```java
final ExactSearcher.ExactSearcherContext exactSearcherContext = ExactSearcher.ExactSearcherContext.builder()
    .useQuantizedVectorsForSearch(false)  // フル精度ベクトルを使用
    .k(k)
    .field(knnQuery.getField())
    .floatQueryVector(knnQuery.getQueryVector())
    .build();
```

## 重要なポイント

1. **RR は量子化前に適用**: ドキュメントもクエリも同じ回転行列で回転してから量子化/検索
2. **ADC は第 1 フェーズの距離計算を改善**: HAMMING の代わりに設定された space type に基づく非対称計算
3. **第 2 フェーズは常にフル精度**: RR/ADC の設定に関係なく、元のベクトルで正確な距離計算
4. **Space type は第 2 フェーズで重要**: 最終的なランキングは設定された space type で決まる

## 参考

- RFC Issue: https://github.com/opensearch-project/k-NN/issues/2714
- 対象バージョン: v3.1.0 (RR + ADC)、v3.2.0 (シリアライゼーション対応)

---

**免責事項**: 本レポートは Kiro および GitHub MCP を使用した分析に基づいて作成されています。内容には誤りを含む可能性があるため、正確な挙動については実際のソースコードや公式ドキュメントを参照してください。
