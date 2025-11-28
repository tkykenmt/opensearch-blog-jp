---
title: "[翻訳] OpenSearch Data Prepper 2.11 のリリースを発表"
emoji: "📊"
type: "tech"
topics: ["opensearch", "dataprepper", "opentelemetry", "aws", "データ取り込み"]
published: false
publication_name: "opensearch"
published_at: 2025-04-24
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/announcing-opensearch-data-prepper-2-11/

## はじめに

OpenSearch Data Prepper 2.11 がダウンロード可能になりました。このリリースには、OpenSearch へのデータ取り込みを支援する多くの改善が含まれています。主な変更点として、新しいデータソースと OpenTelemetry (OTel) サポートの強化があります。

## OTel の改善

従来、OTel ソースの設計と実装は OpenSearch のデータマッピングモデルおよび OpenSearch Dashboards との統合のしやすさと密結合しており、OTel ソースには以下の機能が必要でした。

- 属性内のドット (.) をアットマーク (@) に置換
- 属性のマージとフラット化 — リソース属性、スコープ属性、ログ/メトリクス/スパン属性がすべてマージされ、イベントのルートに格納される
- 非標準フィールドの追加 — サービス名やトレースグループフィールドなどの非標準フィールドが追加される

Data Prepper は、OTel 標準仕様に準拠したイベントの生成をサポートするように変更されました。これをサポートするために、以下の変更が実装されています。

- 各 OTel ソースに新しい `output_format` 設定オプションが追加され、デフォルトは OpenSearch ですが、OTel 準拠のイベントを生成するように設定できます
- OpenTelemetry コーデックは、デフォルトの動作と新しい設定オプションのサポートを反映するように名前が変更されました。非標準フィールドはイベントメタデータに格納されるようになり、追加の変更なしにトレースおよびサービスマッププロセッサとの互換性が維持されます
- 不足していたすべての OTel 標準フィールドが追加されました
- OpenSearch インデックスでのログ、メトリクス、スパンドキュメントの正しいフィールドマッピングを容易にするために、`opensearch` シンクにインデックステンプレートが追加されました

これらの変更により、OTel ログから OTel 準拠のイベントを生成するための OTel ソース設定ファイルは以下のようになります。

```yaml
source:
  otel_logs_source:
      output_format: otel
sink:
  - opensearch:
        hosts: [ "https://..." ]
        aws:
            region: "<<region>>"
            sts_role_arn: "<<role-arn>>"
        index_type: "log-analytics-plain"
```

`opensearch` シンクに送信する前にデータを変換する必要があるユーザーは、既存の Data Prepper プロセッサを活用できます。たとえば、OTel ログで `severityText` と `severityNumber` を severity フィールドの下にネストするには、シンクステージの前に以下の設定を追加します。

```yaml
- add_entries:
       entries:
         - key: "severity/number"
           format: "${/severityNumber}"
         - key: "severity/text"
           format: "${/severityText}"
- delete_entries:
    with_keys: ["severityNumber", "severityText"]
```

## Atlassian Jira をソースとして使用

すべての Jira コンテンツを OpenSearch にシームレスに統合することで、強力なコンテキスト検索機能により Jira エクスペリエンスを変革できるようになりました。Data Prepper の新しい [Atlassian Jira](https://www.atlassian.com/software/jira) ソースプラグインにより、組織は完全な Jira プロジェクトを同期しながら、Jira の更新を継続的に監視し自動同期することで、リアルタイムの関連性を維持した統合検索可能なナレッジベースを作成できます。

この統合により、特定のプロジェクト、課題タイプ、ステータスに対する柔軟なフィルタリングオプションを使用したデータ同期が可能になり、必要な情報のみがインポートされます。安全で信頼性の高い接続を確保するために、プラグインは基本的な API キー認証と OAuth 2.0 認証を含む複数の認証方法をサポートし、AWS Secrets Manager を通じた認証情報管理のセキュリティも追加されています。また、中断のないアクセスを保証する自動トークン更新機能も備えており、継続的な運用を保証します。

Atlassian の堅牢な [api-version-2](https://developer.atlassian.com/cloud/jira/platform/rest/v2/intro/#version%22%3Eapi-version-2) 上に構築されたこの統合により、チームは OpenSearch の高度な検索機能を通じて Jira データから貴重なインサイトを引き出すことができ、組織が Jira コンテンツとやり取りし、価値を引き出す方法を変革します。

以下は設定例です。

```yaml
version: "2"
extension:
    aws:
      secrets:
        jira-account-credentials:
          secret_id: <<secret-arn>>
          region: <<secrets-region>>
          sts_role_arn: <<role-to-access-secret>>
jira-pipeline:
  source:
    jira:
      hosts: ["<<Atlassian-host-url>>"]
      authentication: 
        basic:
          username: ${{aws_secrets:jira-account-credentials:jiraId}}
          password: ${{aws_secrets:jira-account-credentials:jiraCredential}}
      filter:
        project:
          key:
            include:
              - "<<project-key>>"
            exclude:
               - "<<project-key>>"
        issue_type:
          include: 
            - "Story"
            - "Epic"
            - "Task"
          exclude:
            - "Bug"
        status:
          include: 
            - "To Do"
            - "In Progress"
            - "Done"
          exclude:
            - "Closed"
  sink:
    - opensearch:
```

## Atlassian Confluence をソースとして使用

Data Prepper の新しい Confluence ソースプラグインを通じて、[Atlassian Confluence](https://www.atlassian.com/software/confluence) コンテンツを OpenSearch にシームレスに統合することで、チームのナレッジ管理とコラボレーション機能を向上させることもできるようになりました。

この統合により、組織は集合知の一元化された検索可能なリポジトリを作成でき、情報の発見とチームの生産性が向上します。Confluence コンテンツを同期し、更新を継続的に監視することで、プラグインは OpenSearch インデックスが組織の共有ナレッジベースの最新かつ包括的な反映であり続けることを保証します。

この統合は柔軟なフィルタリングオプションを提供し、特定のスペースやページタイプからコンテンツを選択的にインポートでき、同期されるコンテンツを組織のニーズに合わせてカスタマイズできます。プラグインは基本的な API キーと OAuth 2.0 認証方法の両方をサポートし、AWS Secrets Manager を通じて認証情報を安全に管理するオプションも備えています。さらに、プラグインの自動トークン更新機能により、中断のないアクセスとシームレスな運用が保証されます。

Atlassian の Confluence [api-version](https://developer.atlassian.com/cloud/confluence/rest/v1/intro/#auth) 上に構築されたこの統合により、チームは Confluence コンテンツ全体で OpenSearch の高度な検索機能を活用でき、情報のアクセシビリティと活用を劇的に向上させます。

以下は設定例です。

```yaml
version: "2"
extension:
    aws:
      secrets:
        confluence-account-credentials:
          secret_id: <<secret-arn>>
          region: <<secrets-region>>
          sts_role_arn: <<role-to-access-secret>>
confluence-pipeline:
  source:
    confluence:
      hosts: ["<<Atlassian-host-url>>"]
      authentication: 
        basic:
          username: ${{aws_secrets:confluence-account-credentials:confluenceId}}
          password: ${{aws_secrets:confluence-account-credentials:confluenceCredential}}
      filter:
        space:
          key:
            include:
              - "<<space-key>>"
            exclude:
               - "<<space-key>>"
        page_type:
          include: 
            - "page"
            - "blogpost"
            - "comment"
          exclude:
            - "attachment"
  sink:
    - opensearch:
```

## Amazon Aurora/Amazon RDS をソースとして使用

[Amazon Aurora](https://aws.amazon.com/rds/aurora/) と [Amazon Relational Database Service (Amazon RDS)](https://aws.amazon.com/rds/) は、AWS クラウドでリレーショナルデータベースのセットアップ、運用、スケーリングを容易にするフルマネージドリレーショナルデータベースサービスです。Aurora/Amazon RDS のトランザクションデータに対して全文検索やベクトル検索などの高度な検索機能を活用したい場合、Data Prepper を使用して Aurora および Amazon RDS から OpenSearch にデータを同期できるようになりました。

Data Prepper の新しい `rds` ソースは、まず Aurora/Amazon RDS テーブルから既存のデータを OpenSearch インデックスにエクスポートし、その後、リレーショナルデータベースと OpenSearch 間のデータ整合性を維持するために、それらのテーブルからの増分変更をストリーミングします。`rds` ソースは現在、Aurora MySQL、Aurora PostgreSQL、RDS MySQL、RDS PostgreSQL エンジンをサポートしています。

以下は設定例です。

```yaml
aurora-mysql-pipeline:
  source:
    rds:
      db_identifier: "my-aurora-cluster"
      engine: "aurora-mysql"
      database: "hr_db"
      tables:
        include:
          - "employees"
          - "departments"
s3_bucket: "my-s3-bucket"
s3_prefix: "pipeline-data"
export:
  kms_key_id: "1234abcd-1234-abcd-1234-123456abcdef"
  export_role_arn: "arn:aws:iam::123456789012:role/ExportRole"
stream: true
aws:
  sts_role_arn: "arn:aws:iam::123456789012:role/PipelineRole"
  region: "us-east-1"
authentication:
  username: ${{aws_secrets:secret:username}}
  password: ${{aws_secrets:secret:password}}
```

## Amazon SQS をソースとして使用

Data Prepper は、SQS キューからイベントを読み取るための新しい Amazon Simple Queue Service (Amazon SQS) ソースをサポートするようになりました。Amazon SQS はフルマネージドメッセージキューです。Data Prepper の新しい `sqs` ソースは、Amazon SQS からメッセージを効率的に受信し、シンクにルーティングできるイベントを作成します。

Data Prepper は SQS キューから SQS メッセージをバッチで受信し、それらの SQS メッセージから Data Prepper イベントを作成します。デフォルトでは、Data Prepper は SQS メッセージごとに 1 つの Data Prepper イベントを作成します。Data Prepper は、メッセージの形式に応じて解析または grok するために使用できる堅牢な[プロセッサ](https://docs.opensearch.org/docs/latest/data-prepper/pipelines/configuration/processors/processors/)のコレクションを提供しています。

Amazon SQS のコストを削減するために、代わりに SQS データを設計し、メッセージごとに複数のイベントをサポートするように Data Prepper を設定できます。このアプローチを使用すると、データを SQS メッセージに結合することで Amazon SQS のコストが削減され、SQS の送受信回数が減少します。このアプローチを採用するには、送信アプリケーションを設計して、[Data Prepper コーデック](https://docs.opensearch.org/docs/latest/data-prepper/pipelines/configuration/sources/s3/#codec)として利用可能な形式で SQS メッセージを Amazon SQS に送信する必要があります。その後、そのコーデックを使用してメッセージを複数のイベントに解析するように Data Prepper パイプラインを設定できます。

## その他の機能と改善

このリリースには、パイプラインの作成を支援するいくつかの追加機能も含まれています。

- `rename_keys` プロセッサは、正規表現パターンを使用して変数名のキーの名前を変更できるようになりました
- `opensearch` シンクは、OTel ログとメトリクスの新しいインデックスタイプをサポートするようになりました
- Data Prepper の式は、`/` 文字をエスケープできるようにすることで、キー内のスラッシュ (`/`) をサポートするようになりました

## 今後の展望

Data Prepper の開発は継続しており、いくつかの新機能が予定されています。注目すべき機能の 1 つは、ML Commons と Amazon Bedrock の Data Prepper パイプラインへの統合です。この機能は、新しい機械学習 (ML) 推論プロセッサと Amazon Simple Storage Service (Amazon S3) ソースおよびシンクを通じて提供されます。この機能は現在開発中であり、バージョン 2.11 で実験的に利用可能です。

今後の機能の詳細については、[Data Prepper プロジェクトロードマップ](https://github.com/orgs/opensearch-project/projects/221/views/1)をご覧ください。

## コントリビューターへの感謝

このリリースに貢献してくださった以下のコミュニティメンバーに感謝します。

- [akshay0709](https://github.com/akshay0709) — Akshay Pawar
- [chenqi0805](https://github.com/chenqi0805) — Qi Chen
- [dinujoh](https://github.com/dinujoh) — Dinu John
- [divbok](https://github.com/divbok) — Divyansh Bokadia
- [dlvenable](https://github.com/dlvenable) — David Venable
- [FedericoBrignola](https://github.com/FedericoBrignola)
- [Galactus22625](https://github.com/Galactus22625) — Maxwell Brown
- [graytaylor0](https://github.com/graytaylor0) — Taylor Gray
- [janhoy](https://github.com/janhoy) — Jan Høydahl
- [jmsusanto](https://github.com/jmsusanto) — Jeremy Michael
- [juergen-walter](https://github.com/juergen-walter) — Jürgen Walter
- [KarstenSchnitter](https://github.com/KarstenSchnitter) — Karsten Schnitter
- [kkondaka](https://github.com/kkondaka) — Krishna Kondaka
- [MohammedAghil](https://github.com/MohammedAghil) — Mohammed Aghil Puthiyottil
- [oeyh](https://github.com/oeyh) — Hai Yan
- [RashmiRam](https://github.com/RashmiRam) — Rashmi
- [Rishikesh1159](https://github.com/Rishikesh1159) — Rishikesh
- [saketh-pallempati](https://github.com/saketh-pallempati) — Saketh Pallempati
- [san81](https://github.com/san81) — Santhosh Gandhe
- [sb2k16](https://github.com/sb2k16) — Souvik Bose
- [seschis](https://github.com/seschis) — Shane Schisler
- [shenkw1](https://github.com/shenkw1) — Katherine Shen
- [srikanthjg](https://github.com/srikanthjg) — Srikanth Govindarajan
- [TomasLongo](https://github.com/TomasLongo) — Tomas
- [Zhangxunmt](https://github.com/Zhangxunmt) — Xun Zhang
