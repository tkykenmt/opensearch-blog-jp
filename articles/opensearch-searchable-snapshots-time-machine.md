---
title: "[翻訳] データのタイムマシン: OpenSearch の Searchable Snapshots"
emoji: "⏰"
type: "tech"
topics: ["opensearch", "snapshot", "s3", "storage", "aws"]
published: true
publication_name: opensearch
published_at: 2024-04-15
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/a-time-machine-for-your-data-opensearch-searchable-snapshots/

OpenSearch などのオープンソースデータベースをスケールアップしている多くの組織は、膨大なデータを効率的に保存・検索する方法に頭を悩ませています。OpenSearch のマネージドサービスプロバイダーである Instaclustr by NetApp にとって、これは非常に身近な課題です。私たちも社内で OpenSearch を活用し、アプリケーションが日々生成する大量のログデータを整理・保存・検索しています。しかし、コストを抑えつつ、管理に何時間も費やすことなく、すべてのデータを保存するにはどうすればよいのでしょうか。すべてのデータをディスクに保存することもできますが、コストはすぐに膨らみます。あるいは、Amazon Simple Storage Service (Amazon S3) や Azure Blob Storage などの安価なリモートストレージに移すこともできますが、再度アクセスするのが困難になります。過去のデータをコストや手間をかけずに現在に呼び戻せる、タイムマシンのようなものがあればいいのに。

私たちも最近このような課題に直面していました。最大 12 か月分の監査ログを Amazon S3 バケットに保存していましたが、監査が発生した場合、セキュリティチームは S3 から該当するスナップショットを探し出し、OpenSearch クラスターを起動し、スナップショット全体をそのクラスターにダウンロードして、ようやく検索できる状態になります。このプロセスには、すべてが順調に進んでも数時間から数日かかることがありました。

しかし、Searchable Snapshots がこのデータ課題の解決に役立ちました。OpenSearch を使用している組織にとっても同様に役立つと考える理由を説明します。

## Searchable Snapshots で時間を節約

リモートストレージにある OpenSearch スナップショットの管理は時間がかかります。そのデータを検索する必要がある場合、クラスターにリストアしなければなりません。これは非常に手作業が多いプロセスで、インデックスのサイズによっては数時間から数日かかることもあります。

しかし、Searchable Snapshots を使えば、特定の時点に直接戻れるタイムマシンのようなものです。Searchable Snapshots を使用すると、通常の OpenSearch スナップショットと同様に、リモートに保存されたデータをクラスターから直接検索できます。「リモートスナップショット」と呼ばれる特殊なインデックスを取得することで、リモートに保存されたスナップショットデータを素早く簡単に取得できます。

実際には、OpenSearch REST API を使用してスナップショットを「リモートスナップショット」インデックスとしてリストアできます。

```json
POST /_snapshot/custom-repository/test-snapshot-2024-01-01/_restore
{
      "indices": "test_index",
      "storage_type": "remote_snapshot",
      "rename_pattern": "(.+)",
      "rename_replacement": "restored_$1"
}
```

その後、通常のインデックスと同様に Searchable Snapshot インデックスに対して検索を実行できます。

```json
GET /restored_test_index/_search
{
      <検索クエリをここに入力>
}
```

さらに、Instaclustr の OpenSearch クラスターではキャッシュがデフォルトで設定されているため、同じデータセットに対する後続の検索はさらに高速に解決されます。これにより、チームがログを検索するのにかかる時間が数分に短縮されました。

## Searchable Snapshots で手作業を削減

リモートストレージに保存された過去のスナップショットを検索するには手間がかかります。スナップショットのサイズを把握し、クラスターにリストアするために必要なリソースを確保する必要があります。別の OpenSearch クラスターを起動するか、既存のクラスターのディスクサイズを増やす必要があるかもしれません。最後に、検索クエリを実行する前にスナップショット全体をクラスターにリストアする必要があります。これらすべてに、専任の担当者がかなりの労力とリソースを費やすことになります。

しかし、Searchable Snapshots を使用すると、プロセスは 2 つの簡単なステップに削減されます。

1. リモートスナップショットのリストアを実行して、検索対象のリモートスナップショットを OpenSearch に指定する
2. 他のインデックスを検索するときと同様にクエリを送信する

Searchable Snapshots がリモートスナップショットと呼ばれる特殊なスナップショットを使用することを説明しましたが、リモートスナップショットのもう一つの優れた点は、リストアに追加のクラスタースペースが不要なことです。つまり、リモートスナップショットを検索するために追加のインフラストラクチャをプロビジョニングする必要がありません。これにより必要な労力が大幅に削減され、チームはより重要なタスクに集中できるようになります。

## Searchable Snapshots でコストを削減

ログデータは一般的に、ライフサイクルの初期段階でクエリされる可能性が高いことは広く知られています。Searchable Snapshots が登場する前は、タイムリーに取得できるようにするために、数か月から数年分の新しいデータをクラスター内に保持する必要がありました。周知のとおり、「ホット」ディスクへのデータ保存は「コールド」リモートストレージへの保存よりもはるかに高コストです。

Searchable Snapshots を使用すると、クラスターからリモートストレージに移動した後もデータにアクセスできるため、ライフサイクルの早い段階でデータをリモートストレージに移動できます。これにより、古いデータを低コストのリモートストレージに移動することで、クラスターで使用するディスク容量を削減できます。この方法を使用すると、データは引き続き検索可能であり、保存コストも大幅に削減されます。

## Searchable Snapshots の実践

Searchable Snapshots を使用して得られた最大のメリットは、セキュリティチームがログを検索するのにかかる時間が大幅に短縮されたことです。

私たちはデータを 90 日間ディスクに保持し、それより古いデータはすべて S3 ストレージに移動することにしました。以前は、チームが古いスナップショットから完全なリストアを実行するのに数時間かかっていました。Searchable Snapshots を使用すると、そのデータを即座にクエリできます。インデックスポリシーは以下のように設定しました。

```json
{
  "policy": {
    "description": "Rollover indexes every day, delete indexes after 90 days.",
    "error_notification": null,
    "default_state": "hot",
    "states": [
      {
        "name": "hot",
        "actions": [],
        "transitions": [
          {
            "state_name": "rolled-over",
            "conditions": {
              "min_index_age": "1d"
            }
          }
        ]
      },
      {
        "name": "rolled-over",
        "actions": [
          {
            "retry": {
              "count": 3,
              "backoff": "exponential",
              "delay": "1m"
            },
            "rollover": {}
          }
        ],
        "transitions": [
          {
            "state_name": "deleting",
            "conditions": {
              "min_index_age": "91d"
            }
          }
        ]
      },
      {
        "name": "deleting",
        "actions": [
          {
            "retry": {
              "count": 3,
              "backoff": "exponential",
              "delay": "1m"
            },
            "delete": {}
          }
        ],
        "transitions": []
      }
    ],
    "ism_template": [
      {
        "index_patterns": [
          "audit-logging-*"
        ],
        "priority": 150
      }
    ]
  }
}
```

古いログの検索にかかる時間が大幅に短縮されたことで、セキュリティチームはより価値の高い活動に時間を費やせるようになりました。これにより、ビジネス全体でリソースを節約できています。

## 過去を現在に呼び戻す

OpenSearch の Searchable Snapshots を使用することで得られる多くのメリットを紹介しました。リモートに保存されたスナップショットを即座にアクセス可能にすることで時間を節約できます。スナップショット全体をクラスターにリストアする必要がなくなることで手間を省けます。そして、クラスター内のディスクに保存するデータ量を削減することでコストを削減できます。

しかし、Searchable Snapshots の最大のメリットは、過去のデータを現在に呼び戻すポータルを提供し、突然再びアクセス可能にすることです。タイムマシンのように、過去からデータを即座に取得し、より有用で価値のあるものにします。必要なデータを見つけるために過去に簡単かつ即座に移動できる機能をお探しなら、Searchable Snapshots が理想的なソリューションです。

Searchable Snapshots についてさらに詳しく知りたい場合は、[リリースブログ記事](https://www.instaclustr.com/blog/searchable-snapshots-now-available-for-opensearch-on-the-instaclustr-managed-platform/)を参照するか、[support@instaclustr.com](mailto:support@instaclustr.com) までお問い合わせください。
