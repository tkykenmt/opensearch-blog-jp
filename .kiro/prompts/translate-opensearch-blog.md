# OpenSearch Blog 翻訳タスク

指定した URL の blog を翻訳して Zenn に公開する。コンテンツ取得には `web_fetch` ツールを使用すること。GitHub 操作はローカル git コマンドと GitHub MCP を適切に使い分けること。

## リポジトリ情報の取得

最初にローカルの `.git/config` を読み取り、以下の情報を取得:

- `owner`: リモート URL から抽出 (例: `github.com/owner/repo` の `owner`)
- `repo`: リモート URL から抽出 (例: `github.com/owner/repo` の `repo`)

この情報を以降の GitHub MCP 操作で使用する。

## Git 認証

Git コマンドラインでは必ず HTTPS 形式でトークンを含めた URL を使用すること（SSH 形式は使用禁止）。

環境変数 `GITHUB_TOKEN` を使用して認証付き URL を構築:

```
https://${GITHUB_TOKEN}@github.com/<owner>/<repo>.git
```

Git コマンドは `git pull`、`git push`、`git fetch` およびローカル操作（`git checkout`、`git add`、`git commit` 等）に限定する。リモートリポジトリの参照（ブランチ一覧取得等）は GitHub MCP を使用すること。

## 事前確認

1. `git branch --show-current` で現在のブランチを確認し、main 以外なら `git stash && git checkout main` を実行
2. GitHub MCP の `list_issues` で既存の翻訳リクエスト Issue を確認。Issue が存在する場合はエラーなどの指摘が無いか内容をチェックする
3. GitHub MCP の `get_file_contents` でリポジトリのブランチ一覧を取得し、対応中のブランチがあるか確認
4. 対応中のリクエストは途中から作業を再開
5. 未対応の場合のみ最初から作業を実施

## ワークフロー

### 1. slug 決定

記事内容に基づき slug を決定。prefix は `opensearch-`、文字数は 12 文字以上 50 文字以内。利用可能な文字は英数字とハイフンのみ

### 2. Issue 作成

GitHub MCP の `create_issue` で Issue を作成。テンプレート `.github/ISSUE_TEMPLATE/translation.yml` の形式に準拠:

- Title: `[Translation] <記事タイトル>`
- Labels: `["translation"]`
- Body:

  ```
  Original URL： <元記事の URL>
  slug: <slug>
  ```

### 3. ブランチ作成・チェックアウト

```bash
git checkout main
git pull https://${GITHUB_TOKEN}@github.com/<owner>/<repo>.git main
git checkout -b translate/<slug>
```

### 4. 翻訳ファイル作成

1. `npx zenn new:article --slug <slug>` でファイル作成
2. 翻訳内容を追加
3. 画像をダウンロードして配置

### 5. セルフレビュー

翻訳内容をチェックし、問題があれば修正。

### 6. コミット・プッシュ

```bash
git add -A
git commit -m "feat: add translation for <記事タイトル> (#<Issue番号>)"
git push https://${GITHUB_TOKEN}@github.com/<owner>/<repo>.git translate/<slug>
```

### 7. PR 作成

GitHub MCP の `create_pull_request` で PR 作成:

- Title: `[Translation] <記事タイトル>`
- Body: `#<Issue番号>`
- Base: main, Head: translate/<slug>

### 8. PR 確認・マージ

PR 内容を確認し、問題なければ GitHub MCP ツールでマージ。

### 9. 公開確認

**注意**: `published_at` が未来日付でも必ず公開確認を実施すること。スキップ禁止。

1. `https://zenn.dev/opensearch/articles/<slug>` に fetch でアクセス
2. HTTP 200 が返るまで 30 秒間隔でリトライ（最大 5 分）

### 10. 公開記事レビュー

`.kiro/prompts/review-published.md` の内容に従い、公開された記事をレビューする。

- Zenn URL: `https://zenn.dev/opensearch/articles/<slug>`
- ローカルファイル: `articles/<slug>.md`

修正が発生した場合は、コミット・プッシュまで実施する。

### 11. Issue クローズ

GitHub MCP ツールで Issue を close。Close 時に zenn の URL: https://zenn.dev/opensearch/articles/<slug> が公開済みであることが確認できた旨を英語で追記する。

### 12. ブランチを main に戻す

```bash
git stash
git checkout main
git pull
```

## 翻訳ルール

### Front Matter

| 項目             | 値                                                                                              |
| ---------------- | ----------------------------------------------------------------------------------------------- |
| title            | 先頭に `[翻訳]` を付与                                                                          |
| emoji            | 適切な絵文字 (例: 🔍)                                                                           |
| publication_name | `opensearch`                                                                                    |
| topics           | 最大 5 つ (`opensearch` 必須)                                                                   |
| type             | `tech`                                                                                          |
| published        | `true`                                                                                          |
| published_at     | `curl -s <URL> \| grep -oP 'article:published_time.*?content="\K[^"]+' \| cut -d'T' -f1` で取得 |

### 画像処理

1. 元記事から本文中の画像を抽出:
   ```bash
   curl -s <URL> | grep -oP '<figure[^>]*>.*?</figure>' | grep -oP 'src="[^"]+"'
   ```
2. ナビゲーション/アイコン画像を除外し、記事本文の画像のみ取得
3. `mkdir -p images/<slug>` でフォルダ作成
4. `curl -sL <image_url> -o images/<slug>/<filename>` で取得
5. パスは `/images/<slug>/<filename>` (先頭 `/` 必須)
6. 3 MB 超の場合はリサイズ・圧縮
7. 翻訳記事内の適切な位置に `![alt](/images/<slug>/<filename>)` を挿入

### 文章構成

冒頭に以下を配置:

```
:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

<元記事の URL>

<本文>
```

### 表記ルール

- 技術的正確さと読みやすさを重視
- 全角・半角間は半角スペースで分ける
- カッコ `()` `[]` は半角
- 原文の文末コロン `:` → 句点 `。`

### 用語統一

| 原文/元表記                        | 訳語                   |
| ---------------------------------- | ---------------------- |
| 今後の展望                         | 今後の予定             |
| ご覧ください                       | 参照してください       |
| 本ブログ/このブログ記事/ブログ記事 | 本記事/記事            |
| 可観測性                           | オブザーバビリティ     |
| 字句検索                           | テキスト検索           |
| 以下の図は〜を示しています         | 以下の図に〜を示します |
| 以下の手順に従ってください         | 以下の手順で行います   |
| 開示:                              | **注意事項:**          |
