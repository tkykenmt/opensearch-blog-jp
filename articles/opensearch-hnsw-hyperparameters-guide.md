---
title: "[翻訳] HNSW ハイパーパラメータ選択の実践ガイド"
emoji: "🔍"
type: "tech"
topics: ["opensearch", "vectorsearch", "hnsw", "machinelearning"]
published: true
published_at: 2025-04-10
publication_name: "opensearch"
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/a-practical-guide-to-selecting-hnsw-hyperparameters/

ベクトル検索は、多くの機械学習 (ML) やデータサイエンスのパイプラインで重要な役割を果たしています。大規模言語モデル (LLM) の文脈では、ベクトル検索は [Retrieval-Augmented Generation (RAG)](https://aws.amazon.com/what-is/retrieval-augmented-generation/) を支える技術です。RAG は大規模なドキュメントコレクションから関連するコンテンツを取得し、LLM の応答を改善する手法です。大規模データセットに対して厳密な k 近傍 (k-NN) を求めることは計算コストが高いため、効率を向上させるために [Hierarchical Navigable Small Worlds (HNSW)](https://arxiv.org/pdf/1603.09320) などの近似最近傍 (ANN) 検索手法がよく使用されます [1]。

## HNSW の最適化：検索品質と速度のバランス

HNSW を効果的に設定することは、複数の目的を同時に最適化する問題です。本記事では、以下の 2 つの主要な目的に焦点を当てます。

- **検索品質**: recall@k で測定。上位 k 件の真の近傍のうち、HNSW が返す k 件の結果に含まれる割合。
- **検索速度**: クエリスループットで測定。1 秒あたりに実行されるクエリ数。

インデックス構築時間やインデックスサイズも重要ですが、これらは今後の記事で取り上げる予定です。

HNSW グラフの構造はハイパーパラメータによって制御され、ベクトル間の接続密度が決まります。密なグラフは一般的に recall を向上させますがクエリスループットを低下させ、疎なグラフはその逆の効果があります。適切なバランスを見つけるには複数の設定をテストする必要がありますが、これを効率的に行う方法についてのガイダンスは限られています。

## 主要な HNSW ハイパーパラメータ

HNSW で最も重要な 3 つのハイパーパラメータは以下の通りです。

- **`M`** – ベクトルあたりのグラフエッジの最大数。値が大きいほどメモリ使用量が増加しますが、検索品質が向上する可能性があります。
- **`efSearch`** – 検索時の候補キューのサイズ。値が大きいほど検索品質が向上する可能性がありますが、検索レイテンシが増加します。
- **`efConstruction`** – `efSearch` と同様ですが、インデックス構築時に使用されます。値が大きいほど検索品質が向上しますが、インデックス構築時間が増加します。

## 効果的な設定の見つけ方

これらのハイパーパラメータをチューニングする 1 つのアプローチは、**ハイパーパラメータ最適化 (HPO)** です。これはブラックボックス関数の最適な設定を探索する自動化技術です [5, 6]。しかし、HPO は計算コストが高く、特に基礎となるアルゴリズムがよく理解されている場合には、限られた効果しか得られないことがあります [3]。

代替手段として **転移学習** があります。これは、あるデータセットの最適化から得られた知識を別のデータセットに適用する手法です。このアプローチは、効率性を維持しながら最適な結果に近い設定を特定するのに役立ちます [3, 4]。

## 推奨される HNSW 設定

次のセクションでは、HNSW 設定を選択する方法を紹介します。このアプローチに基づき、グラフ密度を段階的に増加させる **5 つの事前計算された設定** を提供します。これらの設定は、異なるデータセット間で検索品質と速度のさまざまなトレードオフをカバーしています。

検索パフォーマンスを最適化するには、**これら 5 つの設定を順番に評価** し、recall が要件を満たした時点で停止できます。設定は検索品質が向上する順に並んでいるため、この順序でテストすると各ステップでより良い検索品質が得られる可能性が高くなります。

```
{'M': 16,  'efConstruction': 128, 'efSearch': 32}
{'M': 32,  'efConstruction': 128, 'efSearch': 32}
{'M': 16,  'efConstruction': 128, 'efSearch': 128}
{'M': 64,  'efConstruction': 128, 'efSearch': 128}
{'M': 128, 'efConstruction': 256, 'efSearch': 256}
```

## HNSW のためのポートフォリオ学習

ポートフォリオ学習 [2, 3, 4] は、異なるシナリオで評価した際に平均的に少なくとも 1 つが良好に機能するような、相補的な設定のセットを選択します。このアプローチを HNSW に適用し、recall とクエリスループットのバランスを取る設定のセットを特定することを目指しました。

これを達成するために、さまざまなモダリティ、埋め込みモデル、距離関数にまたがる 15 のベクトル検索データセットを使用しました (下表参照)。各データセットについて、厳密な k-NN 検索を使用してテストセット内のすべてのクエリに対する上位 10 件の最近傍を計算し、グラウンドトゥルースを確立しました。

| データセット                                                                                                     | 次元数 | 訓練サイズ | テストサイズ | 近傍数 | 距離          | 埋め込み                      | ドメイン                  |
| ---------------------------------------------------------------------------------------------------------------- | ------ | ---------- | ------------ | ------ | ------------- | ----------------------------- | ------------------------- |
| [Fashion-MNIST](https://github.com/zalandoresearch/fashion-mnist)                                                | 784    | 60,000     | 10,000       | 100    | Euclidean     | –                             | 画像、衣類                |
| [MNIST](http://yann.lecun.com/exdb/mnist/)                                                                       | 784    | 60,000     | 10,000       | 100    | Euclidean     | –                             | 画像、数字                |
| [GloVe](https://nlp.stanford.edu/projects/glove/)                                                                | 25     | 1,183,514  | 10,000       | 100    | Angular       | 単語-単語共起行列             | 言語 (wiki, common crawl) |
| [GloVe](https://nlp.stanford.edu/projects/glove/)                                                                | 50     | 1,183,514  | 10,000       | 100    | Angular       | 単語-単語共起行列             | 言語 (wiki, common crawl) |
| [GloVe](https://nlp.stanford.edu/projects/glove/)                                                                | 100    | 1,183,514  | 10,000       | 100    | Angular       | 単語-単語共起行列             | 言語 (wiki, common crawl) |
| [GloVe](https://nlp.stanford.edu/projects/glove/)                                                                | 200    | 1,183,514  | 10,000       | 100    | Angular       | 単語-単語共起行列             | 言語 (wiki, common crawl) |
| [NY Times](https://archive.ics.uci.edu/dataset/164/bag+of+wordsD199572657/)                                      | 256    | 290,000    | 10,000       | 100    | Angular       | BoW                           | 言語、ニュース記事        |
| [NY Times](https://archive.ics.uci.edu/dataset/164/bag+of+wordsD199572657/)                                      | 16     | 290,000    | 10,000       | 100    | Angular       | BoW                           | 言語、ニュース記事        |
| [SIFT](http://corpus-texmex.irisa.fr/)                                                                           | 128    | 1,000,000  | 10,000       | 100    | Euclidean     | SIFT 記述子                   | 画像                      |
| [SIFT](https://github.com/erikbern/ann-benchmarks/tree/main)                                                     | 256    | 1,000,000  | 10,000       | 100    | Hamming       | SIFT 記述子                   | 画像                      |
| [Last.fm](http://millionsongdataset.com/lastfm/)                                                                 | 65     | 292,385    | 50,000       | 100    | Inner product | 行列分解                      | 楽曲レコメンデーション    |
| [Word2bits](https://github.com/agnusmaximus/Word2BitsD199572657/)                                                | 800    | 399,000    | 1,000        | 100    | Hamming       | 量子化パラメータ付き Word2Vec | 言語、英語 Wikipedia      |
| [GIST](http://corpus-texmex.irisa.fr/)                                                                           | 960    | 1,000,000  | 1,000        | 100    | Euclidean     | GIST 記述子、INRIA C 実装     | 画像                      |
| [MS MARCO](https://microsoft.github.io/msmarco/)                                                                 | 384    | 1,000,000  | 50,000       | 100    | Euclidean     | MiniLLM                       | 言語、質問応答            |
| [openai-dbpedia](https://huggingface.co/datasets/Qdrant/dbpedia-entities-openai3-text-embedding-3-large-1536-1M) | 1,536  | 950,000    | 50,000       | 100    | Euclidean     | text-embedding-3-large        | 言語、DBPedia             |

各データセットについて、以下の探索空間に基づく 80 の HNSW 設定のグリッドを評価しました。

```
search_space = {
    "M": [8, 16, 32, 64, 128],
    "efConstruction": [32, 64, 128, 256],
    "efSearch": [32, 64, 128, 256]
}
```

これらの実験では、3 つのクラスターマネージャーノードと 6 つのデータノード (各ノードは `r6g.4xlarge.search` インスタンス) で構成される OpenSearch 2.15 クラスターを使用しました。テストベクトルを 100 件のバッチで評価し、各 HNSW 設定のクエリスループットと recall@10 を記録しました。次のセクションでは、ポートフォリオを学習するために使用したアルゴリズムを紹介します。

### 手法

recall とスループットの異なるトレードオフを捉えるために、シンプルな線形化アプローチを使用し、recall とスループットの両方に 0 から 1 (両端を含む) の値を割り当てました。特定の重み付けが与えられた場合、以下の 4 つのステップで線形化された目的を最大化する設定を特定しました。

1. **recall とスループットの正規化** – 各データセット内で min-max スケーリングを適用し、recall とスループットの値を比較可能にします。
2. **重み付きメトリクスの計算** – 割り当てられた重みを使用して、正規化された recall とスループットを新しい重み付きメトリクスに結合します。
3. **データセット間での平均化** – データセット間で重み付きメトリクスの平均を計算します。
4. **最良の設定を選択** – 平均重み付きメトリクスを最大化する設定を特定します。

以下の図は、2 つのデータセットと 3 つの設定を使用した例でアルゴリズムを説明しています。

![ポートフォリオ学習アルゴリズム](/images/opensearch-hnsw-hyperparameters-guide/hnsw-portfolio-learn.png)

recall とスループットに対して以下の重み付けプロファイルを使用しました。ほとんどのアプリケーションではスループットを最適化する前に良好な recall を達成することを優先するため、スループットに高い重みを割り当てませんでした。

|                | 0   | 1   | 2   | 3   | 4   |
| -------------- | --- | --- | --- | --- | --- |
| `w_recall`     | 0.9 | 0.8 | 0.7 | 0.6 | 0.5 |
| `w_throughput` | 0.1 | 0.2 | 0.3 | 0.4 | 0.5 |

## 評価

2 つのシナリオで手法を評価しました。

1. **Leave-one-out 評価** – 15 のデータセットのうち 1 つをテストデータセットとして使用し、残りのデータセットを訓練セットとして使用します。
2. **デプロイメント評価** – 15 のデータセットすべてを訓練に使用し、訓練セットに含まれていない新しい埋め込みモデル [Cohere-embed-english-v3](https://huggingface.co/Cohere/Cohere-embed-english-v3.0) を使用した 4 つの追加データセットで手法をテストします。

最初のシナリオは機械学習における交差検証を模倣し、2 番目のシナリオは完全な訓練データセットを使用した本番デプロイメントでの評価をシミュレートします。

### Leave-one-out 評価

この評価では、テストデータセットに手法を適用して異なる重み付けでのグラウンドトゥルース設定を決定しました。次に、同じ手法を使用して訓練データセットから導出された予測設定と比較しました。

正規化された (min-max スケーリングされた) recall とスループットについて、予測設定とグラウンドトゥルース設定の間の平均絶対誤差 (MAE) を計算しました。以下の棒グラフは、leave-one-out 評価における 15 のデータセット全体の平均 MAE を示しています。

![MAE 結果](/images/opensearch-hnsw-hyperparameters-guide/mae.png)

結果は、正規化された recall の平均 MAE が 0.1 未満であることを示しています。具体的には、データセットの recall 値が 0.5 から 0.95 の範囲である場合、0.1 の MAE は生の recall 差がわずか 0.045 であることを意味します。これは、予測設定がグラウンドトゥルース設定に近いことを示しており、特に高 recall の重み付けで顕著です。

スループットの MAE はより大きくなっていますが、これはスループット測定が recall 測定よりもノイズが多い傾向があるためと考えられます。ただし、スループットに高い重みを割り当てると MAE は減少します。

### デプロイメント評価

この評価では、15 の訓練データセットに手法を適用し、Cohere-embed-english-v3 埋め込みモデルを使用した 3 つのデータセットで結果の設定をテストしました。目標は、学習された設定が recall とスループットの異なるトレードオフを表すパレートフロントに沿っていることを確認することでした。

以下のプロットは、学習された設定の recall とスループットを異なる色で示し、他の設定はグレーで表示しています。

![トレードオフ結果](/images/opensearch-hnsw-hyperparameters-guide/tradeoff.png)

結果は、選択された 5 つの設定が高 recall および高スループット領域を効果的にカバーしていることを示しています。スループットに高い重みを割り当てなかったため、学習された設定は低 recall・高スループット領域には及んでいません。

## OpenSearch での設定の適用方法

これらの設定を試すには、まずインデックスを作成します。インデックス構築パラメータは動的ではないため、インデックス作成時に指定する必要があります。

```bash
curl -X PUT "localhost:9200/test-index" -H 'Content-Type: application/json' -d'
{
  "settings" : {
    "knn": true
  },
  "mappings": {
    "properties": {
      "my_vector": {
        "type": "knn_vector",
        "dimension": 4,
        "space_type": "l2",
        "method": {
          "name": "hnsw",
          "parameters": {
            "m": 16,
            "ef_construction": 256
          }
        }
      }
    }
  }
}
'
```

次に、データを投入します。

```bash
curl -X PUT "localhost:9200/_bulk" -H 'Content-Type: application/json' -d'
{ "index": { "_index": "test-index" } }
{ "my_vector": [1.5, 5.5, 4.5, 6.4]}
{ "index": { "_index": "test-index" } }
{ "my_vector": [2.5, 3.5, 5.6, 6.7]}
{ "index": { "_index": "test-index" } }
{ "my_vector": [4.5, 5.5, 6.7, 3.7]}
{ "index": { "_index": "test-index" } }
{ "my_vector": [1.5, 5.5, 4.5, 6.4]}
'
```

最後に、検索を実行します。

```bash
curl -X GET "localhost:9200/test-index/_search?pretty&_source_excludes=my_vector" -H 'Content-Type: application/json' -d'
{
  "size": 100,
  "query": {
    "knn": {
      "my_vector": {
        "vector": [0, 0, 0, 0],
        "k": 100,
        "method_parameters": {
          "ef_search": 128
        }
      }
    }
  }
}
'
```

`ef_search` は検索時パラメータであるため、各検索リクエストで動的に設定できます。

### Python クライアントを使用したエンドツーエンドの例

以下は、[boto3](https://pypi.org/project/boto3/) と [opensearch-py](https://pypi.org/project/opensearch-py/) パッケージを使用した Python クライアントでのエンドツーエンドの例です。

#### 必要なモジュールの読み込み

```python
from typing import Tuple, List
import sys
import time
import logging
import random
import hashlib
import json

import h5py
import numpy as np
import pandas as pd
from tqdm import tqdm
import boto3

from opensearchpy import OpenSearch, RequestsHttpConnection, helpers
from opensearchpy.exceptions import RequestError, NotFoundError, TransportError
from opensearchpy.helpers.errors import BulkIndexError
from requests_aws4auth import AWS4Auth
```

#### データ読み込み関数の修正

以下の関数は、`"documents"`、`"queries"`、`"ground_truth"` のキーを持つ `hdf5` ファイルを想定しています。

```python
def load_data(local_file_path: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    local_file_path からベクトルデータセットを読み込む

    Args:
        local_file_path (str): ローカルファイルへのパス

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray]:
        以下を含むタプル:
          - documents (np.ndarray): 検索対象のベクトルセット (n, m)
          - querys (np.ndarray): ANN アルゴリズムをテストするためのクエリベクトルセット (q, m)
          - neighbors (np.ndarray): 各クエリのグラウンドトゥルース上位 k 近傍を含む配列 (q, k)
    """
    hdf5_file = h5py.File(local_file_path, "r")
    vectors = hdf5_file["documents"]
    query_vectors = hdf5_file["queries"]
    neighbors = hdf5_file["ground_truth"]
    return vectors, query_vectors, neighbors
```

#### ユーティリティ関数の読み込み

```python
logger = logging.getLogger(__name__)


def get_client(host: str, region: str, profile: str) -> OpenSearch:
    """指定されたホストと AWS リージョンを使用して OpenSearch クライアントを取得する。
    AWS 認証情報が設定されていることを前提とする。

    Args:
        host (str): OpenSearch ドメインエンドポイント
        region (str): AWS リージョン (例: us-west-2)

    Returns:
        OpenSearch: OpenSearch クライアント
    """
    credentials = boto3.Session(profile_name=profile, region_name=region).get_credentials()

    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        "es",
        session_token=credentials.token,
    )

    client = OpenSearch(
        hosts=[{"host": host, "port": 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        timeout=60 * 60 * 5,
        search_timeout=60 * 60 * 5,
    )
    return client


def create_index_body(config, engine):
    return {
        "settings": {
            "index": {"knn": True, "knn.algo_param.ef_search": config["efSearch"]},
            "number_of_shards": 1,
            "number_of_replicas": 0,
        },
        "mappings": {
            "_source": {"excludes": ["vector"], "recovery_source_excludes": ["vector"]},
            "properties": {
                "vector": {
                    "type": "knn_vector",
                    "dimension": config["dim"],
                    "method": {
                        "name": "hnsw",
                        "space_type": config["space"],
                        "engine": engine,
                        "parameters": {
                            "ef_construction": config["efConstruction"],
                            "m": config["M"],
                        },
                    },
                }
            },
        },
    }


def get_index_name(config: dict) -> str:
    """設定辞書をハッシュ化して一意のインデックス名を取得する

    Args:
        config (dict): 評価する HNSW 設定

    Returns:
        str: ハッシュを使用した一意のインデックス名
    """
    dict_str = "_".join(map(str, config.values()))
    hash_obj = hashlib.md5(dict_str.encode())
    index_name = hash_obj.hexdigest()
    return index_name


def random_delay(lower_time_limit: float = 1.0, upper_time_limit: float = 2.0) -> float:
    return min(lower_time_limit + random.random() * upper_time_limit, upper_time_limit)


def bulk_index_vectors(
    client: OpenSearch,
    index: str,
    vectors: List[np.ndarray],
    source_name: str,
    batch_size=1000,
):
    """batch_size でベクトルを index_name のインデックスにバルク投入する

    Args:
        client (OpenSearch): OpenSearch クライアント
        index (str): ベクトルを投入するインデックス
        vectors (List[np.ndarray]): 投入するベクトルのリスト
        source_name (str): `_source` フィールドで使用する名前
        batch_size (int, optional): デフォルトは 1000
    """
    actions = []
    for i, vector in enumerate(
        tqdm(vectors, desc="Indexing vectors", total=len(vectors), file=sys.stdout)
    ):
        action = {
            "_index": index,
            "_id": i,
            "_source": {source_name: vector.tolist()},
        }
        actions.append(action)

        if len(actions) == batch_size:
            helpers.bulk(client, actions)
            actions = []

    if actions:
        helpers.bulk(client, actions)


def delete_one_index(client: OpenSearch, index: str, max_retry: int = 5):
    try:
        client.indices.clear_cache(
            index=index, fielddata=True, query=True, request=True
        )
    except NotFoundError:
        pass

    success = False
    count = 0
    while not success and count < max_retry:
        try:
            client.indices.delete(index=index)
            success = True
        except NotFoundError:
            logger.error(f"{index} not found, SKIP.")
            success = True
        except RequestError as e:
            delay = random_delay()
            logger.error(f"{index} delete failed {e}, wait {delay} seconds.")
            time.sleep(delay)
        count += 1


def get_graph_memory(client: OpenSearch) -> float:
    resp = client.transport.perform_request(
        method="GET", url=f"/_plugins/_knn/stats?pretty"
    )
    return sum([stat["graph_memory_usage"] for node_id, stat in resp["nodes"].items()])


def knn_bulk_search(client, config, index_name, query_vectors, k):
    msearch_body = ""
    for query_vector in query_vectors:
        search_header = '{"index": "' + index_name + '"}\n'
        search_body = {
            "size": k,
            "query": {
                "knn": {
                    "vector": {
                        "vector": query_vector.tolist(),
                        "k": k,
                    }
                }
            },
            "_source": False,
        }
        msearch_body += search_header + json.dumps(search_body) + "\n"

    response = client.msearch(body=msearch_body)
    return response


def pad_list(input_list, n):
    """
    入力リストの長さが n 未満の場合、右側に -1 でパディングする。
    """
    if len(input_list) < n:
        input_list += [-1] * (n - len(input_list))
    return input_list


def batch_knn_search(client, config, index_name, query_vectors, batch_size, k):
    pred_inds = []
    took_time = 0.0
    for i in tqdm(
        range(0, len(query_vectors), batch_size), desc="Search vectors", file=sys.stdout
    ):
        batch = query_vectors[i : i + batch_size]
        results = knn_bulk_search(client, config, index_name, batch, k)
        for j, result in enumerate(results["responses"]):
            ids = [hit["_id"] for hit in result["hits"]["hits"]]
            if len(ids) < k:
                logger.error(f"{config} batch {i} search needs padding")
                ids = pad_list(ids, k)
            pred_inds.append(ids)
        took_time += results["took"]
    return pred_inds, took_time * 0.001


def compute_recall(labels: np.ndarray, pred_labels: np.ndarray):
    assert labels.shape[0] == pred_labels.shape[0], (
        labels.shape,
        pred_labels.shape,
    )
    assert labels.shape[1] == pred_labels.shape[1], (
        labels.shape,
        pred_labels.shape,
    )
    labels = labels.astype(int)
    pred_labels = pred_labels.astype(int)
    k = labels.shape[1]
    correct = 0
    for pred, truth in zip(pred_labels, labels):
        top_k_pred, truth_k = pred[:k], truth[:k]
        for p in top_k_pred:
            for y in truth_k:
                if p == y:
                    correct += 1
    return float(correct) / (k * labels.shape[0])


def ingest_vectors(
    config: dict,
    engine: str,
    client: OpenSearch,
    index_name: str,
    vectors: List[np.ndarray],
):
    index_body = create_index_body(config, engine)

    success = False
    max_try = 0
    while not success and max_try < 5:
        try:
            client.indices.create(index=index_name, body=index_body)
            logger.info(f"{index_name}: Ingesting vectors")
            bulk_index_vectors(client, index_name, vectors, "vector")
            success = True
        except BulkIndexError as e:
            delay = random_delay()
            delete_one_index(client, index_name)
            max_try += 1
            time.sleep(random_delay())
            logger.error(
                f"{index_name}: BulkIndexError, retrying after {delay} seconds\n{e}"
            )
        except RequestError as e:
            if e.error == "resource_already_exists_exception":
                delay = random_delay()
                logger.error(f"{e}, delete and retry after {delay} seconds")
                delete_one_index(client, index_name)
                time.sleep(random_delay())
                max_try += 1
            else:
                raise


def query_index(config, index_name, client, query_vectors, k) -> list[np.ndarray]:
    success = False
    batch_size = 100
    max_try = 0
    while not success and max_try < 5:
        try:
            pred_inds, search_time = batch_knn_search(
                client, config, index_name, query_vectors, batch_size=batch_size, k=k
            )
            success = True
            return pred_inds, search_time
        except TransportError as e:
            delay = random_delay()
            logger.error(
                f"{index_name}: Query failed, retrying after {delay} seconds {e}"
            )
            time.sleep(delay)
            max_try += 1
    raise Exception(f"{index_name}: Query failed after {max_try} retries")


def eval_config(
    config: dict, local_file_path: str, host: str, region: str, aws_profile: str, engine: str, k=10
):

    vectors, query_vectors, neighbors = load_data(local_file_path)
    client = get_client(host, region, aws_profile)
    index_name = get_index_name(config)

    ingest_vectors(config, engine, client, index_name, vectors)

    client.transport.perform_request(method="POST", url=f"/{index_name}/_refresh")
    client.transport.perform_request(
        method="GET", url=f"/_plugins/_knn/warmup/{index_name}?pretty"
    )
    stats = client.indices.stats(index=index_name, metric="store")
    index_size_in_bytes = stats["indices"][index_name]["total"]["store"][
        "size_in_bytes"
    ]
    graph_mem_in_kb = get_graph_memory(client)

    time.sleep(random_delay(lower_time_limit=5, upper_time_limit=10))

    logger.info(f"{index_name}: Query indexes")
    pred_inds, search_time = query_index(config, index_name, client, query_vectors, k)

    groundtruth_topk_neighbors = [v[:k] for v in neighbors]
    recall = compute_recall(np.array(groundtruth_topk_neighbors), np.array(pred_inds))
    logger.info(f"{index_name}: Recall {recall}")

    config.update(
        {
            f"recall@{k}": recall,
            "search_time": search_time,
            "search_throughput": len(query_vectors) / search_time,
            "index_size_in_bytes": index_size_in_bytes,
            "graph_mem_in_kb": graph_mem_in_kb,
        }
    )

    delete_one_index(client, index_name)
    logger.info(f"Clean up done, finishing evaluation.")
    return config
```

#### 実験用変数の定義

実験用に以下の変数を定義します。

- OpenSearch ドメインとエンジン
- AWS リージョンと AWS プロファイル
- ローカルファイルパス
- データセットの次元数
- HNSW で使用する空間

```python
host = "your_domain_endpoint_without_https://"
engine = "faiss"

region = "us-west-2"
aws_profile = "your_aws_profile"

local_file_path = "your_data_path"
dim = 384  # ベクトル次元数
space = "l2"  # HNSW の空間
```

#### 異なる設定の評価

```python
metrics = []
for i, config in enumerate([
    {'M': 16, 'efConstruction': 128, 'efSearch': 32},
    {'M': 32, 'efConstruction': 128, 'efSearch': 32},
    {'M': 16, 'efConstruction': 128, 'efSearch': 128},
    {'M': 64, 'efConstruction': 128, 'efSearch': 128},
    {'M': 128, 'efConstruction': 256, 'efSearch': 256}
]):
    config.update({"dim": dim, "space": space})
    metric = eval_config(config, local_file_path, host, region, aws_profile, engine)
    metrics.append(metric)
```

ターミナルに以下のような出力が表示されます。

```
Indexing vectors: 100%|██████████| 8674/8674 [00:26<00:00, 321.72it/s]
Search vectors: 100%|██████████| 15/15 [00:09<00:00,  1.55it/s]
Indexing vectors: 100%|██████████| 8674/8674 [00:34<00:00, 248.95it/s]
Search vectors: 100%|██████████| 15/15 [00:07<00:00,  1.88it/s]
Indexing vectors: 100%|██████████| 8674/8674 [00:30<00:00, 280.84it/s]
Search vectors: 100%|██████████| 15/15 [00:07<00:00,  2.09it/s]
Indexing vectors: 100%|██████████| 8674/8674 [00:27<00:00, 311.41it/s]
Search vectors: 100%|██████████| 15/15 [00:07<00:00,  2.07it/s]
Indexing vectors: 100%|██████████| 8674/8674 [00:34<00:00, 250.86it/s]
Search vectors: 100%|██████████| 15/15 [00:07<00:00,  2.03it/s]
```

以下のコードを実行してメトリクスを可視化できます。

```python
df = pd.DataFrame(metrics)
df
```

以下の画像はメトリクス可視化の例です。

![メトリクスの例](/images/opensearch-hnsw-hyperparameters-guide/example_metrics.png)

## 制限事項と今後の課題

本記事では、recall とスループットという 2 つの主要な目的に対する HNSW の最適化に焦点を当てました。ただし、HNSW グラフのサイズをさらに調整するには、`ef_construction` の異なる値を探索することで追加の知見が得られる可能性があります。

現在の手法はすべてのデータセットに対して同じ設定セットを生成しますが、このアプローチには改善の余地があります。各データセットの特性を考慮することで、より的を絞った推奨を作成できる可能性があります。また、現在の設定セットは 15 のデータセットに基づいています。訓練プロセスにより広範なデータセットを組み込むことで、学習された設定の汎化性能が向上するでしょう。

今後は、インデックスサイズをさらに削減しスループットを向上させるために、HNSW と併せて量子化手法の推奨を含めるよう範囲を拡大することが考えられます。

## 参考文献

1. Malkov, Yu A., and Dmitry A. Yashunin. "Efficient and robust approximate nearest neighbor search using hierarchical navigable small world graphs." IEEE transactions on pattern analysis and machine intelligence 42.4 (2018): 824-836.
2. Xu, Lin, Holger Hoos, and Kevin Leyton-Brown. "Hydra: Automatically configuring algorithms for portfolio-based selection." Proceedings of the AAAI Conference on Artificial Intelligence. Vol. 24. No. 1. 2010.
3. Winkelmolen, Fela, et al. "Practical and sample efficient zero-shot hpo." arXiv preprint arXiv:2007.13382 (2020).
4. Salinas, David, and Nick Erickson. "TabRepo: A Large Scale Repository of Tabular Model Evaluations and its AutoML Applications." arXiv preprint arXiv:2311.02971 (2023).
5. Feurer, Matthias, and Frank Hutter. Hyperparameter optimization. Springer International Publishing, 2019.
6. Shahriari, Bobak, et al. "Taking the human out of the loop: A review of Bayesian optimization." Proceedings of the IEEE 104.1 (2015): 148-175.
