---
title: "[翻訳] OpenSearch Dashboards の新機能: 長時間実行オペレーションの通知とコンポーネントテンプレート"
emoji: "🔔"
type: "tech"
topics: ["opensearch", "OpenSearchDashboards", "インデックス管理", "通知"]
published: true
publication_name: "opensearch"
published_at: 2023-07-20
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/long-running-operation-and-component-template/

OpenSearch Dashboards に、インデックス管理を簡素化する 2 つの UI 要素が追加されました。[長時間実行オペレーションの通知](#長時間実行オペレーションの通知)と[コンポーネントテンプレート](#コンポーネントテンプレート)です。長時間実行オペレーションの通知機能では、Notification プラグインがサポートする任意の通知チャネルを通じて、特定のタスクまたはタスクタイプの通知を受け取ることができます。コンポーネントテンプレートでは、複数のインデックスにマッチする単一のインデックスパターンを作成できます。コンポーネントテンプレートとインデックステンプレートを組み合わせることで、大量のデータを管理するための強力なツールとなります。

## 長時間実行オペレーションの通知

従来、長時間実行オペレーションを実行する際は、完了するまで待機し、ステータスを更新するために常にリフレッシュする必要がありました。タスクが完了するまでに数時間かかることもあるため、これは困難な作業でした。この問題を軽減するために、OpenSearch は `reindex` オペレーション用の非同期タスクを導入し、時間のかかるジョブをバックグラウンドで実行できるようになりました。しかし、管理者はタスクが最終状態に進んだことを確認するために、定期的にタスクステータスをチェックする必要がありました。さらに、`shrink` などのオペレーションには、非同期で実行する基本的な機能がありませんでした。

### 長時間実行オペレーションの非同期タスクへの変換

大規模なインデックスの場合、`shrink`、`split`、`clone`、`open`、`force_merge` オペレーションは完了までに約 30 分かかることが知られています。これらを非同期で実行したい場合は、`wait_for_completion` クエリパラメータを `false` に設定することで、これらのオペレーションをタスクに変換できます。

```json
POST /my-old-index/_shrink/my-new-index?wait_for_completion=false
{
  "settings": {
    "index.number_of_replicas": 4,
    "index.number_of_shards": 3
  },
  "aliases":{
    "new-index-alias": {}
  }
}
```

上記のクエリは、オペレーションのステータスを監視するために使用できるタスク ID を返します。

### 非同期タスクの完了または失敗時に通知を受け取る

長時間実行オペレーションの通知をサポートするために、タスクと通知チャネルを統合しました。タスクが完了または失敗したときに通知を受け取るには、以下の画像に示すように通知設定を構成できます。

![通知設定](/images/opensearch-long-running-ops-component-template/notify-tasks.png)

通知の設定に関する詳細な手順については、[Notification settings](https://opensearch.org/docs/latest/dashboards/im-dashboards/notifications/) を参照してください。

### インデックス作成オペレーションの追加ユーザーへの通知

本番インデックスの再インデックス化など、特定のオペレーションのステータスを追加のユーザーに通知したい場合があります。インデックス管理では、以下の画像に示すように、個々のオペレーションに対してデフォルトの通知に追加の通知を付加する機能を提供しています。

![アドホック通知設定](/images/opensearch-long-running-ops-component-template/adhoc-notification.png)

詳細については、[Configuring notification settings for an individual operation](https://opensearch.org/docs/latest/dashboards/im-dashboards/notifications/#configuring-notification-settings-for-an-individual-operation) を参照してください。

### API を通じた通知の設定

`lron` API エンドポイントを使用して、タスクの通知設定を構成できます。例えば、以下のクエリは reindex タスクが失敗したときの通知を設定します。

```json
POST /_plugins/_im/lron
{
  "lron_config": {
      "task_id":"dQlcQ0hQS2mwF-AQ7icCMw:12354",
      "action_name":"indices:data/write/reindex",
      "lron_condition": {
        "success": false,
        "failure": true
      },
      "channels":[
          {"id":"channel1"},
          {"id":"channel2"}
      ]
  }
}
```

`lron` API では、通知設定の作成、取得、更新、削除が可能です。これらのオペレーションの詳細については、[Notification settings](https://opensearch.org/docs/latest/im-plugin/notifications-settings/) を参照してください。

### 通知権限による細かいアクセス制御の設定

特定のユーザーに通知設定のアクセスを制限するために、通知は Security プラグインと統合されており、以下の細かい権限を提供しています。

* `cluster:admin/opensearch/controlcenter/lron/get`: 長時間実行オペレーションの通知設定を `表示` する権限
* `cluster:admin/opensearch/controlcenter/lron/write`: 長時間実行オペレーションの通知設定を `追加または更新` する権限
* `cluster:admin/opensearch/controlcenter/lron/delete`: 長時間実行オペレーションの通知設定を `削除` する権限

ユーザーが通知設定を表示する権限を持っていない場合、以下の画像に示すように権限をリクエストするよう促されます。

![セキュリティ有効時](/images/opensearch-long-running-ops-component-template/security-enabled.png)

## コンポーネントテンプレート

コンポーネントテンプレートを使用すると、複数のインデックスにマッチする単一のインデックスパターンを作成できます。複数のコンポーネントテンプレートを組み合わせてインデックステンプレートを作成できます。

### コンポーネントテンプレートの作成

API を通じてインデックステンプレートを作成する場合、関連するすべてのコンポーネントテンプレートとその設定をマージした後のインデックステンプレートがどのようになるかを判断するのが難しい場合があります。UI を通じてインデックステンプレートを作成または更新する際に、以下の画像に示すように OpenSearch Dashboards でテンプレートをプレビューできるようになりました。

![コンポーネントテンプレート作成](/images/opensearch-long-running-ops-component-template/component-template.png)

コンポーネントテンプレートの作成に関する詳細な手順については、[Component templates](https://opensearch.org/docs/latest/dashboards/im-dashboards/component-templates/) を参照してください。

### 集約されたインデックステンプレートビューによるインデックステンプレートの管理

API を使用する場合、単一のコンポーネントテンプレートを使用しているインデックステンプレートの数を判断するのが難しい場合があります。OpenSearch Dashboards では、特定のコンポーネントテンプレートに関連付けられたすべてのインデックステンプレートの集約ビューを提供し、以下の画像に示すように簡単に管理できるようになりました。

![集約ビュー](/images/opensearch-long-running-ops-component-template/aggregated-view.png)

## 今後の予定

タイムリーな通知が必要な他の非同期タスクシナリオに通知フレームワークを使用する新しい方法を検討しています。フィードバックや提案がある場合は、[OpenSearch forum](https://forum.opensearch.org/) でディスカッションに参加してください。
