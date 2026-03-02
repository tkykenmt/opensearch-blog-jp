# OpenSearch Blog Japanese Translation

OpenSearch Project Blog の記事を日本語に翻訳して Zenn に公開するツール。

## Publication

https://zenn.dev/opensearch

## セットアップ

### 必要なツール

- [Kiro CLI](https://kiro.dev/)
- Python 3.10+
- Node.js (npm)
- git
- gh (GitHub CLI)
- yt-dlp (セッション記事用)
- ffmpeg (セッション記事用)

### 認証

GitHub CLI でログイン済みであること（`gh auth login`）。MCP サーバーが `gh auth token` でトークンを取得します。

## 使い方

### オーケストレーター（推奨）

Kiro CLI の orchestrator エージェントがワークフロー全体を管理します。

```bash
kiro-cli chat --agent orchestrator
```

翻訳する記事の URL またはセッション動画の URL を伝えるだけで、取得→翻訳→レビュー→修正→公開まで自動で実行します。

### 手動実行

個別のスクリプトを手動で実行することもできます。

#### Blog 翻訳

```bash
# 1. 記事を取得
python scripts/fetch.py -u https://opensearch.org/blog/some-article/

# 2. 翻訳（Kiro translator エージェント）
kiro-cli chat --agent translator

# 3. 自動チェック
python scripts/check.py --slug <slug>

# 4. AI レビュー（Kiro reviewer エージェント）
kiro-cli chat --agent reviewer

# 5. 修正（必要な場合、Kiro fixer エージェント）
kiro-cli chat --agent fixer

# 6. 公開（commit & push）
python scripts/publish.py --slug <slug>

# 7. PR 作成・マージは GitHub MCP または gh CLI で実施
```

#### セッション記事

```bash
# 1. 動画から素材を取得
python session.py --urls https://www.youtube.com/watch?v=xxx

# 2. 記事作成（Kiro session-writer エージェント）
kiro-cli chat --agent session-writer

# 3〜7. Blog 翻訳と同じ
```

#### 作業状況の確認

```bash
python scripts/status.py           # 一覧
python scripts/status.py --slug <slug>  # 詳細
```

## ディレクトリ構成

```
opensearch-blog-jp/
├── scripts/              # ワークフロー用スクリプト
│   ├── fetch.py          # 記事取得・画像DL
│   ├── check.py          # 自動チェック
│   ├── publish.py        # ファイルコピー・commit・push
│   └── status.py         # 作業状況確認
├── lib/                  # 共通ライブラリ
├── work/                 # 作業ディレクトリ（.gitignore）
├── articles/             # Zenn 記事
├── images/               # Zenn 画像
├── session.py            # セッション素材取得
└── .kiro/
    ├── agents/           # エージェント設定
    ├── prompts/          # プロンプトファイル
    └── skills/           # SKILL ドキュメント
```

## エージェント

| エージェント | 用途 | 実行方法 |
|-------------|------|---------|
| orchestrator | ワークフロー全体の管理 | `kiro-cli chat --agent orchestrator` |
| translator | Blog 翻訳 | orchestrator の sub-agent |
| reviewer | AI レビュー | orchestrator の sub-agent |
| fixer | レビュー指摘の修正 | orchestrator の sub-agent |
| session-writer | セッション記事作成 | orchestrator の sub-agent |
| dev | ツール自体の開発・改善 | `kiro-cli chat --agent dev` |

## ローカルプレビュー

```bash
npm install
npx zenn preview
```

## Contributing

翻訳リクエストは [Issues](../../issues) から。
