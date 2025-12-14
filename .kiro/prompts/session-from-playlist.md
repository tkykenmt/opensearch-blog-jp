## 実行モード: プレイリスト指定

以下のプレイリストから **全ての動画** を抽出して記事を作成してください。

Playlist URL: {{PLAYLIST_URL}}

### イベント情報の取得

プレイリストタイトルからイベント情報を取得:

```bash
yt-dlp --flat-playlist --print "%(playlist_title)s" "<Playlist URL>" | head -1
```

例: `OpenSearchCon Korea 2025` → 開催場所: `kr`、年: `2025`

### 開催場所コードのマッピング

| プレイリストタイトル | コード |
| --- | --- |
| Japan | `ja` |
| Korea | `kr` |
| Europe | `eu` |
| North America | `na` |
| India | `india` |

### 動画一覧の取得

```bash
yt-dlp --flat-playlist --print "%(id)s %(title)s" "<Playlist URL>"
```

### 処理フロー

1. プレイリストタイトルからイベント情報（開催場所・年）を取得
2. プレイリスト内の全動画 ID とタイトルを取得
3. 既存の Issue/記事と照合し、未処理の動画を特定
4. **未処理の動画を全て順番に処理する（1動画で終了しない）**
5. 各動画の slug は `opensearchcon-<開催場所>-<年>-<セッション内容>` 形式で生成
6. 全動画の処理が完了したら終了

### 重要

- slug の prefix はプレイリストタイトルから決定すること（動画タイトルではない）
- 1 動画の処理が完了したら、次の未処理動画に進むこと
- 全ての未処理動画を処理し終えるまで終了しないこと
- 処理済み/未処理の動画数を報告すること
