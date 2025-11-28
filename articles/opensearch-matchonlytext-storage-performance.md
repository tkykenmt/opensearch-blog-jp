---
title: "[翻訳] match_only_text フィールドでストレージとパフォーマンスを最適化する"
emoji: "💾"
type: "tech"
topics: ["opensearch", "elasticsearch", "検索", "ストレージ最適化"]
published: true
publication_name: "opensearch"
published_at: 2024-07-22
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/optimize-storage-and-performance-using-matchonlytext-field/

OpenSearch Project では、バージョン 2.12 で `match_only_text` という新しいフィールドタイプを導入しました。このフィールドタイプは、ドキュメント内の単語のスコアリングや位置情報が重要でない全文検索シナリオ向けに設計されています。OpenSearch で大規模なデータセットを扱っており、ストレージとパフォーマンスの最適化を検討している場合、`match_only_text` フィールドは興味深い選択肢となるでしょう。

## match_only_text フィールドとは

`match_only_text` フィールドは、OpenSearch の標準的な `text` フィールドの派生型です。通常の `text` フィールドとは以下の点で異なります。

1. **ストレージ要件の削減**: 位置情報、頻度、ノルムの保存を省略することで、全体的なストレージ要件を削減します。
2. **固定スコアリング**: スコアリングを無効化し、マッチしたすべてのドキュメントに固定スコア 1.0 を付与します。
3. **クエリサポートの制限**: interval クエリと span クエリを除く、ほとんどのクエリタイプをサポートします。

頻度と位置情報の保存オーバーヘッドを回避することで、`match_only_text` フィールドはインデックスサイズを小さくし、特に大規模なデータセットでストレージコストを削減できます。

## match_only_text フィールドを使用する理由

`match_only_text` フィールドは、関連性ランキングや単語の近接性・順序に依存するクエリ (interval クエリや span クエリなど) を必要とせず、特定の単語を含むドキュメントを素早く見つけたい場合に特に有効です。例えば、直近 1 時間のログから例外を検索する場合、関連性は重要ではないかもしれません。

`match_only_text` フィールドのストレージ要件削減は、大量のテキストデータを管理する組織にとって大幅なコスト削減につながります。初期ベンチマークによると、標準の `text` フィールドと比較して最大 25% のストレージ削減が可能です。

## match_only_text がインデックスサイズを小さくする仕組み

通常の `text` フィールドでは、転置インデックスに単語からポスティングへのマッピングが保存されます。ポスティングには、その単語が存在するドキュメントの ID に加えて、位置情報、ドキュメント頻度、ノルムなどの追加情報が含まれます。term クエリのように位置情報が不要なクエリを実行する場合、位置情報は読み込まれません。しかし、phrase クエリを実行する場合は、フレーズクエリの各単語が順序通りに並んでいることを確認するために、ドキュメント内の単語の位置情報が必要になります。

`match_only_text` フィールドでは、位置情報が保存されないため、インデックスサイズが小さくなります。位置データなしで phrase クエリを実行するために、OpenSearch は phrase クエリを個々の term クエリの論理積に変換し、マッチしたドキュメントを `_source` フィールドの元のドキュメント内容と Lucene MemoryIndex を使用して照合します。このアプローチは、phrase クエリのパフォーマンスとストレージ要件削減のトレードオフを取っています。

## ストレージ削減量の見積もり

`match_only_text` フィールドでどれだけストレージコストを削減できるか、またサポートされない機能や phrase クエリのパフォーマンスとのトレードオフに見合うかを理解するために、OpenSearch Index Stats API を使用できます。

```
/<index_name>/_stats/segments?level=shards&include_segment_file_sizes&pretty
```

この API は、`pos` (位置情報)、`doc` (頻度)、`nvm` (ノルム) コンポーネントのストレージ使用量に関する情報を提供します。`match_only_text` を使用することで達成できる削減量は、特定のデータとワークロードによって異なりますが、初期ベンチマークでは OpenSearch Benchmark の PMC ワークロードで最大 25% のストレージ削減が示されています。

`_stats` API ではフィールドレベルの統計を取得できないことに注意してください。`text` から `match_only_text` への移行後のストレージ最適化を正確に予測できるよう、この制限に対処するための [GitHub issue](https://github.com/opensearch-project/OpenSearch/issues/6836#issuecomment-1758529469) が作成されています。

## OpenSearch での match_only_text の使用方法

`match_only_text` フィールドを使用するには、OpenSearch のインデックスマッピングで以下のように定義します。

```json
{
  "mappings": {
    "properties": {
      "my_text_field": {
        "type": "match_only_text"
      }
    }
  }
}
```

`match_only_text` フィールドには、phrase クエリのパフォーマンス低下や近接性ベースのクエリが使用できないなどのトレードオフがあることを忘れないでください。このフィールドタイプが OpenSearch アプリケーションに適切な選択かどうかを判断するために、特定のユースケースと要件を評価してください。

詳細については、`match_only_text` フィールドの[ドキュメント](https://opensearch.org/docs/latest/field-types/supported-field-types/match-only-text)を参照してください。
