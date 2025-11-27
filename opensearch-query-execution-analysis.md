# OpenSearch の has_child、has_parent、nested クエリの内部実装解説

OpenSearch のコードベースを確認しながら、これらのクエリがどのように実行されるかを詳細に解説します。

## 1. Nested Query の実装

### 1.1 基本構造

`NestedQueryBuilder` は、ネストされたオブジェクト内を検索するためのクエリです。

**主要なコンポーネント:**
- `path`: ネストされたフィールドのパス
- `query`: ネストされたドキュメントに対する検索クエリ
- `scoreMode`: 子ドキュメントのスコアを親にどう集約するか (None, Avg, Sum, Max, Min)

### 1.2 クエリ生成プロセス (`doToQuery` メソッド)

```java
protected Query doToQuery(QueryShardContext context) throws IOException {
    // 1. ネストされたオブジェクトマッパーを取得
    ObjectMapper nestedObjectMapper = context.getObjectMapper(path);
    
    // 2. 親フィルターの作成
    final BitSetProducer parentFilter;
    if (objectMapper == null) {
        parentFilter = context.bitsetFilter(Queries.newNonNestedFilter());
    } else {
        parentFilter = context.bitsetFilter(objectMapper.nestedTypeFilter());
    }
    
    // 3. 内部クエリの生成（ネストスコープ内で）
    context.nestedScope().nextLevel(nestedObjectMapper);
    innerQuery = this.query.toQuery(context);
    context.nestedScope().previousLevel();
    
    // 4. ToParentBlockJoinQuery の生成
    return new OpenSearchToParentBlockJoinQuery(
        innerQuery,
        parentFilter,
        scoreMode,
        objectMapper == null ? null : objectMapper.fullPath()
    );
}
```

**重要なポイント:**

1. **BitSetProducer**: 親ドキュメントを識別するためのビットセット
2. **NestedScope**: ネストレベルを管理し、正しいコンテキストでクエリを構築
3. **ToParentBlockJoinQuery**: Lucene の Block Join クエリを使用

## 2. Has_Child Query の実装

### 2.1 基本構造

`HasChildQueryBuilder` は、特定の子ドキュメントを持つ親ドキュメントを検索します。

**主要なコンポーネント:**
- `type`: 子ドキュメントのタイプ
- `query`: 子ドキュメントに対する検索クエリ
- `scoreMode`: スコア集約モード
- `minChildren` / `maxChildren`: マッチする子の数の制約

### 2.2 クエリ生成プロセス

```java
protected Query doToQuery(QueryShardContext context) throws IOException {
    // 1. Join フィールドマッパーの取得
    ParentJoinFieldMapper joinFieldMapper = ParentJoinFieldMapper.getMapper(context.getMapperService());
    
    // 2. Parent ID フィールドマッパーの取得
    ParentIdFieldMapper parentIdFieldMapper = joinFieldMapper.getParentIdFieldMapper(type, false);
    
    // 3. フィルターの作成
    Query parentFilter = parentIdFieldMapper.getParentFilter();
    Query childFilter = parentIdFieldMapper.getChildFilter(type);
    Query innerQuery = Queries.filtered(query.toQuery(context), childFilter);
    
    // 4. LateParsingQuery の生成
    return new LateParsingQuery(
        parentFilter,
        innerQuery,
        minChildren(),
        maxChildren(),
        fieldType.name(),
        scoreMode,
        fieldData,
        context.getSearchSimilarity()
    );
}
```

### 2.3 LateParsingQuery の役割

`LateParsingQuery` は遅延評価を行う特殊なクエリです:

```java
public Query rewrite(IndexSearcher searcher) throws IOException {
    IndexReader reader = searcher.getIndexReader();
    IndexOrdinalsFieldData indexParentChildFieldData = fieldDataJoin.loadGlobal((DirectoryReader) reader);
    OrdinalMap ordinalMap = indexParentChildFieldData.getOrdinalMap();
    
    // JoinUtil を使用して実際の Join クエリを生成
    return JoinUtil.createJoinQuery(
        joinField,
        innerQuery,
        toQuery,
        indexSearcher,
        scoreMode,
        ordinalMap,
        minChildren,
        maxChildren
    );
}
```

**重要なポイント:**
- **OrdinalMap**: グローバル序数マップを使用して親子関係を効率的に解決
- **遅延評価**: IndexSearcher が利用可能になってから実際のクエリを生成

## 3. Has_Parent Query の実装

### 3.1 基本構造

`HasParentQueryBuilder` は、特定の親ドキュメントを持つ子ドキュメントを検索します。

```java
protected Query doToQuery(QueryShardContext context) throws IOException {
    ParentIdFieldMapper parentIdFieldMapper = joinFieldMapper.getParentIdFieldMapper(type, true);
    
    // 親フィルターと子フィルターを取得
    Query parentFilter = parentIdFieldMapper.getParentFilter();
    Query innerQuery = Queries.filtered(query.toQuery(context), parentFilter);
    Query childFilter = parentIdFieldMapper.getChildrenFilter();
    
    // has_child と同じ LateParsingQuery を使用（フィルターが逆）
    return new HasChildQueryBuilder.LateParsingQuery(
        childFilter,  // 親子が逆転
        innerQuery,
        HasChildQueryBuilder.DEFAULT_MIN_CHILDREN,
        HasChildQueryBuilder.DEFAULT_MAX_CHILDREN,
        fieldType.name(),
        score ? ScoreMode.Max : ScoreMode.None,
        fieldData,
        context.getSearchSimilarity()
    );
}
```

**has_child との違い:**
- `toQuery` と `innerQuery` のフィルターが逆転
- has_child: 親フィルター → 子クエリ
- has_parent: 子フィルター → 親クエリ

## 4. Bool クエリとの組み合わせ

### 4.1 Bool クエリの構造

Bool クエリは複数のクエリを組み合わせます:

```java
public class BoolQueryBuilder {
    private final List<QueryBuilder> mustClauses = new ArrayList<>();
    private final List<QueryBuilder> filterClauses = new ArrayList<>();
    private final List<QueryBuilder> shouldClauses = new ArrayList<>();
    private final List<QueryBuilder> mustNotClauses = new ArrayList<>();
}
```

### 4.2 Nested + Bool の実行フロー

```json
{
  "query": {
    "bool": {
      "must": [
        { "term": { "parent_field": "value1" } },
        {
          "nested": {
            "path": "children",
            "query": {
              "bool": {
                "must": [
                  { "term": { "children.name": "John" } },
                  { "range": { "children.age": { "gte": 18 } } }
                ]
              }
            }
          }
        }
      ]
    }
  }
}
```

**実行順序:**

1. **親ドキュメントのフィルタリング**: `parent_field: value1` を満たす親を検索
2. **Nested クエリの実行**:
   - ネストスコープに入る
   - 子ドキュメントに対して Bool クエリを実行
   - `children.name: John` AND `children.age >= 18`
3. **ToParentBlockJoinQuery**: 条件を満たす子を持つ親を特定
4. **Bool の AND 結合**: 両方の条件を満たす親ドキュメントのみ返す

### 4.3 Has_Child + Bool の実行フロー

```json
{
  "query": {
    "bool": {
      "must": [
        { "term": { "parent_name": "Company A" } },
        {
          "has_child": {
            "type": "employee",
            "query": {
              "bool": {
                "must": [
                  { "term": { "department": "Engineering" } },
                  { "range": { "salary": { "gte": 100000 } } }
                ]
              }
            },
            "score_mode": "avg"
          }
        }
      ]
    }
  }
}
```

**実行順序:**

1. **親クエリの評価**: `parent_name: Company A` を満たす親を検索
2. **Has_Child の LateParsingQuery**:
   - OrdinalMap をロード
   - 子ドキュメントに対して Bool クエリを実行
   - `department: Engineering` AND `salary >= 100000`
3. **JoinUtil.createJoinQuery**:
   - 条件を満たす子を持つ親を特定
   - スコアを集約（avg モード）
4. **Bool の AND 結合**: 両方の条件を満たす親のみ返す

## 5. 重要な実装の詳細

### 5.1 BitSetProducer の役割

```java
// Nested クエリでの使用例
final BitSetProducer parentFilter = context.bitsetFilter(objectMapper.nestedTypeFilter());
```

- **目的**: 親ドキュメントを効率的に識別
- **実装**: ビットセットを使用して O(1) で親判定
- **キャッシュ**: QueryShardContext でキャッシュされ、再利用される

### 5.2 NestedScope の管理

```java
context.nestedScope().nextLevel(nestedObjectMapper);
try {
    innerQuery = this.query.toQuery(context);
} finally {
    context.nestedScope().previousLevel();
}
```

- **スタック構造**: ネストレベルをスタックで管理
- **コンテキスト分離**: 各レベルで正しいマッパーを使用
- **エラー防止**: finally ブロックで確実にレベルを戻す

### 5.3 OrdinalMap の使用

```java
IndexOrdinalsFieldData indexParentChildFieldData = fieldDataJoin.loadGlobal((DirectoryReader) reader);
OrdinalMap ordinalMap = indexParentChildFieldData.getOrdinalMap();
```

- **グローバル序数**: セグメント間で一貫した序数を提供
- **効率的な Join**: 序数を使用して親子関係を高速に解決
- **メモリ効率**: フィールドデータとして最適化



## 6. パフォーマンスの考慮事項

### 6.1 Nested Query

**利点:**
- Block Join により高速な検索
- 親子が物理的に隣接しているため、キャッシュ効率が良い
- BitSetProducer によるO(1)の親判定

**欠点:**
- 子の更新時に親ドキュメント全体を再インデックス
- ネストが深くなるとメモリ使用量が増加

### 6.2 Has_Child / Has_Parent Query

**利点:**
- 子ドキュメントの独立した更新が可能
- 大量の子ドキュメントに対応

**欠点:**
- OrdinalMap のロードコスト
- Nested より Join 処理が遅い
- グローバル序数のメモリ使用量

### 6.3 Bool Query との組み合わせ

**最適化のポイント:**

1. **フィルターコンテキストの活用**
```json
{
  "bool": {
    "filter": [
      { "term": { "status": "active" } }
    ],
    "must": [
      { "nested": { ... } }
    ]
  }
}
```
- `filter` 句はスコア計算をスキップ
- キャッシュが効きやすい

2. **クエリの順序**
- 選択性の高いクエリを先に配置
- Nested/Has_Child は後に配置

3. **min_children / max_children の活用**
```json
{
  "has_child": {
    "type": "employee",
    "min_children": 5,
    "max_children": 100,
    "query": { ... }
  }
}
```
- 不要な親ドキュメントを早期に除外

## 7. まとめ

### 7.1 実装の核心

1. **Nested Query**
   - `ToParentBlockJoinQuery` を使用
   - `BitSetProducer` で親を識別
   - `NestedScope` でコンテキスト管理

2. **Has_Child Query**
   - `LateParsingQuery` で遅延評価
   - `OrdinalMap` で親子関係を解決
   - `JoinUtil.createJoinQuery` で実際の Join

3. **Has_Parent Query**
   - Has_Child と同じ仕組み
   - フィルターの方向が逆

### 7.2 Bool Query との統合

- Bool Query は各句を独立して評価
- Nested/Has_Child は通常のクエリとして扱われる
- AND/OR/NOT の論理演算で結合
- スコアは ScoreMode に従って集約

### 7.3 選択のガイドライン

**Nested を選ぶべき場合:**
- 親子が密結合
- 子の更新頻度が低い
- 高速な検索が必要

**Parent-Child を選ぶべき場合:**
- 子の独立した更新が必要
- 子ドキュメントが大量
- 親子の関係が疎結合

## 参考リンク

- [OpenSearch GitHub Repository](https://github.com/opensearch-project/OpenSearch)
- [NestedQueryBuilder.java](https://github.com/opensearch-project/OpenSearch/blob/main/server/src/main/java/org/opensearch/index/query/NestedQueryBuilder.java)
- [HasChildQueryBuilder.java](https://github.com/opensearch-project/OpenSearch/blob/main/modules/parent-join/src/main/java/org/opensearch/join/query/HasChildQueryBuilder.java)
- [HasParentQueryBuilder.java](https://github.com/opensearch-project/OpenSearch/blob/main/modules/parent-join/src/main/java/org/opensearch/join/query/HasParentQueryBuilder.java)
