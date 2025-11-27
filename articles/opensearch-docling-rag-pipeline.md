---
title: "[翻訳] Docling と OpenSearch で強力な RAG パイプラインを構築する"
emoji: "🔍"
type: "tech"
topics: ["opensearch"]
published: false
published_at: 2025-11-11
publication_name: "opensearch"
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/building-powerful-rag-pipelines-with-docling-and-opensearch/

Retrieval-Augmented Generation (RAG) は、信頼性の高いドメイン特化型 AI システムを構築するための重要なアプローチとなっています。検索システムと大規模言語モデル (LLM) を組み合わせることで、RAG は外部の知識ソースに基づいた出力を生成できます。しかし、特に複雑なエンタープライズドキュメントや大規模な検索を扱う場合、信頼性の高い RAG システムの構築は依然として困難です。主に 2 つのボトルネックが頻繁に発生します。正確なドキュメント取り込みと高品質な検索です。ここで [Docling](https://github.com/docling-project/docling) と [OpenSearch](https://opensearch.org/) が強力なソリューションを提供します。Docling は正確なドキュメント解析と構造化を保証し、OpenSearch はスケーラブルでメタデータを考慮した検索と取得を可能にします。その結果、多様なドキュメントタイプにわたって知識を正確に表現し、効率的に取得できる RAG 基盤が実現します。

## Docling とは

[Docling](https://github.com/docling-project/docling) は、複雑なドキュメントを構造化された機械可読データに変換し、生成 AI システムを含む AI アプリケーションに活用できるオープンソースのドキュメント処理ツールキットです。PDF、DOCX、PPTX などの幅広いドキュメント形式を解析でき、レイアウト、テーブル、読み順などの重要な構造情報を保持します。解析されたコンテンツは Markdown、JSON、HTML としてエクスポートでき、最新の AI ワークフローにドキュメントデータを簡単に組み込むことができます。

もともと IBM Research で開発された Docling は、2025 年 4 月に LF AI & Data Foundation のインキュベーションステージプロジェクトとして寄贈されました。以来、コミュニティでの採用が急速に進み、GitHub で 42,000 以上のスター、2,400 の GitHub 組織での使用、PyPI から月間 150 万ダウンロードを記録しています。Docling は、柔軟なシリアライザー、メタデータエンリッチメント、階層的チャンキングメカニズムを提供し、より広範な生成 AI エコシステムとシームレスに統合されます。これらはすべて、高品質な RAG ワークフローの重要な実現要素です。

## Docling と OpenSearch を RAG に組み合わせる理由

Docling と OpenSearch を組み合わせることで、RAG の課題の両面に対処できます。

- Docling は、入力ドキュメントを豊富なメタデータを持つ構造化された意味的に意味のあるチャンクに変換します
- OpenSearch は、埋め込みの保存、ベクトル類似性検索の実行、メタデータを使用した結果のフィルタリングや集約が可能なスケーラブルで高性能な検索エンジンを提供します

この組み合わせにより、開発者は実世界のデータを扱う際に正確で説明可能かつ堅牢な AI アプリケーションを構築できます。

## Docling と OpenSearch を活用した高度な RAG

Docling と OpenSearch の統合により、RAG アプリケーションを構築する開発者にいくつかの重要なメリットがもたらされます。

### Docling による忠実なドキュメント変換

Docling は、PDF、DOCX、HTML などのさまざまなドキュメント形式を解析し、JSON 形式の構造化表現 (DoclingDocument) に変換できます。この表現は、セクションやサブセクションなどの階層的な関係を保持し、テーブルや図などの複雑なデータを保存します。Docling はマルチモーダル入力もサポートしており、音声ファイルの文字起こしや画像に対するビジョンモデルの実行により説明的なキャプションを生成できます。これらの機能を融合することで、開発者は複数の形式から単一の一貫した表現で RAG パイプラインを構築できます。

例: Docling の Python API を使用して PDF を構造化データに解析

```python
from docling.document_converter import DocumentConverter

# ドキュメントのパスまたは URL
source = "https://arxiv.org/pdf/2408.09869"

# 構造化形式 (DoclingDocument) に変換
converter = DocumentConverter()
doc = converter.convert(source).document

# 解析された構造を確認
print(len(doc.tables))
#> 3

# Markdown 形式にエクスポート
print(doc.export_to_markdown())
#> "## Docling Technical Report[...]"
```

### チャンキングとカスタムシリアライゼーション

Docling は、開発者がドキュメントを意味のある構造化された単位にセグメント化できる柔軟なチャンキングメカニズムを提供します。HierarchicalChunker は、セクション、段落、テーブル、図などの意味的に一貫したセグメントにコンテンツを分割し、メタデータに論理的なドキュメント階層を保持します。この構造を意識したアプローチにより、検索結果の精度と解釈可能性が向上します。

この基盤の上に、Docling は HybridChunker を導入しています。これは階層的チャンキングの上にトークン化を考慮した改良を適用します。ハイブリッドアプローチにより、結果のチャンクが埋め込みモデルに最適なサイズになり、意味的整合性を維持しながらモデルのトークン制限を尊重します。

さらに、Docling は表形式データ用の Markdown シリアライザーなどのカスタムシリアライザーをサポートしています。これらのシリアライザーにより、生成モデルが情報の構造とコンテキストを理解しやすくなります。ハイブリッドチャンキングと構造化シリアライゼーション、OpenSearch のベクトルインデックス作成を組み合わせることで、開発者は高忠実度のドキュメント理解、スケーラブルなストレージ、正確な検索を実現する RAG パイプラインを構築できます。

### OpenSearch を使用したコンテキスト認識検索

OpenSearch はメタデータフィルタリングを備えたベクトル検索をサポートしており、Docling が提供するセクションタイプ、テーブルの有無、ドキュメントソースなどの意味的類似性とコンテキストフィールドの両方を考慮した検索が可能です。これにより、定量的データや特定のドキュメントセクションに焦点を当てるなど、ドメイン固有の検索戦略が可能になり、より関連性が高く正確な生成出力が得られます。

### より良い回答のためのコンテキスト拡張

Docling はチャンクメタデータに階層的な関係を保持するため、検索時のコンテキスト拡張が可能になります。たとえば、サブセクションが検索された場合、親セクションの関連チャンクを自動的に含めて、より一貫したコンテキストを提供できます。この拡張により、モデルが一貫性のある文脈的に完全な入力を受け取ることが保証され、幻覚が減少し、事実の正確性が向上します。

## RAG ワークフローでの Docling と OpenSearch の統合

[LlamaIndex](https://github.com/run-llama/llama_index) フレームワークは、ドキュメントパーサー、ベクトルストア、LLM を接続することで RAG オーケストレーションを簡素化します。Docling は取り込みと構造化コンポーネントとしてこのワークフローに自然に統合され、OpenSearch はベクトルとメタデータストアとして機能します。

### ファイルの読み込み

```python
from llama_index.core import SimpleDirectoryReader
from llama_index.readers.docling import DoclingReader

my_docs = "/path/to/my/documents"
reader = DoclingReader(export_type=DoclingReader.ExportType.JSON)
dir_reader = SimpleDirectoryReader(
    input_dir=my_docs,
    file_extractor={".pdf": reader},
)
documents = dir_reader.load_data()
```

### 変換の定義

データを取り込む前に、DoclingDocument に適用する変換を定義します。

- `DoclingNodeParser` はドキュメントベースのチャンキングを実行します
- `MetadataTransform` は、生成されたチャンクメタデータが OpenSearch でのインデックス作成に正しくフォーマットされることを保証します

```python
from docling.chunking import HybridChunker
from llama_index.node_parser.docling import DoclingNodeParser

node_parser = DoclingNodeParser(chunker=HybridChunker())

class MetadataTransform(TransformComponent):
    def __call__(self, nodes, **kwargs):
        for node in nodes:
            binary_hash = node.metadata.get("origin", {}).get("binary_hash", None)
            if binary_hash is not None:
                node.metadata["origin"]["binary_hash"] = str(binary_hash)
        return nodes
```

### 埋め込みの計算、挿入、インデックス作成

ベクトル検索が有効な単一の OpenSearch インデックスのロジックをカプセル化する `OpenSearchVectorClient` を作成します。次に、変換されたファイル、Docling ノードパーサー、作成した OpenSearch クライアントを使用してインデックスを初期化します。DoclingDocument オブジェクトはチャンク化され、計算された埋め込みが OpenSearch に保存およびインデックス化されます。

```python
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.opensearch import (
    OpensearchVectorClient,
    OpensearchVectorStore,
)

opensearch_endpoint = "http://localhost:9200"  # OpenSearch エンドポイントを設定
text_field = "content"
embed_field = "embedding"
embed_model = OllamaEmbedding(model_name="granite-embedding:30m")  # LlamaIndex 埋め込みオブジェクトを設定
embed_dim = len(embed_model.get_text_embedding("hi"))

client = OpensearchVectorClient(
    endpoint="http://localhost:9200",
    index=opensearch_endpoint,
    dim=embed_dim,
    embedding_field=embed_field,
    text_field=text_field,
)

vector_store = OpensearchVectorStore(client)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

index = VectorStoreIndex.from_documents(
    documents=documents,
    transformations=[node_parser, MetadataTransform()],
    storage_context=storage_context,
    embed_model=embed_model,
)
```

### RAG システムの組み立てと実行

LlamaIndex のクエリエンジンを使用すると、次のように RAG システムを簡単に実行できます。

```python
from llama_index.llms.ollama import Ollama
from rich.console import Console

gen_model = Ollama(model="granite4:micro")  # LlamaIndex LLM オブジェクトを設定
console = Console(width=88)
query = "Which are the main AI models in Docling?"
query_engine = index.as_query_engine(llm=gen_model)
res = query_engine.query(query)

console.print(f"👤: {query}\n🤖: {res.response.strip()}")
# 👤: Which are the main AI models in Docling?
# 🤖: Docling primarily utilizes two AI models. The first one is a layout analysis model,
# serving as an accurate object-detector for page elements. The second model is
# TableFormer, a state-of-the-art table structure recognition model. Both models are
# pre-trained and their weights are hosted on Hugging Face. They also power the
# deepsearch-experience, a cloud-native service for knowledge exploration tasks.
```

この例は、開発者が Docling のドキュメント理解と OpenSearch の検索機能を簡単に組み合わせて、堅牢な RAG アプリケーションを構築できることを示しています。

## さらに詳しく

これらの統合と機能をより詳しく調べるには、以下のリソースを参照してください。

- [Docling ウェブサイト](https://www.docling.ai/)
- [OpenSearch を使用した RAG のサンプルノートブック](https://github.com/docling-project/docling/blob/main/docs/examples/rag_opensearch.ipynb)
- [OpenSearch ベクトル検索ドキュメント](https://docs.opensearch.org/latest/vector-search/)

Docling の高度なドキュメント理解と OpenSearch のスケーラブルな検索を組み合わせることで、複雑な質問に対して根拠のある高品質な回答を提供する RAG システムを構築できます。
