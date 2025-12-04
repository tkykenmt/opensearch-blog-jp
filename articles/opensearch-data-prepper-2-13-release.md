---
title: "[翻訳] Data Prepper 2.13 でネイティブ OpenSearch データストリームと Prometheus 統合が追加"
emoji: "🔄"
type: "tech"
topics: ["opensearch", "dataprepper", "prometheus", "observability"]
published: true
publication_name: "opensearch"
published_at: 2025-12-03
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/data-prepper-2-13-brings-native-opensearch-data-streams-and-prometheus-integration/

OpenSearch Data Prepper のメンテナーは、Data Prepper 2.13 のリリースを発表しました。このリリースには、Data Prepper をより使いやすくする多くの改善と新機能が含まれています。

## Prometheus シンク

Data Prepper が Prometheus をシンクとしてサポートするようになりました。現時点では、外部 Prometheus シンクとして Amazon Managed Service for Prometheus のみがサポートされています。これにより、Data Prepper パイプライン内で処理されたメトリクスデータを Prometheus エコシステムにエクスポートでき、Data Prepper がさまざまなメトリクスソース (OpenTelemetry、Logstash、Amazon Simple Storage Service [Amazon S3] など) と Prometheus 互換の監視システム間のブリッジとして機能できるようになります。

Prometheus シンクの中核的な側面は、異なるメトリクスタイプの処理です。この実装により、Data Prepper の内部メトリクス表現が Prometheus 時系列ファミリーに正しくマッピングされます。

* **カウンター**: 累積集約時間性と単調増加値を持つ `Sum` メトリクスの場合、シンクはメトリクス名を使用して単一の時系列を生成します。値は累積カウントを表します。
* **ゲージ**: カウンターと同様に、`Gauge` メトリクスは現在の値を持つ単一の時系列にマッピングされます。カウンターにマッピングされない `Sum` メトリクスも同様です。
* **サマリー**: サマリーメトリクスは `quantile` ラベルを持つ時系列に変換され、対応する `_sum` と `_count` 系列も生成されます。
* **ヒストグラム**: ヒストグラムのサポートはより複雑です。シンクは分布を完全に表現するために、各ヒストグラムメトリクスに対して `buckets`、`sum`、`count`、`min`、`max` を含む多くの異なるタイプの時系列を生成します。
* **指数ヒストグラム**: 指数ヒストグラムのサポートも複雑です。シンクは分布を完全に表現するために、各ヒストグラムメトリクスに対して `scale`、`zero threshold`、`zero count`、`sum`、`count`、`min`、`max` を含む多くの異なるタイプの時系列を生成します。

メトリクスのマッピングに加えて、シンクは属性ラベリングと名前のサニタイズを処理し、すべてのメトリクス、リソース、スコープ属性のラベルを作成します。

Amazon Managed Service for Prometheus 向けに以下のように簡単に設定できます。

```yaml
sink:
  - prometheus:
      url: <amp workspace remote-write api url>
      aws:
         region: <region>
         sts_role_arn: <role-arn>
```

## OpenSearch データストリームサポート

Data Prepper が `opensearch` シンクで OpenSearch データストリームをネイティブにサポートするようになりました。この変更により、Data Prepper はインデックスを検索してデータストリームかどうかを判断します。データストリームの場合、シンクへのバルク書き込みがデータストリームと直接連携するように設定されます。

この機能以前は、Data Prepper パイプラインの作成者はデータストリームインデックスに書き込むためにシンク設定を手動で調整する必要がありました。これにより、ユーザーはシンクを正しく設定する最小限の設定を作成できるようになりました。さらに、パイプラインがこの値を設定していない場合、Data Prepper は `@timestamp` フィールドを Data Prepper が受信した時刻に自動的に設定します。

例えば、設定は以下のようにシンプルにできます。

```yaml
sink:
  - opensearch:
      hosts: [ "https://localhost:9200" ]
      index: my-log-index
```

## クロスリージョン S3 ソース

`s3` ソースは S3 バケットからデータを取り込むための人気のある Data Prepper 機能です。このソースは Amazon Simple Queue Service (Amazon SQS) 通知を使用して S3 バケットから読み取るか、複数の S3 バケットをスキャンできます。ユーザーが単一のパイプラインで読み取りたい複数の AWS リージョンに S3 バケットを持っていることは一般的です。例えば、一部のチームは複数のリージョンから VPC フローログを取得し、単一の OpenSearch クラスターに統合したい場合があります。Data Prepper ユーザーは異なるリージョンの複数のバケットから読み取れるようになりました。この機能のためにカスタム設定を作成する必要はありません。Data Prepper がこれを自動的に処理します。

## その他の優れた変更

* メンテナーは式とコアプロセッサのパフォーマンス改善に投資しました。ベンチマークによると、式を使用する際のスループットが 20% 以上向上しています。
* `dynamodb` ソースがシャード内で完全にチェックポイントを作成するようになりました。この変更により、障害発生時の Amazon DynamoDB テーブルからの重複処理が削減されます。この変更以前は、DynamoDB シャードからの読み取りを再開する際、Data Prepper はシャードの最初から開始していました。この変更により、Data Prepper ノードはシャード内で最後に正常に処理されたイベントから開始します。
* `delete_entries` と `select_entries` プロセッサが、フィールドを削除または選択するかどうかを決定するための正規表現パターンをサポートするようになり、パイプライン作成者がイベントをクリーンアップするのに役立ちます。
* `rename_keys` プロセッサがキーを正規化できるようになり、パイプライン作成者がデータを OpenSearch に取り込むためのシンプルなパイプラインを作成できるようになりました。

## はじめに

* Data Prepper をダウンロードするには、[Download & Get Started](https://opensearch.org/downloads.html) ページにアクセスしてください。
* Data Prepper の使用を開始する手順については、[Getting started with OpenSearch Data Prepper](https://opensearch.org/docs/latest/data-prepper/getting-started/) を参照してください。
* Data Prepper 2.14 およびその他のリリースの進行中の作業について詳しくは、[Data Prepper Project Roadmap](https://github.com/orgs/opensearch-project/projects/221) を参照してください。

## コントリビューターへの感謝

このリリースに貢献してくださった以下のコミュニティメンバーに感謝します！

* [akshay0709](https://github.com/akshay0709) — Akshay Pawar
* [alparish](https://github.com/alparish)
* [chenqi0805](https://github.com/chenqi0805) — Qi Chen
* [danhli](https://github.com/danhli) — Daniel Li
* [Davidding4718](https://github.com/Davidding4718) — Siqi Ding
* [derek-ho](https://github.com/derek-ho) — Derek Ho
* [dinujoh](https://github.com/dinujoh) — Dinu John
* [divbok](https://github.com/divbok) — Divyansh Bokadia
* [dlvenable](https://github.com/dlvenable) — David Venable
* [FedericoBrignola](https://github.com/FedericoBrignola)
* [franky-m](https://github.com/franky-m)
* [gaiksaya](https://github.com/gaiksaya) — Sayali Gaikawad
* [Galactus22625](https://github.com/Galactus22625) — Maxwell Brown
* [graytaylor0](https://github.com/graytaylor0) — Taylor Gray
* [huypham612](https://github.com/huypham612) — huyPham
* [ivan-tse](https://github.com/ivan-tse) — Ivan Tse
* [janhoy](https://github.com/janhoy) — Jan Høydahl
* [jayeshjeh](https://github.com/jayeshjeh) — Jayesh Parmar
* [jeffreyAaron](https://github.com/jeffreyAaron) — Jeffrey Aaron Jeyasingh
* [jmsusanto](https://github.com/jmsusanto) — Jeremy Michael
* [joelmarty](https://github.com/joelmarty) — Joël Marty
* [juergen-walter](https://github.com/juergen-walter) — Jürgen Walter
* [KarstenSchnitter](https://github.com/KarstenSchnitter) — Karsten Schnitter
* [kkondaka](https://github.com/kkondaka) — Krishna Kondaka
* [LeeroyHannigan](https://github.com/LeeroyHannigan) — Lee
* [linghengqian](https://github.com/linghengqian) — Ling Hengqian
* [mishavay-aws](https://github.com/mishavay-aws)
* [MohammedAghil](https://github.com/MohammedAghil) — Mohammed Aghil Puthiyottil
* [niketan16](https://github.com/niketan16) — Niketan Chandarana
* [nsgupta1](https://github.com/nsgupta1) — Neha Gupta
* [oeyh](https://github.com/oeyh) — Hai Yan
* [ps48](https://github.com/ps48) — Shenoy Pratik
* [quanghungb](https://github.com/quanghungb) — qhung
* [RashmiRam](https://github.com/RashmiRam) — Rashmi
* [Rishikesh1159](https://github.com/Rishikesh1159) — Rishikesh
* [saketh-pallempati](https://github.com/saketh-pallempati) — Saketh Pallempati
* [san81](https://github.com/san81) — Santhosh Gandhe
* [savit-aluri](https://github.com/savit-aluri) — Savit Aluri
* [sb2k16](https://github.com/sb2k16) — Souvik Bose
* [seschis](https://github.com/seschis) — Shane Schisler
* [shenkw1](https://github.com/shenkw1) — Katherine Shen
* [srikanthjg](https://github.com/srikanthjg) — Srikanth Govindarajan
* [timo-mue](https://github.com/timo-mue)
* [TomasLongo](https://github.com/TomasLongo) — Tomas
* [Zhangxunmt](https://github.com/Zhangxunmt) — Xun Zhang
