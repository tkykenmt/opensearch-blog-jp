---
title: "[翻訳] OpenSearch と Apache Arrow: アーチェリー場ツアー"
emoji: "🏹"
type: "tech"
topics: ["opensearch", "apachearrow", "grpc", "streaming", "performance"]
published: true
publication_name: "opensearch"
published_at: 2025-12-23
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/opensearch-and-apache-arrow-a-tour-of-the-archery-range/

ソフトウェアプロジェクトにおいて、イノベーションを可能にしながらスケーラビリティと効率性を向上させることは重要です。交換すべき情報は常に増え続け、それをより高速に処理する必要性も常に存在します。

OpenSearch コミュニティがこれを理解していることは明らかです。最近、OpenSearch がオプトイン形式の実験的機能として、クラスター内のさまざまなデータ転送ポイントで [Apache Arrow](https://arrow.apache.org/) 標準を使用し始めていることに気づきました。現時点では実験的な段階ですが、この実験はすでに成果を上げています。皆さんにぜひ知っていただきたいと思います。有効化する方法もお見せします！

## Apache Arrow とは？

Apache Arrow は 2 つの異なるイノベーションで構成されています。1 つ目は、アクセスするプログラムやクライアントに依存しない方法でメモリ上に情報を格納するものです。これは「ゼロコピー」最適化技術と呼ばれます。この技術は重要です。データを転送する際、通常は特定の方法でメモリに格納され、保存前に変換が必要になります。別の言語で書かれたクライアントがそのメモリへのブックマークを与えられても、データを理解することはできません。しかし Arrow クライアントなら可能です。メモリ上にデータがあるものの、他のものが読み取って使用するために複製が必要になるこのパターンは「シリアライゼーションとデシリアライゼーション」と呼ばれます。Apache Arrow はこれをスキップできます。

2 つ目のイノベーションは Arrow Flight と呼ばれるコンポーネントで、Arrow フォーマットを使用してデータを交換する RPC フレームワークです。これらが一緒に使用されることを意図していることは驚くことではないでしょう。Arrow は RPC 上で使用されることを想定しています。Flight はその「やり取り」を可能にする RPC フレームワークです。

## OpenSearch のどこで使用されているか？

OpenSearch は以前から gRPC フレームワークを持っており、インメモリストレージには protocol buffers を使用していました。実験的な状態では、Arrow Flight はデータノードとコーディネーターノードの間に位置します。データノードがクエリされると、そのノード上でレコードごとに結果が構築されます。レスポンスは完全に組み立てられて返されるまで、データノードのメモリ上に残ります。

データノードに部分的な結果を返す機能を与えることで、より多くのクエリを同時に処理できるようになります。大規模なデータセットに対する効率的なメモリストレージにより、実際の転送速度も向上します。部分的な結果は利用可能になり次第コーディネーターノードに渡され、データノードからメモリの負担が取り除かれます。

## なぜコミュニティにとって重要か？

大量のデータを移動させている方々にとって、これは 2 つの理由から素晴らしいエントリーポイントになる可能性があります。

- Arrow フォーマットで格納されたデータに対する計算は高速であり、メモリ空間は他の言語で書かれたプログラムと簡単に共有できます。
- 検索のパワーが必要だが、レコードスループットを向上させたいソリューション（テレメトリ、アナリティクス、オブザーバビリティの皆さん、注目です）には、OpenSearch との新たな統合ポイントが提供されます。

高スループットのソリューションを持っているが、クラスター内のデータ転送速度に問題がある場合、何が得られるか確認するために実験してみる価値があります。

## 有効化する方法

2 つのプラグインが必要です: `transport-reactor-netty4` と `arrow-flight-rpc`。コマンドラインを使用してインストールする必要があります。

```bash
bin/opensearch-plugin install transport-reactor-netty4
bin/opensearch-plugin install arrow-flight-rpc
```

次に、`opensearch.yml` ファイルまたは Docker Compose 設定にいくつかの行を追加する必要があります。

```yaml
opensearch.experimental.feature.transport.stream.enabled: true

# セキュリティ設定に基づいて選択
http.type: reactor-netty4        # セキュリティ無効
http.type: reactor-netty4-secure # セキュリティ有効

# マルチノードクラスター設定（該当する場合）
# opensearch.yml には network.host の IP を、Docker にはノード名を使用
arrow.flight.publish_host: <ip>
arrow.flight.bind_host: <ip>

# セキュリティ有効クラスター設定（該当する場合）
transport.stream.type.default: FLIGHT-SECURE
flight.ssl.enable: true
transport.ssl.enforce_hostname_verification: false
```

次に、`jvm.options` ファイルに設定を追加します。

```
-Dio.netty.allocator.numDirectArenas=1
-Dio.netty.noUnsafe=false
-Dio.netty.tryUnsafe=true
-Dio.netty.tryReflectionSetAccessible=true
--add-opens=java.base/java.nio=org.apache.arrow.memory.core,ALL-UNNAMED
```

最後に、ノードに対して API コールを行います。

```json
PUT /_cluster/settings
{
    "persistent": {
        "plugins.ml_commons.stream_enabled": true
    }
}
```

これでクラスターはコーディネーターノードとデータノード間で Arrow Flight ストリーミングを使用するようになります。Arrow ライブラリを使用して OpenSearch と対話する際にヘルプが必要な場合は、[Apache Arrow のインストール](https://arrow.apache.org/install/)を参照して、適切なライブラリを見つけてください。

## まとめ

OpenSearch には機能フラグの背後に Apache Arrow の実装が隠されています。OpenSearch がサポートする非常に大規模なワークロードを考慮すると、試してみる理由がいくつかあります。

- シリアライゼーションとデシリアライゼーションは、ネットワーク経由でデータを転送する際に多くのオーバーヘッドを引き起こします。
- データノードが自身のリソースで大きな結果セットを蓄積する必要がなくなります。Arrow を有効にすると、結果は単一のモノリシックな結果ではなく、部分的なレスポンスのストリームとして配信されます。
- RPC フレームワークに精通している方には、統合ポイントが提供されます。

私たちは Arrow Flight の実装に関する[フィードバックを求めています](https://github.com/opensearch-project/OpenSearch/issues/18725)。いつものように、私たちの方向性と取り組みはコミュニティによって決定されますので、ぜひ声を聞かせてください！
