# OpenSearch Blog Japanese Translation

OpenSearch Project の日本語コンテンツを Zenn で公開するプロジェクト。

## プロジェクト構成

```
├── scripts/           # ワークフロー用スクリプト
├── lib/               # 共通ライブラリ
├── articles/          # Zenn 記事ファイル (.md)
├── images/            # 記事内画像 (images/<slug>/)
├── .github/           # Issue テンプレート等
└── .kiro/
    ├── agents/        # エージェント設定
    ├── prompts/       # プロンプトファイル
    └── skills/        # SKILL ドキュメント
```

## 公開先

https://zenn.dev/opensearch

## エージェント一覧

| エージェント | 用途 | 実行方法 |
|---|---|---|
| orchestrator | ワークフロー全体の管理（取得→翻訳→レビュー→修正→公開） | `kiro-cli chat --agent orchestrator` |
| translator | OpenSearch Blog 記事の日本語翻訳 | orchestrator の sub-agent |
| reviewer | 翻訳記事の AI レビュー | orchestrator の sub-agent |
| fixer | レビュー指摘に基づく修正 | orchestrator の sub-agent |
| session-writer | OpenSearchCon セッション動画の記事作成 | orchestrator の sub-agent |
| dev | ツール自体の開発・改善 | `kiro-cli chat --agent dev` |

## ワークフロー

orchestrator エージェントが以下のフローを自動管理:

1. GitHub Issue 作成
2. `scripts/fetch.py` で記事取得・画像 DL
3. translator sub-agent で翻訳
4. `scripts/check.py` で自動チェック
5. reviewer sub-agent で AI レビュー
6. (エラーあれば) fixer sub-agent で修正 → 4 に戻る
7. `scripts/publish.py` で commit・push
8. GitHub MCP で PR 作成・マージ
9. 公開確認・Issue クローズ

## Git ルール

- main ブランチへの直接コミット禁止
- 作業は `article/{slug}` ブランチで実施し PR 経由でマージ
- HTTPS + トークン認証を使用（SSH 禁止）

## 認証

GitHub CLI でログイン済みであること（`gh auth login`）。MCP サーバーが `gh auth token` でトークンを取得します。

## 前提ツール

- [Kiro CLI](https://kiro.dev/)
- Python 3.10+
- Node.js (npm)
- git, gh (GitHub CLI)
- yt-dlp（セッション記事作成時）
- ffmpeg（タイムスタンプ別サムネイル抽出用）
