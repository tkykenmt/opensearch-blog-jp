---
title: "[翻訳] Late Interaction モデルで検索の関連性を向上させる"
emoji: "🔍"
type: "tech"
topics: ["opensearch", "search", "machinelearning", "vectorsearch", "ai"]
published: true
publication_name: "opensearch"
published_at: 2025-12-04
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/boost-search-relevance-with-late-interaction-models/

ベクトル検索は、現代のセマンティック検索システムの基盤となっています。現在最も一般的なアプローチは単一ベクトル埋め込みを使用するものですが、最新の研究では、Late Interaction モデルによって作成されるマルチベクトル表現が、きめ細かいトークンレベルの情報を保持することで検索の関連性を大幅に向上させることが示されています。

ドキュメント全体を単一のベクトルに圧縮する従来のアプローチとは異なり、Late Interaction モデルは最終的なマッチング段階までトークンレベルの情報を保持し、より精密でニュアンスのある検索結果を可能にします。

本記事では、Late Interaction モデルとは何か、なぜ検索アプリケーションでますます重要になっているのか、そして OpenSearch でこれらを使用してユーザーにより良い検索体験を提供する方法について説明します。

## Late Interaction モデルとは

Late Interaction モデルを理解するために、まずニューラル検索の 3 つの主要なアプローチを見てみましょう。それぞれが効率性と精度の間で異なるトレードオフを提供します。

*Interaction* とは、クエリとドキュメントの関連性を、それらの表現をきめ細かいレベルで比較することによって評価するプロセスです。主な違いは、システムがクエリとドキュメントを比較する *タイミング* と *方法* にあります。

### Bi-encoder モデル (Interaction なし)

Bi-encoder モデルは、現在最も一般的なアプローチであり、クエリとドキュメントを完全に独立して処理します。

このアーキテクチャでは、「シアトル近郊の最高のハイキングコース」のようなクエリは、1 つのエンコーダーを通じて単一のベクトル表現に変換され、各ドキュメントは別のエンコーダーを通じて個別に処理され、それぞれ独自の単一ベクトル表現が生成されます。これらのエンコーディングプロセスは分離して行われ、クエリエンコーダーはドキュメントの内容にアクセスできず、その逆も同様です。関連性は、コサイン類似度やドット積などの類似度メトリクスを使用して、これらの事前計算された単一ベクトルを比較することで決定されます。

**利点:**

* **高効率**: ドキュメントベクトルはオフラインで事前に計算して保存できます。
* **優れたスケーラビリティ**: 大規模なデータセットでも良好に動作します。
* **高速な検索**: 候補の高速な第一段階フィルタリングが可能です。

**制限:**

* **精度の低下**: エンコーディング中にクエリとドキュメント間の Interaction がないため、セマンティックな理解が制限されます。

このアプローチは、ベクトル検索システムにおける高速な第一段階の検索に特に適しています。`amazon.titan-embed-text-v2:0` のようなモデルがこの方法論を例示しています。以下の図は、Bi-encoder アーキテクチャとその独立した処理アプローチを示しています。

### Cross-encoder モデル (Early/Full Interaction)

Cross-encoder モデルはスペクトルの反対側に位置し、包括的なクエリ-ドキュメント間の Interaction を通じて最高の精度を達成します。

このアーキテクチャでは、システムはクエリと各候補ドキュメント (例: 「シアトル近郊の最高のハイキングコース」とドキュメントの内容を結合) を連結し、この結合されたテキストを Transformer モデルを通じて処理します。モデルの Attention メカニズムにより、エンコーディング中にすべてのクエリトークンがすべてのドキュメントトークンに注目でき、クエリとドキュメント要素間のニュアンスのある関係を捉えます。その後、モデルはクエリ-ドキュメントペアの単一の関連性スコアを直接出力します。

**利点:**

* **最高の精度**: 深い Interaction により洗練されたセマンティックな関係を捉えます。
* **優れた理解**: Full Attention メカニズムにより包括的なクエリ-ドキュメント分析が可能です。

**制限:**

* **計算負荷が高い**: 各クエリ-ドキュメントペアにモデルの完全なフォワードパスが必要です。
* **事前計算不可**: キャッシュされた埋め込みを活用できず、スケーラビリティが制限されます。
* **レイテンシの懸念**: 処理オーバーヘッドによりリアルタイムアプリケーションが制限されます。

Cross-encoder モデルは、事前に選択された小さな結果のサブセットを並べ替えて最も関連性の高いマッチを最適化する、第二段階のリランキングシナリオで優れています。Cross-encoder が処理する結果セットのサイズは通常、コスト、レイテンシ、精度に関するシステム要件に依存しますが、これらのモデルは一般的に最初のページの結果のみに適用されます。OpenSearch は、検索パイプラインを通じて Cross-encoder リランキングのネイティブサポートを提供しています。以下の図は、包括的なクエリ-ドキュメント Interaction メカニズムを持つ Cross-encoder アーキテクチャを示しています。

### Late Interaction モデル (バランスの取れたアプローチ)

ColBERT (Contextualized Late Interaction over BERT) に代表される Late Interaction モデルは、前述の 2 つのアプローチ間の最適なバランスを達成します。これらのモデルは Bi-encoder と同様にクエリとドキュメントを独立して処理しますが、単一のベクトルではなく複数のコンテキスト化された埋め込みを生成します。

このアーキテクチャでは、「シアトル近郊の最高のハイキングコース」のようなクエリは、各トークン (「best」「hiking」「trails」「near」「Seattle」) に対して個別の埋め込みを生成します。重要なのは、各埋め込みが Transformer の Attention メカニズムを通じて周囲の単語によってコンテキスト化されることです。ドキュメントも同様の処理を受け、トークンレベルのマルチベクトル表現が生成されます。

Late Interaction モデルの根本的な革新は、そのタイミングにあります。クエリ-ドキュメント間の Interaction は、独立したエンコーディングの *後* に、詳細なトークンレベルの類似度計算を通じて行われます。このアプローチは、独立したエンコーディングの効率性の利点を維持しながら、単一ベクトル比較よりも洗練されたマッチングを可能にします。以下の図は、Late Interaction モデルがそのユニークなアーキテクチャを通じて効率性と精度のバランスをどのように取っているかを示しています。

ColBERT は、そのスコアリングメカニズムを通じてこのアプローチを例示しています。クエリとドキュメントの両方に対してコンテキスト化されたトークン埋め込みを生成した後、モデルは各クエリトークン埋め込みとすべてのドキュメントトークン埋め込み間の最大類似度を計算します。これらの最大類似度は集約されて最終的な関連性スコアが生成されます。

**利点:**

* **効率的な事前計算**: ドキュメント埋め込みはオフラインで計算して保存できます。
* **トークンレベルの精度**: プロセス全体を通じてきめ細かいセマンティック情報を維持します。
* **バランスの取れたパフォーマンス**: Bi-encoder の速度の利点と改善された精度を組み合わせます。

**スコアリングメカニズム**: この「Late Interaction」方法論により、計算効率を維持しながら、単一ベクトル比較よりも洗練されたマッチングが可能になります。

### アーキテクチャのスペクトル

3 つのアプローチは、計算効率と検索精度の間のトレードオフのスペクトルを形成します。

* **Bi-encoder**: 最大の効率性、中程度の精度、クエリ-ドキュメント間の Interaction なし
* **Late Interaction モデル**: バランスの取れた効率性と精度、エンコーディング後のトークンレベルの Interaction
* **Cross-encoder**: 最大の精度、より高い計算コスト、エンコーディング中の Full Interaction

このスペクトルを理解することで、システムアーキテクトはレイテンシ、精度、計算リソースに関する特定の要件に基づいて適切なアプローチを選択できます。

## なぜ検索で Late Interaction モデルを使用するのか

検索で Late Interaction モデルを使用することには、いくつかの魅力的な利点があります。

* **強化されたセマンティック理解**: ドキュメントを単一のベクトルに圧縮する従来のアプローチとは異なり、Late Interaction モデルは最終的なマッチング段階までトークンレベルの情報を保持します。これにより、単一ベクトルモデルでは達成できない精密なトークンレベルのマッチングが可能になります。例えば、マルチモーダルドキュメントコレクション内で「テクスチャの方向性はどのように特徴付けられるか」を検索する場合、ColPali のような Late Interaction モデルは、正確なフレーズがテキストに表示されていなくても、テクスチャの方向性分析について議論している PDF ページ内の特定のセクションを識別できます。モデルのトークンレベルの埋め込みは、「orientation」を「directional analysis」などの関連概念とマッチさせ、「texture」を「surface patterns」と細かいレベルで接続し、これらのマッチを集約して正確なドキュメントランキングを行います。このきめ細かいアプローチは、科学文献、技術文書、法的コンテンツなど、高い精度を必要とする専門分野で特に価値があります。
* **最適な効率性-精度バランス**: Late Interaction モデルは、計算効率と検索精度の間の最適なバランスを達成します。事前計算されたドキュメント埋め込みによる Bi-encoder の効率性と、Cross-encoder に近い精度レベルを組み合わせています。
* **マルチモーダル機能**: ColPali や ColQwen などの最近の開発は、パッチレベルの埋め込みを通じて Late Interaction の原則を画像やその他のメディアタイプに拡張しています。この進歩により、「四半期収益を示すチャート」のような洗練された検索で PDF 内の特定のセクションを特定することが可能になります。これは従来の単一ベクトルモデルにとって大きな課題でした。

## OpenSearch で Late Interaction モデルを使用する方法

検索業界では、パフォーマンスと精度のバランスを取る方法で Late Interaction モデルを統合するために、一般的に 2 段階戦略を採用しています。

**第一段階** では、システムは Bi-encoder モデルからの単一ベクトル埋め込みを使用して高速な近似 k-NN 検索を実行し、フルインデックスから小さな候補ドキュメントセットを選択します。このステップにより、マルチベクトル表現を処理するコストなしに検索空間を削減します。

**第二段階** では、リランカーがこれらの候補に Late Interaction スコアリングを適用し、トークンレベルのマルチベクトルを使用してより精密な関連性スコアを計算します。最終的なランク付けされた結果はこれらのきめ細かい類似度計算を反映し、スケーラビリティを維持しながらニュアンスのあるセマンティックマッチングを可能にします。

OpenSearch 3.3 では、`lateInteractionScore` 関数を使用した Late Interaction リランキングのネイティブサポートが導入されました。この関数は、各クエリベクトルをすべてのドキュメントベクトルと比較し、各クエリベクトルの最大類似度を見つけ、これらの最大スコアを合計して最終的なドキュメントスコアを生成することで、トークンレベルのベクトルマッチングを使用してドキュメントの関連性を計算します。

以下の例は、距離ではなく方向に基づいてベクトルの類似度を測定するコサイン類似度で `lateInteractionScore` 関数を使用する方法を示しています。この例では、関数は `my_vector` という名前のドキュメントベクトルを `query_vectors` パラメータで指定されたクエリベクトルと比較します。この関数を使用するには、ドキュメント取り込み時にオフラインで生成されたマルチベクトルと、クエリ処理時にオンラインで計算されたマルチベクトルが必要です。

```json
GET my_index/_search
{
  "query": {
    "script_score": {
      "query": { "match_all": {} },
      "script": {
        "source": "lateInteractionScore(params.query_vectors, 'my_vector', params._source, params.space_type)",
        "params": {
          "query_vectors": [[[1.0, 0.0]], [[0.0, 1.0]]],
          "space_type": "cosinesimil"
        }
      }
    }
  }
}
```

OpenSearch は、モデル接続から取り込み、検索まで、Late Interaction モデルを使用するための完全なワークフローをサポートしています。この機能を有効にするには、2 つの主要なコンポーネントを設定します。**ml-inference ingest processor** は、ドキュメント取り込み時にテキスト、PDF、または画像から単一ベクトルとマルチベクトルの両方の埋め込みを生成します。**ml-inference search request processor** は、検索時に受信クエリを `lateInteractionScore` 関数を使用する k-NN クエリに書き換えます。これらのコンポーネントを組み合わせることで、多様なコンテンツタイプにわたって改善された関連性を持つマルチモーダル検索が可能になります。詳細な設定手順については、[外部ホストされた Late Interaction モデルによるリランキング](https://opensearch.org/docs/latest/search-plugins/search-pipelines/rerank-processor/) のチュートリアルを参照してください。

Late Interaction モデルの検索パフォーマンスを示すために、[ML playground](https://ml.playground.opensearch.org/app/searchRelevance#/?config=eyJxdWVyeTEiOnsiaW5kZXgiOiJtdWx0aW1vZGFsX2RvY3MiLCJkc2xfcXVlcnkiOiJ7XG4gIFwicXVlcnlcIjoge1xuICAgIFwidGVybVwiOiB7XG4gICAgICBcImNvbHBhbGlfc2VhcmNoXCI6IHtcbiAgICAgICAgXCJ2YWx1ZVwiOiBcIiVTZWFyY2hUZXh0JVwiXG4gICAgICB9XG4gICAgfVxuICB9XG59Iiwic2VhcmNoX3BpcGVsaW5lIjoiY29scGFsaV9zZWFyY2gifSwicXVlcnkyIjp7ImluZGV4IjoibXVsdGltb2RhbF9kb2NzIiwiZHNsX3F1ZXJ5Ijoie1xuICBcInF1ZXJ5XCI6IHtcbiAgICBcInRlcm1cIjoge1xuICAgICAgXCJ0aXRhbl9lbWJlZGRpbmdfc2VhcmNoXCI6IHtcbiAgICAgICAgXCJ2YWx1ZVwiOiBcIiVTZWFyY2hUZXh0JVwiXG4gICAgICB9XG4gICAgfVxuICB9XG59Iiwic2VhcmNoX3BpcGVsaW5lIjoidGl0YW5fZW1iZWRkaW5nX3NlYXJjaCJ9LCJzZWFyY2giOiIgSG93IGNhbiB0aGUgb3JpZW50YXRpb24gb2YgdGV4dHVyZSBiZSBjaGFyYWN0ZXJpemVkPyJ9) には [Vidore データセット](https://huggingface.co/datasets/vidore/syntheticDocQA_artificial_intelligence_test) を使用した並列比較が含まれています。データセットには *人工知能* に関するインターネットソースのテキストが含まれており、20 の代表的なページが ML playground 環境の `multimodal_docs` インデックスにインデックスされています。

このインターフェースでは、Late Interaction リランキングに [ColPali モデル](https://huggingface.co/vidore/colpali-v1.3-hf) を使用する **2 段階パイプライン** と、Late Interaction なしで `amazon.titan-embed-image-v1` を使用する **単一段階ベースライン** を比較できます。さまざまなクエリを試して、Late Interaction モデルがマルチモーダルコンテンツの関連性ランキングをどのように改善するかを確認できます。

### 比較結果分析

以下のテストは、`multimodal_docs` インデックスに対するクエリ「テクスチャの方向性はどのように特徴付けられるか」を使用したパフォーマンスの違いを示しています。比較では 2 つのアプローチを評価しています。

* **左パネル**: ColPali モデルを使用する `colpali_search` 検索パイプライン
* **右パネル**: Titan 埋め込みモデルを使用する `titan_embedding_search` 検索パイプライン

ターゲット結果は 7 ページ目に表示され、テクスチャの方向性は方向のヒストグラムによって特徴付けられるという関連する回答が含まれています。ColPali モデルはこのページをトップ結果としてランク付けしますが (左パネル)、Titan 埋め込みモデルは検索結果にまったく含めていません (右パネル)。以下のスクリーンショットは、2 つのアプローチ間の検索パフォーマンスのこの大きな違いを示しています。

ColPali を使用した RAG アプリケーションについては、Hugging Face で利用可能な [OpenSearch AI デモアプリ](https://huggingface.co/spaces/opensearch-project/OpenSearch-AI) を参照してください。

## 課題と最適化技術

Late Interaction モデルは強力な検索精度を提供しますが、計算とストレージに関する重要な考慮事項も導入します。これらのモデルはドキュメントごとに単一の埋め込みではなく、すべてのトークンに対してベクトルを生成するため、ドキュメントごとに数百から数千のベクトルを生成する可能性があり、従来のアプローチと比較してストレージ要件が 10〜100 倍に増加することがよくあります。

最近の研究では、これらの課題に対処するためのいくつかの戦略が提供されています。PLAID (Performance-optimized Late Interaction Driver) は、精度を維持しながらベクトル数を削減するためにセントロイドとクラスタリングを使用します。量子化技術は、メモリ使用量を削減するためにバイナリまたはプロダクト量子化を使用してマルチベクトルを圧縮します。スマートチャンキングは、埋め込み生成前に戦略的なドキュメントセグメンテーションを適用し、選択的トークン埋め込みは一般的なストップワードを削除するか、Attention メカニズムを使用して最も重要なトークンのみを保持します。これらの最適化を組み合わせることで、Late Interaction モデルは、きめ細かいトークンレベルのセマンティックマッチングというコアの利点を維持しながら、本番環境でより実用的になります。

## Lucene と OpenSearch の今後の開発

OpenSearch ベクトルエンジン (k-NN プラグイン) は現在、Painless スクリプティングを使用した Late Interaction マルチベクトルリスコアリングをサポートしています。リスコアリング実装は SIMD 命令用に最適化されています。マルチベクトルは、OpenSearch の `object` フィールドタイプと `float` フィールドタイプの組み合わせを使用して表現され、Late Interaction モデルで使用されるトークンレベルのベクトル埋め込みの保存と取得を可能にします。

10.3 リリース以降、Lucene も Late Interaction モデルのマルチベクトルを使用した検索結果のリスコアリングのネイティブサポートを提供しています。この機能は `LateInteractionField` を通じて実装されており、`float[][]` マルチベクトル埋め込みを受け入れ、バイナリ表現にエンコードし、`BinaryDocValues` フィールドとしてインデックスします。このフィールドはドキュメントごとに異なる数のベクトルを持つマルチベクトルをサポートしますが、各トークンベクトルは同じ次元数を持つ必要があります。この要件は、クエリベクトルとドキュメントベクトル間の一貫した類似度比較を可能にするため、Late Interaction モデル全体で一般的です。

Lucene には、マルチベクトルの類似度に基づいて結果をリスコアリングするための `LateInteractionRescorer` クラスも含まれています。デフォルトのスコアリング方法は `sum(max(vectorSimilarity))` で、各クエリトークンベクトルとすべてのドキュメントトークンベクトル間の最大類似度を合計します。実際には、各クエリトークンベクトルはすべてのドキュメントトークンベクトルと比較され、それらの最も強い Interaction が最終的な関連性スコアに集約されます。

### 計画されている機能強化

Lucene の `LateInteractionField` を OpenSearch ベクトルエンジンに直接統合する開発が進行中です。この作業 (関連する [GitHub の Issue と PR](https://github.com/opensearch-project/k-NN/issues/2934) で追跡) は、Lucene の組み込みベクトル化プロバイダーを使用し、基盤となるハードウェアでサポートされている場合に操作を自動的にベクトル化し、SIMD 組み込み関数を適用します。この統合により、OpenSearch は上流の Lucene からパフォーマンス最適化を継承し、この急速に進化する分野での継続的な改善の恩恵を受けます。さらに、この統合により、Painless スクリプトがサポートされていない環境でも Late Interaction モデルのリランキングが可能になります。

この取り組みをサポートするために、パッチやプルリクエストの形での貢献を歓迎します。

## Late Interaction モデルを始める

検索の関連性を向上させる準備はできましたか？[リランキングチュートリアル](https://docs.opensearch.org/latest/search-plugins/search-relevance/rerank-by-field-late-interaction/) に従って、OpenSearch デプロイメントで Late Interaction モデルの実験を始めてください。[OpenSearch フォーラム](https://forum.opensearch.org/) で結果を共有し、質問をし、フィードバックを提供してください。皆様のご意見は、これらの機能の将来の開発を形作るのに役立ちます。
