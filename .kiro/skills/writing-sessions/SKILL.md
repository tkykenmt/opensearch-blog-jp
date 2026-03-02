# Writing Session Articles

OpenSearchCon セッション動画から解説記事を作成して Zenn に公開するスキル。

## ワークフロー

```
session.py → session-writer → scripts/check.py → reviewer → scripts/publish.py
```

1. `python session.py --urls <URL1> <URL2> ...` で文字起こし・サムネイル取得
2. session-writer エージェントで記事作成
3. `python scripts/check.py --slug <slug>` で自動チェック
4. `python scripts/publish.py --slug <slug>` で commit・push

## 記事作成タスク

`work/{slug}/` 内の文字起こしファイルとサムネイルを使用して `work/{slug}/translated.md` を作成する。

### slug 命名規則

**prefix**: `opensearchcon-<開催場所>-<年>-`
- 開催場所: `ja`（日本）、`eu`（ヨーロッパ）、`na`（北米）、`india` など
- 年: 4 桁

**例**: `opensearchcon-ja-2024-vector-search-basics`

### Front Matter

```yaml
---
title: "<イベント名>: <セッションタイトル（日本語訳）>"
emoji: "🎬"
type: "tech"
topics: ["opensearch", ...]  # 最大5つ、opensearch必須
publication_name: "opensearch"
published: false
---
```

**title 例**: `OpenSearchCon Korea 2025: 低コストでセマンティック検索を実現する Neural Sparse Search`

### 文章構成

```markdown
:::message
本記事は [OpenSearch Project YouTube チャンネル](https://www.youtube.com/@OpenSearchProject) で公開されているセッション動画の内容を日本語で書き起こしたものです。
:::

**イベント**: [<イベント名>](<プレイリスト URL>)
**プレゼンター**: <プレゼンター名>, <所属>

<YouTube URL>

※ 本記事は動画の自動字幕を基に作成しています。誤字脱字や誤った内容が含まれる可能性があります。

## はじめに

<動画の概要・サマリー>

## 本編

<タイムスタンプ付きセクション>
```

### タイムスタンプリンク

```markdown
[![Thumbnail](/images/{slug}/thumbnail_<seconds>.jpg)](<YouTube URL>&t=<seconds>)

### <セクション見出し>

<文字起こし内容>
```

## 翻訳ルール

### 表記ルール

- 全角・半角間は半角スペースで分ける
- カッコ `()` `[]` は半角
- 技術的正確さと読みやすさを重視

### 用語統一

| 原文 | 訳語 |
|------|------|
| observability | オブザーバビリティ |
| vector search | ベクトル検索 |
| semantic search | セマンティック検索 |
| full-text search | 全文検索 |

## 素材ファイル

session.py が `work/{slug}/` に以下を生成:

- `{video_id}.txt` - 文字起こしテキスト
- `images/{video_id}.jpg` - サムネイル
- `checkpoint.json` - 状態（videos 配列に動画情報）

## 公開後

scripts/publish.py 実行後:
- `articles/{slug}.md` に記事がコピーされる
- `images/{slug}/` に画像がコピーされる
- Git ブランチ `article/{slug}` で commit・push
- GitHub MCP で PR 作成
