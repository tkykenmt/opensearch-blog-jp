---
publication_name: "opensearch"
title: "[翻訳] OpenSearch における AI エージェント入門：シンプルなフローエージェントから高度な ReAct マルチエージェントシステムまで"
emoji: "✨"
type: "tech"
topics:
  - "opensearch"
published: false
---

本記事は OpenSearch Project に投稿された [Introduction to AI agents in OpenSearch: From simple flow agents to advanced ReAct multi-agent systems](https://opensearch.org/blog/introduction-to-ai-agents-in-opensearch-from-simple-flow-agents-to-advanced-react-multi-agent-systems/) の日本語訳版です。

AI エージェント（または単にエージェント）とは、大規模言語モデル（LLM）を活用して問題を解決する調整役です。LLM が推論を行い、取るべき行動を決定した後、エージェントはその行動の実行を調整します。

OpenSearch には、検索拡張生成（RAG）、チャットボット、リサーチ、自動根本原因分析（RCA）など、さまざまなAIタスクに対応する多様なエージェントが用意されています。

本ブログでは、OpenSearch がサポートする多様なエージェントについて紹介し、各タスクに最適なエージェントを選択する際の指針を提供します。理解を明確にするため、まずは最もシンプルなエージェントから始め、徐々により複雑なエージェントへと解説を進めていきます。

## フローエージェント

フローエージェントは最もシンプルなタイプのエージェントです。ワークフロー内で複数のツールを連携させ、エージェントの設定で定義された順序に従って順次実行します。 フローエージェントは、固定されたワークフローのオーケストレーターとして機能します。複数のツールを連携させ、あるツールの出力を別のツールの入力として渡すことで、一連の処理を順次実行します。

フローエージェントは [RAG (Retrieval-Augmented Generation)](https://opensearch.org/blog/using-opensearch-for-retrieval-augmented-generation-rag/) の実装において特に有用です。RAG プロセスでは、エージェントはまずツールを呼び出してナレッジベースから情報を取得し、次に別のツールから LLM を呼び出します。この際、前段階で取得した知識ベースの情報を入力として渡し、さらにクエリも渡します。 これは one-shot プロンプトを実装するのに最適な方法です。

詳細については、[Flow agents](https://docs.opensearch.org/latest/ml-commons-plugin/agents-tools/agents/flow/) のページをご覧ください。

## 会話型フローエージェント

フローエージェントと同様に、会話型フローエージェントは設定で指定された順序に従ってツールを順次実行し、固定されたワークフローを実行します。

ただし、会話型フローエージェントは、セッション中のプロンプト間で会話履歴をメモリインデックスに保存します。この履歴により、エージェントがコンテキストを活用してユーザーのフォローアップ質問に対応できるようになります。 会話型フローエージェントはチャットボットに最適です。チャットボットは大部分のユーザーとのやり取りで定義済みの複数ステップにわたるプロセスを実行する必要があり、かつフォローアップ質問に対応するために会話のコンテキストを保持する必要があるためです。この機能は、few-shot プロンプトを使用することで実現されます。新しいプロンプトが送信されるたびに、過去の会話履歴がコンテキストとして活用されます。

会話履歴は OpenSearch クラスタ内のインデックスに保存され、他のデータと同様に管理されます。この履歴は、エージェントや人間が監査、推論、デバッグを行う際に、クエリや検査のために容易にアクセス可能です。データへのアクセスには [Memory API](https://docs.opensearch.org/latest/ml-commons-plugin/api/memory-apis/index/) を使用します。 詳細については、[Agentic Memory](https://github.com/opensearch-project/project-website/diffs/0?base_sha=15afd7078aa5e60e4c3b29778c0ee9cb7eda6d97&head_user=horovits&name=patch-1&pull_number=3961&sha1=15afd7078aa5e60e4c3b29778c0ee9cb7eda6d97&sha2=52f740a6b1c9e3c2508fedf8b977fa3d69c0f158&short_path=172dd17&unchanged=expanded&w=false#agentic-memory) のページをご覧ください。

## 会話型エージェント

これまでに説明したエージェントとは異なり、対話型エージェントは固定のワークフローに縛られていません。代わりに、LLM ベースの推論機能を活用し、ReAct (推論と行動) エージェントフレームワークに基づいて動的なワークフローをサポートします。 LLM は反復的な推論を行い、最終的な回答を得るか、または反復回数の上限に達するまで、取るべき行動を決定し続けます。

会話型エージェントは、LLM に組み込まれたナレッジベースと、ナレッジを超えた追加情報を取得可能なツール群の 2 つを情報源としての推論を行います。

特定の質問に対しては、エージェントは思考の連鎖 (CoT：Chain-of-Thought) プロセスを用いて、設定済みのツール群から最適なツールを選択し、質問への回答を生成します。

会話型フローエージェントと同様に、会話型エージェントは会話履歴を保持するため、ユーザーは追加の質問をすることができます。会話型エージェントのワークフローは可変的で、後続の質問に応じて変化します。

会話型エージェントは、RAG (Retrieval-Augmented Generation) を活用したチャットボットの開発に有用です。

OpenSearch では、内部のこうしたエージェントを使用することで、[自然言語クエリによるエージェント型検索](https://github.com/opensearch-project/ml-commons/blob/main/docs/tutorials/agentic_search/agentic_search_llm_generated_type.md)を実現しています。

## Plan-execute-reflect エージェント
Plan-execute-reflect エージェントは、より高度な動的ワークフローを採用しています。複雑なタスクを解決するため、多段階のワークフローを動的に計画・実行・改善します。

Plan-execute-reflect エージェントは OpenSearch のマルチエージェントパターンを採用しており、エージェントの連鎖やサブエージェントの定義が可能です。このエージェントでは、計画立案フェーズに CoT (Chain of Thought) エージェントを、個々の計画ステップの実行には対話型エージェントを使用します。 このエージェントは、各ステップにおいてツールの説明内容とコンテキストに基づいて最適なツールを自動的に選択します。

 Plan-execute-reflect エージェントは、研究活動や根本原因分析 (Root Cause Analytics - RCA) など、反復的な推論と適応的な実行が有効な、長時間にわたる探索的プロセスに最適です。

Plan-execute-reflect エージェントの詳細については、[こちらの記事](https://zenn.dev/tkykenmt/articles/92f75324721959)をご覧ください。

## エージェントツールと外部データ連携
エージェントの有効性は、利用可能なツールセットの質と多様性によって決まります。OpenSearch のエージェントフレームワークでは、エージェントが標準のプロトコルを使用して、組み込みツールと外部ツールの両方を柔軟に呼び出すことが可能です。

### ビルトインエージェントツール
OpenSearch では、さまざまなエージェントタイプとシームレスに連携可能な、ビルトインの[ツール群](https://docs.opensearch.org/latest/ml-commons-plugin/agents-tools/tools/index/)を提供しています。 ビルトインツールにより、エージェントは OpenSearch 内のデータを効率的に取得・操作でき、データ検索、分析、管理といった基本的な操作が可能になります。

### MCP コネクタを介した外部データソースとの連携
モデルコンテキストプロトコル (MCP) は、エージェント型ワークフローにおける通信規格として急速に普及しており、AI エージェントが外部ツールと連携する際の利便性を大幅に向上させています。

OpenSearch は、[MCP コネクタ](https://docs.opensearch.org/latest/ml-commons-plugin/agents-tools/mcp/index/)を通じてエージェントの機能を拡張し、外部の MCP サーバーおよび関連ツールとの連携を可能にします。 この強力な機能は、Plan-execute-reflect エージェントや対話型エージェントによってサポートされており、外部のデータソースやサービスを活用できるため、OpenSearch 自体の枠を超えて分析機能と運用能力を大幅に拡張することが可能です。 これらのコネクタは Streamable HTTP プロトコルと Server-Sent Events (SSE) プロトコルをサポートしており、多様な外部 MCP サーバーとの連携において高い柔軟性を提供します。 これらのエージェントは、OpenSearch の内部ツールと外部 MCP サーバー上のツールをシームレスに連携させることが可能で、多様なデータソースやサービスを統合したワークフローを構築できます。これにより、複数の情報源からのデータを分析し、高度な意思決定プロセスを実現することが容易になります。

## エージェントメモリ
エージェントはセッションキャッシュを使用して、会話のコンテキストとして過去のプロンプトを保存できます。これにより、同じセッション内での後続の質問が、以前の質問と回答を考慮に入れることが可能になります。ただし、このキャッシュは現在のセッション内に限定されます。 過去の会話から学習し、より深いレベルのパーソナライゼーションや文脈理解をエージェントに行わせたい場合はどうすればよいでしょうか？このような場合には、短期記憶から長期記憶への移行が必要になります。つまり、単一セッションを超えて持続する記憶を保持し、セッション間で情報を引き継ぎ可能な機能が求められるのです。 OpenSearch がこれらのニーズにどのように対応しているか、詳しく見ていきましょう。

2.12リリースにおいて、OpenSearch は [Memory API](https://docs.opensearch.org/latest/ml-commons-plugin/api/memory-apis/index/) を導入しました。これはOpenSearchインデックス内に会話の生メッセージや使用ツールの記録を保存する機能で、会話履歴の取得やトレースを可能にします。 この Memory API は、会話メッセージやツール使用履歴をそのままの形式で保持し、一種の短期記憶として機能します。

近年、OpenSearch は長期記憶機能もサポートするようになり、新たに「エージェント型メモリ」(agentic memory) 機能が追加されました。 [OpenSearch 3.2](https://opensearch.org/blog/introducing-opensearch-3-2-next-generation-search-and-anayltics-with-enchanced-ai-capabilities/) で導入され、OpenSearch 3.3 で一般提供が開始された agentic memory は、AI エージェントが会話やインタラクションを横断して学習・記憶・推論を行うことを可能にする永続的なメモリシステムです。 この機能は、意味的事実の抽出、ユーザーの嗜好学習、会話要約など、複数の戦略を活用した包括的な記憶管理を提供します。 この機能により、エージェントは会話の文脈を保持し、知識を蓄積し続けることができます。また、記憶の統合・検索・履歴追跡といった高度なメモリ操作も可能になります。

この機能によってエージェントに検索可能な永続記憶が付与されることで、静的な AI インタラクションが、時間とともに進化し、よりコンテキストを認識した動的な体験へと変化します。これにより、よりパーソナライズされたインテリジェントな応答が可能になるとともに、記憶の整理方法や保持ポリシーについてもユーザーが制御できるようになります。 詳細については、[Agentic memory](https://docs.opensearch.org/latest/ml-commons-plugin/agentic-memory/) のドキュメントを参照してください。

## MCPサーバーを利用したエージェント型体験
外部エージェントも、標準MCP経由でツール機能として公開されるOpenSearchの機能を活用することで恩恵を受けられます。OpenSearchでは、多様な統合ニーズに対応するため、以下の2つの包括的な [MCP サーバーソリューション](https://opensearch.org/blog/introducing-mcp-in-opensearch/)を提供しています。

1. ビルトイン MCP サーバー: [ビルトイン MCP サーバー](https://docs.opensearch.org/latest/ml-commons-plugin/api/mcp-server-apis/index/)は OpenSearch 内にネイティブに統合されており、動的なツールの登録・削除が可能な Streamable HTTP 形式の MCP API を提供します。 このソリューションでは、エージェントがOpenSearch の主要機能をシームレスに利用でき、リアルタイムのデータクエリや分析を行うための強力な[ツール](https://docs.opensearch.org/latest/ml-commons-plugin/agents-tools/tools/index/)を呼び出すことが可能です。 このソリューションは `/_plugins/_ml/mcp` エンドポイントを通じて OpenSearch の API に直接アクセスするため、ロールベースアクセス制御 (RBAC) に標準で対応しており、安全かつ詳細なアクセス管理が可能です。
1. スタンドアロン MCP サーバー: [スタンドアロン MCP サーバー](https://github.com/opensearch-project/opensearch-mcp-server-py/blob/main/USER_GUIDE.md)は、`opensearch-mcp-server-py` PyPI パッケージを通じて柔軟なデプロイオプションを提供します。このソリューションは `stdio`、Streamable HTTP、SSE など複数のプロトコルをサポートしており、さまざまな AI エージェントフレームワークとの互換性を備えています。 高度な機能として、ツールフィルタリング機能やマルチクラスター接続機能を備えており、分散環境においても洗練されたエージェントワークフローを実現できます。

どちらのソリューションも、エージェントが検索データに安全かつリアルタイムでアクセスできるようにし、OpenSearch ツールを他の MCP サーバーや外部ツールと連携させることで、高度な分析処理を可能にします。具体的な実装例や活用事例については、こちらの[記事](https://opensearch.org/blog/unlocking-agentic-ai-experiences-with-opensearch/)をご覧ください。

## まとめ
OpenSearchでは、さまざまな AI タスクに対応する多様なエージェントを提供しています。これらのエージェントは、固定されたワークフローから動的なワークフローまで幅広く、簡潔で焦点を絞ったロジック処理から、長時間にわたる探索的プロセスまで、あらゆるタスクに対応しています。

OpenSearch でエージェントを使い始めるには、[チュートリアル](https://docs.opensearch.org/latest/ml-commons-plugin/agents-tools/agents-tools-tutorial/)に記載されている段階的なセットアップ手順に従ってください。

