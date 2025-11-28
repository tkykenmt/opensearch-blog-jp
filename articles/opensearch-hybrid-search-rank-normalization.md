---
title: "[翻訳] ハイブリッド検索におけるランク正規化の仕組み"
emoji: "📊"
type: "tech"
topics: ["opensearch", "hybridsearch", "machinelearning", "search", "algorithm"]
published: true
publication_name: "opensearch"
published_at: 2024-09-19
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/how-does-the-rank-normalization-work-in-hybrid-search/

今日のデジタル時代において、検索エンジンは関連情報を迅速かつ効率的に提供する上で重要な役割を果たしています。検索結果を向上させるために検索エンジンが採用する高度な手法の 1 つがハイブリッド検索です。これは複数の検索アルゴリズムを組み合わせて情報を取得しランク付けする方法です。ハイブリッド検索は異なるアルゴリズムの強みを活用しますが、新たな課題も生じます。それは、これらの多様なソースからのスコアをどのように公平に比較し組み合わせるかという問題です。ここでランク正規化が重要になります。

ランク正規化はハイブリッド検索システムにおいて不可欠です。様々なサブクエリからのスコアを共通のスケールに調整し、正確で意味のある比較を可能にするためです。正規化がなければ、最終的なランキングが歪み、ユーザー満足度に影響を与える最適でない検索結果につながる可能性があります。

OpenSearch はランク正規化に 2 つの主要な手法を採用しています。L2 正規化と min-max 正規化です。これらの手法は異なるサブクエリからのスコアを標準化し、最も関連性の高い結果が適切にランク付けされることを保証します。

本記事では、これらの正規化手法の詳細を解説し、OpenSearch での実装を探り、その適用を示す実践的な例を提供します。検索エンジンを最適化したい開発者の方も、ハイブリッド検索の内部動作に興味がある方も、このガイドで OpenSearch におけるランク正規化を包括的に理解できるでしょう。

## 1. ランク正規化の理解

ランク正規化とは、異なる検索アルゴリズムによって生成されたスコアを共通のスケールに調整するプロセスです。ハイブリッド検索システムでは、複数のサブクエリが実行され、それぞれが異なるスコアリングメカニズムと範囲を使用する可能性があります。ランク正規化により、これらの異なるスコアが比較可能になり、結果の正確で公平な集約が可能になります。主な目的は、単一のスコアリング方法が最終ランキングに不釣り合いな影響を与えることを防ぎ、関連性のバランスの取れた見方を提供することです。

### ランク正規化とハイブリッド検索の統合

ハイブリッド検索は、キーワードベース検索、ベクトル検索、パーソナライズされたレコメンデーションなど、様々な検索技術の強みを組み合わせます。これらの技術はそれぞれ、異なる基準とスケールに基づいてスコアを生成する場合があります。例えば、キーワードベース検索は用語頻度に基づいてドキュメントをスコアリングし、ベクトル検索は意味的類似性に基づいてスコアリングする可能性があります。正規化なしでこれらのスコアを直接組み合わせると、1 つのスコアリング方法が他を圧倒する可能性があるため、誤解を招く結果につながる可能性があります。ランク正規化はこれらのスコアを標準化することでハイブリッド検索に統合され、各サブクエリの貢献が適切に重み付けされることを保証します。

### 検索システムにランク正規化を適用するメリット

1. **精度の向上**: 異なるサブクエリからのスコアが比較可能であることを保証することで、ランク正規化は最も関連性の高い結果を正確に特定するのに役立ちます。
2. **公平性**: ランク正規化は、単一のスコアリング方法が最終検索結果を支配することを防ぎます。
3. **ユーザー体験の向上**: より正確で公平な検索結果のランキングは、より良いユーザー体験に直接つながります。
4. **柔軟性**: ランク正規化により、開発者はスコアリングスケールの非互換性を心配することなく、複数の検索アルゴリズムを実験し統合できます。
5. **スケーラビリティ**: 検索システムが成長し、より多くのデータソースと検索方法を組み込むにつれて、ランク正規化はシステムが堅牢で効果的であり続けることを保証します。

## 2. L2 正規化手法

L2 正規化 (ユークリッド正規化とも呼ばれる) は、すべてのスコアのベクトルのユークリッド距離に関連してスコアをスケーリングすることで調整する方法です。この手法はスコアの大きさを正規化し、異なるスコアを比較するための一貫したスケールを提供します。

### 数学的公式

L2 正規化の公式は、各スコア ($$ \text{score}_i $$) をすべてのスコアの二乗和の平方根で割ることで調整します。

$$
\text{n\_score}_i = \frac {\text{score}_i} {\sqrt{\text{score}_1^2 + \text{score}_2^2 + \dots + \text{score}_n^2}}
$$

### アルゴリズムの手順

1. **すべてのスコアの二乗和を計算**: 各サブクエリの結果を反復処理し、すべてのスコアの二乗和を計算します。
2. **L2 正規化公式を使用して各スコアを更新**: 各スコアについて、前のステップで計算した二乗和の平方根で割ります。

### コードの解説

#### `normalize` メソッドの説明

`normalize` メソッドは正規化プロセスを調整します。まず `getL2Norm` メソッドを使用して各サブクエリの L2 ノルムを計算し、次に各結果を反復処理して `normalizeSingleScore` メソッドを使用してスコアを更新します。

```java
@Override
public void normalize(final List<CompoundTopDocs> queryTopDocs) {
    // 各サブクエリの L2 ノルムを取得
    List<Float> normsPerSubquery = getL2Norm(queryTopDocs);

    // 実際のスコアと L2 ノルムを使用して正規化を実行
    for (CompoundTopDocs compoundQueryTopDocs : queryTopDocs) {
        if (Objects.isNull(compoundQueryTopDocs)) {
            continue;
        }
        List<TopDocs> topDocsPerSubQuery = compoundQueryTopDocs.getTopDocs();
        for (int j = 0; j < topDocsPerSubQuery.size(); j++) {
            TopDocs subQueryTopDoc = topDocsPerSubQuery.get(j);
            for (ScoreDoc scoreDoc : subQueryTopDoc.scoreDocs) {
                scoreDoc.score = normalizeSingleScore(scoreDoc.score, normsPerSubquery.get(j));
            }
        }
    }
}
```

#### `normalizeSingleScore` メソッドの説明

`normalizeSingleScore` メソッドは単一のスコアに L2 正規化公式を適用します。L2 ノルムがゼロの場合、ゼロ除算を避けるために正規化スコアを最小スコアに設定します。

```java
private float normalizeSingleScore(final float score, final float l2Norm) {
    return l2Norm == 0 ? MIN_SCORE : score / l2Norm;
}
```

### L2 正規化の適用例

キーワードベース検索とベクトルベース検索を組み合わせたハイブリッド検索システムを考えます。以下の生スコアがあるとします。

- **キーワードベース検索スコア**: $[3.0, 4.0, 2.0]$
- **ベクトルベース検索スコア**: $[1.5, 3.5, 2.5]$

**L2 正規化の適用**:

1. **二乗和を計算**:
   - キーワードベース: $3.0^2 + 4.0^2 + 2.0^2 = 29$
   - ベクトルベース: $1.5^2 + 3.5^2 + 2.5^2 = 20.75$

2. **L2 ノルムを計算**:
   - キーワードベース: $\sqrt{29} \approx 5.39$
   - ベクトルベース: $\sqrt{20.75} \approx 4.55$

3. **スコアを正規化**:
   - キーワードベース: $[0.56, 0.74, 0.37]$
   - ベクトルベース: $[0.33, 0.77, 0.55]$

## 3. Min-max 正規化手法

Min-max 正規化は、スコアを指定された範囲 (通常は 0 から 1) に収まるようにスケーリングする方法です。この手法はデータセット内の最小値と最大値に基づいてスコアを調整し、最低スコアが 0 に、最高スコアが 1 にマッピングされることを保証します。

### 数学的公式

Min-max 正規化の公式は、各スコア ($\text{score}$) から最小スコアを引き、範囲 (最大スコアから最小スコアを引いた値) で割ることで調整します。

$$
\text{n\_score} = \frac {\text{score} - \text{min\_score}} {\text{max\_score} - \text{min\_score}}
$$

### アルゴリズムの手順

1. **各サブクエリの最小スコアと最大スコアを計算**: 各サブクエリの結果を反復処理して最小スコアと最大スコアを見つけます。
2. **min-max 正規化公式を使用して各スコアを更新**: 各スコアについて、最小スコアを引き、最大スコアと最小スコアの差で割ります。

### `normalizeSingleScore` メソッドの説明

`normalizeSingleScore` メソッドは単一のスコアに min-max 正規化公式を適用します。最小スコアと最大スコアが同じ場合、ゼロ除算を避けるために正規化スコアを事前定義された値に設定します。最小スコアのドキュメントには、0.001 に等しい MIN_SCORE の事前定義された定数が返されます。

```java
private float normalizeSingleScore(final float score, final float minScore, final float maxScore) {
    if (Floats.compare(maxScore, minScore) == 0 && Floats.compare(maxScore, score) == 0) {
        return SINGLE_RESULT_SCORE;
    }
    float normalizedScore = (score - minScore) / (maxScore - minScore);
    return normalizedScore == 0.0f ? MIN_SCORE : normalizedScore;
}
```

### Min-max 正規化の適用例

- **キーワードベース検索スコア**: $[2.0, 5.0, 3.0]$
- **ベクトルベース検索スコア**: $[1.0, 4.0, 2.0]$

**Min-max 正規化の適用**:

1. **最小スコアと最大スコアを計算**:
   - キーワードベース: Min = $2.0$, Max = $5.0$
   - ベクトルベース: Min = $1.0$, Max = $4.0$

2. **スコアを正規化**:
   - キーワードベース: $[0.001, 1.0, 0.33]$
   - ベクトルベース: $[0.001, 1.0, 0.33]$

## 4. L2 正規化と Min-max 正規化の比較

### L2 正規化のメリット

- **滑らかな調整**: L2 正規化は全体的な分布に基づいてスコアを滑らかに調整し、単一のスコアが結果に不釣り合いな影響を与えないことを保証します。
- **大きさの保持**: すべてのスコアの大きさを考慮することで、データセット全体のコンテキストにおける各スコアの相対的な重要性を効果的に保持します。
- **外れ値の処理**: L2 正規化は外れ値の影響を軽減できます。極端な値は min-max 正規化と比較して最終的な正規化スコアへの影響が少ないためです。

### Min-max 正規化のメリット

- **シンプルな解釈**: Min-max 正規化はスコアを固定範囲 (通常 0 から 1) にスケーリングするため、スコアを直接解釈し比較することが容易です。
- **均一なスケール**: この方法はすべてのスコアが同じスケール内に収まることを保証します。
- **極端な値の強調**: Min-max 正規化は最小値と最大値の重要性を強調します。

### 各手法を使用するタイミング

- **L2 正規化**: データセット全体のコンテキスト内で各スコアの相対的な重要性を維持することが目標であり、外れ値の存在を最小化する必要がある場合に適しています。
- **Min-max 正規化**: スコアにシンプルで固定された範囲が必要なアプリケーションや、極端な値を強調する必要がある場合に最適です。

## 5. OpenSearch での実装

OpenSearch は検索パイプラインを通じて正規化手法を実装し、検索結果を処理して異なるサブクエリからのスコアを標準化します。

### OpenSearch 環境での設定と使用方法

1. **検索パイプラインを定義**: 正規化プロセッサを持つ検索パイプラインを作成し、正規化手法を指定します。

```json
PUT /_search/pipeline/nlp-search-pipeline
{
  "description": "Post processor for hybrid search",
  "phase_results_processors": [
    {
      "normalization-processor": {
        "normalization": {
          "technique": "min_max"
        },
        "combination": {
          "technique": "arithmetic_mean",
          "parameters": {
            "weights": [0.3, 0.7]
          }
        }
      }
    }
  ]
}
```

2. **検索パイプラインを使用**: 検索リクエストで検索パイプラインを使用して、検索結果に正規化と組み合わせ手法を適用します。

```json
GET /my-nlp-index/_search?search_pipeline=nlp-search-pipeline
{
  "_source": {
    "exclude": ["passage_embedding"]
  },
  "query": {
    "hybrid": {
      "queries": [
        {
          "match": {
            "text": {
              "query": "horse"
            }
          }
        },
        {
          "neural": {
            "passage_embedding": {
              "query_text": "wild west",
              "model_id": "aVeif4oB5Vm0Tdw8zYO2",
              "k": 5
            }
          }
        }
      ]
    }
  }
}
```

### 開発者向けの実践的なヒント

1. **適切な手法を選択**: データとクエリの性質を評価して、最も適切な正規化手法を選択します。
2. **テストとチューニング**: 正規化された検索結果が関連性とランキング基準を満たしていることを継続的にテストします。
3. **パフォーマンスを監視**: 特に高トラフィック環境では、正規化のパフォーマンスへの影響を追跡します。
4. **エッジケースを処理**: 同一スコアなどのエッジケースに備え、正規化ロジックがこれらのシナリオを結果を歪めることなく処理することを確認します。
5. **ドキュメントを活用**: 正規化手法の実装と最適化に関する追加のガイダンスについては、OpenSearch のドキュメントとコミュニティリソースを活用してください。

詳細については、[OpenSearch の正規化プロセッサに関するドキュメント](https://opensearch.org/docs/latest/search-plugins/search-pipelines/normalization-processor/)を参照してください。

## まとめ

ランク正規化はハイブリッド検索システムにおいて重要であり、異なるアルゴリズムからのスコアが比較可能であることを保証し、正確で公平な検索結果をもたらします。L2 正規化や min-max 正規化などの手法を使用することで、OpenSearch はスコアを効果的に標準化するツールを提供します。これらの方法を試すことで、特定の検索ニーズに最適なものを特定し、関連性とユーザー満足度を最適化できます。

## 参考資料

ハイブリッド検索、正規化プロセッサ、実装の詳細については、以下のリソースを参照してください。

- [Hybrid search](https://opensearch.org/docs/latest/search-plugins/hybrid-search/)
- [Normalization processor](https://opensearch.org/docs/latest/search-plugins/search-pipelines/normalization-processor/)
- [OpenSearch neural-search GitHub repository](https://github.com/opensearch-project/neural-search/tree/main/src/main/java/org/opensearch/neuralsearch/processor/normalization)
