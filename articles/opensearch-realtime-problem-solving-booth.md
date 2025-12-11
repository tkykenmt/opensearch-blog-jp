---
title: "[翻訳] オープンソースの魔法: OpenSearch ブースでのリアルタイム問題解決"
emoji: "✨"
type: "tech"
topics: ["opensearch", "fluentbit", "observability", "kubecon", "opensource"]
published: true
publication_name: "opensearch"
published_at: 2025-12-10
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/the-magic-of-open-source-real-time-problem-solving-at-the-opensearch-booth/

KubeCon + CloudNativeCon North America には特別なエネルギーがあります。数千人のクラウドネイティブ愛好家、最先端のテクノロジー、そしてイノベーションの熱気が満ちています。しかし、最も印象的な瞬間はメインステージで起こるとは限りません。時には、実際の問題が実際の解決策とリアルタイムで出会うブースで起こることもあります。

## 課題

Chronosphere の Eric Schabell が KubeCon の OpenSearch ブースに [OpenSearch Easy Install プロジェクト](https://gitlab.com/o11y-workshops/opensearch-install-demo)を紹介しに来たとき、オブザーバビリティ分野の多くの人が知っている問題を提起しました。彼は [Fluent Bit](https://fluentbit.io) と OpenSearch バックエンド間の頑固な統合問題に直面しており、クラウドネイティブのオブザーバビリティ機能をデモすることができませんでした。何も動作していませんでした。少なくともまだ。

## コミュニティの力

次に起こったことは、オープンソースの精神を示すものでした。OpenSearch チームは Eric と協力して、リアルタイムで問題をトラブルシューティングしました。Eric のラップトップをメインスクリーンに接続し、サポートチケットも待ち時間もなく、ライブデバッグセッションを開始しました。

**図 1: OpenSearch ブースで問題をデバッグする OpenSearch エンジニアたち。(左から右へ) Sumukh Hanumantha Swamy、Jiaxiang (Peter) Zhu、Adam Tackett、Ritvi Bhatt**

Eric はバックエンドと OpenSearch Dashboards コンポーネントの両方について OpenSearch コミュニティのクイックスタートドキュメントに従い、両方のコンポーネントを連携させることができました。問題はテレメトリデータを統合するために OpenSearch バックエンドにアクセスしようとしたときに始まりました。

しかし、Fluent Bit は OpenSearch クラスターにログデータを取り込むことができず、OpenSearch ダッシュボードは送信されているログテレメトリの新しいインデックスを登録していませんでした。

**図 2: 空のインデックスリスト — 何かがおかしい！**

## 突破口

調査が進むにつれ、チームは予想外の場所に潜む本当の問題を発見しました。Fluent Bit が `_type` フィールドを出力しており、OpenSearch の取り込みパイプラインで下流の問題を引き起こしていました。`fluent-bit.yaml` ファイルで以下の設定が使用されていました。

```yaml
service:
  flush: 1
  log_level: info
  http_server: on
  http_listen: 0.0.0.0
  http_port: 2020
  hot_reload: on

pipeline:
  inputs:
    # This entry generates a successful message.
    - name:  dummy
      tag:   event.success
      dummy: '{"message":"true 200 success"}'

    # This entry generates a failure message.
    - name:  dummy
      tag:   event.error
      dummy: '{"message":"false 500 error"}'

  outputs:
    - name: stdout
      match: '*'
      format: json_stream
      json_date_format: java_sql_timestamp

    - name: opensearch
      match: '*'
      host: localhost                # use for source
      #host: host.containers.internal  # use for containers
      port: 9200
      http_user: 'admin'
      http_passwd: 'Opensearch@demo1'
      index: fb-index
      type: fbType
      net.keepalive: off
```

これを実行すると、Fluent Bit のログに以下のエラーが報告されていました。

```
$ fluent-bit –config fluent-bit.yaml

…
{"date":"2025-11-24 13:13:56.770647","message":"true 200 success"}
{"date":"2025-11-24 13:13:56.771520","message":"false 500 error"}
[2025/11/24 14:13:57.790061000] [error] [output:opensearch:opensearch.1] HTTP status=400 URI=/_bulk, response:
{"error":{"root_cause":[{"type":"illegal_argument_exception","reason":"Action/metadata line [1] contains an unknown parameter [_type]"}],"type":"illegal_argument_exception","reason":"Action/metadata line [1] contains an unknown parameter [_type]"},"status":400}
…
[2025/11/24 14:13:57.790149000] [ warn] [engine] failed to flush chunk '34633-1763990036.771042000.flb', retry in 11 seconds: task_id=0, input=dummy.0 > output=opensearch.1 (out_id=1)
[2025/11/24 14:13:57.790197000] [ warn] [engine] failed to flush chunk '34633-1763990036.771542000.flb', retry in 10 seconds: task_id=1, input=dummy.1 > output=opensearch.1 (out_id=1)
…
```

ドキュメントを調べ、集合的な経験を活かして、エンジニアたちは解決策を見つけました。Fluent Bit 設定ファイルの OpenSearch 出力プラグインセクションに `suppress_type_name true` を追加することで問題が解決します。

```yaml
  outputs:
    - name: stdout
      match: '*'
      format: json_stream
      json_date_format: java_sql_timestamp

    - name: opensearch
      match: '*'
      host: localhost                # use for source
      #host: host.containers.internal  # use for containers
      port: 9200
      http_user: 'admin'
      http_passwd: 'Opensearch@demo1'
      index: fb-index
      type: fbType
      net.keepalive: off
      suppress_type_name: true
```

発見してしまえば明らかに思えるエレガントな修正でした。しかし、それを見つけるには、まさにそのブースに存在していた協力的な専門知識が必要でした。スクリプトが動き出し、データが Fluent Bit から OpenSearch に流れ始めました。

これで Fluent Bit のログには `stdout` 出力プラグインのテレメトリデータだけがコンソールに表示されるようになりました。

```
$ fluent-bit –config fluent-bit.yaml

…
{"date":"2025-11-24 13:22:11.125846","message":"true 200 success"}
{"date":"2025-11-24 13:22:11.126130","message":"false 500 error"}
{"date":"2025-11-24 13:22:12.140066","message":"true 200 success"}
{"date":"2025-11-24 13:22:12.140096","message":"false 500 error"}
{"date":"2025-11-24 13:22:13.137258","message":"true 200 success"}
{"date":"2025-11-24 13:22:13.137303","message":"false 500 error"}
…
```

ログテレメトリデータが OpenSearch バックエンドにシームレスに統合されるようになったので、OpenSearch Dashboards UI でそれを確認するだけです！

## 修正を超えて

OpenSearch チームはそこで止まりませんでした。統合が動作するようになると、Eric に OpenSearch インターフェースを案内し、出力ログの可視化を作成する手助けをしました。

**図 3: Fluent Bit 設定で定義されたとおり、受信ログテレメトリデータを保存するために「fb-index」が作成されていることに注目してください。**

このテレメトリデータを表示するには、まず `fb-index` で新しいインデックスパターンを作成する必要がありました。

**図 4: `fb-index` を検索します。**

次に、プライマリ時間フィールドを選択しました。

**図 5: `@timestamp` フィールドを選択します。**

最後に、OpenSearch Dashboards => Discover を開いて Fluent Bit のログテレメトリデータを表示しました。

**図 6: Discover での Fluent Bit ログテレメトリデータ。**

デバッグセッションとして始まったものが、即興のチュートリアルになりました。チームは OpenSearch Dashboards の新しいオブザーバビリティ機能を紹介しました。これには、強化されたログパターン検出、改善されたトレース分析、合理化されたメトリック可視化機能が含まれます。また、カスタムダッシュボードの構築方法、ログパターンに基づくアラートの設定方法、プラットフォームの完全なオブザーバビリティスタックの活用方法も実演しました。これらの洞察は Eric の将来のデモンストレーションを強化することになるでしょう。

## 学び

これがオープンソースの本質です。人々がリアルタイムで実際の問題を解決するために集まり、専門家がチーム外の誰かを喜んで助け、コラボレーションが全員に利益をもたらすという理解があります。最終的に、Eric のデモのブロックは解除されました。Chronosphere は Fluent Bit と OpenSearch の統合についてより深い洞察を得て、OpenSearch エンジニアは実践的な環境で問題解決スキルを適用し、ブースにいた全員が動作する解決策を見つけることに焦点を当てた効果的なコラボレーションを目撃しました。

Eric が[投稿](https://www.linkedin.com/posts/ericschabell_kubecon-fluentbit-cloudnative-ugcPost-7394724705922101248-dqHz/?utm_source=share&utm_medium=member_ios&rcm=ACoAACtb4vwBBPYI1Sx6HI9EhJjpJ0wAKn04nvE)で述べているように、彼は学んだことを新しいワークショップ、デモ、ブログコンテンツを通じて共有する予定です。この種のコラボレーションはコミュニティを強化し、同様の課題に直面している他の人々を助けます。

## より大きな視点

この経験は、私たちがオープンソースで働くことを愛する理由を思い出させてくれました。通常のツールすべてにアクセスできないブース環境での作業は、さらなる困難を加えましたが、コラボレーションを通じて比較的短時間で問題を解決することができました。OpenSearch チームにとって、このような瞬間はカンファレンス参加を単なる質問への回答以上のものにします。私たちは頭を寄せ合い、集合的な知識を活用し、解決策がリアルタイムで展開するのを見守ります。

Eric をはじめ、実際の課題と純粋な好奇心を持ってカンファレンスブースに近づいてくるすべての人へ: ありがとうございます。皆さんは私たちに異なる考え方をさせ、より深く掘り下げさせてくれます。これらの瞬間は、すべての統合問題の背後には意味のあるものを構築しようとしている誰かがいることを思い出させてくれます。

## コミュニティに参加しよう

Fluent Bit と OpenSearch を使用している場合、または独自の統合課題に直面している場合、OpenSearch コミュニティがお手伝いします。カンファレンスの展示フロア、ユーザーグループへの参加、コミュニティフォーラムへの投稿、ドキュメントの閲覧など、どのような形でも、必要なオブザーバビリティソリューションを構築できるよう私たちは尽力しています。

## その他の写真

![image9](/images/opensearch-realtime-problem-solving-booth/image9.png)

![image2](/images/opensearch-realtime-problem-solving-booth/image2.png)

![image6](/images/opensearch-realtime-problem-solving-booth/image6.png)
