# OpenSearchCon セッション記事作成タスク

指定した YouTube 動画の文字起こしから解説記事を作成して Zenn に公開する。

## リポジトリ情報の取得

最初にローカルの `.git/config` を読み取り、以下の情報を取得:

- `owner`: リモート URL から抽出
- `repo`: リモート URL から抽出

## Git 認証

環境変数 `GITHUB_TOKEN` を使用して認証付き URL を構築:

```
https://${GITHUB_TOKEN}@github.com/<owner>/<repo>.git
```

## 事前確認

1. `git branch --show-current` で現在のブランチを確認し、main 以外なら `git stash && git checkout main` を実行
2. GitHub MCP の `list_issues` で既存の Issue を確認
3. 対応中のリクエストは途中から作業を再開

## ワークフロー

### 1. 動画情報の取得

YouTube URL から以下を取得:

- 動画タイトル
- 公開日
- 動画の説明文

### 2. 文字起こしの取得

`yt-dlp` で自動字幕を取得:

```bash
yt-dlp --write-auto-sub --sub-lang en --skip-download --sub-format vtt -o "transcript" "<YouTube URL>"
```

VTT ファイルから文字起こしテキストを抽出。

### 3. slug 決定

動画のタイトルや説明文からイベント情報を抽出し、slug を決定。

**prefix 形式**: `opensearchcon-<開催場所>-<年>-`

- 開催場所: `ja`（日本）、`eu`（ヨーロッパ）、`na`（北米）、`india` など
- 年: 4 桁（例: `2024`, `2025`）

**例**:
- OpenSearchCon Japan 2024 → `opensearchcon-ja-2024-`
- OpenSearchCon Europe 2025 → `opensearchcon-eu-2025-`
- OpenSearchCon North America 2024 → `opensearchcon-na-2024-`

**残り文字数**: prefix 後、最大 29 文字でセッション内容を表す部分を生成。英数字とハイフンのみ。

**完成例**: `opensearchcon-ja-2024-vector-search-basics` (42文字)

### 4. Issue 作成

GitHub MCP の `create_issue` で Issue を作成:

- Title: `[Session] <動画タイトル>`
- Labels: `["session"]`
- Body:

  ```
  YouTube URL: <URL>
  slug: <slug>
  ```

### 5. ブランチ作成・チェックアウト

```bash
git checkout main
git pull https://${GITHUB_TOKEN}@github.com/<owner>/<repo>.git main
git checkout -b session/<slug>
```

### 6. 動画ダウンロードとサムネイル抽出

#### 動画のダウンロード

```bash
yt-dlp -f "best[height<=720]" -o "video.mp4" "<YouTube URL>"
```

#### タイムスタンプごとのサムネイル抽出

各セクションの開始時刻（秒）に対応するフレームを抽出:

```bash
ffmpeg -ss <seconds> -i video.mp4 -vframes 1 -q:v 2 "images/<slug>/thumbnail_<seconds>.jpg"
```

例: 70 秒時点のサムネイル

```bash
ffmpeg -ss 70 -i video.mp4 -vframes 1 -q:v 2 "images/<slug>/thumbnail_70.jpg"
```

#### 画像の最適化

3 MB を超える場合はリサイズ:

```bash
ffmpeg -ss <seconds> -i video.mp4 -vframes 1 -vf "scale=1280:-1" -q:v 3 "images/<slug>/thumbnail_<seconds>.jpg"
```

#### クリーンアップ

記事作成完了後、ダウンロードした動画ファイルを削除:

```bash
rm -f video.mp4
```

### 7. 記事ファイル作成

1. `npx zenn new:article --slug <slug>` でファイル作成
2. 文字起こしを日本語に翻訳して記事を作成
3. 抽出したサムネイル画像を配置

### 8. セルフレビュー

記事内容をチェックし、問題があれば修正。

### 9. コミット・プッシュ

```bash
git add -A
git commit -m "feat: add session article for <動画タイトル> (#<Issue番号>)"
git push https://${GITHUB_TOKEN}@github.com/<owner>/<repo>.git session/<slug>
```

### 10. PR 作成

GitHub MCP の `create_pull_request` で PR 作成:

- Title: `[Session] <動画タイトル>`
- Body: `#<Issue番号>`
- Base: main, Head: session/<slug>

### 11. PR 確認・マージ

PR 内容を確認し、問題なければ GitHub MCP ツールでマージ。

### 12. ブランチを main に戻す

```bash
git stash
git checkout main
git pull
```

## 記事フォーマット

### Front Matter

| 項目             | 値                                        |
| ---------------- | ----------------------------------------- |
| title            | 動画タイトル（日本語訳）                  |
| emoji            | 適切な絵文字 (例: 🎬)                     |
| publication_name | `opensearch`                              |
| topics           | 最大 5 つ (`opensearch` 必須)             |
| type             | `tech`                                    |
| published        | `false`                                   |

### 画像処理

- 各セクションのタイムスタンプに対応するフレームを抽出
- `images/<slug>/` 配下に `thumbnail_<seconds>.jpg` として格納
- パスは `/images/<slug>/thumbnail_<seconds>.jpg` (先頭 `/` 必須)

### 文章構成

```markdown
:::message
本記事は [OpenSearch Project YouTube チャンネル](https://www.youtube.com/@OpenSearchProject) で公開されているセッション動画の内容を日本語で書き起こしたものです。
:::

**イベント**: [<イベント名>](<プレイリスト URL>)（例: OpenSearchCon Korea 2025）
**プレゼンター**: <プレゼンター名>, <所属>（例: Aswath Srinivasan, OpenSearch @ AWS）

<YouTube URL>

※ 本記事は動画の自動字幕を基に作成しています。誤字脱字や誤った内容が含まれる可能性があります。

## はじめに

<動画の概要・サマリー>

## 本編

<タイムスタンプ付きセクション見出しと文字起こし内容>
```

### イベント情報の記載

- イベント名はプレイリストタイトルから取得（例: `OpenSearchCon Korea 2025`）
- プレイリスト URL へのリンクを設置し、同イベントの他セッションへの導線とする

### プレゼンター情報の記載

- 動画タイトルまたは説明文からプレゼンター名と所属を取得
- 複数プレゼンターの場合はカンマ区切りで列挙

### タイムスタンプリンク

セクションごとにタイムスタンプ付きサムネイルとリンクを挿入:

```markdown
[![Thumbnail](/images/<slug>/thumbnail_<seconds>.jpg)](<YouTube URL>&t=<seconds>)

### <セクション見出し>

<文字起こし内容>
```

### 翻訳ルール

- 技術的正確さと読みやすさを重視
- 全角・半角間は半角スペースで分ける
- カッコ `()` `[]` は半角
- 専門用語は適切に訳す（OpenSearch 関連用語は原文維持も可）

### 用語統一

| 原文/元表記 | 訳語               |
| ----------- | ------------------ |
| observability | オブザーバビリティ |
| vector search | ベクトル検索       |
| semantic search | セマンティック検索 |
| full-text search | 全文検索         |
