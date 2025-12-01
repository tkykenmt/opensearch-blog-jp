## 実行モード: 未着手 Issue から検出

未着手の翻訳リクエスト Issue を処理してください。

1. GitHub MCP の list_issues で translation ラベル付きの open Issue を取得
2. 各 Issue について、対応するブランチ (translate/*) が存在するか確認
3. ブランチが存在しない Issue の URL を抽出して翻訳を実行
4. 該当 Issue がなければ「未着手の翻訳リクエストはありません」と報告して終了
