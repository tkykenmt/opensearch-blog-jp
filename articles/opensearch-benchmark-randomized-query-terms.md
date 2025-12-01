---
title: "[翻訳] OpenSearch Benchmark でランダム化されたクエリ用語を使用する"
emoji: "🎲"
type: "tech"
topics: ["opensearch", "benchmark", "performance", "python"]
published: true
publication_name: "opensearch"
published_at: 2023-09-14
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/use-opensearch-benchmark-with-randomized-query-terms/

パフォーマンステストは科学と芸術の両面を持っています。測定の面では、テストケースの実行、メトリクスの収集と可視化、結果の評価に科学を用います。テスト作成の面では、OpenSearch の主要なユースケースとデータをカバーするために、直感と理解を活用します。

[OpenSearch Benchmark](https://opensearch.org/docs/latest/benchmark/index/) は、コミュニティ主導のベンチマークフレームワークで、OpenSearch に対するワークロードのベンチマークを簡単に行えます。OpenSearch Benchmark を使用して、OpenSearch のインデックスからデータを取得し、要件に合わせてカスタマイズしたカスタムワークロードを作成できます。

OpenSearch Benchmark の制限の 1 つは、検索操作を実行する際にクエリ自体がハードコードされていることです。検索用語のセットに対してクエリワークロードをランダム化したい場合、すぐに使える方法はありません。本記事では、[BoardgameGeek.com](https://boardgamegeek.com/) (BGG) のデータを使用してカスタム OpenSearch Benchmark ワークロードを作成します。その後、1 行に 1 クエリを記述したファイルを 2 つ作成し、それらのファイルを使用して OpenSearch へのクエリ用語をランダム化します。

## 前提条件

この例に従うには、以下が必要です。

- **Python 3.8 以上**: [Python 3.8 以上](https://www.python.org/downloads/)のインストール手順に従ってください
- **Java Development Kit (JDK) 17**: [JDK 17 のインストール](https://www.oracle.com/java/technologies/downloads/)手順に従ってください
- **OpenSearch Benchmark**: [OpenSearch Benchmark のインストール](https://opensearch.org/docs/latest/benchmark/installing-benchmark/)手順に従ってください。私はカスタムワークロードと設定を保持するスクラッチディレクトリ内の仮想環境にインストールしました
- **OpenSearch クラスター**: このウォークスルーでは、[Docker Desktop](https://www.docker.com/products/docker-desktop/) を使用してローカルマシンで OpenSearch を実行しました。[OpenSearch クイックスタート](https://opensearch.org/docs/latest/quickstart/)に従って OpenSearch クラスターを作成してください
- **OpenSearch 内のデータ**: [BoardgameGeek は API を提供](https://boardgamegeek.com/wiki/page/BGG_XML_API2)しており、XML 形式でデータを取得できます。この例では、[Open Distro for Elasticsearch プロジェクトのサンプルコード](https://github.com/opendistro-for-elasticsearch/sample-code/tree/main/BGG)を使用・拡張して、BoardGameGeek からゲームをダウンロードし、OpenSearch の `games` インデックスにロードしました。データには名前、説明、評価、ユーザーコメントなどが含まれています。独自のデータセットがある場合は、代わりにそれを OpenSearch にロードできます

## カスタムワークロードの生成

games インデックスにデータをロードしたら、作業ディレクトリを作成して `cd` で移動します。私は `osb` というディレクトリを作成しました。以下を実行してカスタムワークロードを作成します。

```bash
opensearch-benchmark create-workload --workload=bgg --target-hosts="<クラスターエンドポイント>" --client-options="basic_auth_user:'<ユーザー名>',basic_auth_password:'<パスワード>',verify_certs:false" --indices=games --output-path=.
```

**注意:** この例では基本認証を使用しています。上記のコマンドラインで `<ユーザー名>` と `<パスワード>` をセキュリティプラグインの設定時に使用した値に置き換えてください。`<クラスターエンドポイント>` をクラスターのエンドポイントとポートに置き換えてください。

OpenSearch Benchmark は `bgg` ディレクトリを作成し、`games.json` や `workload.py` などのファイルを生成します。`games.json` を確認してください。このファイルには、OpenSearch Benchmark がテストクラスターで games ディレクトリを作成する際に使用するインデックス設定が含まれています。settings セクションでは、Benchmark が `number_of_shards` と `number_of_replicas` のテンプレート化された設定を作成していることがわかります。

```json
    "settings": {
        "index": {
            "number_of_replicas": "{{number_of_replicas | default(1)}}",
            "number_of_shards": "{{number_of_shards | default(1)}}",
            "replication": {
                "type": "DOCUMENT"
            }
        }
    }
```

コマンドラインから Benchmark を実行する際に、これらの値を設定してさまざまなテストケースを試すことができます。

`workload.json` を確認してください。このファイルには、`indices` と `corpora` セクションにワークロードの説明が含まれています。`schedule` セクションは、テストが実行する操作とその順序をデフォルトで定義しています。デフォルトのテストフレームワークは、`games` という名前の既存のインデックスを削除し、新しいインデックスを作成し、クラスターが安定するのを待ってから、ダウンロードしたデータを一括ロードし、`match_all` クエリを実行します。

以下のコマンドでこの設定をテストできます。

```bash
opensearch-benchmark execute-test --pipeline benchmark-only --workload-path=<bgg フォルダへのパス> --target-host=<クラスターエンドポイント> --client-options="use_ssl:true,basic_auth_user:'<ユーザー名>',basic_auth_password:'<パスワード>',verify_certs:false" --workload-params="bulk_size:300"
```

`<ユーザー名>`、`<パスワード>`、`<クラスターエンドポイント>`、`<bgg フォルダへのパス>` を正しい値に置き換えてください。上記のコマンドラインでは、`--workload-params` で実際の `_bulk` サイズを 300 に設定しています。Benchmark は `workload.json` の `bulk` 操作でこの値を解決して挿入します。

```json
    {
      "operation": {
        "operation-type": "bulk",
        "bulk-size": {{bulk_size | default(100)}},
        "ingest-percentage": {{ingest_percentage | default(100)}}
      },
      "clients": {{bulk_indexing_clients | default(8)}}
    }
```

`--workload-params` を使用して、テストケース間で値を変更できます。

## クエリ用語の準備

`workload.json` を見ると、テストが単一の `match-all` クエリを実行していることがわかります。もちろん、これは現実的なテストではありません。クエリをより堅牢にして、1 つまたは複数の match クエリを実行することもできますが、それでは十分なカバレッジにならず、現実的なエンドユーザークエリを表現できません。より良いクエリセットを構築するために、BGG API からゲームをダウンロードし、`primary_name` と `description` フィールドを抽出しました。このデータをトークン化してクリーニングし、1〜5 語のクエリ文字列を生成して、10 万件を `bgg_words.txt` というファイルに書き込みました。次のセクションで、この用語セットを組み込む方法を説明します。以下はサンプルです。

```
Introduces Professional 
declarant petals Machen 
destruyelos 80C tapped enemy 
bombing sculpts Scorn 8022 
Mystical interpose clearance Canope 
fulfilled 
Colony mortality 
5ive 
```

クエリセットにもう少し現実味を持たせるために、単一語のクエリを提供する 1 万語の英単語リスト (`english_words.txt`) もダウンロードしました。インターネットで同様のリストを見つけるか、独自に生成するか、このステップをスキップすることもできます。

BGG の用語と英単語のリスクの 1 つは、どのドキュメントにもマッチしないクエリが多すぎる可能性があることです。これらの「ゼロ結果」クエリは、マッチするクエリよりも高速で負荷が少なくなります。ゼロ結果クエリの比率が高すぎると、テスト結果が正確になりません。これを解決するために、テストの一環として、すべてのクエリのヒット数を追跡し、ワークロードを代表するマッチとゼロ結果クエリになるように用語セットを調整できます。

## カスタムパラメータソースの構築

クエリ用語をワークロードに組み込むには、カスタムパラメータソースを使用します。`workload.json` の検索操作を以下のように変更します。

```json
    {
      "operation": {
        "operation-type": "search",
        "param-source": "search-term-source",
        "index": "games"
      },
      "clients": {{search_clients | default(8)}},
      "iterations": 1000
    }
```

Benchmark のレジストリから `search-term-source` という項目を呼び出す `param-source` パラメータを追加します。`bgg` ディレクトリに `workload.py` を作成します。Benchmark はこの名前のファイルを探し、起動時に実行します。また、この操作の `iterations` 数を 1,000 に増やします。

`workload.json` と同じディレクトリに、以下の内容で `workload.py` というファイルを作成します。`random_search_term` 関数は、英単語コーパスまたは BGG コーパスからランダムな用語を選択し、term クエリボディに挿入します。`register` 関数は、`random_search_term` 関数を `search-term-source` パラメータソースとして登録します。

```python
import random
import logging

# bgg_words と english_words ファイルからソース用語をロードします。
# シンプルにするため、ファイルは 1 行に 1 つの用語セットとして構成されています。
english_words = None
with open('english_words.txt', 'r') as f:
    lines = f.readlines()
    english_words = list(map(lambda x: x.lstrip().rstrip(), lines))


bgg_words = None
with open('bgg_words.txt', 'r') as f:
    lines = f.readlines()
    bgg_words = list(map(lambda x: x.lstrip().rstrip(), lines))


# この関数は完全なクエリボディを生成して返します。
# 以下の関数シグネチャと戻り値の構造に一致させてください。
def random_search_term(track, params, **kwargs):
    index_name = params.get("index")

    # 単一の英単語か、BGG データからのクエリ用語セットの
    # いずれかを選択します。
    collection = random.choice([english_words, bgg_words])
    query = random.choice(collection)

    # logging.log(logging.INFO, f'Query: {query}')

    # description フィールドに対する基本的な term クエリを返します。
    # ほとんどの場合、パフォーマンステストではリクエストキャッシュを無効にします。
    # これはワークロードで指定されたキャッシュパラメータを引き継ぎます。
    return {
        "body": {
            "query": {
                "term": {
                    "description": query
                }
            }
        },
        "index": index_name,
        "cache": params.get("cache", False)
    }


# random_search_term 関数を workload.json で指定された
# search-term-source パラメータソースにマッピングします
def register(registry):
    registry.register_param_source("search-term-source", random_search_term)
```

上記のコマンドラインで OpenSearch Benchmark を実行します。Benchmark が用語を正しく取り込んでいることを検証したい場合は、クエリ用語をログに記録する行のコメントを解除してください。OpenSearch クラスターでスローログを有効にすることもできます。**注意**: 各クエリをログに記録したり、スローログを有効にしたりすると、パフォーマンス結果に大きな影響を与えるため、実際の測定時には必ずオフにしてください。

## まとめ

本記事では、`opensearch-benchmark create-workload` を使用して実行中のクラスターからデータを読み取り、そのデータのテストフレームワークを構築する方法を学びました。テストフレームワークを配置した後、コーパスと英語からの用語を使用して現実的なクエリセットを提供するように検索操作を一般化しました。この方法を一般化して、クエリの要素を取り込んでランダム化し、OpenSearch Benchmark を使用して正確な結果を得ることができます。
