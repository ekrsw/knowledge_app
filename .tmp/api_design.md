# API設計書 - ナレッジ修正案承認システム

## 1. API設計概要

### 1.1 設計原則
- **RESTful設計**: リソースベースのURL設計
- **統一性**: 一貫したレスポンス形式
- **セキュリティ**: JWT認証 + 権限ベースアクセス制御
- **エラーハンドリング**: 標準化されたエラーレスポンス

### 1.2 ベースURL
```
Production: https://knowledge-system.company.com/api/v1
Development: http://localhost:8000/api/v1
```

## 2. 認証・認可

### 2.1 JWT認証
```http
Authorization: Bearer {jwt_token}
```

### 2.2 依存関数による権限制御
```python
get_current_active_user()      # 認証済みアクティブユーザー
get_current_approver_user()    # 承認者権限チェック
get_current_admin_user()       # 管理者権限チェック
```

## 3. APIエンドポイント詳細

### 3.1 修正案管理 (/api/v1/revisions)

#### 修正案一覧取得
```http
GET /api/v1/revisions/
```
**権限**: 認証済みユーザー  
**説明**: 権限に応じた修正案一覧を取得
- Admin: 全修正案
- Approver: 担当グループの修正案
- User: 自分の修正案のみ

**クエリパラメータ**:
- `skip`: int = 0 (オフセット)
- `limit`: int = 100 (取得件数)
- `status`: str (ステータスフィルタ)
- `proposer_id`: UUID (提出者フィルタ、管理者のみ)

**レスポンス**:
```json
{
  "items": [
    {
      "revision_id": "uuid",
      "target_article_id": "string",
      "proposer_id": "uuid",
      "approver_id": "uuid",
      "status": "draft|submitted|approved|rejected|deleted",
      "reason": "string",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "processed_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 150,
  "skip": 0,
  "limit": 100
}
```

#### 修正案詳細取得
```http
GET /api/v1/revisions/{revision_id}
```
**権限**: 修正案の関係者（提出者・承認者・管理者）  
**レスポンス**: 修正案の全詳細情報（after_*フィールド含む）

#### 修正案作成
```http
POST /api/v1/revisions/
```
**権限**: 認証済みユーザー  
**リクエストボディ**:
```json
{
  "target_article_id": "string",
  "approver_id": "uuid",
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

#### 修正案更新
```http
PUT /api/v1/revisions/{revision_id}
```
**権限**: 修正案の提出者（draft状態のみ）  
**制約**: ステータスが'draft'の場合のみ更新可能

#### 修正案削除
```http
DELETE /api/v1/revisions/{revision_id}
```
**権限**: 修正案の提出者または管理者（draft状態のみ）  

#### 修正案提出
```http
POST /api/v1/revisions/{revision_id}/submit
```
**権限**: 修正案の提出者  
**状態遷移**: draft → submitted

#### 修正案撤回
```http
POST /api/v1/revisions/{revision_id}/withdraw
```
**権限**: 修正案の提出者  
**状態遷移**: submitted → draft

### 3.2 承認管理 (/api/v1/approvals)

#### 承認・却下処理
```http
POST /api/v1/approvals/{revision_id}/decide
```
**権限**: 指定された承認者  
**リクエストボディ**:
```json
{
  "action": "approve|reject",
  "comment": "string"
}
```
**状態遷移**: submitted → approved/rejected

#### 承認状況取得
```http
GET /api/v1/approvals/{revision_id}/status
```
**権限**: 修正案の関係者  
**レスポンス**:
```json
{
  "revision_id": "uuid",
  "status": "submitted",
  "approver": {
    "id": "uuid",
    "username": "string",
    "full_name": "string"
  },
  "can_approve": true,
  "approval_deadline": "2024-01-15T00:00:00Z"
}
```

#### 承認待ち一覧
```http
GET /api/v1/approvals/queue
```
**権限**: 承認者  
**説明**: 全承認者の承認待ち案件

#### 自分の承認待ち一覧
```http
GET /api/v1/approvals/my-queue
```
**権限**: 承認者  
**説明**: 自分が承認者として指定された案件のみ

#### 承認統計
```http
GET /api/v1/approvals/metrics
```
**権限**: 承認者・管理者  
**レスポンス**:
```json
{
  "pending_count": 15,
  "approved_today": 5,
  "rejected_today": 1,
  "avg_approval_time": "2.5 days",
  "approval_rate": 85.5
}
```

#### 一括承認・却下
```http
POST /api/v1/approvals/batch
```
**権限**: 承認者  
**リクエストボディ**:
```json
{
  "revision_ids": ["uuid1", "uuid2"],
  "action": "approve|reject",
  "comment": "string"
}
```

### 3.3 差分表示 (/api/v1/diffs)

#### 差分データ取得
```http
GET /api/v1/diffs/{revision_id}
```
**権限**: 修正案の関係者  
**レスポンス**:
```json
{
  "revision_id": "uuid",
  "diffs": {
    "title": {
      "field_name": "title",
      "current_value": "既存タイトル",
      "proposed_value": "新しいタイトル", 
      "change_type": "modified"
    },
    "keywords": {
      "field_name": "keywords",
      "current_value": null,
      "proposed_value": "新規キーワード",
      "change_type": "added"
    }
  }
}
```

#### プレビュー表示用データ
```http
GET /api/v1/diffs/{revision_id}/preview
```
**権限**: 修正案の関係者  
**レスポンス**:
```json
{
  "current_article": {
    "title": "既存タイトル",
    "info_category": "uuid",
    "keywords": "既存キーワード"
  },
  "proposed_changes": {
    "title": "新しいタイトル",
    "info_category": "uuid",
    "keywords": "新しいキーワード"
  },
  "merged_preview": {
    "title": "新しいタイトル",
    "info_category": "uuid", 
    "keywords": "新しいキーワード"
  }
}
```

#### 変更サマリー
```http
GET /api/v1/diffs/{revision_id}/summary
```
**権限**: 修正案の関係者  
**レスポンス**:
```json
{
  "total_changes": 3,
  "change_breakdown": {
    "added": 1,
    "modified": 2,
    "deleted": 0
  },
  "affected_fields": ["title", "keywords", "importance"],
  "change_summary": "タイトルを変更し、キーワードを追加、重要度を設定しました",
  "impact_level": "medium"
}
```

### 3.4 ユーザー管理 (/api/v1/users)

#### ユーザー一覧取得
```http
GET /api/v1/users/
```
**権限**: 管理者

#### ユーザー詳細取得
```http
GET /api/v1/users/{user_id}
```
**権限**: 本人または管理者

#### 現在のユーザー情報取得
```http
GET /api/v1/users/me
```
**権限**: 認証済みユーザー

#### 承認者一覧取得
```http
GET /api/v1/users/approvers
```
**権限**: 認証済みユーザー（修正案作成時の承認者選択用）

### 3.5 記事管理 (/api/v1/articles)

#### 記事一覧取得
```http
GET /api/v1/articles/
```
**権限**: 認証済みユーザー

#### 記事詳細取得
```http
GET /api/v1/articles/{article_id}
```
**権限**: 認証済みユーザー

#### 記事作成
```http
POST /api/v1/articles/
```
**権限**: 管理者

### 3.6 承認グループ管理 (/api/v1/approval-groups)

#### 承認グループ一覧
```http
GET /api/v1/approval-groups/
```
**権限**: 管理者

#### 承認グループ詳細
```http
GET /api/v1/approval-groups/{group_id}
```
**権限**: 管理者またはグループメンバー

### 3.7 情報カテゴリ管理 (/api/v1/info-categories)

#### カテゴリ一覧
```http
GET /api/v1/info-categories/
```
**権限**: 認証済みユーザー

### 3.8 通知管理 (/api/v1/notifications)

#### 通知一覧取得
```http
GET /api/v1/notifications/
```
**権限**: 認証済みユーザー（自分の通知のみ）

#### 通知既読化
```http
POST /api/v1/notifications/{notification_id}/read
```
**権限**: 通知の受信者

### 3.9 システム情報 (/api/v1/system)

#### ヘルスチェック
```http
GET /api/v1/system/health
```
**権限**: なし（public）  
**レスポンス**:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### システム情報
```http
GET /api/v1/system/info
```
**権限**: 管理者  
**レスポンス**:
```json
{
  "version": "1.0.0",
  "environment": "production",
  "uptime": "15 days 3 hours",
  "active_users": 45
}
```

## 4. 共通レスポンス形式

### 4.1 成功レスポンス
```json
{
  "data": { /* リソースデータ */ },
  "message": "操作が完了しました",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 4.2 エラーレスポンス
```json
{
  "detail": "エラーの詳細メッセージ",
  "error_code": "PROPOSAL_NOT_FOUND",
  "timestamp": "2024-01-01T00:00:00Z",
  "path": "/api/v1/revisions/invalid-uuid"
}
```

### 4.3 バリデーションエラー
```json
{
  "detail": "Validation error",
  "errors": [
    {
      "field": "approver_id",
      "message": "承認者IDは必須です",
      "code": "required"
    }
  ]
}
```

## 5. ステータスコード

- **200 OK**: 正常取得
- **201 Created**: 正常作成
- **204 No Content**: 正常削除
- **400 Bad Request**: 不正なリクエスト
- **401 Unauthorized**: 認証エラー
- **403 Forbidden**: 権限エラー
- **404 Not Found**: リソース未発見
- **409 Conflict**: 状態競合エラー
- **422 Unprocessable Entity**: バリデーションエラー
- **500 Internal Server Error**: サーバーエラー

## 6. レート制限

### 6.1 制限値
- **一般API**: 1000 requests/hour per user
- **認証API**: 100 requests/hour per IP
- **アップロードAPI**: 50 requests/hour per user

### 6.2 制限ヘッダー
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## 7. キャッシュ戦略

### 7.1 キャッシュ対象
- **ユーザー情報**: 15分
- **記事一覧**: 5分
- **カテゴリ一覧**: 1時間
- **承認グループ**: 30分

### 7.2 キャッシュヘッダー
```http
Cache-Control: public, max-age=300
ETag: "abc123"
```

## 8. APIバージョニング

### 8.1 バージョニング方式
- **URLパス**: `/api/v1/`, `/api/v2/`
- **後方互換性**: v1は最低2年間サポート
- **廃止予告**: 6ヶ月前に通知

### 8.2 バージョン情報
```http
API-Version: 1.0
```

このAPI設計により、ナレッジ修正案承認システムの全機能が統一的で使いやすいインターフェースで提供されます。