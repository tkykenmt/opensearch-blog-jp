---
title: "[翻訳] OpenSearch 2.17 の紹介"
emoji: "🚀"
type: "tech"
topics: ["opensearch", "vectorsearch", "machinelearning", "search", "aws"]
published: true
publication_name: "opensearch"
published_at: 2024-09-17
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/introducing-opensearch-2-17/

OpenSearch 2.17 がリリースされました！[最新バージョンをダウンロード](https://opensearch.org/downloads.html)して、機械学習 (ML) 統合、スケーラビリティ、コスト効率、検索パフォーマンスを向上させるために設計された新機能と機能強化をお試しください。このリリースには、ML 推論検索プロセッサの強化、バッチ処理機能の拡張、高度な検索最適化などの重要なアップデートが含まれています。これらの強力な新機能について詳しく見ていきましょう。完全な内訳については、[リリースノート](https://github.com/opensearch-project/opensearch-build/blob/main/release-notes/opensearch-release-notes-2.17.0.md)をご確認ください。[OpenSearch Playground](https://playground.opensearch.org/app/home#/) で新しい OpenSearch Dashboards を試したり、詳細なガイダンスについては[ドキュメント](https://opensearch.org/docs/latest/)を参照してください。

## ベクトルデータベースと生成 AI

OpenSearch 2.17 では、アプリケーション開発を加速し、生成 AI ワークロードを実現するために、OpenSearch のベクトルデータベースと生成 AI 機能に多くの機能が追加されました。

### シームレスなディスク最適化ベクトル検索でコスト削減と効率向上を実現

OpenSearch 2.17 では、ベクトルワークロードの運用コストを大幅に削減する新しい[ディスク最適化ベクトル検索](https://opensearch.org/docs/latest/field-types/supported-field-types/knn-vector/#vector-workload-modes)が導入されました。この機能は[バイナリ量子化 (BQ)](https://opensearch.org/docs/latest/search-plugins/knn/knn-vector-quantization/#binary-quantization) を使用し、メモリ使用量を 32 倍圧縮します。この機能は、0.9 以上の再現率と 200 ミリ秒未満の p90 レイテンシを維持しながら、最大 70% のコスト削減を実現できます。ディスク最適化ベクトル検索の主な利点の 1 つは、複雑な前処理やトレーニングステップを必要としない、シームレスなすぐに使える (OOB) 統合です。

### バイトベクトルエンコーディングでメモリ使用量を削減しパフォーマンスを向上

OpenSearch の Faiss エンジンが[バイトベクトルエンコーディング](https://opensearch.org/docs/latest/field-types/supported-field-types/knn-vector/#byte-vectors)をサポートするようになりました。このメモリ効率の高いエンコーディング技術は、再現率の損失を最小限に抑えながらメモリ使用量を最大 75% 削減し、大規模ワークロードに適しています。特に入力ベクトルに -128 から 127 の範囲の値が含まれる場合にバイトベクトルの使用をお勧めします。

### Flow Framework プラグインでセキュリティを強化し更新を効率化

Flow Framework プラグインが[高度なユーザーレベルセキュリティ](https://opensearch.org/docs/latest/automating-configurations/workflow-security/)をサポートするようになりました。バックエンドロールを使用して、ロールに基づいて個々のワークフローへのきめ細かいアクセスを設定できるようになりました。バージョン 2.17 の新機能として、[reprovision パラメータ](https://opensearch.org/docs/latest/automating-configurations/api/create-workflow/#query-parameters)により、以前にプロビジョニングされたテンプレートを更新してプロビジョニングできます。

### 非同期バッチインジェストで大量 ML タスク処理を効率化

OpenSearch 2.17 では[非同期バッチインジェスト](https://opensearch.org/docs/latest/ml-commons-plugin/remote-models/async-batch-ingestion/)も導入されました。これにより、バッチ推論ジョブをトリガーし、ジョブステータスを監視し、バッチ処理が完了したら結果をインジェストできます。これにより、大規模データセットのエンベディング生成や k-NN インデックスへのインジェストなどの大量 ML タスクが効率化されます。

### ML 推論検索レスポンスプロセッサをユースケースに合わせてカスタマイズ

OpenSearch 2.16 では、検索クエリの実行中にモデル予測を実行できる ML 推論検索プロセッサが導入されました。OpenSearch 2.17 からは、すべてのドキュメントに対して単一のリクエストでモデル予測を実行するか、各ドキュメントに対して個別にモデル予測を実行するかを選択できるようになり、検索レスポンスプロセッサがさらに強化されました。

## 検索

このリリースでは、検索とクエリのパフォーマンス向上に焦点を当てた新機能も提供されています。

### 並行セグメント検索の設定強化とサポート拡大で検索パフォーマンスを最適化

[並行セグメント検索](https://opensearch.org/docs/latest/search-plugins/concurrent-segment-search/)は OpenSearch 2.12 から一般提供されています。OpenSearch 2.17 では、インデックスレベルとクラスターレベルの両方で新しい設定が導入されました。これらの設定と[プラガブルな decider ロジック](https://github.com/opensearch-project/OpenSearch/pull/15363)により、どのリクエストが並行検索を使用するかをより細かく制御できます。このリリースでは、[スクリプトを使用した複合集約](https://github.com/opensearch-project/OpenSearch/pull/15072)や[派生フィールド](https://github.com/opensearch-project/OpenSearch/pull/15326)など、より多くのスクリプトベースの検索リクエストをサポートするように並行セグメント検索が拡張されました。

### 効率的な数値タームエンコーディングと Roaring Bitmap でクエリパフォーマンスを向上

OpenSearch 2.17 では、[数値タームの値を Roaring Bitmap としてエンコードするサポート](https://github.com/opensearch-project/OpenSearch/pull/14774)が追加されました。値をより効率的にエンコードすることで、検索リクエストは 100 万件以上のドキュメントにマッチする保存済みフィルターを、より低い取得レイテンシとメモリ使用量で使用できます。詳細については、[Bitmap filtering](https://opensearch.org/docs/latest/query-dsl/term/terms/#bitmap-filtering) を参照してください。

### 計算負荷の高いクエリの新技術で検索パフォーマンスを加速

検索パフォーマンス向上への継続的な取り組みの一環として、計算負荷の高いクエリのパフォーマンスを向上させることを目的とした新しい実験的機能セットを導入しています。近似フレームワークは、クエリ内の関連ドキュメントのみをスコアリングすることで、長時間実行されるクエリをショートカットする新しい技術をもたらします。バージョン 2.17 でこのフレームワークを最初に活用するクエリは、他の句を持たないトップレベルの範囲クエリです。これらのクエリは、この最適化により最大 50 倍高速なクエリ実行時間のベンチマーク結果を示しています。

## オブザーバビリティとログ分析

このリリースでは、OpenSearch のオブザーバビリティとログ分析機能が拡張されています。

### 高度なフィルタリングとクロスクラスターサポートを備えた新しいカスタムトレースソースでトレース分析を強化

OpenSearch 2.17 では、実験的機能として新しいカスタムトレースソースが導入されました。この新しいトレースソースは OpenTelemetry スキーマに基づいており、トレースメタデータの高度なフィルタリング機能と最適化されたパフォーマンスを提供する、トレースとサービスの再設計された概要ページが含まれています。

### 柔軟なデータソース、高度な補完方法、ドメイン固有ルールで異常検出を強化

OpenSearch 2.17 リリースでは、異常検出プラグインに以下の機能強化が追加されました。

- **リモートおよび複数データソースのサポート**: 異常検出ダッシュボードがリモートインデックス選択をサポートするようになり、ローカルインデックスに加えてリモートクラスターからインデックスを選択できます。
- **欠損データの高度な補完方法**: データストリームのギャップに対処するために、ゼロ、前の値、またはカスタム値で欠損値を埋める[新しい補完方法](https://opensearch.org/docs/latest/observing-your-data/ad/index/#setting-an-imputation-option)が導入されました。
- **ML モデルとドメイン固有ルールの統合**: 予測精度を向上させるために、ML モデルとドメイン固有ルールを組み合わせました。比率しきい値または絶対値しきい値を使用して、実際の値と期待値の関係に基づいて異常をフィルタリングできるようになりました。

## 使いやすさ

このリリースには使いやすさの向上も含まれています。

### アプリケーションベースの設定テンプレートでインデックス作成を簡素化

OpenSearch 2.17 では、実験的機能として[アプリケーションベースの設定テンプレート](https://opensearch.org/docs/latest/im-plugin/index-context/)が導入されました。この機能が有効になっている場合、クラスターはユースケースに基づいてインデックスとインデックステンプレートを作成する際に使用できる、事前定義されたコンポーネントテンプレートのセットを提供します。これらのテンプレートは、ログやメトリクスなどの様々なユースケースのパフォーマンスを最適化するように設計されています。

## コスト、パフォーマンス、スケーラビリティ

このリリースでは、OpenSearch クラスターの安定性、可用性、回復力を向上させるためのアップデートが導入されています。

### 一元化された操作と改善されたデータ分散でスナップショットのスケーラビリティと回復力を強化

OpenSearch 2.17 では、スナップショットに複数の最適化が追加され、よりスケーラブルで回復力のあるものになりました。リモートバックストレージが有効なクラスターでは、スナップショット操作がクラスターマネージャーノードに一元化され、クラスター内の他のノードとの通信オーバーヘッドが削除されました。非リモートバックストレージクラスターでは、[ハッシュプレフィックス](https://opensearch.org/docs/latest/api-reference/snapshots/create-repository/)を使用して、設定されたスナップショットストアにデータを均等に分散するサポートが追加されました。

### リモートクラスター状態パブリケーションでオーバーヘッドを削減し効率を向上

リモートクラスター状態パブリケーションは OpenSearch 2.15 で実験的機能として導入され、OpenSearch 2.17 で一般提供されるようになりました。この機能が有効になっている場合、アクティブなクラスターマネージャーノードはクラスター状態をリモートバックストレージにアップロードし、トランスポート層経由で送信するのではなく、フォロワーノードにリモートバックストレージからクラスター状態をダウンロードするよう通知します。

### 検索専用レプリカシャードでパフォーマンスを向上しトラフィックを管理

OpenSearch 2.17 では、クラスター内でインデックス作成と検索の分離を実現するための実験的メカニズムが導入されました。検索トラフィックのみを処理することを目的とした新しいレプリカシャードタイプが追加されました。このシャードは `_bulk` 書き込みパスから分離されており、プライマリ適格ではありません。この機能を試すには、`opensearch.yml` で `opensearch.experimental.feature.read.write.split.enabled` を `true` に設定してください。

## OpenSearch 2.17 を始めよう

最新機能を試す準備はできましたか？[ダウンロードページ](https://opensearch.org/downloads.html)にアクセスして OpenSearch 2.17 をダウンロードしてください。詳細については、[リリースノート](https://github.com/opensearch-project/opensearch-build/blob/main/release-notes/opensearch-release-notes-2.17.0.md)、[ドキュメントリリースノート](https://github.com/opensearch-project/documentation-website/blob/main/release-notes/opensearch-documentation-release-notes-2.17.0.md/)、および[ドキュメント](https://opensearch.org/docs/latest/)を参照してください。[OpenSearch Playground](https://playground.opensearch.org/app/home#/) で新しい可視化オプションを試すこともできます。いつものように、このリリースに関するフィードバックを[コミュニティフォーラム](https://forum.opensearch.org/)でお待ちしています。最新機能についての皆様の体験をお聞かせください！
