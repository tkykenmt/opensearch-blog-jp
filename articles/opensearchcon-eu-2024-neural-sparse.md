---
title: "低コストでセマンティック検索を実現する Neural Sparse Search"
emoji: "🔍"
type: "tech"
topics: ["opensearch", "検索", "機械学習", "セマンティック検索", "NLP"]
publication_name: "opensearch"
published: false
---

:::message
本記事は [OpenSearch Project YouTube チャンネル](https://www.youtube.com/@OpenSearchProject) で公開されているセッション動画の内容を日本語で書き起こしたものです。
:::

https://www.youtube.com/watch?v=kx71KFf-Nv0

※ 本記事は動画の自動字幕を基に作成しています。誤字脱字や誤った内容が含まれる可能性があります。

## はじめに

このセッションでは、AWS の OpenSearch チームの Aswath Srinivasan 氏が、予算に優しいセマンティック検索を実現する Neural Sparse Search について解説します。BM25 を使用している検索チームが、KNN 検索の大規模なノード要件によるコスト制約を抱えながらもセマンティック検索を実装したい場合に最適な内容です。

主なトピック:
- スパースベクトルとデンスベクトルの使い分け
- スパース埋め込みモデルのホスティング方法
- OpenSearch で利用可能な事前学習済みモデル
- Document-only エンコーダーと Bi-encoder の選択
- ハイブリッド検索との組み合わせ
- GPU アクセラレーションの推奨事項
- ベンチマークとベストプラクティス

## 語彙ミスマッチ問題

[![Thumbnail](/images/opensearchcon-eu-2024-neural-sparse/intro.jpg)](https://www.youtube.com/watch?v=kx71KFf-Nv0&t=30)

検索における根本的な課題として「語彙ミスマッチ問題」があります。例えば、オンラインショップで「ソファ」を検索しても、販売者が「カウチ」「ラブシート」「ソファベッド」などの別名で登録していると、商品が見つかりません。

### 従来の解決策

[![Thumbnail](/images/opensearchcon-eu-2024-neural-sparse/vocabulary-mismatch.jpg)](https://www.youtube.com/watch?v=kx71KFf-Nv0&t=180)

1. **SEO 的アプローチ**: 商品タイトルに「ソファ/カウチ/ダイベッド」のように複数の名称を詰め込む方法
2. **シノニム辞書**: 検索エンジンに同義語辞書を設定し、インデックス時や検索時に用語を展開する方法

しかし、シノニム辞書のアプローチには課題があります:
- 一般的なドメインでは公開辞書が使えるが、製薬・ヘルスケア・石油ガス・自動車などの専門分野では手動でのキュレーションが必要
- 辞書の作成は網羅的にならず、完成することがない
- 静的な辞書では文脈を考慮できない

## SPLADE モデルの登場

[![Thumbnail](/images/opensearchcon-eu-2024-neural-sparse/splade.jpg)](https://www.youtube.com/watch?v=kx71KFf-Nv0&t=360)

2021年中頃に登場した SPLADE (Sparse Lexical and Expansion) モデルは、この問題を解決します。

### 学習可能な用語展開

SPLADE は文脈に基づいて用語を展開します。例えば「Apple」という単語を含む2つの文書があるとします:

- 「Apple products are expensive」→ 展開される用語: device, expensive, chip, money, budget, manufacturer など
- 「An apple a day keeps the doctor away」→ 展開される用語: doctor, daily, medical など

静的なシノニム辞書とは異なり、文脈に応じて適切な用語に展開されます。

### 重み付け

展開された各用語には重みが付与されます。すべての展開が同じ重要度ではないため、この重みによって関連性を判断できます。

### スコアリング

検索時のスコアリングは、ドキュメントとクエリの展開された用語の内積の合計で計算されます。デンスベクトルの数値表現とは異なり、どの用語がマッチしたかが明確にわかるため、解釈性が高いのが特徴です。

## 事前学習済みモデル

OpenSearch では複数の事前学習済みモデルが利用可能です:

| モデルタイプ | 説明 |
|------------|------|
| **Bi-encoder (V2 distill)** | インデックス時と検索時の両方で用語展開を行う |
| **Doc-only encoder (V3 GTE)** | インデックス時のみ用語展開を行う（推奨） |

Bi-encoder は検索時にオンライン推論が必要となり、レイテンシに影響します。Doc-only encoder を使用し、検索時にはトークナイザーを使用することで、より効率的な検索が可能です。

## デモ: Neural Sparse Search の実装

[![Thumbnail](/images/opensearchcon-eu-2024-neural-sparse/demo.jpg)](https://www.youtube.com/watch?v=kx71KFf-Nv0&t=600)

### 1. モデルのデプロイ

まず、OpenSearch のドキュメントページから事前学習済みモデルの設定 URL を取得し、モデルをデプロイします。

```
推奨: モデルは専用の ML ノードにデプロイするか、
Amazon SageMaker や Amazon Bedrock などの外部サービスでホストする
```

### 2. Ingest Pipeline の作成

Sparse encoding processor を含むパイプラインを作成します。必要な設定は3つ:
- **model_id**: 使用するモデルの ID
- **field_map**: 展開対象のテキストフィールド
- **output_field**: 展開結果を格納するフィールド

### 3. インデックスの作成

```json
{
  "mappings": {
    "properties": {
      "text": { "type": "text" },
      "sparse_vector": { "type": "rank_features" }
    }
  },
  "settings": {
    "default_pipeline": "sparse-encoding-pipeline"
  }
}
```

`rank_features` フィールドタイプは、スパースベクトルドキュメントのスコアリングをブーストまたはブロックできます。

### 4. Neural Sparse Search の実行

```json
{
  "query": {
    "neural_sparse": {
      "sparse_vector": {
        "query_text": "can I use it as an internet phone?",
        "model_id": "<tokenizer_model_id>"
      }
    }
  }
}
```

## スコアリングの仕組み

[![Thumbnail](/images/opensearchcon-eu-2024-neural-sparse/scoring.jpg)](https://www.youtube.com/watch?v=kx71KFf-Nv0&t=1200)

`explain: true` を設定すると、スコアリングの詳細が確認できます。

例えば「phone」というトークンの場合:
- クエリ側の重み: 4.58
- ドキュメント側の重み: 7.0
- スコア: 4.58 × 7.0 = 32.06

最終スコアは、マッチしたすべてのトークンの内積の合計です。

## Lexical Search との比較

[![Thumbnail](/images/opensearchcon-eu-2024-neural-sparse/comparison.jpg)](https://www.youtube.com/watch?v=kx71KFf-Nv0&t=1500)

OpenSearch の Search Relevancy タブを使用して、Lexical Search と Neural Sparse Search を比較できます。

**クエリ例**: 「is there something in the inventory anymore」（在庫があるか）

| Lexical Search | Neural Sparse Search |
|----------------|---------------------|
| アダプターに関する結果 | 「all items in stock」を含む結果 |
| 解像度に関する結果 | 在庫・物流に関する結果 |
| 価格に関する結果 | 在庫状況に関する結果 |

クエリに「stock」という単語がなくても、Neural Sparse Search は文脈を理解して関連する結果を返します。

### ハイブリッド検索

完全一致検索（ダブルクォート検索）など、Neural Sparse Search が苦手なケースもあります。そのような場合は、Lexical Search と Neural Sparse Search を組み合わせたハイブリッド検索が有効です。

## プルーニングによる最適化

プルーニングは、重みの低い展開用語を削除することで、ストレージとインデックスサイズを削減し、検索速度を向上させる技術です。

### インデックス時のプルーニング

```json
{
  "prune_type": "abs_value",
  "prune_ratio": 0.48
}
```

重みが 0.48 未満のトークンを削除します。`max_ratio` を使用して上位 40% のみを保持することも可能です。

### 検索時のプルーニング (Two-phase processor)

1. 最初に上位 40% のトークンで検索を実行し、候補を絞り込む
2. 絞り込まれた候補に対して、すべてのトークンを使用してリランキング

これにより、検索レイテンシを大幅に改善できます。

## 新しい Semantic フィールドタイプ

最新バージョンの OpenSearch では、`semantic` フィールドタイプを使用することで、より簡単に Neural Sparse Search を実装できます:

```json
{
  "mappings": {
    "properties": {
      "content": {
        "type": "semantic",
        "model_id": "<doc_only_model_id>",
        "search_model_id": "<tokenizer_model_id>"
      }
    }
  }
}
```

従来の複雑な設定が、わずか3ステップで完了します。

## なぜ「予算に優しい」のか

### デンスベクトルのコスト問題

KNN 検索でデンスベクトルを使用する場合:
- 500万ベクトルで 16GB のメモリが必要
- 64GB メモリのインスタンスタイプが必要
- 1000万、10億ベクトルになると、コストが急激に増加

### スパースベクトルの利点

- ネイティブの Lucene インデックスに統合されている（別途 KNN インデックスが不要）
- インデックスサイズが小さい
- 必要なメモリと CPU が少ない
- ゼロショット性能が良好（新しいドメインへの適用が容易）
- ファインチューニングがデンスベクトルより軽量

## スケーラビリティの向上

従来、スパースベクトルは 1000万ドキュメントまでが推奨でしたが、OpenSearch 3.3 で ANN (Approximate Nearest Neighbor) サポートが追加され、1億ベクトルまでスケール可能になりました。

## ベストプラクティス

1. **Doc-only encoder を使用する** - より効率的
2. **Deep Learning tokenizer を活用** - 最新バージョンではトークナイザーのデプロイが不要に
3. **モデルは専用ノードまたは外部サービスでホスト** - Amazon SageMaker、Amazon Bedrock など
4. **最新の事前学習済みモデルを確認** - ドキュメントで最新情報をチェック
5. **Two-phase processor でプルーニング** - 検索速度の向上
6. **インデックス時のプルーニング** - ストレージ削減
7. **Lucene バージョンを最新に保つ** - パフォーマンス向上
8. **GPU アクセラレーション** - 推論速度の向上
9. **OpenSearch のベストプラクティスを遵守** - Concurrent segment merge、Segment replication など

## まとめ

Neural Sparse Search は、デンスベクトルによる KNN 検索のコスト問題を解決しながら、セマンティック検索の恩恵を受けられる優れた選択肢です。特に予算制約がある場合や、まずセマンティック検索を試してみたい場合に最適です。

## 参考リンク

- [OpenSearch Neural Sparse Search ドキュメント](https://opensearch.org/docs/latest/search-plugins/neural-sparse-search/)
- [事前学習済みモデル一覧](https://opensearch.org/docs/latest/ml-commons-plugin/pretrained-models/)
- [Hugging Face - OpenSearch モデル](https://huggingface.co/opensearch-project)
