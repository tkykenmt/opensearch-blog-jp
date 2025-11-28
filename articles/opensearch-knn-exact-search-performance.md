---
title: "[翻訳] k-NN 厳密検索のパフォーマンス向上"
emoji: "⚡"
type: "tech"
topics: ["opensearch", "knn", "vectorsearch", "simd", "lucene"]
published: true
publication_name: "opensearch"
published_at: 2024-11-19
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/boosting-k-nn-exact-search/

OpenSearch の厳密 k 近傍法 (k-NN) 検索では、カスタムスコアリング関数を定義して、クエリベクトルとの近接度に基づいてドキュメントを取得できます。この方法は非常に正確な検索結果を提供するため、正確で決定論的なマッチングが必要な場合に最適です。

OpenSearch の `script_score` クエリを使用すると、厳密 k-NN 検索を実行してクエリベクトルに最も近い近傍を見つけることができます。このクエリタイプでは、ドキュメント属性、ユーザー設定、外部データなどの要素を考慮した複雑なスコアリング関数を作成できます。

厳密 k-NN 検索は、数百から数千のドキュメントを含むデータセットに特に効果的です。これは、完全な再現率 (1.0) を保証するためです。この方法は、近似 k-NN の計算オーバーヘッドが速度の利点を上回る可能性がある、小規模または専門的なデータセットに適していることが多いです。ただし、大規模なデータセットでは、レイテンシ管理の観点から近似検索の方が適している場合があります。

## Lucene の SIMD 最適化による高速 k-NN 検索

[Lucene 9.7](https://lucene.apache.org/core/9_7_0/index.html) のリリースでは、Project Panama の Java Vector API が導入され、SIMD (Single Instruction, Multiple Data) 演算を通じて k-NN ベクトル計算が高速化されました。SIMD により、CPU は同じ演算を複数のデータポイントに対して同時に実行できるため、データ並列処理に依存する検索タスクが高速化されます。

OpenSearch 2.15 では、k-NN プラグインのスクリプトスコアリングに SIMD 最適化が追加され、x86 の AVX2 や AVX512、ARM の NEON など、SIMD をサポートする CPU で大幅なパフォーマンス向上が実現しました。OpenSearch 2.17 でのさらなる改善では、最適化されたメモリマップファイルアクセスを含む Lucene の新しいベクトルフォーマットが導入されました。これらの機能強化により、サポートされているハードウェアでの厳密 k-NN 検索の検索レイテンシが大幅に削減されます。

## 厳密 k-NN 検索の実行方法

厳密 k-NN 検索を開始するには、ベクトルデータを格納する 1 つ以上の `knn_vector` フィールドを持つインデックスを作成します。

```json
PUT my-knn-index-1
{
  "mappings": {
    "properties": {
      "my_vector1": { "type": "knn_vector", "dimension": 2 },
      "my_vector2": { "type": "knn_vector", "dimension": 4 }
    }
  }
}
```

次に、サンプルデータをインデックスします。

```json
POST _bulk
{ "index": { "_index": "my-knn-index-1", "_id": "1" } }
{ "my_vector1": [1.5, 2.5], "price": 12.2 }
{ "index": { "_index": "my-knn-index-1", "_id": "2" } }
{ "my_vector1": [2.5, 3.5], "price": 7.1 }
// 簡潔にするため追加のドキュメントは省略
```

最後に、`script_score` クエリを使用して厳密 k-NN 検索を実行します。

```json
GET my-knn-index-1/_search
{
 "size": 4,
 "query": {
   "script_score": {
     "query": { "match_all": {} },
     "script": {
       "source": "knn_score",
       "lang": "knn",
       "params": {
         "field": "my_vector2",
         "query_value": [2.0, 3.0, 5.0, 6.0],
         "space_type": "l2"
       }
     }
   }
 }
}
```

厳密 k-NN 検索と `script_score` クエリの詳細については、[スコアリングスクリプトを使用した厳密 k-NN](https://opensearch.org/docs/latest/search-plugins/knn/knn-score-script/) を参照してください。k-NN 厳密検索の設定方法とカスタムスコアリングの活用方法に関する詳細なガイドが記載されています。

## 実験で実証された実際のパフォーマンス向上

これらの最適化の影響を測定するために、シングルノードクラスターで OpenSearch 2.14 と OpenSearch 2.17 を比較する A/B テストを実施しました。

### クラスター構成

| 項目 | 値 |
|------|------|
| データセット | Cohere 1m |
| データノード | 1 |
| CPU | 8 |
| EBS ボリューム (GB) | 500 |

### 結果

以下の表は、OpenSearch バージョン 2.14 と 2.17 のレイテンシ比較を示しています。

| 空間タイプ | バージョン | 50 パーセンタイルレイテンシ (ms) | 90 パーセンタイルレイテンシ (ms) | 99 パーセンタイルレイテンシ (ms) |
|------------|------------|----------------------------------|----------------------------------|----------------------------------|
| **内積** | 2.14 | 668.84 | 816.95 | 948.21 |
| | 2.17 | 99.58 | 117.08 | 121.37 |
| | **改善率** | 85.11% | 85.67% | 87.20% |
| **L2** | 2.14 | 670.99 | 682.85 | 693.12 |
| | 2.17 | 104.37 | 118.85 | 127.61 |
| | **改善率** | 84.45% | 82.59% | 81.59% |

### 結論

テストの結果、OpenSearch の新しい SIMD サポートと最適化されたメモリアクセスにより、大幅なレイテンシ削減が実現されました。特に内積空間タイプでは、99 パーセンタイルで最大 87% のレイテンシ削減が見られました。

## 厳密 k-NN 検索の今後

将来の OpenSearch バージョンでは、さらに多くの k-NN 検索の柔軟性が提供される予定です。クエリ時に厳密検索と近似検索を切り替えることができるようになります。さらに、将来のバージョンでは、厳密検索タイプと近似検索タイプのインデックスを構築するフィールドを指定する機能も提供される予定です。OpenSearch の k-NN 検索機能の改善を続けていきますので、今後のアップデートにご期待ください。

:::message
OpenSearch 2.17 で最適化された Lucene フォーマットを使用するには、近似最近傍 (ANN) データ構造を構築するために `index.knn` を `true` に設定してください。OpenSearch 2.18 では、新しい `index.knn.advanced.approximate_threshold` 設定が利用可能です。厳密検索のみを実行する場合は、この値を `-1` に設定してインデックス作成時間を短縮できます。
:::
