---
title: "[翻訳] OpenSearch における GPU アクセラレーションベクトル検索: 新たなフロンティア"
emoji: "🚀"
type: "tech"
topics: ["opensearch", "gpu", "vectorsearch", "nvidia", "performance"]
published: false
published_at: 2025-03-18
publication_name: "opensearch"
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/gpu-accelerated-vector-search-opensearch-new-frontier/

生成 AI アプリケーションの台頭に伴い、OpenSearch の[ベクトルデータベース](https://opensearch.org/platform/search/vector-database.html)としての採用が大幅に増加しています。ベクトル検索ワークロードは数百万から数十億のベクトルにスケールしており、従来の CPU ベースのインデックス作成は時間がかかりコストも高くなっています。この課題に対処するため、OpenSearch は [NVIDIA cuVS](https://github.com/rapidsai/cuvs) を使用して、今後の 3.0 リリースで OpenSearch Vector Engine の[プレビュー機能](https://github.com/opensearch-project/k-NN/issues/2293)として GPU アクセラレーションを導入します。GPU の大規模な並列処理能力を活用することで、この新機能はインデックス構築時間を劇的に短縮し、大規模ベクトルワークロードに対して優れたパフォーマンスを提供しながら運用コストを大幅に削減します。

### GPU アクセラレーションを使用する理由

OpenSearch Vector Engine は 2024 年に[大きな進歩](https://github.com/opensearch-project/k-NN/issues/1599)を遂げ、[AVX512 SIMD サポート](https://github.com/opensearch-project/k-NN/issues/2056)、セグメントレプリケーション、ベクトルの読み書きのための[効率的なベクトルフォーマット](https://github.com/opensearch-project/k-NN/issues/1853)、[反復的インデックス構築](https://github.com/opensearch-project/k-NN/issues/1938)、[インテリジェントグラフ構築](https://github.com/opensearch-project/k-NN/issues/1942)、ベクトルの[派生ソース](https://github.com/opensearch-project/k-NN/issues/2377)など、さまざまな最適化を実装しました。これらの機能と最適化はインデックス作成時間の段階的な改善をもたらしましたが、主にベクトル検索の周辺コンポーネントを強化するものであり、コアベクトル操作の根本的なパフォーマンスボトルネックには対処していませんでした。

ベクトル操作、特に距離計算は計算集約型のタスクであり、並列処理に最適です。GPU は大規模な並列アーキテクチャにより、数千の計算を同時に実行できるため、この分野で優れています。これらの計算負荷の高いベクトル操作に GPU アクセラレーションを活用することで、OpenSearch はインデックス構築時間を劇的に短縮できます。これはパフォーマンスを向上させるだけでなく、処理時間の短縮によりリソース使用率が低下し、運用コストが削減されるため、大幅なコスト削減にもつながります。GPU がこれらの並列計算を効率的に処理する能力は、ベクトル検索操作の高速化に自然に適しており、大規模ベクトルデータセットを扱う組織にとって魅力的なソリューションを提供します。

## 新しいアーキテクチャ

合理化された分離型 GPU アクセラレーションインデックス作成システムは、3 つのコアコンポーネントで構成されています。

1. **Vector Index Build Service** – 高性能ベクトルインデックス構築に特化した専用 GPU フリート。このサービスは独立して動作し、最適な GPU リソース使用率を確保します。
2. **OpenSearch Vector Engine** – インジェストから検索まで、ベクトル関連の操作を管理し、CPU と GPU アクセラレーションワークフローをシームレスに統合する k-NN プラグイン。
3. **オブジェクトストア** – OpenSearch のリポジトリ抽象化を使用してベクトルデータを安全に保存および処理する、フォールトトレラントな中間ストレージレイヤー。

以下の画像は新しいアーキテクチャを示しています。

![高レベルアーキテクチャ](/images/opensearch-gpu-accelerated-vector-search/high-level-arch.jpg)

新しいシステムは以下のワークフローを使用します。

1. ベクトルを含むドキュメントが Bulk API を使用して OpenSearch に取り込まれます。
2. フラッシュ/マージ操作中に、OpenSearch Vector Engine は以下を行います。
   - ベクトルをオブジェクトストアにアップロード
   - GPU フリートに GPU アクセラレーションインデックス構築リクエストを開始
   - 構築の進行状況を監視
3. Vector Index Build Service は以下を行います。
   - GPU アクセラレーションを使用してインデックスを構築
   - インデックスを CPU 互換フォーマットに変換
   - 完成したインデックスをオブジェクトストアにアップロード
4. 最後に、OpenSearch Vector Engine は以下を行います。
   - 最適化されたインデックスをダウンロード
   - 既存のセグメントファイルと統合
   - セグメント作成プロセスを完了

いずれかのステップでエラーが発生した場合、システムは継続的な運用を確保するために自動的に CPU ベースのインデックス構築にフォールバックします。詳細については、[技術設計ドキュメント](https://github.com/opensearch-project/k-NN/issues/2293)と[アーキテクチャ図](https://github.com/opensearch-project/k-NN/issues/2294)を参照してください。

### CAGRA アルゴリズムを使用したベクトルインデックス構築

GPU ワーカーは、[Faiss](https://github.com/facebookresearch/faiss) ライブラリを通じて統合された [NVIDIA cuVS](https://github.com/rapidsai/cuvs) CAGRA アルゴリズムを活用します。[CAGRA](https://arxiv.org/abs/2308.15136) ((C)UDA (A)NNS (GRA)ph-based) は、GPU アクセラレーション用にゼロから構築されたグラフベースインデックス作成への新しいアプローチです。CAGRA は、[IVF-PQ](https://developer.nvidia.com/blog/accelerating-vector-search-nvidia-cuvs-ivf-pq-deep-dive-part-1/) または [NN-DESCENT](https://docs.rapids.ai/api/cuvs/nightly/cpp_api/neighbors_nn_descent/) を使用して k-NN グラフを最初に構築し、次に近傍間の冗長なパスを削除することでグラフ表現を構築します。

以下の画像は CAGRA アルゴリズムを示しています。

![CAGRA アルゴリズムの説明](/images/opensearch-gpu-accelerated-vector-search/cagra-algo-explained.png)

Vector Index Build リクエストが GPU ワーカーによって受信されると、セグメント固有のベクトルインデックスを構築するために必要なすべてのパラメータが含まれています。Vector Index Build コンポーネントは、オブジェクトストアからベクトルファイルを取得し、CPU メモリにロードすることでプロセスを開始します。これらのベクトルは Faiss を通じて CAGRA インデックスに挿入されます。インデックス構築が完了すると、システムは自動的に CAGRA インデックスを HNSW ベースのフォーマットに変換し、CPU ベースの検索操作との互換性を確保します。変換されたインデックスはオブジェクトストアにアップロードされ、構築リクエストの正常な完了を示します。これにより、GPU で構築されたインデックスは、インデックス構築のパフォーマンス上の利点を維持しながら、CPU マシンで効率的に検索できます。

**出典: [CAGRA: Highly Parallel Graph Construction and Approximate Nearest Neighbor Search for GPUs](https://arxiv.org/pdf/2308.15136)**

## ベンチマーク結果

初期ベンチマークでは、インデックス作成パフォーマンスとコスト効率の大幅な改善が示されました。実験では [10M 768D データセット](https://github.com/opensearch-project/opensearch-benchmark-workloads/blob/main/vectorsearch/workload.json#L54-L64)と [OpenSearch Benchmark](https://opensearch.org/docs/latest/benchmark/) を使用しました。

### テストセットアップ

| キー | 値 |
|------|-----|
| データノード数 | 3 |
| データノードタイプ | r6g.4xlarge |
| GPU ワーカー数 | 3 |
| GPU ワーカータイプ | g5.2xlarge |
| OpenSearch バージョン | 2.19.0 |

### インデックス設定

| キー | 値 |
|------|-----|
| プライマリシャード数 | 6 |
| レプリカ数 | 1 |

### パフォーマンス比較

以下の表は実験結果を示しています。

| メトリクス | ベースライン | GPU アクセラレーション | 改善率 |
|----------|------------|---------------------|--------|
| 最適化インデックス構築時間 (分) | 273.78 | 29.13 | 9.4x |
| 最大 CPU 使用率 (%) | 100 | 40 | 2.5x |
| クラスターコスト (3 x r6g.4xlarge) | $11.04 | $1.17 | - |
| GPU コスト (3 x g5.2xlarge) | $0 | $1.77 | - |
| 総コスト | $11.04 | $2.94 | 3.75x |
| 平均インデックス作成スループット | 8,203 | 16,796 | 2.0x |
| インデックスサイズ (GB、レプリカなし) | 58.7 | 58.7 | - |

これらの結果は、GPU アクセラレーションが**インデックス作成速度を 9.3 倍向上**させながら、**コストを 3.75 倍削減**したことを示しています。さらに、**CPU 使用率はベースラインと比較して 2.5 倍低く**、インデックス作成スループットは **2 倍向上**しました。ベクトルインデックス構築が CPU 上で行われなくなったため、OpenSearch クラスターは追加のスケーリングなしでより高いインデックス作成トラフィックを処理でき、重いワークロードに対してより効率的になります。

## 主な利点

GPU アクセラレーションは、OpenSearch のベクトル検索にいくつかの利点を提供します。

- **分離アーキテクチャ**: OpenSearch と GPU ワーカーは独立して動作し、それぞれが個別に進化できます。この柔軟性により、相互依存なしに価格性能比の継続的な最適化が可能になります。さらに、複数の OpenSearch クラスターが同じ GPU リソースをタイムシェアベースで共有できます。
- **効率的なリソース使用**: GPU ノードはセグメントレベルでのベクトルインデックス構築のみに集中し、テキストインデックス構築を回避します。この的を絞った使用により GPU 使用時間が最小化され、リソース効率とコスト効果が最大化されます。
- **強化されたフォールトトレランス**: 中間ストレージレイヤーがバッファとして機能し、堅牢なエラー処理を提供します。GPU ワーカーがプロセス中に失敗した場合、インデックス構築ジョブはベクトルの再アップロードを必要とせずにシームレスに再開でき、ダウンタイムとデータ転送オーバーヘッドを大幅に削減します。

## まとめ

GPU アクセラレーションベクトルインデックス作成は、大規模 AI ワークロードをサポートするための OpenSearch の進化における重要なマイルストーンです。ベンチマークでは、GPU アクセラレーションが CPU ベースのソリューションと比較して**インデックス作成速度を 9.3 倍向上**させながら**コストを 3.75 倍削減**し、数十億規模のインデックス構築に必要な時間を数日から数時間に短縮しました。GPU インスタンスは CPU インスタンスより **1.5 倍高価**ですが、大幅な速度向上により強力な価格性能上の優位性が得られ、マルチテナント使用のための共有 GPU フリートモデルによってさらに増幅されます。

**分離設計**により柔軟性が確保され、OpenSearch は将来のハードウェアアクセラレータやアルゴリズムの改善を採用できます。デプロイメントモデルにより、クラウドおよびオンプレミス環境全体でシームレスな採用が可能になります。NVIDIA の cuVS ライブラリの **CAGRA アルゴリズム**を活用し、**GPU-CPU インデックス相互運用性**をサポートすることで、OpenSearch は本番環境の信頼性のための組み込みエラー処理とフォールバックメカニズムを備えた、堅牢でスケーラブルなソリューションを提供します。

## 今後の予定

初期の GPU ベースインデックス構築アルゴリズムリリースは、GPU ベースインデックスアクセラレーション用の **FP32** をサポートします。今後のリリースでは、価格性能をさらに向上させるために **FP16 およびバイト**サポートが導入されます。さらに、OpenSearch コミュニティは、大規模なベクトル検索の新しい可能性を解き放つために、低レイテンシで高スループットの検索を可能にするベクトルエンジン機能の強化を続けています。

## 参考文献

1. [CAGRA: Highly Parallel Graph Construction and Approximate Nearest Neighbor Search for GPUs](https://arxiv.org/pdf/2308.15136)
2. OpenSearch Vector Engine のインデックス作成パフォーマンス向上のための[メタイシュー](https://github.com/opensearch-project/k-NN/issues/1599)
3. [GPU を使用した OpenSearch Vector Engine パフォーマンスの向上](https://github.com/opensearch-project/k-NN/issues/2293) RFC
4. CAGRA インデックスとの統合に使用される [Faiss ライブラリ](https://github.com/facebookresearch/faiss)
5. OpenSearch クラスターのセットアップ用ワーカーイメージは[こちら](https://github.com/navneet1v/VectorSearchForge/tree/main/remote-index-build-service)
6. リモートインデックス構築ワーカーとのインデックス構築を統合するための [OpenSearch Vector Engine コード](https://github.com/navneet1v/k-NN/tree/remote-vector-staging-2.19)
7. OpenSearch クラスターのセットアップ用 [OpenSearch クラスター CDK](https://github.com/opensearch-project/opensearch-cluster-cdk)
