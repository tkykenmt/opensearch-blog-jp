---
title: "[翻訳] system-generated search pipeline で検索をよりスマートに"
emoji: "🔍"
type: "tech"
topics: ["opensearch", "pipeline", "search", "ai"]
published: true
published_at: 2025-11-06
publication_name: "opensearch"
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/making-search-smarter-with-system-generated-search-pipelines/

OpenSearch 3.3 では、プラグイン開発者向けの新機能として **system-generated search pipeline** が導入されました。この機能により、OpenSearch はリクエストのコンテキストとパラメータに基づいて、実行時に system-generated processor を自動的に生成し、アタッチできるようになります。

この機能を使用すると、検索時の処理ロジックをプラグインに直接組み込むことができます。検索パイプラインを手動で作成・設定する必要がなく、統合が簡素化され、すぐに使える、よりスマートな検索体験を実現できます。

従来、カスタム検索プロセッサを構築する際には、プロセッサを含む検索パイプラインを明示的に設定し、クエリでそれを参照する必要がありました。system-generated search pipeline を使用すると、OpenSearch がこれらのプロセッサを自動的に生成・管理するため、手動設定が不要になり、ユーザー定義パイプラインとの完全な互換性も維持されます。

## system-generated search pipeline と標準検索パイプラインの比較

OpenSearch では、標準検索パイプラインは [Search Pipeline API](https://docs.opensearch.org/latest/search-plugins/search-pipelines/index/) を使用して定義します。これらのパイプラインは手動で設定し、検索リクエストで参照する必要があります。

system-generated search pipeline も同様に動作します。検索リクエストのライフサイクル中に 1 つ以上のプロセッサを実行しますが、手動で設定する必要はありません。代わりに、OpenSearch がプラグインに登録された system-generated processor factory と受信リクエストの詳細に基づいて、クエリ時にパイプラインを自動生成します。

以下の表に、OpenSearch における標準検索パイプラインと system-generated search pipeline の主な違いをまとめます。

| パイプラインタイプ | 定義方法 | トリガー方法 | 無効化方法 |
|---|---|---|---|
| **標準検索パイプライン** | Search Pipeline API を使用して手動で定義 | 検索リクエストで名前で参照するか、クラスタ設定でデフォルト検索パイプラインとして設定 | 検索リクエストからパイプライン参照を削除するか、デフォルトパイプライン設定をクリア |
| **system-generated search pipeline** | リクエスト評価とプラグイン登録されたプロセッサファクトリに基づいて OpenSearch が自動生成 | 検索リクエストが system-generated processor factory で定義された基準に一致すると自動的にトリガー | すべての system-generated processor factory はデフォルトで無効。有効にするには、system-generated search pipeline を使用する前に `cluster.search.enabled_system_generated_factories` クラスタ設定を更新 |

## 仕組み

OpenSearch が検索リクエストを受信すると、リクエストパラメータとコンテキストを評価して、system-generated processor を生成するかどうかを判断します。これらのプロセッサは、検索ライフサイクルのさまざまな段階に挿入できます。

- **system-generated search request processor**: 実行前に受信リクエストを変更または拡張
- **system-generated search phase results processor**: シャードレベルの結果が収集された後に動作し、中間結果の集約や変換が可能
- **system-generated search response processor**: クライアントに返される前に最終レスポンスを変更

評価中、OpenSearch は system-generated search pipeline を動的に構築し、リクエストで指定されたユーザー定義パイプラインとマージします。system-generated processor は、プラグインのファクトリ実装で定義された特定の基準をリクエストが満たす場合にのみ作成されます。たとえば、クエリに特定のパラメータが含まれている場合や、特定の検索タイプ (neural や k-NN など) が検出された場合などです。

以下の図に、OpenSearch がクエリ実行中に system-generated search pipeline を解決する方法を示します。

![system-generated search pipeline の生成](/images/opensearch-system-generated-search-pipelines/generate-system-search-pipeline.png)

OpenSearch は実行順序を自動的に管理し、system-generated processor が正しいフェーズと、ユーザー定義プロセッサに対する相対的な位置で実行されることを保証します。これにより、追加設定なしで互換性と予測可能な実行が保証されます。

以下の図に、OpenSearch がクエリ実行中に system-generated search request processor を実行する方法を示します。system-generated search phase results processorと検索レスポンスプロセッサにも同じパターンが使用されます。

![system-generated search pipeline の実行](/images/opensearch-system-generated-search-pipelines/execute-system-search-pipeline.png)

## system-generated processorありとなしのワークフローの比較

検索ワークフローは、system-generated processor が有効かどうかによって異なります。

### system-generated processorあり

system-generated processor が有効な場合、追加設定なしで [ネイティブ maximal marginal relevance (MMR) サポート](https://docs.opensearch.org/latest/vector-search/specialized-operations/vector-search-mmr/)などの機能をすぐに利用できます。プロセッサは関連するクエリに自動的に適用されるため、運用オーバーヘッドが大幅に削減され、ユーザー体験が簡素化されます。たとえば、MMR ベースのベクトル検索を実行するには、以下のリクエストを送信します。

```json
POST /my-index/_search
{
  "query": {
    "neural": {
      "product_description": {
        "query_text": "Red apple"
      }
    }
  },
  "ext":{
    "mmr":{
      "candidates": 10,
      "diversity": 0.5
    }
  }
}
```

この例では、OpenSearch が system-generated processor を使用して MMR リランキングロジックのセットアップとオーケストレーションを自動的に処理します。これにより、パイプライン設定ではなく、検索ロジックに純粋に集中できます。

### system-generated processorなし

system-generated processor を使用しない場合、MMR や同様の後処理機能を有効にするために検索パイプラインを手動で設定する必要があります。これには、カスタム検索パイプラインを作成し、登録し、インデックスのデフォルトパイプラインとして設定するか、各検索リクエストで指定する必要があります。

```json
PUT /_search/pipeline/my_pipeline
{
  "request_processors": [
    {
      "mmr_over_sample_factory": {}
    }
  ],
  "response_processors": [
    {
      "mmr_rerank_factory": {}
    }
  ]
}
```

## カスタムsystem-generated processorの構築

プラグインでカスタムsystem-generated processor を定義できます。そのためには以下が必要です。

- **system-generated processorの作成**: 検索プロセッサインターフェース (`SearchRequestProcessor`、`SearchPhaseResultProcessor`、`SearchResponseProcessor` など) のいずれかを拡張してプロセッサロジックを実装
- **プロセッサファクトリの作成**: OpenSearch がプロセッサを生成してアタッチするタイミングを決定するファクトリを実装
- **ファクトリの登録**: OpenSearch プラグインにファクトリを登録して、自動パイプライン生成に参加できるようにする

以下の手順で、シンプルなsystem-generated search request processorの例を構築します。

### ステップ 1: system-generated processorの作成

```java
/**
 * ユーザー定義プロセッサの前に実行されるsystem-generated search request processorの例
 */
public class ExampleSearchRequestPostProcessor implements SearchRequestProcessor, SystemGeneratedProcessor {
    public static final String TYPE = "example-search-request-post-processor";
    public static final String DESCRIPTION = "This is a system-generated search request processor which will be"
        + "executed after the user defined search request. It will increase the query size by 2.";
    private final String tag;
    private final boolean ignoreFailure;

    public ExampleSearchRequestPostProcessor(String tag, boolean ignoreFailure) {
        this.tag = tag;
        this.ignoreFailure = ignoreFailure;
    }

    @Override
    public SearchRequest processRequest(SearchRequest request) {
        if (request == null || request.source() == null) {
            return request;
        }
        int size = request.source().size();
        request.source().size(size + 2);
        return request;
    }

    @Override
    public String getType() {
        return TYPE;
    }

    @Override
    public String getTag() {
        return this.tag;
    }

    @Override
    public String getDescription() {
        return DESCRIPTION;
    }

    @Override
    public boolean isIgnoreFailure() {
        return this.ignoreFailure;
    }

    @Override
    public ExecutionStage getExecutionStage() {
        // このプロセッサはユーザー定義検索リクエストプロセッサの後に実行される
        return ExecutionStage.POST_USER_DEFINED;
    }
}
```

### ステップ 2: プロセッサファクトリの作成

```java
public class Factory implements SystemGeneratedFactory<SearchRequestProcessor> {
    public static final String TYPE = "example-search-request-post-processor-factory";

    // 元のクエリサイズが 5 未満の場合、プロセッサを自動生成
    @Override
    public boolean shouldGenerate(ProcessorGenerationContext context) {
        SearchRequest searchRequest = context.searchRequest();
        if (searchRequest == null || searchRequest.source() == null) {
            return false;
        }
        int size = searchRequest.source().size();
        return size < 5;
    }

    @Override
    public SearchRequestProcessor create(
        Map<String, Processor.Factory<SearchRequestProcessor>> processorFactories,
        String tag,
        String description,
        boolean ignoreFailure,
        Map<String, Object> config,
        PipelineContext pipelineContext
    ) throws Exception {
        return new ExampleSearchRequestPostProcessor(tag, ignoreFailure);
    }
}
```

`shouldGenerate()` メソッドはすべての検索リクエストに対して呼び出されます。このメソッドで時間のかかる処理やリソース集約的なロジックを実行しないでください。軽量に保つ必要があります。その唯一の目的は、プロセッサを生成する必要があるかどうかを迅速に判断することです。

### ステップ 3: プラグインにファクトリを登録

```java
@Override
public Map<String, SystemGeneratedProcessor.SystemGeneratedFactory<SearchRequestProcessor>> getSystemGeneratedRequestProcessors(
    Parameters parameters
) {
    return Map.of(
        ExampleSearchRequestPostProcessor.Factory.TYPE,
        new ExampleSearchRequestPostProcessor.Factory()
    );
}
```

ファクトリが登録されると、OpenSearch は受信検索リクエストを自動的に評価し、該当する場合に system-generated processor を生成し、ランタイム検索パイプラインに挿入します。その他の例については、[サンプルプラグイン](https://github.com/opensearch-project/OpenSearch/tree/main/plugins/examples/system-search-processor/src/main/java/org/opensearch/example/systemsearchprocessor)を参照してください。

現在、OpenSearch では各検索リクエストに対して、タイプとステージごとに 1 つのsystem-generated processorのみが許可されています。たとえば、ユーザー定義プロセッサの前に実行できるsystem-generated search request processor は 1 つだけです。この設計により、実行順序の管理が簡素化され、異なるプラグイン間で予測可能な動作が保証されます。

ほとんどの場合、タイプとステージごとに 1 つのプロセッサで十分ですが、ユースケースが発生した場合、将来のリリースで複数のプロセッサをサポートする可能性があります。

また、プロセッサにロジックを追加して、system-generated processorとユーザー定義プロセッサ間の競合を検出・処理することもできます。これは、プロセッサが特定のユーザー定義プロセッサと共存できない場合や、実行制約を強制する必要がある場合に便利です。

以下は、system-generated processorとユーザー定義検索プロセッサ間の競合を処理する例です。

```java
@Override
public void evaluateConflicts(ProcessorConflictEvaluationContext context) throws IllegalArgumentException {
    boolean hasTruncateHitsProcessor = context.getUserDefinedSearchResponseProcessors()
        .stream()
        .anyMatch(processor -> CONFLICT_PROCESSOR_TYPE.equals(processor.getType()));

    if (hasTruncateHitsProcessor) {
        throw new IllegalArgumentException(
            String.format(
                Locale.ROOT,
                "The [%s] processor cannot be used in a search pipeline because it conflicts with the [%s] processor, "
                    + "which is automatically generated when executing a match query against [%s].",
                CONFLICT_PROCESSOR_TYPE,
                TYPE,
                TRIGGER_FIELD
            )
        );
    }
}
```

検索リクエストにそのプロセッサをトリガーするパラメータが含まれている場合、カスタムsystem-generated processor factoryが有効かどうかを確認する検証ステップを追加することをお勧めします。これにより、リクエストが何もせずに終了するのではなく、どのファクトリが必要かについて明確なエラーメッセージを受け取ることができます。

`SearchPipelineService` で定義されている以下の関数を使用して、特定のファクトリが有効かどうかを確認します。

```java
public boolean isSystemGeneratedFactoryEnabled(String factoryName) {
    return enabledSystemGeneratedFactories != null
        && (enabledSystemGeneratedFactories.contains(ALL) || enabledSystemGeneratedFactories.contains(factoryName));
}
```

## system-generated processorの監視

OpenSearch は Search Pipeline Stats API を提供しており、ユーザー定義プロセッサと system-generated processorの両方のパフォーマンスと実行メトリクスを監視できます。

以下のコマンドでメトリクスにアクセスできます。

```bash
GET /_nodes/stats/search_pipeline
```

レスポンスには、各プロセッサタイプの統計を報告する `system_generated_processors` セクションと、各プロセッサファクトリの評価と生成メトリクスを報告する `system_generated_factories` セクションが含まれます。

```json
{
  "nodes": {
    "gv8NncXIRiSaA7egwHzfJg": {
      "search_pipeline": {
        "system_generated_processors": {
          "request_processors": [
            {
              "example-search-request-post-processor": {
                "type": "mmr-search-request-processor",
                "stats": {
                  "count": 13,
                  "time_in_millis": 1,
                  "failed": 0
                }
              }
            }
          ]
        },
        "system_generated_factories": {
          "request_processor_factories": [
            {
              "example-search-request-post-processor-factory": {
                "type": "example-search-request-post-processor-factory",
                "evaluation_stats": {
                  "count": 37,
                  "time_in_microseconds": 185,
                  "failed": 0
                },
                "generation_stats": {
                  "count": 13,
                  "time_in_microseconds": 1,
                  "failed": 0
                }
              }
            }
          ]
        }
      }
    }
  }
}
```

`system_generated_factories` セクションは、OpenSearch がプロセッサを評価・生成した回数を報告します。

- `evaluation_stats`: プロセッサを生成すべきかどうかを判断するためにファクトリが評価した検索リクエストの数
- `generation_stats`: プロセッサが実際に作成された回数と、生成にかかった時間

これらのメトリクスにより、system-generated processor が期待どおりに動作しているかを簡単に判断でき、潜在的なパフォーマンスのボトルネックを特定できます。

## まとめ

system-generated search pipelineは、リクエストコンテキストに基づいて検索プロセッサの自動生成と実行を可能にすることで、OpenSearch の検索フレームワークを拡張します。これにより、プラグイン開発が簡素化され、手動設定が不要になり、検索がよりスマートで適応的になります。

プラグインを開発する際、この機能を使用して、リランキング、結果の多様化、クエリエンリッチメントなど、自動的に実行されるカスタムロジックを組み込むことができます。検索パイプラインを手動で定義する必要はありません。ぜひこの機能を試して、[OpenSearch フォーラム](https://forum.opensearch.org/)でフィードバックをお寄せください。
