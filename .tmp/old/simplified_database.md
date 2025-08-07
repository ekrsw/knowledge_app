# シンプル化されたデータベース設計 - ナレッジ修正案システム

## 1. 概要

実際のナレッジベースフィールドに特化したシンプルな修正案管理システム。
複雑なワークフロー機能を削除し、基本的な提出・承認機能に絞った設計。

## 2. コアテーブル設計

### 2.1 ユーザー管理（最小限）

#### users (ユーザー)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    sweet_name VARCHAR(50) UNIQUE,
    ctstage_name VARCHAR(50) UNIQUE,
    role VARCHAR(20) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'approver', 'admin')),
    approval_group_id VARCHAR(50) REFERENCES approval_groups(group_id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

### 2.2 承認グループテーブル

#### approval_groups (承認グループ)
```sql
CREATE TABLE approval_groups (
    group_id VARCHAR(50) PRIMARY KEY,
    group_name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

### 2.3 情報カテゴリテーブル

#### info_categories (情報カテゴリ)
```sql
CREATE TABLE info_categories (
    category_id VARCHAR(50) PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

### 2.4 既存記事テーブル（参照専用）

#### articles (既存記事)
```sql
CREATE TABLE articles (
    article_id VARCHAR(100) PRIMARY KEY,
    article_pk VARCHAR(200) NOT NULL,
    article_number VARCHAR(100) NOT NULL,
    article_url TEXT,
    approval_group VARCHAR(50) REFERENCES approval_groups(group_id),
    title TEXT,
    info_category VARCHAR(50) REFERENCES info_categories(category_id),
    keywords TEXT,
    importance BOOLEAN,
    publish_start TIMESTAMPTZ,
    publish_end TIMESTAMPTZ,
    target VARCHAR(100),
    question TEXT,
    answer TEXT,
    additional_comment TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

### 2.5 修正案テーブル（メイン）

#### revisions (修正案)
```sql
CREATE TABLE revisions (
    revision_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 対象記事情報
    target_article_id VARCHAR(100) NOT NULL,
    target_article_pk VARCHAR(200) NOT NULL,
    
    -- 提案者情報
    proposer_id UUID NOT NULL REFERENCES users(id),
    
    -- 修正後データ（全てnullable）
    after_title TEXT,
    after_info_category VARCHAR(50) REFERENCES info_categories(category_id),
    after_keywords TEXT,
    after_importance BOOLEAN,
    after_publish_start TIMESTAMPTZ,
    after_publish_end TIMESTAMPTZ,
    after_target VARCHAR(100),
    after_question TEXT,
    after_answer TEXT,
    after_additional_comment TEXT,
    
    -- 修正理由とステータス
    reason TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'approved', 'rejected', 'deleted')),
    
    -- 承認情報
    approver_id UUID REFERENCES users(id),
    processed_at TIMESTAMPTZ,
    
    -- タイムスタンプ
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

### 2.6 簡単な通知テーブル

#### simple_notifications (シンプル通知)
```sql
CREATE TABLE simple_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    type VARCHAR(50) NOT NULL,
    revision_id UUID REFERENCES revisions(revision_id),
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

## 3. インデックス（必要最小限）

```sql
-- users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_approval_group ON users(approval_group_id);

-- approval_groups
CREATE INDEX idx_approval_groups_active ON approval_groups(is_active) WHERE is_active = true;

-- info_categories
CREATE INDEX idx_info_categories_active ON info_categories(is_active) WHERE is_active = true;

-- articles
CREATE INDEX idx_articles_pk ON articles(article_pk);
CREATE INDEX idx_articles_number ON articles(article_number);
CREATE INDEX idx_articles_approval_group ON articles(approval_group);
CREATE INDEX idx_articles_info_category ON articles(info_category);

-- revisions
CREATE INDEX idx_revisions_proposer ON revisions(proposer_id);
CREATE INDEX idx_revisions_status ON revisions(status);
CREATE INDEX idx_revisions_approver ON revisions(approver_id);
CREATE INDEX idx_revisions_created_at ON revisions(created_at DESC);
CREATE INDEX idx_revisions_target_article ON revisions(target_article_id);

-- 全文検索（修正後のタイトル・質問・回答）
CREATE INDEX idx_revisions_search ON revisions USING GIN(
    to_tsvector('japanese', 
        coalesce(after_title, '') || ' ' ||
        coalesce(after_question, '') || ' ' ||
        coalesce(after_answer, '')
    )
);

-- notifications
CREATE INDEX idx_notifications_user_unread ON simple_notifications(user_id, is_read) WHERE is_read = false;
```

## 4. トリガー（最小限）

```sql
-- updated_at自動更新
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_approval_groups_updated_at BEFORE UPDATE ON approval_groups
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_info_categories_updated_at BEFORE UPDATE ON info_categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_articles_updated_at BEFORE UPDATE ON articles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_revisions_updated_at BEFORE UPDATE ON revisions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

## 5. 基本データ投入

```sql
-- 承認グループマスタデータ
INSERT INTO approval_groups (group_id, group_name, description) VALUES
('HR_APPROVERS', '人事承認グループ', '人事関連記事の承認を担当'),
('IT_APPROVERS', 'IT承認グループ', 'IT関連記事の承認を担当'),
('FINANCE_APPROVERS', '財務承認グループ', '財務関連記事の承認を担当'),
('GENERAL_APPROVERS', '総合承認グループ', '全般的な記事の承認を担当');

-- 情報カテゴリマスタデータ
INSERT INTO info_categories (category_id, category_name, display_order) VALUES
('01', '_会計・財務', 1),
('02', '_起動トラブル', 2),
('03', '_給与・年末調整', 3),
('04', '_減価・ﾘｰｽ/資産管理', 4),
('05', '_公益・医療会計', 5),
('06', '_工事・原価', 6),
('07', '_債権・債務', 7),
('08', '_事務所管理', 8),
('09', '_人事', 9),
('10', '_税務関連', 10),
('11', '_電子申告', 11),
('12', '_販売', 12),
('13', 'EdgeTracker', 13),
('14', 'MJS-Connect関連', 14),
('15', 'インストール・MOU', 15),
('16', 'かんたん！シリーズ', 16),
('17', 'その他（システム以外）', 17),
('18', 'その他MJSシステム', 18),
('19', 'その他システム（共通）', 19),
('20', 'ハード関連(HHD)', 20),
('21', 'ハード関連（ソフトフェア）', 21),
('22', 'マイナンバー', 22),
('23', 'ワークフロー', 23),
('24', '一時受付用', 24),
('25', '運用ルール', 25),
('26', '顧客情報', 26);

-- 基本ロールのユーザー作成例
INSERT INTO users (username, email, password_hash, full_name, role, approval_group_id) VALUES
('admin', 'admin@example.com', '$2b$12$...', '管理者', 'admin', NULL),
('hr_approver1', 'hr_approver1@example.com', '$2b$12$...', '人事承認者1', 'approver', 'HR_APPROVERS'),
('it_approver1', 'it_approver1@example.com', '$2b$12$...', 'IT承認者1', 'approver', 'IT_APPROVERS'),
('user1', 'user1@example.com', '$2b$12$...', 'ユーザー1', 'user', NULL);
```

## 6. API設計（シンプル化）

### 6.1 修正案API
```python
# 修正案一覧取得
GET /api/revisions?status=submitted&page=1&limit=20

# 修正案作成（下書きとして作成）
POST /api/revisions
{
    "target_article_id": "ART001",
    "target_article_pk": "unique_pk_value",
    "reason": "誤字修正",
    "after_title": "新タイトル",
    "after_question": "新質問",
    # ... 他の修正後フィールド
}

# 修正案のステータス更新
PUT /api/revisions/{revision_id}/status
{
    "status": "submitted"  # draft -> submitted
}

# 修正案承認/却下
PUT /api/revisions/{revision_id}/process
{
    "action": "approved",  # or "rejected"
}

# 修正案削除（論理削除）
DELETE /api/revisions/{revision_id}
# -> statusを'deleted'に更新
```

### 6.2 差分表示API
```python
# 差分データ取得（記事の現在データと修正案を比較）
GET /api/revisions/{revision_id}/diff
# レスポンス例
{
    "title": {"current": "現在のタイトル", "after": "新タイトル", "changed": true},
    "question": {"current": "現在の質問", "after": "新質問", "changed": true},
    "keywords": {"current": "keyword1", "after": "keyword1,keyword2", "changed": true}
}
```

## 7. フロントエンド構成（シンプル）

### 7.1 主要画面
1. **修正案一覧画面** - ステータス別フィルタ
2. **修正案作成画面** - before/afterフォーム
3. **修正案詳細・承認画面** - 差分表示と承認ボタン
4. **ダッシュボード** - 基本統計情報

### 7.2 削除した複雑機能
- ワークフローテンプレート
- 多段階承認プロセス
- 複雑な権限管理
- カテゴリ管理
- ファイル添付
- コメントスレッド
- 高度な統計・レポート

## 8. Redis活用（シンプル）

```python
# セッション管理
"session:{token}" -> {"user_id": "uuid", "expires": timestamp}

# 簡単な通知カウント
"notification_count:{user_id}" -> count

# 修正案統計キャッシュ
"stats:revisions" -> {"total": 100, "draft": 10, "submitted": 20, "approved": 60, "rejected": 8, "deleted": 2}
```

この設計は元の複雑な設計から約70%の機能を削減し、実際のナレッジベースフィールドに特化した構成となっています。