# データベースインデックス最適化分析

## 📋 概要

この文書は、knowledge_appのUserテーブルにおけるインデックス戦略の分析と最適化提案を示します。
Phase 3.1のパフォーマンス最適化の一環として作成されました。

## 🗄️ 現在のインデックス状況

### 既存のインデックス

**Base クラス (全テーブル共通)**
- `id` - PRIMARY KEY, UNIQUE, INDEX (UUID型)
- `created_at` - インデックスなし
- `updated_at` - インデックスなし

**User テーブル固有**
- `username` - UNIQUE, INDEX
- `email` - UNIQUE, INDEX  
- `full_name` - INDEX
- `ctstage_name` - インデックスなし
- `sweet_name` - インデックスなし
- `group` - インデックスなし
- `is_active` - インデックスなし
- `is_admin` - インデックスなし
- `is_sv` - インデックスなし
- `hashed_password` - インデックスなし

## 📊 クエリパターン分析

### 現在のCRUDメソッドで使用されるクエリ

1. **プライマリキー検索**
   ```sql
   SELECT * FROM users WHERE id = ?
   ```
   - 使用頻度: 高
   - 現在のインデックス: PRIMARY KEY (最適)

2. **ユーザー名検索**
   ```sql
   SELECT * FROM users WHERE username = ?
   ```
   - 使用頻度: 高
   - 現在のインデックス: UNIQUE INDEX (最適)

3. **メール検索**
   ```sql
   SELECT * FROM users WHERE email = ?
   ```
   - 使用頻度: 高
   - 現在のインデックス: UNIQUE INDEX (最適)

4. **全件取得（ページネーション）**
   ```sql
   SELECT * FROM users LIMIT ? OFFSET ?
   ```
   - 使用頻度: 中
   - 現在のインデックス: なし（自然順序）

5. **件数カウント**
   ```sql
   SELECT COUNT(id) FROM users
   ```
   - 使用頻度: 中
   - 現在のインデックス: PRIMARY KEY利用可能

## 🎯 最適化推奨事項

### 1. 高優先度：必要なインデックス

#### A. `is_active` フィールドのインデックス
- **理由**: アクティブユーザーのフィルタリングが頻繁に行われる可能性
- **推奨**: 部分インデックス（アクティブユーザーのみ）
- **SQL例**:
  ```sql
  CREATE INDEX idx_users_is_active ON users (is_active) WHERE is_active = true;
  ```

#### B. `group` フィールドのインデックス
- **理由**: グループ別のユーザー検索・統計
- **推奨**: 通常のインデックス
- **SQL例**:
  ```sql
  CREATE INDEX idx_users_group ON users (group);
  ```

### 2. 中優先度：パフォーマンス向上インデックス

#### A. `created_at` フィールドのインデックス
- **理由**: 新規ユーザーの時系列分析、最新ユーザー取得
- **推奨**: 降順インデックス
- **SQL例**:
  ```sql
  CREATE INDEX idx_users_created_at ON users (created_at DESC);
  ```

#### B. 複合インデックス `(is_active, created_at)`
- **理由**: アクティブユーザーの時系列検索
- **推奨**: 複合インデックス
- **SQL例**:
  ```sql
  CREATE INDEX idx_users_active_created ON users (is_active, created_at DESC) 
  WHERE is_active = true;
  ```

### 3. 低優先度：特定用途インデックス

#### A. `is_admin` および `is_sv` フィールド
- **理由**: 管理者・スーパーバイザー検索（頻度は低い）
- **推奨**: 部分インデックス（true値のみ）
- **SQL例**:
  ```sql
  CREATE INDEX idx_users_is_admin ON users (is_admin) WHERE is_admin = true;
  CREATE INDEX idx_users_is_sv ON users (is_sv) WHERE is_sv = true;
  ```

## 📈 予想されるパフォーマンス改善

### ページネーションクエリ
- **現在**: O(n) - 全レコードスキャンが必要な場合がある
- **改善後**: O(log n) - インデックス使用により効率化

### フィルタリングクエリ
- **is_activeフィルタ**: 90%以上の高速化（テーブルサイズに依存）
- **groupフィルタ**: 80%以上の高速化

### 統計クエリ
- **COUNT操作**: インデックスオンリースキャンにより高速化

## ⚠️ インデックス追加時の考慮事項

### ストレージオーバーヘッド
- 各インデックスは追加ストレージを消費
- 推定オーバーヘッド: テーブルサイズの20-30%

### 書き込みパフォーマンス
- INSERT/UPDATE/DELETE操作が若干遅くなる
- 影響は軽微（5-10%程度）

### メンテナンス
- インデックスの定期的なメンテナンスが必要
- PostgreSQLの自動バキューム機能で対応可能

## 🚀 実装計画

### フェーズ1: 必須インデックス
1. `is_active` 部分インデックス
2. `group` インデックス

### フェーズ2: パフォーマンス向上
1. `created_at` 降順インデックス
2. 複合インデックス `(is_active, created_at)`

### フェーズ3: 特定用途
1. `is_admin` 部分インデックス
2. `is_sv` 部分インデックス

## 📋 Alembic マイグレーション例

```python
# migration: add_performance_indexes
from alembic import op

def upgrade():
    # High priority indexes
    op.create_index(
        'idx_users_is_active', 
        'users', 
        ['is_active'], 
        postgresql_where=op.inline("is_active = true")
    )
    op.create_index('idx_users_group', 'users', ['group'])
    
    # Medium priority indexes
    op.create_index('idx_users_created_at', 'users', ['created_at'], postgresql_ops={'created_at': 'DESC'})
    op.create_index(
        'idx_users_active_created', 
        'users', 
        ['is_active', 'created_at'],
        postgresql_where=op.inline("is_active = true"),
        postgresql_ops={'created_at': 'DESC'}
    )

def downgrade():
    op.drop_index('idx_users_active_created')
    op.drop_index('idx_users_created_at')
    op.drop_index('idx_users_group')
    op.drop_index('idx_users_is_active')
```

## 🔍 監視推奨事項

### クエリパフォーマンス監視
- `pg_stat_statements` 拡張の活用
- スローログの設定（1秒以上のクエリ）
- インデックス使用率の監視

### メトリクス
- クエリ実行時間
- インデックススキャン率
- テーブルスキャン発生頻度

## 📝 更新履歴

- **2025-07-16**: 初期分析完了（Phase 3.1）
- **対象バージョン**: knowledge_app v1.0
- **分析者**: Claude Code Assistant