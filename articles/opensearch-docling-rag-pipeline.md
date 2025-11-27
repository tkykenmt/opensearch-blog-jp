---
title: "[翻訳] Docling と OpenSearch で強力な RAG パイプラインを構築する"
emoji: "🔍"
type: "tech"
topics: ["opensearch"]
published: true
published_at: 2025-11-11
publication_name: "opensearch"
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/building-powerful-rag-pipelines-with-docling-and-opensearch/

Retrieval-Augmented Generation (RAG) は、信頼性の高いドメイン特化型 AI システムを構築するうえで欠かせないアプローチとなっています。検索システムと大規模言語モデル (LLM) を組み合わせることで、外部の知識ソースに基づいた出力を生成できるのが RAG の強みです。しかし、複雑な企業向けドキュメントや大規模な検索を扱う場合、信頼性の高い RAG システムの構築は依然として難しい課題です。特に「正確なドキュメントの取り込み」と「高品質な検索」という 2 つのボトルネックが頻繁に問題となります。

ここで [Docling](https://github.com/docling-project/docling) と [OpenSearch](https://opensearch.org/) の出番です。Docling は正確なドキュメント解析と構造化を実現し、OpenSearch はスケーラブルでメタデータを活用した検索・取得を可能にします。この組み合わせにより、多様なドキュメント形式から知識を正確に抽出し、効率的に取得できる RAG 基盤を構築できます。

## Docling とは

[Docling](https://github.com/docling-project/docling) は、複雑なドキュメントを構造化された機械可読データに変換するオープンソースのドキュメント処理ツールキットです。生成 AI システムをはじめとする様々な AI アプリケーションで活用できます。PDF、DOCX、PPTX など幅広いドキュメント形式に対応し、レイアウト、テーブル、読み順といった重要な構造情報を保持したまま解析できます。解析したコンテンツは Markdown、JSON、HTML 形式でエクスポートでき、最新の AI ワークフローへの組み込みも容易です。

Docling はもともと IBM Research で開発され、2025 年 4 月に LF AI & Data Foundation のインキュベーションステージプロジェクトとして寄贈されました。以来、コミュニティでの採用が急速に進み、GitHub で 42,000 以上のスター、2,400 の GitHub 組織での利用、PyPI からの月間 150 万ダウンロードを達成しています。柔軟なシリアライザー、メタデータエンリッチメント、階層的チャンキング機能を備え、生成 AI エコシステムとシームレスに連携できます。これらはすべて、高品質な RAG ワークフローを実現するための重要な要素です。

## Docling と OpenSearch を RAG に組み合わせる理由

Docling と OpenSearch を組み合わせることで、RAG における 2 つの課題を同時に解決できます。

- Docling は、入力ドキュメントを豊富なメタデータを持つ、構造化された意味のあるチャンクに変換します
- OpenSearch は、埋め込みの保存、ベクトル類似性検索の実行、メタデータによる結果のフィルタリングや集約が可能な、スケーラブルで高性能な検索エンジンを提供します

この組み合わせにより、実際のデータを扱う際にも正確で説明可能、かつ堅牢な AI アプリケーションを構築できます。

## Docling と OpenSearch を活用した高度な RAG

Docling と OpenSearch を統合することで、RAG アプリケーションを構築する開発者は以下のようなメリットを得られます。

### Docling による高精度なドキュメント変換

Docling は、PDF、DOCX、HTML などさまざまなドキュメント形式を解析し、JSON 形式の構造化表現 (DoclingDocument) に変換できます。この表現では、セクションやサブセクションなどの階層関係が保持され、テーブルや図といった複雑なデータも適切に格納されます。また、マルチモーダル入力にも対応しており、音声ファイルの文字起こしや画像に対するビジョンモデルの実行による説明的なキャプション生成も可能です。これらの機能により、複数の形式のドキュメントを単一の一貫した表現で扱う RAG パイプラインを構築できます。

例: Docling の Python API を使用して PDF を構造化データに変換

```python
from docling.document_converter import DocumentConverter

# ドキュメントのパスまたは URL を指定
source = "https://arxiv.org/pdf/2408.09869"

# 構造化形式 (DoclingDocument) に変換
converter = DocumentConverter()
doc = converter.convert(source).document

# 解析された構造を確認
print(len(doc.tables))
#> 3

# Markdown 形式でエクスポート
print(doc.export_to_markdown())
#> "## Docling Technical Report[...]"
```

### チャンキングとカスタムシリアライゼーション

Docling は、ドキュメントを意味のある構造化された単位に分割するための柔軟なチャンキング機能を提供します。HierarchicalChunker は、セクション、段落、テーブル、図などの意味的に一貫したセグメントにコンテンツを分割し、メタデータには論理的なドキュメント階層を保持します。この構造を意識したアプローチにより、検索結果の精度と解釈しやすさが向上します。

さらに Docling は、階層的チャンキングにトークン化を考慮した改良を加えた HybridChunker も提供しています。このハイブリッドアプローチにより、生成されるチャンクが埋め込みモデルに最適なサイズとなり、意味的な整合性を保ちながらモデルのトークン制限にも対応できます。

また、表形式データ用の Markdown シリアライザーなど、カスタムシリアライザーもサポートしています。これにより、生成モデルが情報の構造とコンテキストを理解しやすくなります。ハイブリッドチャンキングと構造化シリアライゼーション、そして OpenSearch のベクトルインデックス作成を組み合わせることで、高精度なドキュメント理解、スケーラブルなストレージ、正確な検索を兼ね備えた RAG パイプラインを構築できます。

### OpenSearch によるコンテキストを考慮した検索

OpenSearch はメタデータフィルタリング付きのベクトル検索をサポートしており、意味的類似性だけでなく、Docling が提供するセクションタイプ、テーブルの有無、ドキュメントソースなどのコンテキスト情報も考慮した検索が可能です。これにより、定量的データや特定のドキュメントセクションに焦点を当てるといったドメイン固有の検索戦略を実現でき、より関連性が高く正確な生成出力を得られます。

### コンテキスト拡張によるより良い回答

Docling はチャンクメタデータに階層関係を保持するため、検索時にコンテキストを拡張できます。たとえば、あるサブセクションが検索でヒットした場合、親セクションの関連チャンクを自動的に含めることで、より一貫したコンテキストを提供できます。この拡張により、モデルが一貫性のある文脈的に完全な入力を受け取れるため、ハルシネーション(幻覚)が減少し、事実の正確性が向上します。

## RAG ワークフローでの Docling と OpenSearch の統合

[LlamaIndex](https://github.com/run-llama/llama_index) フレームワークは、ドキュメントパーサー、ベクトルストア、LLM を接続することで RAG のオーケストレーションを簡素化します。Docling は取り込みと構造化を担うコンポーネントとしてこのワークフローに自然に組み込まれ、OpenSearch はベクトルとメタデータのストアとして機能します。

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

### 変換処理の定義

データを取り込む前に、DoclingDocument に適用する変換処理を定義します。

- `DoclingNodeParser` はドキュメントベースのチャンキングを実行します
- `MetadataTransform` は、生成されたチャンクのメタデータが OpenSearch でのインデックス作成に適した形式になるよう整形します

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

ベクトル検索が有効な単一の OpenSearch インデックスのロジックをカプセル化する `OpenSearchVectorClient` を作成します。次に、変換済みのファイル、Docling ノードパーサー、作成した OpenSearch クライアントを使用してインデックスを初期化します。DoclingDocument オブジェクトがチャンク化され、計算された埋め込みが OpenSearch に保存・インデックス化されます。

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

LlamaIndex のクエリエンジンを使用すると、RAG システムを簡単に実行できます。

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

この例は、Docling のドキュメント理解機能と OpenSearch の検索機能を組み合わせることで、堅牢な RAG アプリケーションを簡単に構築できることを示しています。

## さらに詳しく

これらの統合や機能についてより詳しく知りたい方は、以下のリソースをご参照ください。

- [Docling ウェブサイト](https://www.docling.ai/)
- [OpenSearch を使用した RAG のサンプルノートブック](https://github.com/docling-project/docling/blob/main/docs/examples/rag_opensearch.ipynb)
- [OpenSearch ベクトル検索ドキュメント](https://docs.opensearch.org/latest/vector-search/)

Docling の高度なドキュメント理解機能と OpenSearch のスケーラブルな検索機能を組み合わせることで、複雑な質問に対しても根拠に基づいた高品質な回答を提供できる RAG システムを構築できます。
