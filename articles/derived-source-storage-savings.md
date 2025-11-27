---
title: "[翻訳] Derived Source でストレージを最大 2 倍節約"
emoji: "💾"
type: "tech"
topics: ["opensearch"]
published: true
publication_name: opensearch
published_at: 2025-10-22
---

:::message
この記事は [OpenSearch Project の公式ブログ記事](https://opensearch.org/blog/save-up-to-2x-on-storage-with-derived-source/) の日本語翻訳です。
:::

ストレージは、OpenSearch クラスターのインフラストラクチャコストを左右する重要な要素です。データが増加するにつれて、OpenSearch がドキュメントを複数の形式で保存するかどうかに応じて、ストレージ要件は何倍にも増加する可能性があります。ここで derived source が登場し、ストレージコストを最適化します。

このブログ記事では、OpenSearch でドキュメントがどのように保存されるか、そして derived source を使用してコスト効率の高い方法でそれらのドキュメントを取得する方法について説明します。

## OpenSearch でドキュメントはどのように保存されるか?

ドキュメントが取り込まれると、OpenSearch は元のドキュメント本体を [`_source`](https://docs.opensearch.org/latest/field-types/metadata-fields/source/) フィールドに保存します。さらに、ドキュメントのフィールドは、次の画像に示すように、[indexed](https://docs.opensearch.org/latest/field-types/mapping-parameters/index-parameter/)、[stored](https://docs.opensearch.org/latest/field-types/mapping-parameters/store/)、[doc values](https://docs.opensearch.org/latest/field-types/mapping-parameters/doc-values/) などのさまざまな形式で保存されます。

![ドキュメントフィールド値](/images/derived-source-storage-savings/doc-field-values.png)

OpenSearch がデータをさまざまな形式で保存するのは、各フィールドタイプが最適化された検索のために特定の形式で値を保存する必要があるためです。たとえば、全文検索は転置インデックスに依存し、キーワードフィールドの正確な用語集約は doc values に依存します。元のドキュメントは、すべてのフィールドを 1 つの場所に含む別のデータ構造に保存されるため、フェッチフェーズで簡単に取得できます。このセットアップは、データの重複によるストレージコストを犠牲にして、検索レイテンシを削減します。

次の画像は、約 10 億のドキュメントを含むテストデータセットで実施された実験中のフィールド分布を示しています。

## OpenSearch は \_source フィールドをどのように使用するか?

`_source` フィールドは、検索操作中のドキュメント取得だけでなく、更新、再インデックス操作、スクリプト化された更新、リカバリ操作などの操作にも使用されます。`_source` を無効にすると、これらの操作が利用できなくなり、データリカバリができなくなるため、推奨されません。

OpenSearch 2.9.0 は [ZSTD 圧縮](https://docs.opensearch.org/latest/im-plugin/index-codecs/) を導入し、高速で高い圧縮率を提供します。ストレージフットプリントを測定する同じ実験では、ZSTD 圧縮を有効にすると、保存されたフィールドサイズが 216 GB に削減され、約 46% の削減になりました。ただし、この削減があっても、保存されたフィールドは依然としてかなりの量のストレージを占有します。

## Derived source とは?

ユースケースが `min`、`max`、`avg`、`sum`、`terms` などの集約を必要とするが、一致したドキュメント自体は必要としない場合、すべてのデータを保存することは収穫逓減をもたらします。実際のドキュメントは不要で、集約だけで十分だからです。

OpenSearch 3.2.0 以降、このようなユースケースに対して _derived source_ を使用してストレージを最適化できます。Derived source モードは、取り込み中に `_source` フィールドを除外するようにインデックスの動作を変更し、データの重複を防ぎ、ストレージ要件を削減します。これらのドキュメントは、オンデマンドで異なる形式のフィールドストレージ (`doc_values` や stored fields など) を使用して動的に取得されます。このアプローチは、検索機能を保持し、実際に `_source` フィールドを保存することなく、再インデックス、更新、スクリプト化された更新、リカバリなど、`_source` データに依存する操作をサポートします。

この変更されたドキュメント取得動作により、検索クエリのフェッチフェーズ中に、OpenSearch は `doc_values` や stored fields などの形式を使用して各フィールドの値を取得し、結果を組み合わせて最終的なドキュメントを生成します。次の画像に示すとおりです。

![Derived source の生成](/images/derived-source-storage-savings/derived-source-generation.png)

Derived source でインデックスを構成する場合、OpenSearch はすべてのフィールドがサポートされているタイプであることを検証します。検索、更新、リカバリなどの操作を通じてドキュメントにアクセスすると、derived source はインデックスマッピングで定義されているように、`doc_values` または stored fields から各フィールドの値を再構築します。これには、単一の `_source` フェッチではなく、各フィールドのディスク位置からデータを読み取る必要があるため、大量のドキュメントを取得する際にレイテンシの低下が見られる場合があります。

## Derived source の設定方法

Derived source はインデックスレベルで設定できます。元の `_source` を保存するデフォルトの動作を変更するため、この設定はインデックスの作成後に更新できません。この制限により、元の保存されたソースと動的に生成されたソース (出力では元のソースと似ているように見える可能性があります) の間の混合動作が防止されます。

Derived source を設定するには、インデックス設定で `derived_source.enabled` を `true` に設定します。

```json
PUT sample-index1
{
  "settings": {
    "index": {
      "derived_source": {
        "enabled": true
      }
    }
  },
  "mappings": {
    <index fields>
  }
}
```

詳細については、[Derived source](https://docs.opensearch.org/latest/field-types/metadata-fields/source/#derived-source) を参照してください。

## パフォーマンスベンチマーク

実験の実行に基づいて、derived source は特定のワークロードに対して大幅なストレージ削減を提供できます。次の表に示すとおりです。

| ワークロード | ストレージ削減 |
| ------------ | -------------- |
| nyc_taxis    | 41%            |
| http logs    | 43%            |
| elb logs     | 58%            |

検索レイテンシは、10% (terms 集約での 1K ドキュメント) から 100% (match-all クエリでの 10K ドキュメント) の範囲で回帰を示しました。ただし、一部のクエリではレイテンシが改善されました。`doc_values` からの読み取りは、保存された `_source` フィールドにアクセスする際に必要な解凍を回避することが多いためです。

これらのベンチマーク全体で、最大 18% のインデックス作成スループットの大幅な改善と、20% から 48% の範囲のマージ時間の削減が観察されました。これは、最適化されたセグメントを生成する際の CPU オーバーヘッドが低いためで、マージオーバーヘッドの削減にも役立ちます。

インデックスサイズが削減されると、追加の利点が明らかになります。小さなシャードは、ノードの再起動やシャードの再配置中のリカバリを高速化し、小さなセグメントは必要なディスク I/O とページキャッシュスワップが少なくなり、より効率的なクエリが実現します。

ファイルベースのリカバリは高速のままですが、操作ベースのリカバリは `_source` を再生成する必要があるため、遅くなる可能性があります。操作ベースのリカバリには 2 つのタイプがあります。

1. Lucene ベース - derived source を使用したドキュメントレプリケーションの影響を受けます。
2. Translog ベース - 元の `_source` を読み取ることは、再生成する代わりに、derived source がトランスログ内のドキュメントを処理する方法のために、最大 2 倍の時間がかかる可能性があります。

Translog ベースのリカバリのパフォーマンスへの影響を回避するには、メインインデックスで有効にしたまま、トランスログの derived source を無効にできます。

```json
PUT sample-index1
{
  "settings": {
    "index": {
      "derived_source": {
        "enabled": true,
        "translog": {
          "enabled": false
        }
      }
    }
  }
}
```

## 制限事項

Derived source は大幅なストレージ削減を提供しますが、クエリレスポンスの生成と返却方法に特定の制限を課します。

### 日付の表現

複数の[フォーマット](https://docs.opensearch.org/latest/field-types/supported-field-types/date/#formats)が指定された [date](https://docs.opensearch.org/latest/field-types/supported-field-types/date/) フィールドの場合、derived source は、元の取り込まれた値に関係なく、リストの最初のフォーマットをすべての要求されたドキュメントに使用します。

### Geopoint の表現

[Geopoint](https://docs.opensearch.org/latest/field-types/supported-field-types/geo-point/) フィールド値は複数の形式で取り込むことができますが、derived source は常に固定形式 `{"lat": lat_val, "lon": lon_val}` で表現します。インデックス作成中に精度の損失が発生する可能性があり、derived source でも同じ程度の精度損失が現れる可能性があります。

### 複数値フィールドの順序と重複排除

Derived source は、次の例に示すように、複数値配列の値を自動的にソートし、キーワードフィールドの場合は重複を排除します。

```
1. Keyword field
 a. Ingested source
 {
   "keyword": ["b", "c", "a", "c"]
 }
 b. Derived source
 {
   "keyword": ["a", "b", "c"]
 }
2. Number field
 a. Ingested source
 {
   "number": [3, 1, 2, 1]
 }
 b. Derived source
 {
   "number": [1, 1, 2, 3]
 }
```

フィールドレベルの制限については、[Supported fields](https://docs.opensearch.org/latest/field-types/metadata-fields/source/#supported-fields-and-parameters) の特定のサポートされているフィールドのドキュメントを参照してください。

## 次は何か?

Derived source は現在、最も一般的に使用されるフィールドタイプのほとんどをサポートしていますが、インデックスマッピングでこれらのフィールドを定義する際にいくつかの制限があります。将来的には、より多くのユースケースで derived source を利用できるようにするために、これらの制限を削除する予定です。開発ロードマップには、[range](https://docs.opensearch.org/latest/field-types/supported-field-types/range/) や [geoshape](https://docs.opensearch.org/latest/field-types/supported-field-types/geo-shape/) フィールドなど、追加のフィールドタイプへのサポートの拡張も含まれています。機能の拡張に加えて、ドキュメント取得戦略を改善するパフォーマンスの最適化に焦点を当てており、大量のドキュメントを要求する際の検索レイテンシを削減します。これらの組み合わせた改善により、derived source はより広範なシナリオでより柔軟で高性能になります。

アプリケーションで derived source を試して、[OpenSearch フォーラム](https://forum.opensearch.org/) でフィードバックを共有することをお勧めします。あなたの洞察は、将来の改善の優先順位付けに役立ち、ニーズを満たす機能を構築していることを確認するのに役立ちます。

## 著者について

**Tanik** は、2022 年から Amazon で働いているソフトウェア開発エンジニアです。Amazon では、Tanik は主に Amazon OpenSearch Service の可観測性に焦点を当てています。
