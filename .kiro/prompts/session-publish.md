## 実行モード: 記事公開

指定した slug の記事を公開してください。

slug: {{SLUG}}

### 処理フロー

1. `articles/<slug>.md` を読み込み
2. Front Matter の `published: false` を `published: true` に変更
3. `published_at` に現在日付を追加（YYYY-MM-DD 形式）
4. コミット・プッシュ
5. `https://zenn.dev/opensearch/articles/<slug>` に fetch でアクセス
6. HTTP 200 が返るまで 30 秒間隔でリトライ（最大 5 分）
7. 公開確認後、対応する Issue を close（Zenn URL を記載）
