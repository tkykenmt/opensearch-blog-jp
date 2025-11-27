---
title: "[翻訳] OpenSearch Approximation Framework"
emoji: "⚡"
type: "tech"
topics: ["opensearch"]
published: true
publication_name: opensearch
published_at: 2025-07-24
---

:::message
この記事は [OpenSearch Project の公式ブログ記事](https://opensearch.org/blog/opensearch-approximation-framework/) の日本語翻訳です。
:::

OpenSearch ユーザーであれば、最新のログ、メトリクス、イベントを取得するために OpenSearch クエリを頻繁に実行していることでしょう。たとえば、過去 24 時間の最新 100 件のエラーログを取得したり、異常検知のために過去 7 日間のシステムメトリクスを特定したりします。これらのクエリには、時間または数値フィールドの範囲フィルター (例: `@timestamp > now-1d`)、ソート (通常は降順)、またはダッシュボードの視覚化とアラートを強化するための `match_all` クエリが含まれることがよくあります。これらはインタラクティブまたはストリーミングダッシュボードで使用されるため、レイテンシと効率がこのエクスペリエンスにとって重要です。

これらのクエリは通常、スコアリングを行わず、時系列またはイベントベースのデータを視覚化する最初のステップとしてよく使用されます。たとえば、最新のイベントを取得するためにタイムスタンプフィールドで降順に結果をソートしたり、特定の時間枠内の最も古いエントリを分析するために昇順にソートしたりすることがあります。Lucene は、スコアリングを行わない範囲クエリを実行する際にインデックス全体をスキャンする代わりに doc values をインテリジェントに使用する最適化 (`IndexOrDocValuesQuery`) を導入しましたが、デフォルトのアルゴリズムは依然としてすべてのセグメントをトラバースし、必要以上に多くのドキュメントをスコアリングすることがよくあります。これにより、実際には上位結果の小さなサブセット (例: 最初の 50 または 100 ヒット) のみが必要であるにもかかわらず、大量のドキュメントセットを不必要に処理することになります。

これに対処するために、_Approximation Framework_ を導入しました。これは、適格なクエリに対して BKD ツリートラバーサル中に早期終了ロジックを適用します。アイデアは、デフォルトの `PointRangeQuery` をオーバーライドし、要求されたヒット数が収集されると停止するカスタム `IntersectVisitor` を注入することで、クエリレイテンシを大幅に削減することです。このアプローチは、結果の正確性を保持しながら不必要な作業を回避し、大量の時間ベースまたはイベントベースのワークロードにとって価値のある最適化となります。

バージョン 3.0.0 以降、OpenSearch には Approximation Framework が GA 機能として含まれています。

## 概要

OpenSearch Approximation Framework は、早期終了を伴うカスタム BKD ツリートラバーサルを実装するクエリ最適化技術です。重要な洞察は、サイズ制限のあるクエリの場合、Approximation Framework はすべての一致するドキュメントを訪問する必要がなく、十分な結果を収集するとすぐに停止できるということです。

フレームワークは、次の機能を持つ標準 Lucene クエリ (`PointRangeQuery` など) のカスタムバージョンを作成します。

- サイズ制限に達すると BKD ツリートラバーサルの**早期終了**
- **正確な結果を返す**ため、返されるドキュメントは常に正しい一致です
- ソート要件に基づく**最適化されたトラバーサル順序**

## サポートされているサンプルクエリの形状とタイプ

Approximation Framework は現在、特に `track_total_hits` が `true` に設定されておらず、集約が含まれていない場合に、次のクエリパターンに利益をもたらします。フレームワークは、`int`、`long`、`float`、`double`、`half_float`、`unsigned_long`、`scaled_float` を含むすべての数値タイプをサポートします。

### 範囲クエリ

```json
{
  "query": {
    "range": {
      "@timestamp": {
        "gte": "2023-01-01T00:00:00",
        "lt": "2023-01-03T00:00:00"
      }
    }
  }
}
```

フレームワークは BKD ツリーをトラバースし、要求された `size` が満たされると停止します。

### Match all + ソート (ASC/DESC)

```json
{
  "query": { "match_all": {} },
  "sort": [{ "@timestamp": "desc" }]
}
```

クエリは自動的に早期終了を伴う境界付き `range` クエリに書き換えられます。

### 範囲 + ソート (ASC/DESC)

```json
{
  "query": {
    "range": {
      "@timestamp": {
        "gte": "2023-01-01T00:00:00",
        "lte": "2023-01-13T00:00:00"
      }
    }
  },
  "sort": [{ "@timestamp": "asc" }]
}
```

フレームワークは、左から右 (`ASC`) または右から左 (`DESC`) のトラバーサルを最適化して、上位 `size` ドキュメントを迅速に見つけます。

## BKD ウォーク (カスタム BKD ツリートラバーサル)

すべての一致するドキュメントを訪問する Lucene の標準ツリートラバーサルを使用する代わりに、フレームワークはソート対応トラバーサルを伴うカスタム `intersectLeft` および `intersectRight` メソッドを実装し、不必要なノードを訪問することなく正しい上位 N ドキュメントの収集を保証します。

- **`ASC` ソート**: `intersectLeft` を使用して、最小値から最大値へトラバースします。このメソッドはデフォルトであり、プレーンな範囲クエリに使用されます。
- **`DESC` ソート**: `intersectRight` を使用して、最大値から最小値へトラバースします。

### 例: 近似を伴うトラバーサル

次の例は、近似を伴う BKD ツリートラバーサルを示しています。

### intersectLeft トラバーサル

次の図は、Approximation Framework が次のパラメータを持つクエリに対して BKD ツリートラバーサルを実行する方法を示しています。

- `size` = 1100
- `range` = 10:00 – 10:30

![intersectLeft トラバーサル](/images/opensearch-approximation-framework/intersectLeft-traversal-1024x426.png)

目標は 1,100 個の一致するドキュメントのみを収集することであるため、このしきい値が満たされるとトラバーサルはショートサーキットします。

### トラバーサルパス

ツリーは次のようにトラバースされます。

```
Root → Left1 → Left2 → L1 → L2 → Right2 → L3 → Done
```

- `Right1`、`Left3`、`Right3` とそのすべての子 (`L5`–`L8`) のようなノードは、ツリーの左側から十分なドキュメントがすでに収集されているため、完全にスキップされます。
- これは、フレームワークが不必要なサブツリーの訪問を回避し、正確な上位 N 結果を返しながらクエリレイテンシを削減する方法を示しています。

### intersectRight トラバーサル

次の図は、Approximation Framework が次のパラメータを持つクエリに対して降順ソート (`SortOrder.DESC`) トラバーサルを実行する方法を示しています。

- `size` = 1100
- `range` = 10:00 – 10:30

クエリは降順でソートされているため、トラバーサルは最も右側 (最新) の値を最初に優先します。

![intersectRight トラバーサル](/images/opensearch-approximation-framework/intersectRight-traversal-1024x426.png)

### トラバーサルパス

ツリーは次のようにトラバースされます。

```
Root → Right1 → Right3 → L8 → L7 → Left3 → L6 → Done
```

- トラバーサルが十分なドキュメント (≥1,100) を収集するとすぐに、早期に終了し、左側の残りのサブツリーをスキップします。
- `Left1`、`Left2`、`Right2`、およびそれぞれのリーフの子のようなノードは、降順の優先範囲外にあるか、もはや必要ないため、完全にスキップされます。

## パフォーマンス: ベンチマークテストと結果

数値の `sort`、`range`、`match_all` クエリは全体的に大幅なパフォーマンス向上を見せていますが、以下は P90 レイテンシの改善を強調する特定のシナリオです。

### big5: 範囲クエリ

`range` クエリは、次のグラフに示すように、**約 28 ms** から **約 6 ms** に改善されました。

![big5 範囲クエリ (近似なし)](/images/opensearch-approximation-framework/big5-range-query-without-approximation-1024x552.png)

![big5 範囲クエリ (近似あり)](/images/opensearch-approximation-framework/big5-range-query-with-approximation-1024x576.png)

### big5: desc_sort_timestamp クエリ

`desc_sort_timestamp` クエリは **約 20 ms** から **約 10 ms** に改善されました。

![big5 desc_sort_timestamp クエリ (近似なし)](/images/opensearch-approximation-framework/big5-desc_sort_timestamp-query-without-approximation-1024x558.png)

### http_logs: desc_sort_timestamp クエリ

`desc_sort_timestamp` クエリは、次のグラフに示すように、**約 280 ms** から **約 15 ms** に改善されました。

![http_logs desc_sort_timestamp クエリ (近似なし)](/images/opensearch-approximation-framework/http_logs-desc_sort_timestamp-query-without-approximation-1024x547.png)

![http_logs desc_sort_timestamp クエリ (近似あり)](/images/opensearch-approximation-framework/http_logs-desc_sort_timestamp-query-with-approximation-1024x547.png)

### http_logs: asc_sort_timestamp クエリ

`asc_sort_timestamp` クエリは、次のグラフに示すように、**約 15 ms** から **約 8 ms** に改善されました。

![http_logs asc_sort_timestamp クエリ (近似なし)](/images/opensearch-approximation-framework/http_logs-asc_sort_timestamp-query-without-approximation-1024x371.png)

![http_logs asc_sort_timestamp クエリ (近似あり)](/images/opensearch-approximation-framework/http_logs-asc_sort_timestamp-query-with-approximation-1024x381.png)

### 追加の改善

特に `sort` クエリのパフォーマンスにおけるさらなる改善が OpenSearch 3.1 リリースで観察され、[3.1.0 リリース issue](https://github.com/opensearch-project/opensearch-build/issues/5487#issuecomment-2989202040) で詳細に共有されています。

この結果は、`desc_sort_timestamp` の単一セグメントテストから得られたものです。[このコメント](https://github.com/opensearch-project/OpenSearch/pull/18439#issuecomment-2961325856) によると、最適化されたカスタム BKD ウォーク (`intersectRight`) を使用した単一セグメントへの強制マージにより、P90 レイテンシが **2,111 ms** から **6.1 ms** へと劇的に削減されました。この改善は、BKD トラバーサル中の早期終了を可能にする Approximation Framework によって可能になり、最小限のオーバーヘッドで最も関連性の高いドキュメントを効率的に収集します。

開発フェーズからのベンチマーク結果をキャプチャした [このコメント](https://github.com/opensearch-project/OpenSearch/pull/18439#issuecomment-2942212895) に示されているように、いくつかのクエリタイプで大幅な改善が見られました。`http_logs`: `desc_sort_size` は **80% 以上**改善し、`http_logs`: `desc_sort_timestamp` は **80% 以上**改善し、`asc_sort_timestamp` は **80.55% 以上**のパフォーマンス改善を達成しました。

## 今後の改善

高レベルの [META issue](https://github.com/opensearch-project/OpenSearch/issues/18619) には、Approximation Framework に関連する次の一連の機能強化が含まれています。

以下は、すべての数値タイプをサポートするように Approximation Framework を拡張することを含む、3.2.0 リリースで計画されている今後の改善の一部です ([この関連 PR](https://github.com/opensearch-project/OpenSearch/pull/18530) を参照)。次の図に示すように、特に歪んだ `http_logs` データセットでテストした場合、`range` および `sort` クエリでも追加のパフォーマンス向上が観察されています。

![http_logs パフォーマンス比較](/images/opensearch-approximation-framework/http_logs-performance-comparison-1024x450.png)

### http_logs: range_with_asc_sort (2.19.1–3.2.0)

`range_with_asc_sort` クエリは、次のグラフに示すように、**約 300 ms** から **約 30 ms** に改善されました。

![http_logs range_with_asc_sort クエリ (近似あり)](/images/opensearch-approximation-framework/http_logs-range_with_asc_sort-query-with-approximation-1024x446.png)

### http_logs: range_size (2.19.1–3.2.0)

`range_size` クエリは、次のグラフに示すように、**約 48 ms** から **約 8 ms** に改善されました。

![http_logs range_size クエリ (近似あり)](/images/opensearch-approximation-framework/http_logs-range_size-query-with-approximation-1024x443.png)

### http_logs: range_with_desc_sort (2.19.1–3.2.0)

`range_with_desc_sort` クエリは、次のグラフに示すように、**約 312 ms** から **約 31 ms** に改善されました。

![http_logs range_with_desc_sort クエリ (近似あり)](/images/opensearch-approximation-framework/http_logs-range_with_desc_sort-query-with-approximation-1024x448.png)

### nyc_taxis: desc_sort_passenger_count (3.1.0–3.2.0)

`desc_sort_passenger_count` クエリは、次のグラフに示すように、**約 17 ms** から **約 12 ms** に改善されました。

![nyc_taxis desc_sort_passenger_count クエリ (近似あり)](/images/opensearch-approximation-framework/nyc_taxis-desc_sort_passenger_count-query-with-approximation-1024x443.png)

### 探索中の追加のクエリ形状とタイプ

Approximation Framework を追加のクエリタイプに拡張するいくつかの有望な拡張を探索しています。将来のリリースでターゲットにできるクエリのタイプは次のとおりです。

### Term クエリ

数値フィールドの最上位 `term` クエリにフレームワークを拡張する概念実証では、`http_logs` データセットでレイテンシが約 **25%** 減少することが示されました。詳細については、[これらの関連ベンチマーク結果](https://github.com/opensearch-project/OpenSearch/pull/18679#issuecomment-3071292692) と [この関連 issue](https://github.com/opensearch-project/OpenSearch/issues/18620) を参照してください。

### Boolean クエリ

[この関連 issue](https://github.com/opensearch-project/OpenSearch/issues/18692) と [RFC](https://github.com/opensearch-project/OpenSearch/issues/18784) は、概念実証として、単一および複数句の `boolean` クエリの両方を最適化できる `ApproximateBooleanQuery` の実装に関する情報を提供します。

### 数値 search_after クエリ

[この issue](https://github.com/opensearch-project/OpenSearch/issues/18546) で概説されている概念実証の取り組み中に、大規模なデータセットの効率的なディープページネーション用に設計された `search_after` パラメータを使用する数値クエリで大幅な改善が観察されました。`asc_sort_with_after_timestamp` のテストでは、P90 レイテンシが **194.828 ms** から **8.459 ms** に低下し、`desc_sort_with_after_timestamp` では **188.037 ms** から **7.09 ms** に低下しました。
