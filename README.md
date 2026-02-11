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
- yt-dlp (セッション記事用)
- ffmpeg (セッション記事用)

### 環境変数

| 変数 | 説明 |
|------|------|
| `GITHUB_TOKEN` | GitHub API 認証トークン |

## 使い方

### Blog 翻訳

```bash
# 1. 記事を取得 & 翻訳（work/{slug}/content.html → work/{slug}/translated.md）
python translate.py -u https://opensearch.org/blog/some-article/

# 2. レビュー
python review.py --slug <slug>

# 3. 公開
python publish.py --slug <slug>
```

取得のみ（翻訳スキップ）:
```bash
python translate.py -u https://opensearch.org/blog/some-article/ --no-translate
```

### セッション記事

```bash
# 1. 動画から素材を取得
python session.py --urls https://www.youtube.com/watch?v=xxx

# 2. Kiro で記事作成
kiro-cli chat --agent session-writer

# 3. レビュー
python review.py --slug <slug>

# 4. 公開
python publish.py --slug <slug>
```

## ディレクトリ構成

```
opensearch-blog-jp/
├── translate.py          # 翻訳 CLI
├── session.py            # セッション CLI
├── review.py             # レビュー CLI
├── publish.py            # 公開 CLI
├── lib/                  # 共通ライブラリ
├── work/                 # 作業ディレクトリ（.gitignore）
├── articles/             # Zenn 記事
├── images/               # Zenn 画像
└── .kiro/
    ├── skills/           # Skill ドキュメント
    └── agents/           # エージェント設定
```

## エージェント

| エージェント | 用途 |
|-------------|------|
| translator | Blog 翻訳 |
| session-writer | セッション記事作成 |
| reviewer | 記事レビュー |

## ローカルプレビュー

```bash
npm install
npx zenn preview
```

## Contributing

翻訳リクエストは [Issues](../../issues) から。
