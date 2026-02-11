# Translating OpenSearch Blogs

OpenSearch Project Blog の記事を日本語に翻訳して Zenn に公開するスキル。

## ワークフロー

```
translate.py → review.py → publish.py
```

1. `python translate.py -u <URL>` で記事取得・画像ダウンロード・Kiro 翻訳を一括実行
   - `--no-translate` で取得のみ（翻訳スキップ）
2. `python review.py --slug <slug>` で自動チェック
3. `python publish.py --slug <slug>` で Git PR 作成・マージ

## 翻訳タスク

`work/{slug}/content.html` を読み、`work/{slug}/translated.md` を作成する。

### Front Matter

zenn-writing スキルの Front Matter ルールに従う。翻訳記事固有の設定:

```yaml
---
title: "[翻訳] <タイトル（70文字以内）>"
emoji: "🔍"
type: "tech"
topics: ["opensearch", ...]  # 最大5つ、opensearch必須
publication_name: "opensearch"
published: true
published_at: <元記事の公開日 YYYY-MM-DD>
---
```

### 文章構成

```markdown
:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

<元記事の URL>

<本文>
```

### 画像

- `work/{slug}/images/` に保存済み
- パス: `/images/{slug}/<filename>` (先頭 `/` 必須)
- checkpoint.json の `image_mapping` を参照して URL を置換

## 翻訳ルール

### 表記ルール

- 全角・半角間は半角スペースで分ける
- カッコ `()` `[]` は半角
- 原文の文末コロン `:` → 句点 `。`
- 技術的正確さと読みやすさを重視

### 用語統一

| 原文/元表記 | 訳語 |
|------------|------|
| 今後の展望 | 今後の予定 |
| ご覧ください | 参照してください |
| 本ブログ/このブログ記事 | 本記事/記事 |
| 可観測性 | オブザーバビリティ |
| 字句検索 | テキスト検索 |
| 以下の図は〜を示しています | 以下の図に〜を示します |
| 以下の手順に従ってください | 以下の手順で行います |
| 開示: | **注意事項:** |

### 避けるべき表現

| 避ける | 推奨 |
|--------|------|
| 悪いイベント | 望ましくないケース |
| ブックキーピング | 整合性管理 |
| 0 中心の | 平均 0 の |

## レビュー観点

review.py が自動チェックする項目:

1. Front Matter の必須フィールド
2. タイトル文字数（70文字以内）
3. 画像リンクの存在確認
4. 全角・半角間のスペース
5. 日本語文中の半角括弧

## 公開後

publish.py 実行後:
- `articles/{slug}.md` に記事がコピーされる
- `images/{slug}/` に画像がコピーされる
- Git ブランチ `article/{slug}` で PR 作成
- マージ後 https://zenn.dev/opensearch/articles/{slug} で公開
