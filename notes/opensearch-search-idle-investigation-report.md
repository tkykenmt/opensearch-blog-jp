# OpenSearch Search Idle 機能調査レポート

## 概要

本レポートは、OpenSearchの `index.search.idle.after` 設定によるSearch Idle機能について、ソースコードを調査した結果をまとめたものです。

---

## 1. refresh_interval の明示的設定によるアイドル状態遷移の回避

### 結論

**`refresh_interval` を明示的に設定することで、`index.search.idle.after` によるアイドル状態への遷移を回避できます。**

### コードによる根拠

`IndexShard.java` の `scheduledRefresh()` メソッドにアイドル状態への遷移判定ロジックがあります：

```java
public boolean scheduledRefresh() {
    verifyNotClosed();
    boolean listenerNeedsRefresh = refreshListeners.refreshNeeded();
    if (isReadAllowed() && (listenerNeedsRefresh || getEngine().refreshNeeded())) {
        if (listenerNeedsRefresh == false
            && isSearchIdleSupported()
            && isSearchIdle()
            && indexSettings.isExplicitRefresh() == false  // ← ポイント
            && active.get()) {
            // lets skip this refresh since we are search idle and
            // don't necessarily need to refresh.
            final Engine engine = getEngine();
            engine.maybePruneDeletes();
            setRefreshPending(engine);
            return false;  // リフレッシュをスキップ
        } else {
            return getEngine().maybeRefresh("schedule");  // 通常のリフレッシュ実行
        }
    }
    // ...
}
```

`isExplicitRefresh()` の定義（`IndexSettings.java`）：

```java
public boolean isExplicitRefresh() {
    return INDEX_REFRESH_INTERVAL_SETTING.exists(settings);
}
```

### 動作の仕組み

| 条件 | `isExplicitRefresh()` | アイドル状態への遷移 |
|------|----------------------|-------------------|
| `refresh_interval` 未設定（デフォルト値使用） | `false` | 可能性あり |
| `refresh_interval` 明示的に設定（デフォルト値 `1s` でも可） | `true` | 回避される |

### 設定例

```json
PUT /my-index/_settings
{
  "index.refresh_interval": "1s"
}
```

デフォルト値と同じ `1s` であっても、明示的に設定することでアイドル状態への遷移を防げます。

### 出典

- [IndexShard.java - scheduledRefresh()](https://github.com/opensearch-project/OpenSearch/blob/main/server/src/main/java/org/opensearch/index/shard/IndexShard.java)
- [IndexSettings.java - isExplicitRefresh()](https://github.com/opensearch-project/OpenSearch/blob/main/server/src/main/java/org/opensearch/index/IndexSettings.java)

---

## 2. アイドル状態の確認方法

### 結論

**`search_idle_reactivate_count_total` メトリクスで、アイドル状態から再アクティブ化された回数を確認できます。**

### 確認方法

#### Index Stats API

```bash
GET /_stats/search
# または特定のインデックス
GET /my-index/_stats/search
```

レスポンス例：

```json
{
  "indices": {
    "my-index": {
      "primaries": {
        "search": {
          "open_contexts": 0,
          "query_total": 100,
          "query_time_in_millis": 500,
          "search_idle_reactivate_count_total": 5
        }
      }
    }
  }
}
```

#### Node Stats API

```bash
GET /_nodes/stats/indices/search
```

### コードによる根拠

`ShardSearchStats.java`:

```java
@Override
public void onSearchIdleReactivation() {
    totalStats.searchIdleMetric.inc();
}
```

`SearchStats.java` でAPIレスポンスに含まれるフィールド定義：

```java
static final String SEARCH_IDLE_REACTIVATE_COUNT_TOTAL = "search_idle_reactivate_count_total";
```

### 注意点

- このメトリクスは**アイドル状態から復帰した回数**をカウント
- 「現在アイドル状態かどうか」を直接示すものではない
- カウントが増えている = 過去にアイドル状態になったことがある
- ノード再起動でリセットされる

### 出典

- [ShardSearchStats.java](https://github.com/opensearch-project/OpenSearch/blob/main/server/src/main/java/org/opensearch/index/search/stats/ShardSearchStats.java)
- [SearchStats.java](https://github.com/opensearch-project/OpenSearch/blob/main/server/src/main/java/org/opensearch/index/search/stats/SearchStats.java)

---

## 3. isSearchIdle() の実装

### 実装コード

`IndexShard.java`:

```java
/**
 * Returns true if this shards is search idle
 */
public final boolean isSearchIdle() {
    return (threadPool.relativeTimeInMillis() - lastSearcherAccess.get()) 
           >= indexSettings.getSearchIdleAfter().getMillis();
}
```

### 判定ロジック

```
(現在時刻 - 最後のSearcherアクセス時刻) >= index.search.idle.after設定値
```

| 要素 | 説明 |
|------|------|
| `threadPool.relativeTimeInMillis()` | 現在の相対時刻（ミリ秒） |
| `lastSearcherAccess.get()` | 最後にSearcherにアクセスした時刻 |
| `indexSettings.getSearchIdleAfter()` | `index.search.idle.after` の設定値（デフォルト30秒） |

### isSearchIdleSupported() - アイドル機能のサポート判定

```java
public final boolean isSearchIdleSupported() {
    // Remote Store有効、またはContext Aware有効の場合はサポートしない
    if (isRemoteTranslogEnabled() || indexSettings.isAssignedOnRemoteNode() 
        || indexSettings.isContextAwareEnabled()) {
        return false;
    }
    // Segment Replicationでレプリカがある場合もサポートしない
    return indexSettings.isSegRepEnabledOrRemoteNode() == false 
           || indexSettings.getNumberOfReplicas() == 0;
}
```

### 出典

- [IndexShard.java - isSearchIdle()](https://github.com/opensearch-project/OpenSearch/blob/main/server/src/main/java/org/opensearch/index/shard/IndexShard.java)

---

## 4. lastSearcherAccess の実装

### フィールド定義

```java
private final AtomicLong lastSearcherAccess = new AtomicLong();
```

### 初期化

コンストラクタで現在時刻に初期化：

```java
lastSearcherAccess.set(threadPool.relativeTimeInMillis());
```

### 更新メソッド

```java
private void markSearcherAccessed() {
    lastSearcherAccess.lazySet(threadPool.relativeTimeInMillis());
}
```

### 更新タイミング

| メソッド | 説明 |
|---------|------|
| `acquireSearcherSupplier()` | Point-in-time reader取得時 |
| `acquireSearcher()` | Searcher取得時（検索実行時） |
| `awaitShardSearchActive()` | アイドル状態から復帰時 |

### 実装詳細

```java
// Searcher取得時
private Engine.Searcher acquireSearcher(String source, Engine.SearcherScope scope) {
    readAllowed();
    markSearcherAccessed();  // ← 更新
    final Engine engine = getEngine();
    return engine.acquireSearcher(source, scope, this::wrapSearcher);
}

// アイドル状態から復帰時
public final void awaitShardSearchActive(Consumer<Boolean> listener) {
    boolean isSearchIdle = isSearchIdle();
    markSearcherAccessed();  // ← 更新（アイドル解除）
    final Translog.Location location = pendingRefreshLocation.get();
    if (location != null) {
        if (isSearchIdle) {
            SearchOperationListener searchOperationListener = getSearchOperationListener();
            searchOperationListener.onSearchIdleReactivation();  // ← メトリクス更新
        }
        // ...
    }
}
```

### 出典

- [IndexShard.java](https://github.com/opensearch-project/OpenSearch/blob/main/server/src/main/java/org/opensearch/index/shard/IndexShard.java)

---

## 5. 関連設定一覧

| 設定 | デフォルト値 | 説明 |
|------|-------------|------|
| `index.search.idle.after` | `30s` | アイドル状態と判定されるまでの時間 |
| `index.refresh_interval` | `1s` | リフレッシュ間隔（明示的設定でアイドル回避） |

---

## 6. Search Idle 機能の全体フロー

```
┌─────────────────────────────────────────────────────────────────┐
│                    定期リフレッシュ (scheduledRefresh)            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │ isSearchIdleSupported() ?     │
              │ (Remote Store/SegRep確認)      │
              └───────────────────────────────┘
                              │
                    Yes       │       No
              ┌───────────────┴───────────────┐
              ▼                               ▼
    ┌─────────────────┐              ┌─────────────────┐
    │ isSearchIdle()? │              │ 通常リフレッシュ  │
    │ (30秒経過確認)   │              │ 実行            │
    └─────────────────┘              └─────────────────┘
              │
      Yes     │     No
    ┌─────────┴─────────┐
    ▼                   ▼
┌─────────────────┐  ┌─────────────────┐
│isExplicitRefresh│  │ 通常リフレッシュ  │
│ == false ?      │  │ 実行            │
└─────────────────┘  └─────────────────┘
        │
  Yes   │   No (明示的設定あり)
  ┌─────┴─────┐
  ▼           ▼
┌─────────┐ ┌─────────────────┐
│リフレッシュ│ │ 通常リフレッシュ  │
│スキップ   │ │ 実行            │
│(Idle状態) │ └─────────────────┘
└─────────┘
```

---

## 7. テストコードによる検証

`SearchIdleIT.java` でこの動作が検証されています：

```java
IndexService indexService = createIndex("test", builder.build());
assertFalse(indexService.getIndexSettings().isExplicitRefresh());
```

### 出典

- [SearchIdleIT.java](https://github.com/opensearch-project/OpenSearch/blob/main/server/src/internalClusterTest/java/org/opensearch/index/shard/SearchIdleIT.java)

---

## 8. まとめ

1. **アイドル状態の回避**: `refresh_interval` を明示的に設定（デフォルト値でも可）することで、Search Idle機能によるリフレッシュスキップを回避できる

2. **アイドル状態の確認**: `search_idle_reactivate_count_total` メトリクスで過去にアイドル状態になった回数を確認可能

3. **アイドル判定**: 最後のSearcherアクセスから `index.search.idle.after`（デフォルト30秒）経過で判定

4. **制限事項**: Remote Store、Segment Replication（レプリカあり）、Context Aware有効時はSearch Idle機能は無効化される

---

## 参考リンク

- [OpenSearch GitHub Repository](https://github.com/opensearch-project/OpenSearch)
- [IndexShard.java](https://github.com/opensearch-project/OpenSearch/blob/main/server/src/main/java/org/opensearch/index/shard/IndexShard.java)
- [IndexSettings.java](https://github.com/opensearch-project/OpenSearch/blob/main/server/src/main/java/org/opensearch/index/IndexSettings.java)
- [ShardSearchStats.java](https://github.com/opensearch-project/OpenSearch/blob/main/server/src/main/java/org/opensearch/index/search/stats/ShardSearchStats.java)
- [SearchStats.java](https://github.com/opensearch-project/OpenSearch/blob/main/server/src/main/java/org/opensearch/index/search/stats/SearchStats.java)
- [SearchIdleIT.java](https://github.com/opensearch-project/OpenSearch/blob/main/server/src/internalClusterTest/java/org/opensearch/index/shard/SearchIdleIT.java)

---

*調査日: 2025年12月2日*


---

**免責事項**: 本レポートは Kiro および GitHub MCP を使用した分析に基づいて作成されています。内容には誤りを含む可能性があるため、正確な挙動については実際のソースコードや公式ドキュメントを参照してください。
