---
title: "[翻訳] OpenSearch のセマンティックハイライト機能の紹介"
emoji: "🔍"
type: "tech"
topics: ["opensearch", "semantic", "highlighting", "search"]
published: true
published_at: 2025-07-17
publication_name: "opensearch"
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/introducing-semantic-highlighting-in-opensearch/

OpenSearch 3.0 では、[セマンティックハイライト](https://docs.opensearch.org/docs/latest/search-plugins/searching-data/highlight/#the-semantic-highlighter) という AI を活用した新機能が導入されました。この機能は、検索結果のドキュメント内から最も関連性の高い箇所を特定して返します。本記事では、この AI モデルの仕組みを解説し、検索クエリにセマンティックハイライトを組み込む方法を紹介します。

## セマンティックハイライトとは

ハイライトとは、ドキュメント内でクエリに最も関連する部分を抽出する検索機能です。セマンティックハイライトは、OpenSearch に新しいハイライターを導入し、既存のものとは 2 つの点で異なる動作をします。1 つ目は、クエリとテキスト間のセマンティック (意味的) な類似性に基づいて関連性を測定する点です。2 つ目は、キーワードの完全一致ではなく、テキストの範囲 (スパン) をハイライトする点です。AI モデルが各文を評価し、クエリと周囲のテキストの両方のコンテキストを使用して関連性を判断します。

この機能は、ユーザーが正確な単語よりもクエリの意味を重視する AI 検索のユースケース向けに設計されています。セマンティックハイライトは、ドキュメント内で最も意味のある箇所を表示することで、この考え方を拡張しています。

## セマンティックハイライトと字句ハイライトの違い

OpenSearch の字句 (レキシカル) ハイライターは、ユーザーが正確な単語やフレーズをハイライトしたい場合に効果的です。クエリ用語との直接的な一致に基づいてテキストを素早く特定します。一方、セマンティックハイライトは、表現が異なっていても、クエリと概念的に関連する箇所に関心がある場合に有用です。正確な一致ではなく意味に焦点を当てることで、字句ハイライトを補完します。

## セマンティックハイライトと字句ハイライトの比較例

セマンティックハイライトと字句ハイライトの違いを示すために、[WikiSum データセット](https://registry.opendata.aws/wikisum/) のハウツーガイドを使った例を見てみましょう。このデータセットでは、`summary` フィールドに段落形式の手順が含まれています。`summary` フィールドを「how long to cook pasta sauce」(パスタソースの調理時間) というクエリで検索した場合、各方式で上位の結果がどのようにハイライトされるかを以下に示します。

**字句ハイライター**

> To make a red **pasta** sauce, start by adding water, tomato paste, and diced tomatoes to a large saucepan. Then, sprinkle in some finely-grated carrots, diced onions, chopped garlic, and some spices like celery salt, dried oregano, and dried basil. Next, bring everything to a boil over medium heat before reducing the temperature to low. Finally, cover the pot and simmer the sauce for 15-30 minutes.

**セマンティックハイライター**

> To make a red pasta sauce, start by adding water, tomato paste, and diced tomatoes to a large saucepan. Then, sprinkle in some finely-grated carrots, diced onions, chopped garlic, and some spices like celery salt, dried oregano, and dried basil. Next, bring everything to a boil over medium heat before reducing the temperature to low. **Finally, cover the pot and simmer the sauce for 15-30 minutes.**

この例では、字句ハイライターは直接的な単語の一致 (「pasta」) を見つけますが、実際にクエリに答える文を見逃しています。一方、セマンティックハイライターは質問の意図に対応する回答を正しく特定しています。

## セマンティックハイライトの活用シーン

セマンティックハイライトは、さまざまなシナリオで活用できます。以下にいくつかの例を示します。

1. **法務文書検索**: 用語が異なる場合でも、長い契約書や法的文書内の関連する条項やセクションを効率的に特定できます。
2. **カスタマーサポート**: ナレッジベースの記事やサポートチケット内で、顧客の問題に対処する最も関連性の高い文をハイライトすることで、カスタマーエージェントの効率とセルフサービスポータルを改善できます。
3. **EC サイトの商品検索**: 商品の特徴や利点に関するユーザーの自然言語クエリと意味的に一致する、商品説明やカスタマーレビュー内の文をハイライトすることで、商品の発見性を向上させます。

## セマンティックハイライトの使い方

OpenSearch でセマンティックハイライトを使用するには、以下の手順に従います。

- **モデルのデプロイ**: セマンティック文ハイライトモデルを OpenSearch クラスターにデプロイします。
- **検索でセマンティックハイライトを有効化**: 検索を実行し、`highlight` オブジェクトに `model_id` を指定して、結果にセマンティックハイライトを適用します。

### ステップ 1: セマンティックハイライトモデルのデプロイ

まず、セマンティックハイライトモデルをデプロイします。

**オプション A: ローカルデプロイ (簡単なセットアップ)**

素早いセットアップとテストのために、OpenSearch クラスター内に直接モデルをデプロイできます。

```json
POST /_plugins/_ml/models/_register?deploy=true
{
    "name": "amazon/sentence-highlighting/opensearch-semantic-highlighter-v1",
    "version": "1.0.0",
    "model_format": "TORCH_SCRIPT",
    "function_name": "QUESTION_ANSWERING"
}
```

この方法は簡単ですが、クラスターの CPU リソース上で実行されるため、高負荷のワークロードではパフォーマンスに影響を与える可能性があります。

**オプション B: 外部デプロイ (本番環境推奨)**

高いパフォーマンスが求められる本番ワークロードでは、Amazon SageMaker などの GPU アクセラレーション対応のリモートエンドポイントにモデルをデプロイすることを推奨します。ベンチマークによると、GPU ベースのデプロイはローカル CPU デプロイと比較して約 4.5 倍高速です。詳細なセットアップ手順については、[ブループリント](https://github.com/opensearch-project/ml-commons/blob/main/docs/remote_inference_blueprints/standard_blueprints/sagemaker_semantic_highlighter_standard_blueprint.md) を参照してください。

### ステップ 2: 検索でセマンティックハイライトを有効化

モデルがデプロイされたら (ローカルまたは外部)、ハイライトしたいフィールドの `highlight` オブジェクトで `type` を `semantic` に設定してセマンティックハイライトを有効にします。

以下の例 ([チュートリアル](https://docs.opensearch.org/docs/latest/tutorials/vector-search/semantic-highlighting-tutorial/) より) は、ニューラル検索クエリでセマンティックハイライトを使用する方法を示しています。このクエリは、`neural-search-index` という名前のインデックスで「treatments for neurodegenerative diseases」(神経変性疾患の治療法) を検索します。インデックス内のドキュメントには、ベクトル埋め込みを含む `text_embedding` フィールドと、元のドキュメントコンテンツを含む `text` フィールドがあります。

```json
POST /neural-search-index/_search
{
  "_source": {
    "excludes": ["text_embedding"]
  },
  "query": {
    "neural": {
      "text_embedding": {
        "query_text": "treatments for neurodegenerative diseases",
        "model_id": "<your-text-embedding-model-id>",
        "k": 1
      }
    }
  },
  "highlight": {
    "fields": {
      "text": {
        "type": "semantic"
      }
    },
    "options": {
      "model_id": "<your-semantic-highlighting-model-id>"
    }
  }
}
```

このクエリには以下のオブジェクトが含まれています。

- `neural` オブジェクトは、デプロイしたテキスト埋め込みモデルを使用してセマンティック検索を実行します。
- `highlight` オブジェクトは、デプロイしたセマンティックハイライトモデルを使用して text フィールドにセマンティックハイライトを適用します。
- `_source` フィルターは、結果を簡潔に保つために `text_embedding` フィールドをレスポンスから除外します。

検索結果の例を以下に示します。この例は簡潔にするために短縮されており、使用するモデルによってハイライトされる文は異なる場合があります。

```json
{
  "took": 38,
  "timed_out": false,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": {
      "value": 1,
      "relation": "eq"
    },
    "max_score": 0.52716815,
    "hits": [
      {
        "_index": "neural-search-index",
        "_id": "1",
        "_score": 0.52716815,
        "_source": {
          "text": "Alzheimer's disease is a progressive neurodegenerative disorder ..."
        },
        "highlight": {
          "text": [
            "Alzheimer's disease is a progressive neurodegenerative disorder characterized by accumulation of amyloid-beta plaques and neurofibrillary tangles in the brain. Early symptoms include short-term memory impairment, followed by language difficulties, disorientation, and behavioral changes. While traditional treatments such as cholinesterase inhibitors and memantine provide modest symptomatic relief, they do not alter disease progression. <em>Recent clinical trials investigating monoclonal antibodies targeting amyloid-beta, including aducanumab, lecanemab, and donanemab, have shown promise in reducing plaque burden and slowing cognitive decline.</em> Early diagnosis using biomarkers such as cerebrospinal fluid analysis and PET imaging may facilitate timely intervention and improved outcomes."
          ]
        }
      }
    ]
  }
}
```

`semantic` ハイライターは、各検索結果ドキュメントのコンテキスト内で、モデルがクエリに最も意味的に関連すると判断した文を特定します。デフォルトでは、ハイライトされた文は `<em>` タグで囲まれます。

## サポートされるクエリ

セマンティックハイライトは、さまざまな検索戦略に対応する柔軟性を備えています。以下のクエリタイプで動作します。

- **Match クエリ**: 標準的なテキストクエリ
- **Term クエリ**: 正確な用語のマッチング
- **Boolean クエリ**: クエリの論理的な組み合わせ
- **Query string クエリ**: 高度なクエリ構文
- **Neural クエリ**: ベクトルベースのセマンティック検索
- **Hybrid クエリ**: 従来の検索とニューラル検索の組み合わせ

## セマンティックハイライトモデル

セマンティックハイライトは、学習済み AI モデルを使用して、検索結果ドキュメント内でハイライトクエリに関連する箇所を自動的に検出します。具体的には、このモデルは抽出型質問応答のための多様なパブリックドメインデータセットで学習された文レベルの分類器です。文レベルでハイライトすることで、結果が意味的に意味のあるものとなり、統一された予測フレームワークを維持しながら多様なデータソースでモデルを学習できます。

このモデルは、[BERT (Bidirectional Encoder Representations from Transformers)](https://huggingface.co/docs/transformers/en/model_doc/bert) に基づくトランスフォーマーベースのアーキテクチャを採用しています。ドキュメントとクエリテキストの両方を同時にエンコードし、ドキュメント内の周囲のテキストとクエリ自体の両方からコンテキストを組み込んだ各文の表現を生成します。多様なデータソースでモデルを学習し、幅広いドメインやユースケースに適用できるハイライトルールを学習するよう促しています。モデルのパフォーマンスは、主に _分布外_ データでのハイライトの精度と再現率の観点で評価し、標準的な学習コーパスを超えて堅牢なパフォーマンスを持つハイライトモデルを選択することを目標としています。

## パフォーマンスベンチマーク

[MultiSpanQA データセット](https://multi-span.github.io/) を使用して、セマンティックハイライトのレイテンシと精度を評価しました。テスト環境は以下のように構成されています。

| **OpenSearch クラスター**          | `opensearch-cluster-cdk` を使用してデプロイしたバージョン 3.1.0                                                                                                   |
| ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **データノード**                   | 3 × r6g.2xlarge (各 8 vCPU、64 GB メモリ)                                                                                                                         |
| **コーディネーターノード**         | 3 × c6g.xlarge (各 4 vCPU、8 GB メモリ)                                                                                                                           |
| **セマンティックハイライトモデル** | GPU ベースの ml.g5.xlarge (1〜3 インスタンスでスケーラブル) を使用した Amazon SageMaker エンドポイントにリモートデプロイした `opensearch-semantic-highlighter-v1` |
| **埋め込みモデル**                 | OpenSearch クラスター内にデプロイした `sentence-transformers/all-MiniLM-L6-v2`                                                                                    |
| **ベンチマーククライアント**       | ARM64、16 コア、61 GB RAM                                                                                                                                         |
| **テスト構成**                     | 10 回のウォームアップ、50 回のテスト、1 シャード、0 レプリカ                                                                                                      |
| **データセット**                   | MultiSpanQA (1,959 ドキュメント)                                                                                                                                  |
| **ドキュメント統計**               | 平均: 1,213 文字、P50: 1,111、P90: 2,050、最大: 6,689                                                                                                             |
| **関連文**                         | 1,541 (全体の 9.51%)                                                                                                                                              |

**注**: このベンチマークでは、セマンティックハイライトモデルに Amazon SageMaker の ml.g5.xlarge GPU インスタンスを使用し、ローカルにデプロイした OpenSearch 機械学習モデルと比較して大幅なパフォーマンス向上を実現しました。GPU アクセラレーションにより、P50 レイテンシが約 4.5 倍削減されました (k=1 の場合、180ms から 40ms に短縮)。オートスケーリング構成 (1〜3 インスタンス) により、一貫したパフォーマンスを維持しながら、変動するワークロード需要に対応できます。Amazon SageMaker へのモデルデプロイについては、[ドキュメントとスクリプト](https://github.com/opensearch-project/opensearch-py-ml/tree/main/docs/source/examples/aws_sagemaker_sentence_highlighter_model) を参照してください。

### レイテンシ

検索クライアント数と取得ドキュメント数 (k 値) の範囲で、セマンティックハイライト付きセマンティック検索のレイテンシを測定しました。比較のため、ハイライトなしのセマンティック検索のレイテンシも含めています。結果を以下の表に示します。

| k 値 | 検索クライアント数 | セマンティック検索のみ P50 レイテンシ (ms) | セマンティックハイライト付き P50 レイテンシ (ms) | セマンティック検索のみ P90 レイテンシ (ms) | セマンティックハイライト付き P90 レイテンシ (ms) | セマンティック検索のみ P100 レイテンシ (ms) | セマンティックハイライト付き P100 レイテンシ (ms) |
| ---- | ------------------ | ------------------------------------------ | ------------------------------------------------ | ------------------------------------------ | ------------------------------------------------ | ------------------------------------------- | ------------------------------------------------- |
| 1    | 1                  | 21                                         | 38                                               | 23                                         | 42                                               | 24                                          | 59                                                |
| 1    | 4                  | 24                                         | 37                                               | 25                                         | 45                                               | 27                                          | 78                                                |
| 1    | 8                  | 24                                         | 40                                               | 26                                         | 52                                               | 28                                          | 81                                                |
| 10   | 1                  | 26                                         | 180                                              | 27                                         | 199                                              | 28                                          | 237                                               |
| 10   | 4                  | 25                                         | 209                                              | 27                                         | 240                                              | 29                                          | 312                                               |
| 10   | 8                  | 26                                         | 267                                              | 28                                         | 323                                              | 31                                          | 407                                               |
| 20   | 1                  | 24                                         | 348                                              | 25                                         | 383                                              | 25                                          | 410                                               |
| 20   | 4                  | 24                                         | 401                                              | 28                                         | 449                                              | 30                                          | 530                                               |
| 20   | 8                  | 26                                         | 545                                              | 28                                         | 625                                              | 32                                          | 770                                               |
| 50   | 1                  | 24                                         | 806                                              | 25                                         | 861                                              | 26                                          | 954                                               |
| 50   | 4                  | 25                                         | 987                                              | 26                                         | 1,074                                            | 29                                          | 1,162                                             |
| 50   | 8                  | 26                                         | 1,358                                            | 28                                         | 1,490                                            | 32                                          | 1,687                                             |

包括的なベンチマークにより、この機能は一般的な検索シナリオ (k≤10) で良好に動作し、インタラクティブなアプリケーションの要件を満たす 200ms 未満のレスポンスを提供することが実証されました。レイテンシは返されるドキュメント数に応じて増加し、セマンティックハイライトモデルの推論にかかる追加コストを反映しています。

### 精度

MultiSpanQA 検証セットで文レベルのハイライトの精度、再現率、F1 スコアを計算して、ハイライターの精度を測定しました。結果を以下の表に示します。

| 指標                 | 値     | 説明                                                 |
| -------------------- | ------ | ---------------------------------------------------- |
| **精度 (Precision)** | 66.40% | ハイライトされた文のうち、実際に関連性のある文の割合 |
| **再現率 (Recall)**  | 79.20% | 関連性のある文のうち、正しくハイライトされた文の割合 |
| **F1 スコア**        | 72.20% | 精度と再現率のバランスを取った調和平均               |

ハイライターは、堅牢な精度 (66.4%) を維持しながら高い再現率 (79.2%) を示し、72.2% の堅実な F1 スコアを達成しました。このパフォーマンス特性は、誤検出を管理可能な範囲に抑えながら最も関連性の高いコンテンツを捕捉することが重要な検索アプリケーションに適しています。

実際には、ハイライターの精度はデータによって異なる場合があります。多くのドメインで高いパフォーマンスを発揮するよう、多様なデータセットでハイライトモデルを学習しましたが、データがこの学習セットと大きく異なる場合、精度が低下する可能性があります。

## 高度なカスタマイズ

事前学習済みモデル `semantic-sentence-highlighter-model-v1` (チュートリアルでは `amazon/sentence-highlighting/opensearch-semantic-highlighter-v1` として参照され、Hugging Face では [`opensearch-project/opensearch-semantic-highlighter-v1`](https://huggingface.co/opensearch-project/opensearch-semantic-highlighter-v1) として公開) は優れた汎用パフォーマンスを提供しますが、OpenSearch は上級ユーザー向けの柔軟性も備えています。

OpenSearch のセマンティックハイライト機能は、OpenSearch ML Commons プラグインにデプロイされたさまざまな文ハイライトモデルで動作するよう設計されています。特定のドメインやタスクがある場合、ML Commons フレームワークと互換性のある独自の文ハイライトモデルを学習してデプロイできます。

カスタムモデルの準備 (モデルのトレースや関連する CI プロセスを含む) の詳細に興味がある場合は、[`opensearch-py-ml` GitHub リポジトリ](https://github.com/opensearch-project/opensearch-py-ml/tree/main) を参照してください。このリポジトリには、独自のモデルを OpenSearch に導入するためのツールと例が用意されています。カスタムモデルの準備とデプロイが完了したら、ハイライトオプションでカスタム `model_id` を参照できます。

## 今後の展望

OpenSearch のセマンティックハイライトは、検索結果の表示における大きな進歩を表しています。キーワードの一致だけでなく、セマンティックな関連性に基づいてコンテンツをハイライトすることで、より意味のある、コンテキストを考慮した検索結果を提供します。

商品カタログ、研究論文、法務文書、その他のテキストベースのコンテンツを検索する場合でも、この機能はユーザー体験を向上させます。ぜひセマンティックハイライトをお試しいただき、OpenSearch コミュニティにフィードバックをお寄せください。

セマンティックハイライト機能について、いくつかの改善を検討しています。

- **バッチサポート**: バッチ処理により、特に複数のヒットをハイライトする際のレイテンシを削減できます。
- **カスタムハイライトフレーズ**: 複雑なクエリからの自動抽出に頼るのではなく、ハイライトする正確な文を指定できる機能により、ハイライトの表示方法をより細かく制御できます。
- **グローバルモデル設定**: モデル ID をグローバルに設定する方法を提供することで、各クエリ句でモデル ID を指定する必要がなくなります。

これらの機能についてコミュニティからのフィードバックを歓迎します。GitHub ディスカッションや [OpenSearch フォーラム](https://forum.opensearch.org/) で、ユースケースや要件をぜひ共有してください。
