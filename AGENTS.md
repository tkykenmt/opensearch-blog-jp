# OpenSearch Blog Japanese Translation

OpenSearch Project の日本語コンテンツを Zenn で公開するプロジェクト。

## プロジェクト構成

```
├── articles/          # Zenn 記事ファイル (.md)
├── images/            # 記事内画像 (images/<slug>/)
├── .github/           # Issue テンプレート等
└── .kiro/
    ├── agents/        # エージェント設定
    ├── prompts/       # プロンプトファイル
    └── commands/      # 実行スクリプト
```

## 公開先

https://zenn.dev/opensearch

## エージェント一覧

| エージェント | 用途 |
| --- | --- |
| opensearch-blog-translator | OpenSearch Blog 記事の日本語翻訳 |
| opensearchcon-session-writer | OpenSearchCon セッション動画の文字起こし記事作成 |

## Git ルール

- main ブランチへの直接コミット禁止
- 作業は機能ブランチで実施し PR 経由でマージ
- HTTPS + トークン認証を使用（SSH 禁止）

## 環境変数

| 変数 | 用途 |
| --- | --- |
| `GITHUB_TOKEN` | GitHub API / git push 認証 |

## 前提ツール

- Node.js (npm)
- git, curl
- yt-dlp（セッション記事作成時）
- ffmpeg（タイムスタンプ別サムネイル抽出用）
