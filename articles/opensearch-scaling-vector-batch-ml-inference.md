---
title: "[翻訳] ベクトル生成のスケーリング: OpenSearch Ingestion と ML Commons によるバッチ ML 推論"
emoji: "🤖"
type: "tech"
topics: ["opensearch", "machinelearning", "vectorsearch", "batch"]
published: true
publication_name: "opensearch"
published_at: 2025-08-20
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/scaling-vector-generation-batch-ml-inference-with-opensearch-ingestion-and-ml-commons/

大規模な機械学習 (ML) アプリケーションの時代において、最も重要な課題の 1 つは、OpenSearch へのデータ取り込み時にベクトル埋め込みを効率的に生成することです。ML モデルを使用して数百万、さらには数十億のドキュメントを高次元ベクトルに変換するプロセスは、効果的なニューラル検索アプリケーションを構築する上で重要なボトルネックとなっています。従来のリアルタイム API はベクトル生成への直接的なアプローチを提供しますが、大規模な取り込みワークフローを扱う際には大きな制限があります。

リアルタイムのベクトル生成アプローチは、推論あたりのコストが高く、レート制限が低いことが多く、取り込みフェーズで大きなボトルネックを生み出します。大規模なドキュメントコレクションをベクトル化しようとすると、これらの制限により取り込み時間が延長され、運用コストが増加します。この課題は、初期のドキュメント処理からベクトル生成、そして OpenSearch への最終的なインデックス作成まで、パイプライン全体を調整する複雑さによってさらに深刻化します。

これらのベクトル生成の課題に対処し、取り込みワークフローを効率化するために、OpenSearch Ingestion と ML Commons の強力な統合をご紹介します。この統合により、オフラインモードでのシームレスなバッチ ML 推論処理が可能になり、大規模なドキュメントコレクションのベクトルを生成できます。取り込みパイプラインのベクトル生成フェーズを最適化することで、ニューラル検索アプリケーションをこれまで以上に簡単かつ効率的に構築・スケールできるようになります。

## ML Commons は OpenSearch Ingestion とどのように統合されるのか?

オフラインバッチ推論ジョブを作成するために ML Commons と統合する新しい [`ml_inference` プロセッサ](https://docs.opensearch.org/latest/data-prepper/pipelines/configuration/processors/ml-inference/)を OpenSearch Ingestion に追加しました。OpenSearch 2.17 以降、ML Commons は [Batch Predict API](https://docs.opensearch.org/latestml-commons-plugin/api/model-apis/batch-predict/) を提供しており、Amazon Bedrock、Amazon SageMaker、Cohere、OpenAI などの外部モデルサーバーにデプロイされたモデルを使用して、オフラインの非同期モードで大規模なデータセットに対して推論を実行します。ML Commons と OpenSearch Ingestion を統合することで、Batch Predict API が OpenSearch Ingestion に組み込まれ、OpenSearch Ingestion パイプラインが取り込み中にバッチ推論ジョブを実行できるようになります。以下の図は、このプロセスをエンドツーエンドで実行するために複数のコンポーネントを調整する OpenSearch Ingestion パイプラインを示しています。

![OpenSearch Ingestion パイプラインの図](/images/opensearch-scaling-vector-batch-ml-inference/OSI_Ml_Commons_Integration.png)

このソリューションでは、`s3` ソースが推論パイプラインで生成された新しいファイルのイベントを監視します。その後、新しいファイル名をバッチ推論のための入力として ML Commons に送信します。アーキテクチャには 3 つのサブパイプラインが含まれており、それぞれがデータフローで異なるタスクを実行します。

- **パイプライン 1 (データの準備と変換)**
  1. ソース: ユーザーが提供し、OpenSearch Data Prepper がサポートする外部ソースからデータが取り込まれます。
  2. データ変換プロセッサ: 生データが処理・変換され、リモート AI サーバーでのバッチ推論に適した形式に準備されます。
  3. `s3` (シンク): 変換されたデータは、AI サーバーへの入力として Amazon S3 バケットに保存され、中間ストレージレイヤーとして機能します。

- **パイプライン 2 (ML バッチ推論のトリガー)**
  1. ソース: S3 スキャンがパイプライン 1 で生成された新しい S3 ファイルのイベントを監視します。
  2. `ml_inference` プロセッサ: ML Commons Batch Predict API を呼び出してバッチジョブを作成します。
  3. タスク ID: 各バッチジョブには追跡と管理のためのタスク ID が関連付けられます。
  4. ML Commons: リアルタイムニューラル検索用のモデルをホストし、リモート AI サーバーへのコネクタを管理し、バッチ推論とジョブ管理のための API を提供します。
  5. AI サービス: データに対してバッチ推論を実行し、予測や洞察を生成します。ML Commons はこれらの AI サービス (Amazon SageMaker や Amazon Bedrock など) と対話します。結果は別の S3 ファイルに非同期で保存されます。

- **パイプライン 3 (バルク取り込みの実行)**
  1. `s3` (ソース): バッチジョブの結果を保存します。S3 がこのパイプラインのソースです。
  2. データ変換プロセッサ: OpenSearch インデックスにデータが正しくマッピングされるように、取り込み前にバッチ推論出力をさらに処理・変換します。
  3. OpenSearch インデックス (シンク): 処理された結果を OpenSearch にインデックス化し、保存、検索、さらなる分析を行います。

## ml_inference プロセッサの使用方法

現在の OpenSearch Ingestion 実装では、バッチ処理のための S3 スキャンソースと `ml_inference` プロセッサ間の特殊な統合が特徴です。この初期リリースでは、S3 スキャンはメタデータのみモードで動作し、実際のファイル内容を読み取ることなく S3 ファイル情報を効率的に収集します。`ml_inference` プロセッサは、S3 ファイル URL を使用して ML Commons とバッチ処理を調整します。この設計により、スキャンフェーズ中の不要なデータ転送を最小限に抑え、バッチ推論ワークフローを最適化します。

`ml_inference` プロセッサは以下のパラメータで定義できます。

```yaml
processor:
    - ml_inference:
        # OpenSearch ドメインのエンドポイント URL
        host: "https://search-xunzh-test-offlinebatch-kitdj4jwpiencfmxpklyvwarwa.us-west-2.es.amazonaws.com"

        # 推論操作のタイプ:
        # - batch_predict: バッチ処理用
        # - predict: リアルタイム推論用
        action_type: "batch_predict"
        
        # リモート ML モデルサービスプロバイダー (bedrock または sagemaker)
        service_name: "bedrock"
        
        # ML モデルの一意の識別子
        model_id: "EzNlGZcBo9m_Jklj4T0j"
        
        # バッチ推論結果が保存される S3 パス
        output_path: "s3://xunzh-offlinebatch/bedrock-multisource/output-multisource/"
        
        # AWS 設定
        aws:
            # Lambda 関数がデプロイされている AWS リージョン
            region: "us-west-2"
            # Lambda 関数実行用の IAM ロール ARN
            sts_role_arn: "arn:aws:iam::388303208821:role/Admin"
            
        # プロセッサをトリガーするタイミングを決定する条件式
        # この場合、バケットが "xunzh-offlinebatch" に一致する場合のみ処理
        ml_when: /bucket == "xunzh-offlinebatch"
```

## ml_inference プロセッサを使用した取り込みパフォーマンスの改善

OpenSearch Ingestion の `ml_inference` プロセッサは、ML 対応検索のデータ取り込みパフォーマンスを大幅に向上させます。セマンティック検索、マルチモーダル検索、ドキュメントエンリッチメント、クエリ理解など、ML モデルで生成されたデータを必要とするユースケースに最適です。セマンティック検索では、プロセッサは大量の高次元ベクトルの作成と取り込みを桁違いに高速化できます。

プロセッサのオフラインバッチ推論機能は、リアルタイムモデル呼び出しに比べて明確な利点を提供します。リアルタイム処理には容量制限のあるライブモデルサーバーが必要ですが、バッチ推論はオンデマンドでコンピューティングリソースを動的にスケールし、データを並列処理します。例えば、OpenSearch Ingestion パイプラインが 10 億件のソースデータリクエストを受信すると、ML バッチ推論入力用に 100 個の S3 ファイルを作成します。`ml_inference` プロセッサは、100 台の `ml.m4.xlarge` Amazon EC2 インスタンスを使用して Amazon SageMaker バッチジョブを開始し、10 億件のリクエストのベクトル化を 14 時間で完了します。これはリアルタイムモードでは事実上不可能なタスクです。このプロセスを以下の図に示します。

![SageMaker バッチジョブの図](/images/opensearch-scaling-vector-batch-ml-inference/SageMaker_Batch_Job.png)

このソリューションは、ワーカーを追加することで処理時間を線形に削減できる優れたスケーラビリティを提供します。例えば、100 台の `ml.m4.xlarge` EC2 インスタンスを使用した初期セットアップで 10 億件のドキュメントリクエストを 14 時間で処理した場合、ワーカー数を 200 インスタンスに倍増させると、処理時間を 7 時間に短縮できる可能性があります。この線形スケーリング機能は、ワーカー数とインスタンスタイプを調整するだけでさまざまなパフォーマンス要件を満たすソリューションの柔軟性を示しており、特定のニーズと緊急性に基づいて処理時間を最適化できます。

さらに、ほとんどの AI サーバーは約 50% 低いコストでバッチ推論 API を提供しており、半分の価格で同様のパフォーマンスを実現できます。

## はじめに

OpenSearch Ingestion の `ml_inference` プロセッサを使用して、テキスト埋め込みモデルを使用したセマンティック検索用に 10 億件のデータリクエストを取り込む実践的な例を見ていきましょう。

### ステップ 1: OpenSearch でコネクタを作成しモデルを登録する

[このブループリント](https://github.com/opensearch-project/ml-commons/blob/main/docs/remote_inference_blueprints/batch_inference_sagemaker_connector_blueprint.md)を使用して、Amazon SageMaker でコネクタとモデルを作成します。

Amazon SageMaker でバッチ変換用の Deep Java Library (DJL) ML モデルを作成します。

```json
POST https://api.sagemaker.us-east-1.amazonaws.com/CreateModel
{
   "ExecutionRoleArn": "arn:aws:iam::419213735998:role/aos_ml_invoke_sagemaker",
   "ModelName": "DJL-Text-Embedding-Model-imageforjsonlines",
   "PrimaryContainer": { 
      "Environment": { 
         "SERVING_LOAD_MODELS" : "djl://ai.djl.huggingface.pytorch/sentence-transformers/all-MiniLM-L6-v2" 
      },
      "Image": "763104351884.dkr.ecr.us-east-1.amazonaws.com/djl-inference:0.29.0-cpu-full"
   }
}
```

`actions` フィールドに新しい `action` タイプとして `batch_predict` を持つコネクタを作成します。

返されたコネクタ ID を使用して Amazon SageMaker モデルを登録します。

```json
POST /_plugins/_ml/models/_register
{
    "name": "SageMaker model for batch",
    "function_name": "remote",
    "description": "test model",
    "connector_id": "a3Y8O5IBOcD45O-eoq1g"
}
```

`batch_predict` アクションタイプでモデルを呼び出します。

```json
POST /_plugins/_ml/models/teHr3JABBiEvs-eod7sn/_batch_predict
{
  "parameters": {
    "TransformJobName": "SM-offline-batch-transform"
  }
}
```

レスポンスにはバッチジョブのタスク ID が含まれます。

```json
{
 "task_id": "oSWbv5EB_tT1A82ZnO8k",
 "status": "CREATED"
}
```

バッチジョブのステータスを確認するには、Get Task API を使用してタスク ID を指定します。

```
GET /_plugins/_ml/tasks/oSWbv5EB_tT1A82ZnO8k
```

### ステップ 1 (代替): AWS CloudFormation を使用する

AWS CloudFormation を使用して、ML 推論に必要なすべての Amazon SageMaker コネクタとモデルを自動的に作成できます。このアプローチは、Amazon OpenSearch Service コンソールで利用可能な事前設定されたテンプレートを使用することでセットアップを簡素化します。詳細については、[AWS CloudFormation を使用したセマンティック検索用リモート推論のセットアップ](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/cfn-template.html)を参照してください。

必要なすべての Amazon SageMaker コネクタとモデルを作成する CloudFormation スタックをデプロイするには、以下の手順を使用します。

1. OpenSearch Service コンソールで、**Integrations** に移動し、`SageMaker` を検索します。
2. **Integration with text embedding models through Amazon SageMaker** を選択します。
3. **Configure domain** を選択し、適切に **Configure VPC domain** または **Configure public domain** を選択します。

![OpenSearch Service コンソールのスクリーンショット](/images/opensearch-scaling-vector-batch-ml-inference/CFN_Console_Integration.png)

4. スタックデプロイを開始する際、**Enable Offline Batch Inference** ドロップダウンリストを `true` に設定して、オフラインバッチ処理用のリソースをプロビジョニングします。

![Enable Offline Batch Inference ドロップダウン](/images/opensearch-scaling-vector-batch-ml-inference/CFN_Parameters.png)

5. CloudFormation スタックが作成されたら、CloudFormation コンソールの **Outputs** タブを開いて `connector_id` と `model_id` を確認します。これらの値は後のパイプライン設定手順で必要になります。

### ステップ 2: OpenSearch Ingestion パイプラインを作成する

設定エディタで以下のコードを使用して OpenSearch Ingestion パイプラインを作成します。

```yaml
version: '2'
extension:
  osis_configuration_metadata:
    builder_type: visual
sagemaker-batch-job-pipeline:
  source:
    s3:
      acknowledgments: true
      delete_s3_objects_on_read: false
      scan:
        buckets:
          - bucket:
              name: xunzh-offlinebatch
              data_selection: metadata_only
              filter:
                include_prefix:
                  - sagemaker/sagemaker_djl_batch_input
                exclude_suffix:
                  - .manifest
          - bucket:
              name: xunzh-offlinebatch
              data_selection: data_only
              filter:
                include_prefix:
                  - sagemaker/output/
        scheduling:
          interval: PT6M
      aws:
        region: us-west-2
      default_bucket_owner: 388303208821
      codec:
        ndjson:
          include_empty_objects: false
      compression: none
      workers: '1'
  processor:
    - ml_inference:
        host: "https://search-xunzh-test-offlinebatch-kitdj4jwpiencfmxpklyvwarwa.us-west-2.es.amazonaws.com"
        aws_sigv4: true
        action_type: "batch_predict"
        service_name: "sagemaker"
        model_id: "9t4AbpYBQb1BoSOe8x8N"
        output_path: "s3://xunzh-offlinebatch/sagemaker/output"
        aws:
          region: "us-west-2"
          sts_role_arn: "arn:aws:iam::388303208821:role/Admin"
        ml_when: /bucket == "xunzh-offlinebatch"
    - copy_values:
        entries:
          - from_key: /content/0
            to_key: chapter
          - from_key: /content/1
            to_key: title
          - from_key: /SageMakerOutput/0
            to_key: chapter_embedding
          - from_key: /SageMakerOutput/1
            to_key: title_embedding
    - delete_entries:
        with_keys:
          - content
          - SageMakerOutput
  sink:
    - opensearch:
        hosts: ["https://search-xunzh-test-offlinebatch-kitdj4jwpiencfmxpklyvwarwa.us-west-2.es.amazonaws.com"]
        aws:
          serverless: false
          region: us-west-2
        routes:
          - ml-ingest-route
        index_type: custom
        index: test-nlp-index
  routes:
    - ml-ingest-route: /chapter != null and /title != null
```

### ステップ 3: 取り込み用のデータを準備する

この例では、自然言語処理タスク用の実際のユーザークエリのコレクションである [MS MARCO データセット](https://microsoft.github.io/msmarco/Datasets.html)を使用します。データセットは JSONL 形式で構造化されており、各行は ML 埋め込みモデルに送信されるリクエストを表します。

```json
{"_id": "1185869", "text": ")what was the immediate impact of the success of the manhattan project?", "metadata": {"world war 2"}}
{"_id": "1185868", "text": "_________ justice is designed to repair the harm to victim, the community and the offender caused by the offender criminal act. question 19 options:", "metadata": {"law"}}
{"_id": "597651", "text": "what color is amber urine", "metadata": {"nothing"}}
{"_id": "403613", "text": "is autoimmune hepatitis a bile acid synthesis disorder", "metadata": {"self immune"}}
...
```

このテストでは、100 個のファイルに分散された 10 億件の入力リクエストを構築しました。各ファイルには 1,000 万件のリクエストが含まれています。これらのファイルは、プレフィックス `s3://offlinebatch/sagemaker/sagemaker_djl_batch_input/` で S3 に保存されています。OpenSearch Ingestion パイプラインはこれらの 100 個のファイルを同時にスキャンし、並列処理用に 100 ワーカーで Amazon SageMaker バッチジョブを開始し、10 億件のドキュメントを効率的にベクトル化して OpenSearch Service に取り込みます。

本番環境では、OpenSearch Ingestion パイプラインを使用してバッチ推論入力用の S3 ファイルを生成できます。パイプラインはさまざまなデータソース ([Sources](https://docs.opensearch.org/latest/data-prepper/pipelines/configuration/sources/sources/) を参照) をサポートし、スケジュールに従って動作し、ソースデータを継続的に S3 ファイルに変換します。これらのファイルは、スケジュールされたオフラインバッチジョブを通じて AI サーバーによって自動的に処理され、継続的なデータ処理と取り込みを保証します。

### ステップ 4: バッチ推論ジョブを監視する

Amazon SageMaker コンソールまたは CLI を使用してバッチ推論ジョブを監視できます。または、Get Task API を使用してバッチジョブを監視することもできます。

```json
GET /_plugins/_ml/tasks/_search
{
  "query": {
    "bool": {
      "filter": [
        {
          "term": {
            "state": "RUNNING"
          }
        }
      ]
    }
  },
  "_source": ["model_id", "state", "task_type", "create_time", "last_update_time"]
}
```

### ステップ 5: セマンティック検索を実行する

これで、10 億件のベクトル化されたデータポイントに対してセマンティック検索を実行できます。生のベクトルを検索するには、`knn` クエリタイプを使用し、入力として `vector` 配列を提供し、返される結果の `k` 数を指定します。

```json
GET /my-raw-vector-index/_search
{
  "query": {
    "knn": {
      "my_vector": {
        "vector": [0.1, 0.2, 0.3],
        "k": 2
      }
    }
  }
}
```

AI を活用した検索を実行するには、`neural` クエリタイプを使用します。`query_text` 入力、OpenSearch Ingestion パイプラインで設定した埋め込みモデルの `model_id`、返される結果の `k` 数を指定します。検索結果から埋め込みを除外するには、`_source.excludes` パラメータで埋め込みフィールドの名前を指定します。

```json
GET /my-ai-search-index/_search
{
  "_source": {
    "excludes": [
      "output_embedding"
    ]
  },
  "query": {
    "neural": {
      "output_embedding": {
        "query_text": "What is AI search?",
        "model_id": "mBGzipQB2gmRjlv_dOoB",
        "k": 2
      }
    }
  }
}
```

## まとめ

ML Commons と OpenSearch Ingestion の統合は、大規模な ML データ処理と取り込みにおける大きな前進を表しています。OpenSearch Ingestion のマルチパイプライン設計は、データ準備、バッチ推論、取り込みを効率的に処理し、Amazon Bedrock や Amazon SageMaker などの AI サービスをサポートします。このシステムは、並列処理と動的なリソース使用により 10 億件のリクエストを処理でき、リアルタイム処理と比較してバッチ推論コストを 50% 削減します。これにより、高速で大規模なベクトル作成が重要なセマンティック検索、マルチモーダル検索、ドキュメントエンリッチメントなどのタスクに最適なソリューションとなります。全体として、この統合は OpenSearch での ML を活用した検索と分析を改善し、これらの操作をよりアクセスしやすく、効率的で、コスト効果の高いものにします。

## 今後の予定

今後、`ml_inference` プロセッサの機能をリアルタイムモデル予測をサポートするように拡張する予定です。この機能強化により、`s3` `scan` ソースに新しい動作モードが導入されます。このモードでは、プロセッサは入力ファイルの内容を完全に読み取り処理し、リアルタイム推論による即時のベクトル生成を可能にします。このデュアルモード機能により、大規模な操作のための効率的なバッチ処理と、即時の推論ニーズのためのリアルタイム処理を柔軟に選択できるようになります。

詳細については、`ml_inference` プロセッサのドキュメントを参照してください。[OpenSearch フォーラム](https://forum.opensearch.org/)でのフィードバックをお待ちしています。
