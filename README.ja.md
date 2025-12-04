# OpenSearch Blog 日本語翻訳

[OpenSearch Project Blog](https://opensearch.org/blog/) の記事を日本語に翻訳し、[Zenn](https://zenn.dev/opensearch) で公開しています。

## 公開先

https://zenn.dev/opensearch

## ローカル環境

```bash
npm install
npx zenn preview
```

## セットアップ

### 事前要件

- [Kiro CLI](https://kiro.dev/) がインストールされていること
- Node.js (npm)
- git, curl

### Kiro CLI のインストール

macOS:
```bash
curl -fsSL https://cli.kiro.dev/install | bash
```

Ubuntu:
```bash
wget https://desktop-release.q.us-east-1.amazonaws.com/latest/kiro-cli.deb
sudo dpkg -i kiro-cli.deb
```

その他の Linux は [公式ドキュメント](https://kiro.dev/docs/cli/installation/) を参照してください。

### 環境変数

翻訳タスクの実行には以下の環境変数が必要です。

| 変数名 | 説明 |
| --- | --- |
| `GITHUB_TOKEN` | GitHub API 認証用トークン |

### リポジトリ設定

Settings > General > Pull Requests で「Automatically delete head branches」を ON にすることを推奨します。

## 翻訳の実行

```bash
.kiro/commands/translate-opensearch-blog.sh <記事URL>
```

複数の記事を一度に翻訳する場合:

```bash
.kiro/commands/translate-opensearch-blog.sh <URL1> <URL2> ...
```

## 貢献

翻訳リクエストは [Issue](../../issues) からお願いします。
