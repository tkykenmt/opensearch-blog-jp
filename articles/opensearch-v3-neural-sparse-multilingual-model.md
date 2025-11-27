---
title: "[翻訳] OpenSearch v3 ニューラルスパースモデルと多言語検索モデルによる検索の進化"
emoji: "🔍"
type: "tech"
topics: ["opensearch"]
published: true
published_at: 2025-09-25
publication_name: opensearch
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/advancing-search-with-opensearch-v3-neural-sparse-models-and-a-multilingual-retrieval-model/

ニューラルスパース検索は、OpenSearch における意味検索のための強力かつ効率的な手法です。テキストを (トークン, 重み) のエントリにエンコードすることで、Lucene の転置インデックスを使用した効率的なインデックス作成と検索を可能にします。[OpenSearch 2.11](https://opensearch.org/blog/improving-document-retrieval-with-sparse-semantic-encoders/) での導入と [v2 シリーズ](https://opensearch.org/blog/neural-sparse-v2-models/)による改善以来、ニューラルスパース検索は推論不要の検索による効率性のメリットとともに、高い検索精度を実現してきました。本日、2 つの大きな進化をお知らせします。

- **v3 シリーズのニューラルスパースモデル** – これまでで最も高精度なスパース検索モデルです。軽量で推論不要の効率性を維持しながら、検索精度を大幅に向上させました。
- **新しい多言語検索モデル** – OpenSearch 初の多言語ニューラルスパース検索モデルです。

## ニューラルスパース検索 v3 モデル: 検索精度の向上

v3 ニューラルスパースモデルのリリースをお知らせします。

- **v3-distill**: v2-distill モデルの成功を基に、改良されたトレーニングにより検索精度を向上させました (NDCG@10 が v2-distill の 0.504 から 0.517 に向上)。高速なインジェストと低メモリ使用量を実現する軽量アーキテクチャはそのまま維持しています。
- **v3-gte**: 最も高精度な v3 モデルです。すべてのベンチマークで最高の検索精度を達成しながら (NDCG@10 が v3-distill の 0.517 に対して 0.546)、doc-only スパース検索の高効率性と低レイテンシ性能を維持しています。

v3 モデルは [OpenSearch](https://docs.opensearch.org/latest/ml-commons-plugin/pretrained-models/) と [Hugging Face](https://huggingface.co/opensearch-project) の両方で利用可能です。

すべての v3 モデルは、v2 モデルよりも**優れた検索精度**を達成しています。以下の表は、モデル世代間の検索精度を比較したものです。

| モデル             | [v1](https://huggingface.co/opensearch-project/opensearch-neural-sparse-encoding-v1) | [v2-distill](https://huggingface.co/opensearch-project/opensearch-neural-sparse-encoding-v2-distill) | [doc-v1](https://huggingface.co/opensearch-project/opensearch-neural-sparse-encoding-doc-v1) | [doc-v2-distill](https://huggingface.co/opensearch-project/opensearch-neural-sparse-encoding-doc-v2-distill) | [doc-v2-mini](https://huggingface.co/opensearch-project/opensearch-neural-sparse-encoding-doc-v2-mini) | [doc-v3-distill](https://huggingface.co/opensearch-project/opensearch-neural-sparse-encoding-doc-v3-distill) | [doc-v3-gte](https://huggingface.co/opensearch-project/opensearch-neural-sparse-encoding-doc-v3-gte) |
| ------------------ | ------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------- |
| 推論不要           | ✔️                                                                                   | ✔️                                                                                                   | ✔️                                                                                           | ✔️                                                                                                           | ✔️                                                                                                     | ✔️                                                                                                           | ✔️                                                                                                   |
| モデルパラメータ数 | 133M                                                                                 | 67M                                                                                                  | 133M                                                                                         | 67M                                                                                                          | 23M                                                                                                    | 67M                                                                                                          | 133M                                                                                                 |
| 平均 NDCG@10       | 0.524                                                                                | 0.528                                                                                                | 0.49                                                                                         | 0.504                                                                                                        | 0.497                                                                                                  | 0.517                                                                                                        | 0.546                                                                                                |
| 平均 FLOPS         | 11.4                                                                                 | 8.3                                                                                                  | 2.3                                                                                          | 1.8                                                                                                          | 1.7                                                                                                    | 1.8                                                                                                          | 1.7                                                                                                  |

## v2 から v3 シリーズモデルへの進化

OpenSearch における v2 から v3 モデルへの移行は、v2 シリーズの特徴である効率性を維持しながら、ニューラルスパース検索の精度を大幅に向上させる重要な進歩を表しています。

### v2 モデルの課題

v2 シリーズモデルは、モデルパラメータ数を大幅に削減し、インジェストスループットを向上させながら、ほぼ同等の検索精度を維持することで、ニューラルスパース検索を広く利用可能にしました。しかし、検索ワークロードやデータセットが複雑化するにつれて、いくつかの課題が浮上しました。

- **精度のボトルネック**: v2 モデルは高い効率性と堅実な性能を提供しましたが、推論不要の設計では、十分にトレーニングされた Siamese 密ベクトル検索器やスパース検索器の検索品質には及びませんでした。
- **教師モデルからの学習が限定的**: v2 モデルは主に異種バイエンコーダー教師モデルによる蒸留に依存しており、大規模言語モデル (LLM) などのより強力なモデルからの豊富なランキングシグナルを活用していませんでした。

これらの課題が、次世代モデルのトレーニング戦略とモデルアーキテクチャの両方を再考する動機となりました。

### v3 モデルの進化

v3 シリーズでは、v2 モデルの軽量性と低レイテンシ特性を維持しながら、検索精度を新たなレベルに引き上げることを主な目標としました。主な進化点は以下のとおりです。

- **v3-distill**: v2-distill を基に、[ℓ0 ベースのスパース化技術](https://arxiv.org/abs/2504.14839)を組み込み、より大規模で多様なデータセットでトレーニングしています。この組み合わせにより、高速なインジェストと低メモリ使用量を実現する同じ軽量アーキテクチャを維持しながら、検索精度を向上させています。
- **v3-gte**: v3-distill のバックボーンを General Text Embedding (GTE) アーキテクチャに置き換え、より強力な意味表現と 8192 トークンのコンテキストウィンドウをサポートしています。このモデルは LLM 教師モデルを採用し、より豊かな意味的ニュアンスを捉え、OpenSearch のスパース検索精度の新たなベンチマークを確立しています。

## v3 モデルを支える技術

v3 モデルの技術的改善を支える 2 つのコア技術があります。効率的なドキュメント表現のための ℓ0 ベースのスパース化と、トレーニング品質向上のための LLM 教師モデルを用いた GTE アーキテクチャです。

これらの進化により、v3 シリーズは従来世代の速度、効率性、推論不要の利点を維持しながら、検索精度を大幅に向上させています。これにより、スケーラビリティやレイテンシを犠牲にすることなく、最先端の検索性能を実現できます。

### ℓ0 ベースのスパース化

ℓ0 ベースのアプローチは、効率性とランキング品質のバランスを取るために、ドキュメント側の表現を選択的にスパース化します。

- **ℓ0 マスク損失**: 目標のスパース性閾値を超えるドキュメントベクトルのみを正則化します。
- **ℓ0 近似活性化**: ℓ0 の微分可能な近似を提供し、トレーニング中の正確なスパース性制御を可能にします。

拡張されたトレーニングデータと組み合わせることで、v3-distill は効率性を犠牲にすることなく、より高い精度を達成しています。

### LLM 教師モデルを用いた GTE アーキテクチャ

GTE アーキテクチャは意味表現を強化し、より長い入力を処理できます。一方、LLM ベースの教師シグナルはより豊かなランキングの学習を可能にします。この組み合わせにより、v3-gte はすべての OpenSearch スパース検索器の中で最高の精度スコアを達成しています。

## 検索精度ベンチマーク

[以前のブログ記事](https://opensearch.org/blog/neural-sparse-v2-models/)で説明したテストと同様に、BEIR ベンチマークでモデルの検索精度を評価しました。検索精度の結果を以下の表に示します。すべての v3 シリーズモデルは v2 および v1 モデルを上回り、v3-gte はすべてのテストで最高の精度スコアを達成し、OpenSearch ニューラルスパース検索モデルの新記録を樹立しました。

| モデル                                                                                                       | 平均  | Trec-Covid | NFCorpus | NQ    | HotpotQA | FiQA  | ArguAna | Touche | DBPedia | SciDocs | FEVER | ClimateFEVER | SciFact | Quora |
| ------------------------------------------------------------------------------------------------------------ | ----- | ---------- | -------- | ----- | -------- | ----- | ------- | ------ | ------- | ------- | ----- | ------------ | ------- | ----- |
| [v1](https://huggingface.co/opensearch-project/opensearch-neural-sparse-encoding-v1)                         | 0.524 | 0.771      | 0.36     | 0.553 | 0.697    | 0.376 | 0.508   | 0.278  | 0.447   | 0.164   | 0.821 | 0.263        | 0.723   | 0.856 |
| [v2-distill](https://huggingface.co/opensearch-project/opensearch-neural-sparse-encoding-v2-distill)         | 0.528 | 0.775      | 0.347    | 0.561 | 0.685    | 0.374 | 0.551   | 0.278  | 0.435   | 0.173   | 0.849 | 0.249        | 0.722   | 0.863 |
| [doc-v1](https://huggingface.co/opensearch-project/opensearch-neural-sparse-encoding-doc-v1)                 | 0.49  | 0.707      | 0.352    | 0.521 | 0.677    | 0.344 | 0.461   | 0.294  | 0.412   | 0.154   | 0.743 | 0.202        | 0.716   | 0.788 |
| [doc-v2-distill](https://huggingface.co/opensearch-project/opensearch-neural-sparse-encoding-doc-v2-distill) | 0.504 | 0.69       | 0.343    | 0.528 | 0.675    | 0.357 | 0.496   | 0.287  | 0.418   | 0.166   | 0.818 | 0.224        | 0.715   | 0.841 |
| [doc-v2-mini](https://huggingface.co/opensearch-project/opensearch-neural-sparse-encoding-doc-v2-mini)       | 0.497 | 0.709      | 0.336    | 0.51  | 0.666    | 0.338 | 0.48    | 0.285  | 0.407   | 0.164   | 0.812 | 0.216        | 0.699   | 0.837 |
| [doc-v3-distill](https://huggingface.co/opensearch-project/opensearch-neural-sparse-encoding-doc-v3-distill) | 0.517 | 0.724      | 0.345    | 0.544 | 0.694    | 0.356 | 0.52    | 0.294  | 0.424   | 0.163   | 0.845 | 0.239        | 0.708   | 0.863 |
| [doc-v3-gte](https://huggingface.co/opensearch-project/opensearch-neural-sparse-encoding-doc-v3-gte)         | 0.546 | 0.734      | 0.36     | 0.582 | 0.716    | 0.407 | 0.52    | 0.389  | 0.455   | 0.167   | 0.86  | 0.312        | 0.725   | 0.873 |

## 多言語スパース検索

**multilingual-v1** のリリースもお知らせします。これは OpenSearch 初の多言語ニューラルスパース検索モデルです。英語版 v2 シリーズと同じ実績あるトレーニング技術を使用し、multilingual-v1 は英語モデルと同等の効率性を維持しながら、多言語ベンチマークで高い精度を達成し、幅広い言語に高品質なスパース検索を提供します。

以下の表は、BM25 と比較した **multilingual-v1** の各言語における詳細な検索精度評価を示しています。結果は MIRACL ベンチマークを使用して報告されています。**multilingual-v1** はすべての言語で BM25 を大幅に上回り、ニューラルスパース検索技術を英語以外の言語に適用する効果を実証しています。また、プルーニング版の multilingual-v1 (プルーニング比率 0.1) の結果も示しており、インデックスサイズを削減しながら競争力のある精度を維持しています。

| モデル                                                                                                                          | 平均  | bn    | te    | es    | fr    | id    | hi    | ru    | ar    | zh    | fa    | ja    | fi    | sw    | ko    | en    |
| ------------------------------------------------------------------------------------------------------------------------------- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| BM25                                                                                                                            | 0.305 | 0.482 | 0.383 | 0.077 | 0.115 | 0.297 | 0.35  | 0.256 | 0.395 | 0.175 | 0.287 | 0.312 | 0.458 | 0.351 | 0.371 | 0.267 |
| [multilingual-v1](https://huggingface.co/opensearch-project/opensearch-neural-sparse-encoding-multilingual-v1)                  | 0.629 | 0.67  | 0.74  | 0.542 | 0.558 | 0.582 | 0.486 | 0.658 | 0.74  | 0.562 | 0.514 | 0.669 | 0.767 | 0.768 | 0.607 | 0.575 |
| [multilingual-v1; prune_ratio 0.1](https://huggingface.co/opensearch-project/opensearch-neural-sparse-encoding-multilingual-v1) | 0.626 | 0.667 | 0.74  | 0.537 | 0.555 | 0.576 | 0.481 | 0.655 | 0.737 | 0.558 | 0.511 | 0.664 | 0.761 | 0.766 | 0.604 | 0.572 |

## 関連記事

ニューラルスパース検索の詳細については、以下の過去のブログ記事をご覧ください。

- [Neural sparse models are now available in Hugging Face Sentence Transformers](https://opensearch.org/blog/neural-sparse-models-are-now-available-in-hugging-face-sentence-transformers/)
- [Improving search efficiency and accuracy with the newest v2 neural sparse models](https://opensearch.org/blog/neural-sparse-v2-models/)
- [Improving document retrieval with sparse semantic encoders](https://opensearch.org/blog/improving-document-retrieval-with-sparse-semantic-encoders)
- [A deep dive into faster semantic sparse retrieval in OpenSearch 2.12](https://opensearch.org/blog/A-deep-dive-into-faster-semantic-sparse-retrieval-in-OS-2.12)
- [Introducing the neural sparse two-phase algorithm](https://opensearch.org/blog/Introducing-a-neural-sparse-two-phase-algorithm)

## 次のステップ

最新の v3 ニューラルスパースモデルを OpenSearch クラスターで試して、[OpenSearch フォーラム](https://forum.opensearch.org/)で体験を共有してください。皆様のフィードバックは、将来のバージョンの改善に役立ちます。
