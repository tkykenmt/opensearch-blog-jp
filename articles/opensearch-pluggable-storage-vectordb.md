---
title: "[翻訳] OpenSearch VectorDB でプラガブルストレージを実現する"
emoji: "🔌"
type: "tech"
topics: ["opensearch", "vectorsearch", "knn", "snapshot", "lucene"]
published: true
published_at: 2024-12-18
publication_name: "opensearch"
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/enable-pluggable-storage-in-opensearch-vectordb/

2019 年、OpenSearch はベクトルエンジンを導入し、Non-Metric Space Library (NMSLIB)、Facebook AI Similarity Search (Faiss)、Lucene の 3 つのネイティブエンジンをサポートしました。Java ベースの Lucene とは異なり、Faiss と NMSLIB は C++ ライブラリであり、OpenSearch は軽量な Java Native Interface (JNI) レイヤーを通じてアクセスします。しかし、これらのネイティブエンジンはファイルベースの API を使用して I/O を処理しており、Faiss は `FILE` ポインタに依存し、NMSLIB は `std::fstream` を使用してグラフインデックスを管理しています。

本記事では、パフォーマンスを損なうことなくネイティブエンジンにデータをロードするための抽象化レイヤーを導入することで、これらの制限にどのように対処したかを説明します。まず k-NN 検索の概要から始め、ファイル API 依存の課題について議論し、実装したソリューションを説明します。最後に、これらの変更がベクトルインデックスの検索可能スナップショットをどのようにサポートするかを探ります。これにより、ネイティブエンジンを使用してリモートスナップショット上で近似 k-NN 検索を実行できるようになります。

## k-NN 検索とは

k 近傍法 (k-NN) 検索アルゴリズムは、与えられたクエリベクトルに最も近い k 個のベクトルを特定します。コサイン類似度などの距離メトリクスを使用してベクトル間の類似性を測定し、近い点ほど類似していると見なされます。

OpenSearch ベクトルデータベースでは、さまざまなベクトル検索アルゴリズムから選択できます。高次元空間での近似最近傍 (ANN) 検索に人気のあるアルゴリズムは、Hierarchical Navigable Small World (HNSW) です。HNSW はデータポイントを多層グラフに整理し、各層には効率的なデータナビゲーションのための接続が含まれています。スキップリストに着想を得た HNSW グラフレイヤーは、深さに比例して密度が増加するさまざまな密度を持っています。これにより、検索空間をより広い領域からより具体的な領域へと絞り込むことができます。国から始めて州、市、通りへと住所を特定するのと同様です。

k-NN 類似検索エンジンの構築の詳細については、[ドキュメント](https://opensearch.org/docs/latest/search-plugins/knn/index/)を参照してください。

## ファイルベース API の課題

Faiss や NMSLIB などのネイティブベクトルエンジンは、高いパフォーマンスと予測可能なレイテンシを提供します。しかし、ファイルベースの API に依存しているため、ファイルシステムベースではないストレージとの統合が困難です。

Lucene は Java ベースの **Directory** 抽象化を使用してファイルの読み書きを行います。**Directory** クラスはファイルストレージを抽象化し、多様なストレージシステム間で読み取り、書き込み、ファイルメタデータの管理などの操作を可能にします。この抽象化により、Lucene ベクトルエンジンは基盤となる OpenSearch ストレージとは独立してファイルを保存できます。

Lucene とは異なり、ネイティブエンジンはファイルベースの I/O と密結合しています。これらの制限に対処するため、Lucene の原則をネイティブエンジンに適用しました。I/O レイヤーを抽象化することで、エンジンの特定のファイル API への密結合を排除しました。この強化により、任意の OpenSearch ディレクトリ実装との統合が可能になり、ベクトル検索がより広範なストレージシステムと互換性を持つようになりました。

## ローディングレイヤーの導入

Faiss と NMSLIB はどちらも、グラフベースのベクトルインデックスをストレージからメモリにロードします。このプロセス中、グラフを再構築するために必要なバイトを取得するために `fread` を使用します。

柔軟性を向上させるため、`fread` を読み取りインターフェースに置き換えました。Faiss はさまざまなストレージシステムからインデックスデータを読み取るための **IOReader** インターフェースを提供しています。NMSLIB には、**NmslibIOReader** と呼ばれる同様の読み取りインターフェースを導入しました。これらのインターフェースにより、ネイティブエンジンは抽象化レイヤーを通じてデータを読み取ることができ、OpenSearch のディレクトリ実装との統合が可能になります。

k-NN 検索はグラフがメモリにロードされた後に実行されるため、この変更は平均検索パフォーマンスに影響しません。

以下の図は、ネイティブエンジンにおけるローディングレイヤーの概要を示しています。

![ローディングレイヤーの概要](/images/opensearch-pluggable-storage-vectordb/loading_layer_high_level.png)

## パフォーマンスベンチマーク

以下のセクションでは、パフォーマンスベンチマークの結果を示します。

### ベンチマーク環境

以下の構成でベンチマークテストを実行しました。

|  |  |
| --- | --- |
| OpenSearch バージョン | 2.18 |
| vCPU | 48 |
| 物理メモリ | 128 GB |
| ストレージタイプ | Amazon Elastic Block Store (Amazon EBS) |
| JVM | 63 GB |
| 総ベクトル数 | 100 万 |
| 次元数 | 128 |

### ベンチマーク結果

ベンチマーク中、ローディングレイヤーの導入によりベースラインと同一の検索パフォーマンスが得られることを確認しました。また、ローディングレイヤーを導入した際のシステムメトリクスや JVM GC メトリクスにも違いはありませんでした。

これらの結果から、File API の密結合を Lucene の **IndexInput** に正常に置き換えることができたと結論付けました。この変更により、同じ検索パフォーマンスが維持されました。さらに、この変更により OpenSearch にカスタム **Directory** を統合し、好みのストレージシステムにベクトルインデックスを保存できるようになりました。

以下の表は、ローディングレイヤー (候補) とベースラインのクエリレイテンシを比較したベンチマーク結果です。

| エンジン | メトリクス | 説明 | ベースライン | 候補 |
| --- | --- | --- | --- | --- |
| Faiss | 平均クエリレイテンシ | ベクトル検索クエリの処理時間 | 3.5832 ms | 3.83349 ms |
| Faiss | p99 クエリレイテンシ | ベクトル検索クエリ処理の p99 レイテンシ | 22.1628 ms | 23.8439 ms |
| Faiss | Young Gen JVM GC 合計時間 | JVM での Young GC に費やされた時間 | 0.338 秒 | 0.342 秒 |

結果は、ファイルベースの API を Lucene の **IndexInput** に置き換えても、より広範なストレージ互換性を実現しながら検索パフォーマンスが維持されることを示しています。

## ベクトル検索用の検索可能スナップショットの設定

ローディングレイヤーが導入されたことで、リモートスナップショット上で直接ベクトル検索を実行できるようになりました。大まかには、ベクトルインデックスを作成し、インデックスのスナップショットを取得し、スナップショット上でベクトル検索を実行します。以下の図はこれらの手順を示しています。

![検索可能スナップショットの概要](/images/opensearch-pluggable-storage-vectordb/searchable_snapshots_overview-1024x838.png)

検索可能スナップショットを設定するには、以下の手順に従ってください。

### 前提条件

クラスターを検索可能スナップショット用に設定します。詳細な手順については、[検索可能スナップショットを使用するためのノードの設定](https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/snapshots/searchable_snapshot/#configuring-a-node-to-use-searchable-snapshots)を参照してください。

### ステップ 1: ローカルインデックスの作成

以下のリクエストを使用してローカルベクトルインデックスを作成します。

```json
PUT /knn-index/
{
  "settings": {
    "index": {
      "knn": true
    }
  },
  "mappings": {
    "properties": {
      "my_vector": {
        "type": "knn_vector",
        "dimension": 2
      }
    }
  }
}
```

### ステップ 2: データの取り込み

インデックスにデータを取り込みます。

```json
POST _bulk?refresh
{ "index": { "_index": "knn-index", "_id": "1" } }
{ "my_vector": [1.5, 2.5], "price": 12.2 }
{ "index": { "_index": "knn-index", "_id": "2" } }
{ "my_vector": [2.5, 3.5], "price": 7.1 }
{ "index": { "_index": "knn-index", "_id": "3" } }
{ "my_vector": [3.5, 4.5], "price": 12.9 }
{ "index": { "_index": "knn-index", "_id": "4" } }
{ "my_vector": [5.5, 6.5], "price": 1.2 }
{ "index": { "_index": "knn-index", "_id": "5" } }
{ "my_vector": [4.5, 5.5], "price": 3.7 }
```

### ステップ 3: ローカルインデックスのクエリ

ローカルインデックスをクエリして、正しく設定されていることを確認します。

```json
POST knn-index/_search
{
  "query": {
    "knn": {
      "my_vector": {
        "vector": [2, 3],
        "k": 2
      }
    }
  }
}
```

レスポンスはクエリベクトルに最も近いベクトルを返します。

```json
{
  "took": 16,
  "timed_out": false,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": {
      "value": 2,
      "relation": "eq"
    },
    "max_score": 0.6666667,
    "hits": [
      {
        "_index": "knn-index",
        "_id": "1",
        "_score": 0.6666667,
        "_source": {
          "my_vector": [1.5, 2.5],
          "price": 12.2
        }
      },
      {
        "_index": "knn-index",
        "_id": "2",
        "_score": 0.6666667,
        "_source": {
          "my_vector": [2.5, 3.5],
          "price": 7.1
        }
      }
    ]
  }
}
```

### ステップ 4: スナップショットの取得

インデックスのスナップショットを取得します。詳細な手順については、[スナップショットの取得と復元](https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/snapshots/snapshot-restore/)を参照してください。スナップショットを取得した後、`knn-index` を削除してローカルで利用できないようにします。

### ステップ 5: スナップショットから検索可能スナップショットインデックスを作成

以下のリクエストを使用して、スナップショットから元のインデックスを復元し、検索可能スナップショットインデックスを作成します。

```json
POST _snapshot/<SNAPSHOT_REPO>/<SNAPSHOT_NAME>/_restore
{
  "storage_type": "remote_snapshot",
  "indices": "knn-index"
}
```

検索可能スナップショットインデックスが正常に作成されたことを確認するには、以下のリクエストを使用します。

```
GET /_cat/indices
```

詳細については、[検索可能スナップショットインデックスの作成](https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/snapshots/searchable_snapshot/#create-a-searchable-snapshot-index)を参照してください。

### ステップ 6: ベクトル検索クエリの実行

検索可能スナップショットインデックス上でベクトル検索クエリを実行します。

```json
POST knn-index/_search
{
  "query": {
    "knn": {
      "my_vector": {
        "vector": [2, 3],
        "k": 2
      }
    }
  }
}
```

クエリはステップ 3 のローカルインデックスクエリと同じ結果を返します。

## まとめ

Lucene の **Directory** 抽象化を使用する I/O レイヤーを導入することで、ネイティブエンジンのローカルファイルシステムへのストレージを制限するファイルベース API への依存を排除しました。この変更により、ベクトルエンジンは OpenSearch の **Directory** 実装でサポートされる任意のストレージシステムからグラフデータ構造を読み取ることができます。広範なベンチマークテストにより、この変更が元のファイル API ベースのアプローチの検索パフォーマンスを維持することが確認されました。特に、グラフがメモリにロードされた後の検索時間に回帰は見られませんでした (グラフのロードは適切にスケーリングされたクラスターでは一度きりの操作です)。

この新しい読み取りインターフェースにより、任意の OpenSearch **Directory** 実装でベクトルインデックスを使用できるようになりました。この柔軟性の追加により、Amazon Simple Storage Service (Amazon S3) などのリモートストレージソリューションにベクトルデータを保存することが可能になります。

## 今後の展望

バージョン 2.18 では、Lucene の **Directory** および **IndexInput** クラスでベクトル検索クエリを使用する機能を導入しました。今後、バージョン 2.19 ではこの機能をネイティブインデックス作成プロセスに拡張します。具体的には、k-NN プラグインは **IndexOutput** クラスを使用してグラフファイルをセグメントに直接書き込むようになります。詳細については、[この GitHub issue](https://github.com/opensearch-project/k-NN/issues/2033) を参照してください。

さらに、k-NN プラグインがベクトルデータ構造ファイルをストリーミングできるようになったことで、これらのファイルの部分的なロードの機会が生まれました。この強化により、クラスターのメモリ負荷が軽減され、特に高負荷条件下でより良い価格性能比が実現されます。詳細については、[この GitHub issue](https://github.com/opensearch-project/k-NN/issues/1693) を参照してください。
