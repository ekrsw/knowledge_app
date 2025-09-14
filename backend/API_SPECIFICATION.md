# Knowledge System Approval Platform (KSAP) API仕様書

## 概要

Knowledge System Approval Platform (KSAP)は、知識改訂提案の作成、承認ワークフロー、変更追跡を管理するためのRESTful APIです。

- **ベースURL**: `http://localhost:8000/api/v1`
- **認証方式**: JWT Bearer Token
- **API ドキュメント**: `http://localhost:8000/docs` (開発環境)

## 認証とロール

### ユーザーロール

| ロール | 説明 | 権限 |
|--------|------|------|
| `user` | 一般ユーザー | 自身の改訂提案の作成・管理 |
| `approver` | 承認者 | 割り当てられたドメインの提案レビュー・承認/却下 |
| `admin` | 管理者 | システム全体へのフルアクセス |

### 認証フロー

1. `/auth/login` または `/auth/login/json` でユーザー名/メールとパスワードを送信
2. JWTトークンを受け取る
3. 以降のリクエストでは `Authorization: Bearer {token}` ヘッダーを付与

## APIエンドポイント仕様

### 1. 認証 (Authentication)

#### POST `/auth/login`
OAuth2互換のトークンログイン

**リクエストボディ** (form-data):
```
username: string
password: string
```

**レスポンス**:
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

**アクセス可能ロール**: 全ユーザー

---

#### POST `/auth/login/json`
JSON形式でのログイン

**リクエストボディ**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**レスポンス**:
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

**アクセス可能ロール**: 全ユーザー

---

#### POST `/auth/register`
新規ユーザー登録

**リクエストボディ**:
```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "password123",
  "full_name": "string",
  "sweet_name": "string",  // optional
  "ctstage_name": "string" // optional
}
```

**レスポンス**:
```json
{
  "id": "uuid",
  "username": "string",
  "email": "user@example.com",
  "full_name": "string",
  "sweet_name": "string",
  "ctstage_name": "string",
  "role": "user",
  "approval_group_id": null,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

**アクセス可能ロール**: 全ユーザー

---

#### GET `/auth/me`
現在のユーザー情報取得

**レスポンス**:
```json
{
  "id": "uuid",
  "username": "string",
  "email": "user@example.com",
  "full_name": "string",
  "sweet_name": "string",
  "ctstage_name": "string",
  "role": "user",
  "approval_group_id": "uuid",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

**アクセス可能ロール**: 認証済みユーザー

---

#### POST `/auth/logout`
ログアウト（クライアント側でトークンを破棄）

**レスポンス**:
```json
{
  "message": "Successfully logged out",
  "detail": "For stateless JWT authentication, please discard the token on client side"
}
```

**アクセス可能ロール**: 認証済みユーザー

---

#### GET `/auth/verify`
JWTトークンの検証

**レスポンス**:
```json
{
  "valid": true,
  "user": { /* User object */ },
  "token_type": "bearer"
}
```

**アクセス可能ロール**: 認証済みユーザー

---

#### GET `/auth/status`
認証ステータス取得

**レスポンス**:
```json
{
  "authenticated": true,
  "user_id": "uuid",
  "username": "string",
  "role": "user",
  "is_active": true
}
```

**アクセス可能ロール**: 認証済みユーザー

---

### 2. 改訂提案 (Revisions)

#### GET `/revisions/`
改訂一覧取得（権限に基づくフィルタリング）

**クエリパラメータ**:
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)

**レスポンス**:
```json
[
  {
    "revision_id": "uuid",
    "article_number": "ART001",
    "reason": "string",
    "after_title": "string",
    "after_info_category": "uuid",
    "after_keywords": "string",
    "after_importance": true,
    "after_publish_start": "2024-01-01",
    "after_publish_end": "2024-12-31",
    "after_target": "string",
    "after_question": "string",
    "after_answer": "string",
    "after_additional_comment": "string",
    "status": "draft",
    "processed_at": null,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
    "proposer_name": "John Doe",
    "approver_name": "Jane Smith"
  }
]
```

**アクセス可能ロール**:
- `admin`: 全ての改訂を閲覧可能
- その他: submitted/approved改訂 + 自身のdraft/rejected改訂を閲覧可能

---

#### GET `/revisions/my-revisions`
自分の改訂一覧取得

**クエリパラメータ**:
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)

**レスポンス**: 上記と同じ形式

**アクセス可能ロール**: 認証済みユーザー

---

#### GET `/revisions/{revision_id}`
特定の改訂取得

**レスポンス**:
```json
{
  "revision_id": "uuid",
  "target_article_id": "string",
  "reason": "string",
  "approver_id": "uuid",
  "after_title": "string",
  "after_info_category": "uuid",
  "after_keywords": "string",
  "after_importance": true,
  "after_publish_start": "2024-01-01",
  "after_publish_end": "2024-12-31",
  "after_target": "string",
  "after_question": "string",
  "after_answer": "string",
  "after_additional_comment": "string",
  "proposer_id": "uuid",
  "status": "draft",
  "approval_group_id": "uuid",
  "submitted_at": null,
  "processed_at": null,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

**アクセス可能ロール**:
- `admin`: 全て閲覧可能
- その他: submitted/approved は全員閲覧可能、draft/rejectedは提案者のみ

---

#### POST `/revisions/`
新規改訂作成

**リクエストボディ**:
```json
{
  "target_article_id": "string",
  "reason": "string",
  "approver_id": "uuid",
  "after_title": "string",
  "after_info_category": "uuid",
  "after_keywords": "string",
  "after_importance": true,
  "after_publish_start": "2024-01-01",
  "after_publish_end": "2024-12-31",
  "after_target": "string",
  "after_question": "string",
  "after_answer": "string",
  "after_additional_comment": "string"
}
```

**レスポンス**: 作成された改訂オブジェクト

**アクセス可能ロール**: 認証済みユーザー

---

#### PUT `/revisions/{revision_id}`
改訂更新

**リクエストボディ**:
```json
{
  "reason": "string",
  "status": "draft",
  "after_title": "string",
  "after_info_category": "uuid",
  "after_keywords": "string",
  "after_importance": true,
  "after_publish_start": "2024-01-01",
  "after_publish_end": "2024-12-31",
  "after_target": "string",
  "after_question": "string",
  "after_answer": "string",
  "after_additional_comment": "string"
}
```

**レスポンス**: 更新された改訂オブジェクト

**アクセス可能ロール**:
- draft改訂: 提案者のみ
- approved改訂: 承認者またはadmin

---

#### PATCH `/revisions/{revision_id}/status`
改訂ステータス更新

**リクエストボディ**:
```json
{
  "status": "submitted" // submitted, approved, rejected, deleted
}
```

**レスポンス**: 更新された改訂オブジェクト

**アクセス可能ロール**: `approver`, `admin`

---

#### GET `/revisions/by-status/{status}`
ステータス別改訂取得

**クエリパラメータ**:
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)

**レスポンス**: 改訂リスト

**アクセス可能ロール**:
- `admin`: 全ステータス閲覧可能
- その他: submitted/approvedは全員、draft/rejectedは権限に応じて

---

#### GET `/revisions/by-article/{target_article_id}`
記事別改訂取得（公開改訂のみ）

**クエリパラメータ**:
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)

**レスポンス**: 改訂リスト

**アクセス可能ロール**: 認証済みユーザー

---

### 3. 提案管理 (Proposals)

#### PUT `/proposals/{revision_id}`
提案更新（ドラフトのみ）

**リクエストボディ**:
```json
{
  "reason": "string",
  "after_title": "string",
  "after_info_category": "uuid",
  "after_keywords": "string",
  "after_importance": true,
  "after_publish_start": "2024-01-01",
  "after_publish_end": "2024-12-31",
  "after_target": "string",
  "after_question": "string",
  "after_answer": "string",
  "after_additional_comment": "string"
}
```

**レスポンス**: 更新された改訂オブジェクト

**アクセス可能ロール**: 提案者本人

---

#### POST `/proposals/{revision_id}/submit`
提案を承認申請

**レスポンス**: 更新された改訂オブジェクト（status: "submitted"）

**アクセス可能ロール**: 提案者本人

---

#### POST `/proposals/{revision_id}/withdraw`
提案を取り下げ（ドラフトに戻す）

**レスポンス**: 更新された改訂オブジェクト（status: "draft"）

**アクセス可能ロール**: 提案者本人

---

#### PUT `/proposals/{revision_id}/approved-update`
承認済み提案の更新

**リクエストボディ**: 改訂更新と同じ

**レスポンス**: 更新された改訂オブジェクト

**アクセス可能ロール**: `approver`, `admin`

---

#### DELETE `/proposals/{revision_id}`
提案削除（ドラフトのみ）

**レスポンス**: 204 No Content

**アクセス可能ロール**: 提案者本人

---

#### GET `/proposals/my-proposals`
自分の提案一覧

**クエリパラメータ**:
- `status`: string (optional)
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)

**レスポンス**: 改訂リスト

**アクセス可能ロール**: 認証済みユーザー

---

#### GET `/proposals/for-approval`
承認待ち提案一覧

**クエリパラメータ**:
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)

**レスポンス**: 改訂リスト

**アクセス可能ロール**: `approver`, `admin`

---

#### GET `/proposals/statistics`
提案統計情報

**クエリパラメータ**:
- `user_id`: uuid (optional, adminのみ)

**レスポンス**:
```json
{
  "total_proposals": 10,
  "draft": 2,
  "submitted": 3,
  "approved": 4,
  "rejected": 1,
  "approval_rate": 80.0
}
```

**アクセス可能ロール**: 認証済みユーザー（自分の統計のみ、adminは全ユーザー）

---

### 4. 承認管理 (Approvals)

#### POST `/approvals/{revision_id}/decide`
承認判定処理

**リクエストボディ**:
```json
{
  "action": "approve", // approve, reject, request_changes, defer
  "comment": "string",
  "conditions": ["condition1", "condition2"],
  "priority": "medium", // low, medium, high, urgent
  "estimated_implementation_time": 60
}
```

**レスポンス**: 更新された改訂オブジェクト

**アクセス可能ロール**: `approver`, `admin`

---

#### GET `/approvals/queue`
承認キュー取得

**クエリパラメータ**:
- `priority`: string (low, medium, high, urgent)
- `limit`: integer (default: 50, max: 100)

**レスポンス**:
```json
[
  {
    "revision_id": "string",
    "target_article_id": "string",
    "article_number": "ART001",
    "proposer_name": "string",
    "reason": "string",
    "priority": "medium",
    "impact_level": "high",
    "total_changes": 5,
    "critical_changes": 2,
    "estimated_review_time": 30,
    "submitted_at": "2024-01-01T00:00:00",
    "days_pending": 3,
    "is_overdue": false
  }
]
```

**アクセス可能ロール**: `approver`, `admin`

---

#### GET `/approvals/workload`
承認者の作業負荷情報

**レスポンス**:
```json
{
  "approver_id": "uuid",
  "approver_name": "string",
  "pending_count": 5,
  "overdue_count": 1,
  "completed_today": 3,
  "completed_this_week": 15,
  "average_review_time": 25,
  "current_capacity": "medium"
}
```

**アクセス可能ロール**: `approver`, `admin`

---

#### GET `/approvals/metrics`
承認プロセスメトリクス

**クエリパラメータ**:
- `days_back`: integer (default: 30, min: 1, max: 365)

**レスポンス**:
```json
{
  "total_pending": 10,
  "total_overdue": 2,
  "average_approval_time": 48.5,
  "approval_rate": 75.0,
  "rejection_rate": 25.0,
  "by_priority": {
    "low": 2,
    "medium": 5,
    "high": 3,
    "urgent": 0
  },
  "by_impact_level": {
    "low": 3,
    "medium": 4,
    "high": 3
  },
  "bottlenecks": ["approval_group_1"],
  "performance_trends": {}
}
```

**アクセス可能ロール**: `approver`, `admin`

---

#### GET `/approvals/{revision_id}/can-approve`
承認権限確認

**レスポンス**:
```json
{
  "can_approve": true
}
```

**アクセス可能ロール**: 認証済みユーザー

---

#### GET `/approvals/history`
承認履歴

**クエリパラメータ**:
- `revision_id`: uuid (optional)
- `approver_id`: uuid (optional)
- `limit`: integer (default: 50, max: 200)

**レスポンス**:
```json
[
  {
    "approval_id": "string",
    "revision_id": "string",
    "approver_id": "string",
    "approver_name": "string",
    "action": "approve",
    "comment": "string",
    "conditions": ["condition1"],
    "priority": "medium",
    "estimated_implementation_time": 60,
    "created_at": "2024-01-01T00:00:00"
  }
]
```

**アクセス可能ロール**: 認証済みユーザー（adminは全履歴、その他は自分のみ）

---

#### GET `/approvals/statistics/dashboard`
承認ダッシュボード

**レスポンス**:
```json
{
  "workload": { /* ApprovalWorkload object */ },
  "recent_queue": [ /* ApprovalQueue array */ ],
  "urgent_items": [ /* ApprovalQueue array */ ],
  "metrics": { /* ApprovalMetrics object */ },
  "summary": {
    "pending_count": 5,
    "overdue_count": 1,
    "urgent_count": 0,
    "capacity_status": "medium"
  }
}
```

**アクセス可能ロール**: `approver`, `admin`

---

#### POST `/approvals/{revision_id}/quick-actions/{action}`
クイック承認アクション

**クエリパラメータ**:
- `comment`: string (optional)

**レスポンス**:
```json
{
  "revision_id": "uuid",
  "action": "approve",
  "new_status": "approved",
  "message": "Revision approved successfully"
}
```

**アクセス可能ロール**: `approver`, `admin`

---

### 5. 記事 (Articles)

#### GET `/articles/`
記事一覧取得

**クエリパラメータ**:
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)

**レスポンス**:
```json
[
  {
    "article_id": "string",
    "article_number": "ART001",
    "article_url": "https://example.com/article",
    "approval_group": "uuid",
    "title": "string",
    "info_category": "uuid",
    "keywords": "string",
    "importance": true,
    "publish_start": "2024-01-01",
    "publish_end": "2024-12-31",
    "target": "string",
    "question": "string",
    "answer": "string",
    "additional_comment": "string",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

**アクセス可能ロール**: 全ユーザー

---

#### GET `/articles/{article_id}`
特定記事取得

**レスポンス**: 記事オブジェクト

**アクセス可能ロール**: 全ユーザー

---

#### POST `/articles/`
記事作成

**リクエストボディ**:
```json
{
  "article_id": "string",
  "article_number": "ART001",
  "article_url": "https://example.com/article",
  "approval_group": "uuid",
  "title": "string",
  "info_category": "uuid",
  "keywords": "string",
  "importance": true,
  "publish_start": "2024-01-01",
  "publish_end": "2024-12-31",
  "target": "string",
  "question": "string",
  "answer": "string",
  "additional_comment": "string"
}
```

**レスポンス**: 作成された記事オブジェクト

**アクセス可能ロール**: `admin`

---

#### PUT `/articles/{article_id}`
記事更新

**リクエストボディ**: 記事作成と同じ（article_idを除く）

**レスポンス**: 更新された記事オブジェクト

**アクセス可能ロール**: `admin`

---

#### GET `/articles/by-category/{info_category}`
カテゴリ別記事取得

**レスポンス**: 記事リスト

**アクセス可能ロール**: 全ユーザー

---

#### GET `/articles/by-group/{approval_group}`
承認グループ別記事取得

**レスポンス**: 記事リスト

**アクセス可能ロール**: 全ユーザー

---

#### GET `/articles/id-by-number/{article_number}`
記事番号から記事ID取得

**レスポンス**:
```json
{
  "article_id": "string"
}
```

**アクセス可能ロール**: 全ユーザー

---

#### GET `/articles/number-by-id/{article_id}`
記事IDから記事番号取得

**レスポンス**:
```json
{
  "article_number": "ART001"
}
```

**アクセス可能ロール**: 全ユーザー

---

### 6. ユーザー管理 (Users)

#### GET `/users/`
ユーザー一覧取得

**クエリパラメータ**:
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)

**レスポンス**: ユーザーリスト

**アクセス可能ロール**: `admin`

---

#### GET `/users/{user_id}`
特定ユーザー取得

**レスポンス**: ユーザーオブジェクト

**アクセス可能ロール**: `admin`、本人

---

#### POST `/users/`
ユーザー作成

**リクエストボディ**:
```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "password123",
  "full_name": "string",
  "sweet_name": "string",
  "ctstage_name": "string",
  "role": "user",
  "approval_group_id": "uuid",
  "is_active": true
}
```

**レスポンス**: 作成されたユーザーオブジェクト

**アクセス可能ロール**: `admin`

---

#### PUT `/users/{user_id}`
ユーザー更新

**リクエストボディ**: ユーザー作成と同じ（passwordを除く）

**レスポンス**: 更新されたユーザーオブジェクト

**アクセス可能ロール**: `admin`

---

#### DELETE `/users/{user_id}`
ユーザー削除

**レスポンス**: 204 No Content

**アクセス可能ロール**: `admin`

---

#### PUT `/users/{user_id}/role`
ユーザーロール更新

**リクエストボディ**:
```json
{
  "role": "approver"
}
```

**レスポンス**: 更新されたユーザーオブジェクト

**アクセス可能ロール**: `admin`

---

#### PUT `/users/{user_id}/approval-group`
ユーザー承認グループ更新

**リクエストボディ**:
```json
{
  "approval_group_id": "uuid"
}
```

**レスポンス**: 更新されたユーザーオブジェクト

**アクセス可能ロール**: `admin`

---

#### PUT `/users/{user_id}/password`
パスワード変更（自分のみ）

**リクエストボディ**:
```json
{
  "current_password": "oldpassword",
  "new_password": "newpassword123"
}
```

**レスポンス**: 成功メッセージ

**アクセス可能ロール**: 本人

---

#### PUT `/users/{user_id}/password-reset`
パスワードリセット（管理者用）

**リクエストボディ**:
```json
{
  "new_password": "newpassword123",
  "reason": "Admin password reset"
}
```

**レスポンス**: 成功メッセージ

**アクセス可能ロール**: `admin`

---

### 7. 情報カテゴリ (Info Categories)

#### GET `/info-categories/`
情報カテゴリ一覧取得

**レスポンス**:
```json
[
  {
    "category_id": "uuid",
    "category_name": "string",
    "description": "string",
    "display_order": 1,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

**アクセス可能ロール**: 全ユーザー

---

#### GET `/info-categories/{category_id}`
特定カテゴリ取得

**レスポンス**: カテゴリオブジェクト

**アクセス可能ロール**: 全ユーザー

---

#### POST `/info-categories/`
カテゴリ作成

**リクエストボディ**:
```json
{
  "category_name": "string",
  "description": "string",
  "display_order": 1
}
```

**レスポンス**: 作成されたカテゴリオブジェクト

**アクセス可能ロール**: `admin`

---

#### PUT `/info-categories/{category_id}`
カテゴリ更新

**リクエストボディ**: カテゴリ作成と同じ

**レスポンス**: 更新されたカテゴリオブジェクト

**アクセス可能ロール**: `admin`

---

#### DELETE `/info-categories/{category_id}`
カテゴリ削除

**レスポンス**: 204 No Content

**アクセス可能ロール**: `admin`

---

### 8. 承認グループ (Approval Groups)

#### GET `/approval-groups/`
承認グループ一覧取得

**レスポンス**:
```json
[
  {
    "group_id": "uuid",
    "group_name": "string",
    "description": "string",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

**アクセス可能ロール**: 全ユーザー

---

#### GET `/approval-groups/{group_id}`
特定グループ取得

**レスポンス**: グループオブジェクト

**アクセス可能ロール**: 全ユーザー

---

#### POST `/approval-groups/`
グループ作成

**リクエストボディ**:
```json
{
  "group_name": "string",
  "description": "string"
}
```

**レスポンス**: 作成されたグループオブジェクト

**アクセス可能ロール**: `admin`

---

#### PUT `/approval-groups/{group_id}`
グループ更新

**リクエストボディ**: グループ作成と同じ

**レスポンス**: 更新されたグループオブジェクト

**アクセス可能ロール**: `admin`

---

#### DELETE `/approval-groups/{group_id}`
グループ削除

**レスポンス**: 204 No Content

**アクセス可能ロール**: `admin`

---

#### GET `/approval-groups/{group_id}/members`
グループメンバー取得

**レスポンス**: ユーザーリスト

**アクセス可能ロール**: 全ユーザー

---

### 9. 通知 (Notifications)

#### GET `/notifications/`
通知一覧取得

**クエリパラメータ**:
- `unread_only`: boolean (default: false)
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)

**レスポンス**:
```json
[
  {
    "notification_id": "uuid",
    "user_id": "uuid",
    "title": "string",
    "message": "string",
    "notification_type": "info",
    "is_read": false,
    "created_at": "2024-01-01T00:00:00"
  }
]
```

**アクセス可能ロール**: 認証済みユーザー（自分の通知のみ）

---

#### GET `/notifications/{notification_id}`
特定通知取得

**レスポンス**: 通知オブジェクト

**アクセス可能ロール**: 通知の受信者

---

#### PATCH `/notifications/{notification_id}/read`
通知を既読にする

**レスポンス**: 更新された通知オブジェクト

**アクセス可能ロール**: 通知の受信者

---

#### POST `/notifications/mark-all-read`
全通知を既読にする

**レスポンス**:
```json
{
  "message": "All notifications marked as read",
  "count": 5
}
```

**アクセス可能ロール**: 認証済みユーザー

---

#### DELETE `/notifications/{notification_id}`
通知削除

**レスポンス**: 204 No Content

**アクセス可能ロール**: 通知の受信者

---

#### GET `/notifications/unread-count`
未読通知数取得

**レスポンス**:
```json
{
  "unread_count": 3
}
```

**アクセス可能ロール**: 認証済みユーザー

---

### 10. 差分 (Diffs)

#### GET `/diffs/{revision_id}`
改訂の差分取得

**レスポンス**:
```json
{
  "revision_id": "uuid",
  "changes": [
    {
      "field": "title",
      "before": "Old Title",
      "after": "New Title",
      "change_type": "update"
    }
  ],
  "summary": {
    "total_changes": 3,
    "fields_changed": ["title", "keywords", "answer"],
    "has_critical_changes": true
  }
}
```

**アクセス可能ロール**: 改訂の閲覧権限を持つユーザー

---

#### GET `/diffs/{revision_id}/formatted`
フォーマット済み差分取得

**クエリパラメータ**:
- `format`: string (html, markdown, plain) (default: html)

**レスポンス**:
```json
{
  "revision_id": "uuid",
  "formatted_diff": "<html>formatted diff content</html>",
  "format": "html"
}
```

**アクセス可能ロール**: 改訂の閲覧権限を持つユーザー

---

#### GET `/diffs/compare`
2つの改訂を比較

**クエリパラメータ**:
- `revision_id_1`: uuid
- `revision_id_2`: uuid

**レスポンス**: 差分情報

**アクセス可能ロール**: 両方の改訂の閲覧権限を持つユーザー

---

### 11. システム (System)

#### GET `/system/health`
ヘルスチェック

**レスポンス**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "version": "1.0.0",
  "database": "connected"
}
```

**アクセス可能ロール**: 全ユーザー

---

#### GET `/system/stats`
システム統計

**レスポンス**:
```json
{
  "total_users": 100,
  "total_articles": 500,
  "total_revisions": 1500,
  "active_sessions": 25,
  "database_size": "256MB"
}
```

**アクセス可能ロール**: `admin`

---

#### GET `/system/config`
システム設定取得

**レスポンス**:
```json
{
  "max_upload_size": 10485760,
  "session_timeout": 3600,
  "approval_timeout_days": 7,
  "features": {
    "notifications": true,
    "bulk_approval": false
  }
}
```

**アクセス可能ロール**: 認証済みユーザー

---

## エラーレスポンス

APIは以下の形式でエラーを返します：

```json
{
  "detail": "エラーメッセージ"
}
```

### HTTPステータスコード

| コード | 意味 | 説明 |
|--------|------|------|
| 200 | OK | リクエスト成功 |
| 201 | Created | リソース作成成功 |
| 204 | No Content | 削除成功 |
| 400 | Bad Request | 不正なリクエスト |
| 401 | Unauthorized | 認証が必要 |
| 403 | Forbidden | アクセス権限なし |
| 404 | Not Found | リソースが見つからない |
| 422 | Unprocessable Entity | バリデーションエラー |
| 500 | Internal Server Error | サーバーエラー |

## 開発環境での利用

### APIドキュメント

開発環境では、以下のURLでインタラクティブなAPIドキュメントを利用できます：

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### テスト用トークン取得

```bash
# ログインしてトークンを取得
curl -X POST "http://localhost:8000/api/v1/auth/login/json" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# トークンを使用してAPIにアクセス
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer {access_token}"
```

## フロントエンド実装のヒント

### 認証フロー実装例

```javascript
// ログイン
async function login(email, password) {
  const response = await fetch('/api/v1/auth/login/json', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });

  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('token', data.access_token);
    return data;
  }
  throw new Error('Login failed');
}

// APIリクエスト例
async function fetchMyRevisions() {
  const token = localStorage.getItem('token');
  const response = await fetch('/api/v1/revisions/my-revisions', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (response.ok) {
    return await response.json();
  }

  if (response.status === 401) {
    // トークンが無効 - 再ログインが必要
    window.location.href = '/login';
  }

  throw new Error('Failed to fetch revisions');
}
```

### ロールベースのUI制御

```javascript
// ユーザー情報を取得してロールを確認
async function checkUserRole() {
  const response = await fetch('/api/v1/auth/me', {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  });

  if (response.ok) {
    const user = await response.json();

    // ロールに基づいてUIを表示/非表示
    if (user.role === 'admin') {
      document.querySelector('.admin-panel').style.display = 'block';
    }

    if (user.role === 'approver' || user.role === 'admin') {
      document.querySelector('.approval-section').style.display = 'block';
    }

    return user;
  }

  throw new Error('Failed to get user info');
}
```

### エラーハンドリング

```javascript
async function handleApiCall(url, options = {}) {
  try {
    const token = localStorage.getItem('token');
    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      const error = await response.json();

      switch(response.status) {
        case 401:
          // 認証エラー - 再ログイン
          window.location.href = '/login';
          break;
        case 403:
          // 権限エラー
          alert('このアクションを実行する権限がありません');
          break;
        case 404:
          // リソースが見つからない
          alert('要求されたリソースが見つかりません');
          break;
        default:
          // その他のエラー
          alert(error.detail || 'エラーが発生しました');
      }

      throw new Error(error.detail);
    }

    return await response.json();
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
}
```

## 注意事項

1. **JWT トークンの有効期限**: デフォルトで8日間（設定により変更可能）
2. **CORS設定**: 開発環境では`localhost:3000`と`localhost:3001`からのアクセスを許可
3. **レート制限**: 本番環境では適切なレート制限を設定することを推奨
4. **データベース**: PostgreSQLを使用（テスト環境ではSQLite）
5. **非同期処理**: すべてのエンドポイントは非同期で実装されている