# データベース設計書 - ナレッジ修正案管理システム

## 1. 概要

PostgreSQL 17を使用した独立したナレッジ修正案管理システムのデータベース設計。
Windows Server 2019環境での運用を前提とし、高い可用性とパフォーマンスを提供する。

## 2. データベース構成

### 2.1 データベース名
- **メインDB**: `knowledge_revision_system`
- **テストDB**: `knowledge_revision_system_test`

### 2.2 スキーマ構成
- **public**: 基本テーブル
- **audit**: 監査ログテーブル
- **cache**: キャッシュ関連テーブル

## 3. テーブル設計

### 3.1 ユーザー管理テーブル

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
    role_id UUID NOT NULL REFERENCES roles(id),
    is_active BOOLEAN DEFAULT true,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

#### roles (役割)
```sql
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

#### user_sessions (ユーザーセッション)
```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 修正案管理テーブル

#### proposals (修正案)
```sql
CREATE TABLE proposals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    original_content TEXT NOT NULL,
    modified_content TEXT NOT NULL,
    content_type VARCHAR(20) DEFAULT 'markdown' 
        CHECK (content_type IN ('markdown', 'html', 'plain_text')),
    category_id UUID REFERENCES proposal_categories(id),
    status proposal_status_enum DEFAULT 'draft',
    priority priority_enum DEFAULT 'medium',
    submitter_id UUID NOT NULL REFERENCES users(id),
    assigned_approver_id UUID REFERENCES users(id),
    reason TEXT NOT NULL,
    tags TEXT[],
    metadata JSONB DEFAULT '{}',
    version INTEGER DEFAULT 1,
    parent_proposal_id UUID REFERENCES proposals(id),
    estimated_effort INTEGER, -- 工数見積もり（時間）
    due_date TIMESTAMPTZ,
    submitted_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

#### proposal_categories (修正案カテゴリ)
```sql
CREATE TABLE proposal_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    color VARCHAR(7), -- HEX color code
    icon VARCHAR(50),
    parent_category_id UUID REFERENCES proposal_categories(id),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

#### proposal_attachments (修正案添付ファイル)
```sql
CREATE TABLE proposal_attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id UUID NOT NULL REFERENCES proposals(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    uploaded_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

### 3.3 承認ワークフローテーブル

#### approval_workflows (承認ワークフロー)
```sql
CREATE TABLE approval_workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id UUID NOT NULL REFERENCES proposals(id) ON DELETE CASCADE,
    workflow_template_id UUID REFERENCES workflow_templates(id),
    current_step INTEGER DEFAULT 1,
    total_steps INTEGER NOT NULL,
    status workflow_status_enum DEFAULT 'pending',
    started_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,
    timeout_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

#### approval_steps (承認ステップ)
```sql
CREATE TABLE approval_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES approval_workflows(id) ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    approver_id UUID NOT NULL REFERENCES users(id),
    status step_status_enum DEFAULT 'pending',
    action_type VARCHAR(20) DEFAULT 'approve' 
        CHECK (action_type IN ('approve', 'review', 'verify')),
    comment TEXT,
    decision decision_enum,
    decided_at TIMESTAMPTZ,
    timeout_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(workflow_id, step_number)
);
```

#### workflow_templates (ワークフローテンプレート)
```sql
CREATE TABLE workflow_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    steps_config JSONB NOT NULL, -- ステップ設定
    conditions JSONB DEFAULT '{}', -- 適用条件
    timeout_hours INTEGER DEFAULT 72,
    is_active BOOLEAN DEFAULT true,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

### 3.4 通知・コメントテーブル

#### notifications (通知)
```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    sender_id UUID REFERENCES users(id) ON DELETE SET NULL,
    type notification_type_enum NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    related_entity_type VARCHAR(50), -- 'proposal', 'approval_workflow' etc
    related_entity_id UUID,
    data JSONB DEFAULT '{}',
    is_read BOOLEAN DEFAULT false,
    read_at TIMESTAMPTZ,
    priority notification_priority_enum DEFAULT 'medium',
    delivery_method VARCHAR(20)[] DEFAULT ARRAY['web'], -- web, email, slack
    scheduled_for TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

#### comments (コメント)
```sql
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id UUID NOT NULL REFERENCES proposals(id) ON DELETE CASCADE,
    author_id UUID NOT NULL REFERENCES users(id),
    parent_comment_id UUID REFERENCES comments(id),
    content TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT false, -- 内部コメント（承認者のみ表示）
    mentioned_users UUID[],
    attachments JSONB DEFAULT '[]',
    edited_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

### 3.5 監査・履歴テーブル

#### audit.activity_logs (活動ログ)
```sql
CREATE TABLE audit.activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

#### proposal_history (修正案履歴)
```sql
CREATE TABLE proposal_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id UUID NOT NULL REFERENCES proposals(id) ON DELETE CASCADE,
    changed_by UUID NOT NULL REFERENCES users(id),
    change_type VARCHAR(50) NOT NULL,
    field_name VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    change_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

### 3.6 統計・レポートテーブル

#### statistics (統計情報)
```sql
CREATE TABLE statistics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC NOT NULL,
    dimensions JSONB DEFAULT '{}',
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(metric_name, dimensions, period_start, period_end)
);
```

## 4. ENUM型定義

```sql
-- 修正案ステータス
CREATE TYPE proposal_status_enum AS ENUM (
    'draft',        -- 下書き
    'submitted',    -- 提出済み
    'in_review',    -- レビュー中
    'approved',     -- 承認済み
    'rejected',     -- 却下
    'withdrawn',    -- 取り下げ
    'completed'     -- 完了
);

-- 優先度
CREATE TYPE priority_enum AS ENUM (
    'low',          -- 低
    'medium',       -- 中
    'high',         -- 高
    'urgent'        -- 緊急
);

-- ワークフローステータス
CREATE TYPE workflow_status_enum AS ENUM (
    'pending',      -- 待機中
    'in_progress',  -- 進行中
    'completed',    -- 完了
    'cancelled',    -- キャンセル
    'timeout'       -- タイムアウト
);

-- ステップステータス
CREATE TYPE step_status_enum AS ENUM (
    'pending',      -- 待機中
    'in_progress',  -- 進行中
    'completed',    -- 完了
    'skipped'       -- スキップ
);

-- 決定
CREATE TYPE decision_enum AS ENUM (
    'approved',     -- 承認
    'rejected',     -- 却下
    'request_changes' -- 修正依頼
);

-- 通知タイプ
CREATE TYPE notification_type_enum AS ENUM (
    'proposal_submitted',       -- 修正案提出
    'approval_requested',       -- 承認依頼
    'proposal_approved',        -- 修正案承認
    'proposal_rejected',        -- 修正案却下
    'comment_added',           -- コメント追加
    'deadline_approaching',     -- 期限接近
    'workflow_timeout',        -- ワークフロータイムアウト
    'mention'                  -- メンション
);

-- 通知優先度
CREATE TYPE notification_priority_enum AS ENUM (
    'low',
    'medium', 
    'high',
    'urgent'
);
```

## 5. インデックス設計

### 5.1 基本インデックス
```sql
-- users テーブル
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_sweet_name ON users(sweet_name) WHERE sweet_name IS NOT NULL;
CREATE INDEX idx_users_ctstage_name ON users(ctstage_name) WHERE ctstage_name IS NOT NULL;
CREATE INDEX idx_users_role_id ON users(role_id);
CREATE INDEX idx_users_is_active ON users(is_active) WHERE is_active = true;

-- proposals テーブル
CREATE INDEX idx_proposals_submitter_id ON proposals(submitter_id);
CREATE INDEX idx_proposals_status ON proposals(status);
CREATE INDEX idx_proposals_category_id ON proposals(category_id);
CREATE INDEX idx_proposals_assigned_approver_id ON proposals(assigned_approver_id);
CREATE INDEX idx_proposals_created_at ON proposals(created_at);
CREATE INDEX idx_proposals_due_date ON proposals(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_proposals_tags ON proposals USING GIN(tags);
CREATE INDEX idx_proposals_metadata ON proposals USING GIN(metadata);

-- approval_workflows テーブル  
CREATE INDEX idx_approval_workflows_proposal_id ON approval_workflows(proposal_id);
CREATE INDEX idx_approval_workflows_status ON approval_workflows(status);
CREATE INDEX idx_approval_workflows_timeout_at ON approval_workflows(timeout_at) WHERE timeout_at IS NOT NULL;

-- approval_steps テーブル
CREATE INDEX idx_approval_steps_workflow_id ON approval_steps(workflow_id);
CREATE INDEX idx_approval_steps_approver_id ON approval_steps(approver_id);
CREATE INDEX idx_approval_steps_status ON approval_steps(status);

-- notifications テーブル
CREATE INDEX idx_notifications_recipient_id ON notifications(recipient_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read) WHERE is_read = false;
CREATE INDEX idx_notifications_type ON notifications(type);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);

-- comments テーブル
CREATE INDEX idx_comments_proposal_id ON comments(proposal_id);
CREATE INDEX idx_comments_author_id ON comments(author_id);
CREATE INDEX idx_comments_parent_comment_id ON comments(parent_comment_id) WHERE parent_comment_id IS NOT NULL;
```

### 5.2 複合インデックス
```sql
-- 修正案の効率的な検索
CREATE INDEX idx_proposals_status_submitter ON proposals(status, submitter_id);
CREATE INDEX idx_proposals_status_created_at ON proposals(status, created_at DESC);

-- 承認ワークフローの効率的な検索
CREATE INDEX idx_approval_steps_approver_status ON approval_steps(approver_id, status);

-- 通知の効率的な検索
CREATE INDEX idx_notifications_recipient_read_created ON notifications(recipient_id, is_read, created_at DESC);
```

### 5.3 全文検索インデックス
```sql
-- 修正案の全文検索
CREATE INDEX idx_proposals_fts ON proposals USING GIN(
    to_tsvector('japanese', coalesce(title, '') || ' ' || coalesce(description, '') || ' ' || coalesce(original_content, '') || ' ' || coalesce(modified_content, ''))
);
```

## 6. 制約とトリガー

### 6.1 チェック制約
```sql
-- proposals テーブル
ALTER TABLE proposals ADD CONSTRAINT chk_proposals_version_positive 
CHECK (version > 0);

ALTER TABLE proposals ADD CONSTRAINT chk_proposals_effort_positive 
CHECK (estimated_effort IS NULL OR estimated_effort > 0);

ALTER TABLE proposals ADD CONSTRAINT chk_proposals_due_date_future 
CHECK (due_date IS NULL OR due_date > created_at);

-- approval_steps テーブル
ALTER TABLE approval_steps ADD CONSTRAINT chk_approval_steps_step_positive 
CHECK (step_number > 0);
```

### 6.2 トリガー

#### updated_at自動更新トリガー
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 各テーブルにトリガーを追加
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_proposals_updated_at BEFORE UPDATE ON proposals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_approval_workflows_updated_at BEFORE UPDATE ON approval_workflows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_approval_steps_updated_at BEFORE UPDATE ON approval_steps
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

#### 監査ログトリガー
```sql
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit.activity_logs (
        user_id, action, entity_type, entity_id, old_values, new_values, created_at
    ) VALUES (
        current_setting('app.current_user_id', true)::UUID,
        TG_OP,
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        CASE WHEN TG_OP = 'DELETE' THEN row_to_json(OLD) ELSE NULL END,
        CASE WHEN TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN row_to_json(NEW) ELSE NULL END,
        CURRENT_TIMESTAMP
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- 重要テーブルに監査トリガーを追加
CREATE TRIGGER audit_proposals AFTER INSERT OR UPDATE OR DELETE ON proposals
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_approval_steps AFTER INSERT OR UPDATE OR DELETE ON approval_steps
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
```

## 7. パーティショニング

### 7.1 時系列パーティショニング（大容量対応）
```sql
-- 監査ログの月次パーティション
CREATE TABLE audit.activity_logs (
    id UUID DEFAULT gen_random_uuid(),
    user_id UUID,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (created_at);

-- 月次パーティションの例
CREATE TABLE audit.activity_logs_2024_01 PARTITION OF audit.activity_logs
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

## 8. セキュリティ設定

### 8.1 行レベルセキュリティ（RLS）
```sql
-- 修正案の行レベルセキュリティ
ALTER TABLE proposals ENABLE ROW LEVEL SECURITY;

-- ポリシー: ユーザーは自分の修正案のみ編集可能
CREATE POLICY proposals_user_policy ON proposals
    FOR ALL
    TO app_user
    USING (submitter_id = current_setting('app.current_user_id')::UUID);

-- ポリシー: 承認者は割り当てられた修正案を閲覧可能
CREATE POLICY proposals_approver_policy ON proposals
    FOR SELECT
    TO app_user
    USING (assigned_approver_id = current_setting('app.current_user_id')::UUID);
```

### 8.2 ロール設定
```sql
-- アプリケーション用ロール
CREATE ROLE app_user;
CREATE ROLE app_admin;

-- 基本権限の設定
GRANT CONNECT ON DATABASE knowledge_revision_system TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- 管理者権限
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_admin;
```

## 9. パフォーマンス最適化

### 9.1 接続プール設定
```sql
-- PostgreSQL設定（postgresql.conf）
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
```

### 9.2 統計情報更新
```sql
-- 統計情報の自動更新設定
ALTER TABLE proposals SET (autovacuum_analyze_scale_factor = 0.02);
ALTER TABLE notifications SET (autovacuum_analyze_scale_factor = 0.02);
```

## 10. バックアップ戦略

### 10.1 バックアップスクリプト
```sql
-- 日次バックアップ
pg_dump -h localhost -U postgres -d knowledge_revision_system -f backup_$(date +%Y%m%d).sql

-- ポイントインタイムリカバリ用WAL設定
archive_mode = on
archive_command = 'copy "%p" "C:\\backup\\wal\\%f"'
```

これで詳細なデータベース設計書を作成しました。PostgreSQL 17の機能を活用し、Windows Server 2019環境に最適化された設計となっています。

何か特定の部分について詳しく説明が必要でしたら、お聞かせください。