---
name: orchestrating-workflow
description: 翻訳・セッション記事のワークフロー全体の手順定義。orchestrator エージェントがフロー制御に使用。
---

# Orchestrating Workflow

## スクリプト一覧

| スクリプト | 用途 | 使い方 |
|---|---|---|
| `python scripts/fetch.py -u <URL>` | HTML 取得・画像 DL | `--slug` で slug 指定可 |
| `python scripts/check.py --slug <slug>` | 自動チェック実行 | review_checks.json に結果保存 |
| `python scripts/publish.py --slug <slug>` | ファイルコピー・commit・push | `--no-push` で commit のみ |
| `python scripts/status.py` | 作業一覧表示 | `--slug` で詳細表示 |

## Blog 翻訳フロー

### 1. Issue 作成

GitHub MCP で Issue を作成する。

- タイトル: `[Translation] <元記事タイトル>`
- ラベル: `translation`
- 本文: 元記事の URL

### 2. 記事取得

```bash
python scripts/fetch.py -u <URL>
```

- `work/{slug}/content.html` と画像が保存される
- `checkpoint.json` が `status: fetched` になる
- slug が長すぎる場合は `--slug` で指定する

### 3. 翻訳

translator sub-agent に委譲する。

指示例:
> work/{slug}/content.html を翻訳して work/{slug}/translated.md を作成してください。
> checkpoint.json の image_mapping を参照して画像 URL を置換してください。

完了後、`checkpoint.json` の `status` を `translated` に更新する。

### 4. 自動チェック

```bash
python scripts/check.py --slug <slug>
```

- `review_checks.json` に結果が保存される
- エラーがあれば修正が必要

### 5. AI レビュー

reviewer sub-agent に委譲する。

指示例:
> work/{slug}/translated.md をレビューしてください。
> 自動チェック結果: work/{slug}/review_checks.json
> レビュー結果を work/{slug}/review.md に保存してください。

完了後、`checkpoint.json` の `status` を `reviewed` に更新する。

### 6. 修正（エラーがある場合）

fixer sub-agent に委譲する。

指示例:
> work/{slug}/translated.md を以下のレビュー指摘に基づいて修正してください。
> 自動チェック結果: work/{slug}/review_checks.json
> AI レビュー結果: work/{slug}/review.md

修正後、ステップ 4（自動チェック）に戻る。最大 3 回まで繰り返す。

### 7. 公開

```bash
python scripts/publish.py --slug <slug>
```

- `article/{slug}` ブランチで commit・push される
- GitHub MCP で PR を作成する
  - タイトル: `Add article: <タイトル>`
  - ベース: `main`
- GitHub MCP で PR を squash merge する

### 8. 公開確認・Issue クローズ

- `https://zenn.dev/opensearch/articles/{slug}` にアクセスして公開を確認
- GitHub MCP で Issue をクローズする
- `git checkout main` で main ブランチに戻る

## セッション記事フロー

### 1. Issue 作成

GitHub MCP で Issue を作成する。

- タイトル: `[Session] <セッションタイトル>`
- ラベル: `session`
- 本文: YouTube URL と slug

### 2. 素材取得

```bash
python session.py --urls <URL1> <URL2> ...
```

### 3. 記事作成

session-writer sub-agent に委譲する。

指示例:
> work/{slug}/ の素材から記事を作成して work/{slug}/translated.md に保存してください。

### 4〜8. レビュー・修正・公開

Blog 翻訳フローのステップ 4〜8 と同じ。

## 判断基準

- 自動チェックでエラー 0 件 → 公開可能
- 自動チェックでエラーあり → fixer で修正
- 修正 3 回でもエラー解消しない → ユーザーに報告して判断を仰ぐ
- AI レビューで重大な問題指摘 → fixer で修正

## checkpoint.json の状態遷移

```
init → fetched → translated → reviewed → fixed → pushed → live
```

各ステップ完了時に `checkpoint.json` の `status` を更新すること。
