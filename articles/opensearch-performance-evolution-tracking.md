---
title: "[翻訳] OpenSearch パフォーマンスの進化を追跡する"
emoji: "📊"
type: "tech"
topics: ["opensearch", "performance", "benchmark"]
published: true
published_at: 2025-03-06
publication_name: "opensearch"
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/tracking-the-evolution-of-opensearch-performance/

独立した調査・コンサルティング会社である [Trail of Bits](https://www.trailofbits.com/) が、OpenSearch のパフォーマンスに関する詳細な分析を完了しました。Big5 ワークロードの主要なパフォーマンスメトリクスについては、[記事](https://blog.trailofbits.com/2025/03/06/benchmarking-opensearch-and-elasticsearch/)と[詳細分析](https://github.com/trailofbits/publications/blob/master/reports/OpenSearch-Benchmarking.pdf)を参照してください。

[OpenSearch](https://opensearch.org/) は、Linux Foundation 傘下の完全オープンソース、Apache v2 ライセンスのプロジェクトであり、字句検索、ログ分析、セマンティック検索および生成 AI ワークロード向けのベクトルデータベースを提供します。このプロジェクトには、検索エンジンである [OpenSearch](https://github.com/opensearch-project/OpenSearch)、可視化および監視 UI である [OpenSearch Dashboards](https://opensearch.org/docs/latest/dashboards/)、インジェストおよび処理エンジンである [OpenSearch Data Prepper](https://opensearch.org/docs/latest/data-prepper/)、OpenSearch のパフォーマンスを測定するためのベンチマークツールである [OpenSearch Benchmark](https://opensearch.org/docs/latest/benchmark/) が含まれています。
