# Knowledge System Approval Platform (KSAP) API仕様書（実装準拠版）

## 概要

Knowledge System Approval Platform (KSAP)は、知識改訂提案の作成、承認ワークフロー、変更追跡を管理するためのRESTful APIです。本書は 2025-09-14 時点の実装（`backend/app/api/v1`）に準拠しています。

- ベースURL: `http://localhost:8000/api/v1`
- 認証方式: JWT Bearer Token
- APIドキュメント（開発環境）: `http://localhost:8000/docs`（OpenAPI: `/api/v1/openapi.json`）

## 認証とロール

### ユーザーロール

| ロール | 説明 | 権限 |
|--------|------|------|
| `user` | 一般ユーザー | 自身の改訂提案の作成・管理 |
| `approver` | 承認者 | 担当領域の提案レビュー・承認/却下 |
| `admin` | 管理者 | システム全体へのフルアクセス |

### 認証フロー

1. `/auth/login` または `/auth/login/json` でユーザー名/メールとパスワードを送信
2. JWTトークンを受け取る
3. 以降のリクエストでは `Authorization: Bearer {token}` ヘッダーを付与

---

## APIエンドポイント仕様

以下は実装されているエンドポイントと入出力・権限制約です。

### 1. 認証 (Authentication)

#### POST `/auth/login`
OAuth2互換のトークンログイン（`form-data`）

リクエスト（form-data）:
```
username: string
password: string
```

レスポンス:
```json
{ "access_token": "string", "token_type": "bearer" }
```

アクセス: 全ユーザー

---

#### POST `/auth/test-token`
トークン検証（現在のユーザー情報を返す）

レスポンス: `GET /auth/me` と同じ

アクセス: 認証済みユーザー

---

#### POST `/auth/login/json`
JSON形式でのログイン

リクエスト:
```json
{ "email": "user@example.com", "password": "password123" }
```

レスポンス:
```json
{ "access_token": "string", "token_type": "bearer" }
```

アクセス: 全ユーザー

---

#### POST `/auth/register`
新規ユーザー登録

リクエスト:
```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "password123",
  "full_name": "string",
  "sweet_name": "string",
  "ctstage_name": "string"
}
```

レスポンス（User）: 作成されたユーザー

アクセス: 全ユーザー

---

#### GET `/auth/me`
現在のユーザー情報取得

レスポンス（User）

アクセス: 認証済みユーザー

---

#### POST `/auth/logout`
ログアウト（クライアント側でトークン破棄）

レスポンス:
```json
{
  "message": "Successfully logged out",
  "detail": "For stateless JWT authentication, please discard the token on client side"
}
```

アクセス: 認証済みユーザー

---

#### GET `/auth/verify`
JWTトークン検証（ユーザー含む簡易応答）

レスポンス:
```json
{ "valid": true, "user": { /* User */ }, "token_type": "bearer" }
```

アクセス: 認証済みユーザー

---

#### GET `/auth/status`
認証ステータス

レスポンス:
```json
{ "authenticated": true, "user_id": "uuid", "username": "string", "role": "user", "is_active": true }
```

アクセス: 認証済みユーザー

---

#### JWTトークン仕様（クレーム）

- 署名アルゴリズム: `HS256`
- 署名鍵: サーバの `SECRET_KEY`
- 有効期限: `exp`（UTCのUNIXエポック秒）。デフォルトは `ACCESS_TOKEN_EXPIRE_MINUTES`（既定値: 8日）に基づき付与されます。
- 発行者/オーディエンス: 本実装では `iss`/`aud` は付与・検証していません。
- ペイロードに含まれる主なクレーム:
  - `sub`: ユーザーID（UUID文字列）。サーバ側はこのIDでユーザーを特定します。
  - `exp`: トークンの有効期限（UTC）
  - `role`: ユーザーの役割（`user` | `approver` | `admin`）。ログイン時に付与。省略される場合があります。

注意事項:
- サーバ側の認可判定はDB上のユーザー情報を参照して行います。`role` クレームのみでは権限制御しません。
- トークンはステートレスで、サーバ側にセッションは持ちません。失効やログアウトはクライアントでトークンを破棄してください。

例: JWTペイロード（デコード後）
```json
{
  "sub": "e7a5f1e0-1234-4c9a-9a1a-abcdef012345",
  "exp": 1726400000,
  "role": "approver"
}
```

---

### 2. 改訂提案 (Revisions)

#### GET `/revisions/`
改訂一覧取得（権限フィルタ）。レスポンスは提案者/承認者名と記事番号を含む拡張形。

クエリ:
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)

レスポンス（RevisionWithNames）例:
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

アクセス:
- `admin`: 全件
- その他: submitted/approved + 自身の draft/rejected

---

#### GET `/revisions/my-revisions`
自分の改訂一覧（拡張形）

---

#### GET `/revisions/{revision_id}`
特定の改訂取得

アクセス:
- `admin`: 全て
- `submitted/approved`: 全員
- `draft`: 提案者のみ
- `rejected`: 提案者または承認者

---

#### POST `/revisions/`
新規改訂作成（`proposer_id` はログインユーザーに自動設定）

リクエスト（RevisionCreate）: `target_article_id`, `reason`, `approver_id` は必須。`after_*` は任意。

---

#### PUT `/revisions/{revision_id}`
改訂更新

アクセス:
- draft: 提案者のみ
- approved: 承認者または `admin`（一部メタデータ更新は制限）

---

#### PATCH `/revisions/{revision_id}/status`
改訂ステータス更新（`submitted|approved|rejected|deleted`）

アクセス: `approver`, `admin`

---

#### GET `/revisions/by-status/{status}`
ステータス別改訂（`RevisionWithNames` 配列）

---

#### GET `/revisions/by-article/{target_article_id}`
記事別の公開改訂（`submitted`/`approved` のみ）

---

#### GET `/revisions/by-proposer/{proposer_id}`
提案者別改訂（本人または `admin`）

---

### 3. 提案管理 (Proposals)

提案の作成は `/revisions/` に統合済み。以下はビジネス操作のエンドポイント。

#### PUT `/proposals/{revision_id}`
ドラフト提案の更新（本人のみ）

#### POST `/proposals/{revision_id}/submit`
承認申請（ステータスを `submitted`）

#### POST `/proposals/{revision_id}/withdraw`
取り下げ（`draft` に戻す）

#### PUT `/proposals/{revision_id}/approved-update`
承認済み提案の更新（承認者または `admin`）

#### DELETE `/proposals/{revision_id}`
ドラフト提案の削除

#### GET `/proposals/my-proposals`
自分の提案一覧（`status`/`skip`/`limit`）

#### GET `/proposals/for-approval`
承認待ち一覧（承認者/`admin`）

#### GET `/proposals/statistics`
提案統計（`admin` は任意の `user_id` 指定可。一般は自分のみ）

#### GET `/proposals/{revision_id}`
提案詳細（公開・権限ルールは Revisions と同様）

---

### 4. 承認管理 (Approvals)

#### POST `/approvals/{revision_id}/decide`
承認判定（`approve|reject|request_changes|defer`、コメント等を含む）

#### GET `/approvals/queue`
承認キュー（`priority` フィルタ、`limit` 最大100）

#### GET `/approvals/workload`
承認者の作業負荷

#### GET `/approvals/metrics`
承認メトリクス（`days_back`）

#### GET `/approvals/{revision_id}/can-approve`
自身が当該改訂を承認可能か

#### GET `/approvals/history`
承認履歴（一般ユーザーは自身分のみ、`admin` は全体）

#### GET `/approvals/statistics/dashboard`
ダッシュボード（workload/queue/metrics などのサマリ）

#### POST `/approvals/{revision_id}/quick-actions/{action}`
クイック承認アクション（簡易判定）

---

### 5. 記事 (Articles)

#### GET `/articles/`
記事一覧（`skip`/`limit`）

#### GET `/articles/{article_id}`
記事取得

#### POST `/articles/`
記事作成（`admin`）

#### PUT `/articles/{article_id}`
記事更新（`admin`）

#### GET `/articles/by-category/{info_category}`
カテゴリ別一覧

#### GET `/articles/by-group/{approval_group}`
承認グループ別一覧

#### GET `/articles/id-by-number/{article_number}`
記事番号からID取得 → `{ "article_id": "string" }`

#### GET `/articles/number-by-id/{article_id}`
記事IDから番号取得 → `{ "article_number": "ART001" }`

---

### 6. ユーザー管理 (Users)

#### GET `/users/`
ユーザー一覧（`admin`）

#### GET `/users/{user_id}`
ユーザー取得（本人または `admin`）

#### POST `/users/`
ユーザー作成（`admin`）

#### PUT `/users/{user_id}`
ユーザー更新（本人または `admin`）。管理者のみ `role`/`approval_group_id` を変更可能。

#### DELETE `/users/{user_id}`
ユーザー削除（`admin`）

#### PUT `/users/{user_id}/password`
自身のパスワード変更（現パスワード検証あり）

#### PUT `/users/{user_id}/admin-reset-password`
管理者によるパスワードリセット（理由付与、監査想定）

---

### 7. 情報カテゴリ (Info Categories)

#### GET `/info-categories/`
情報カテゴリ一覧

レスポンス例:
```json
[
  {
    "category_id": "uuid",
    "category_name": "string",
    "is_active": true,
    "description": "string",
    "display_order": 1,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

#### GET `/info-categories/active`
有効カテゴリ一覧

#### GET `/info-categories/{category_id}`
カテゴリ取得

#### POST `/info-categories/`
カテゴリ作成（`admin`）

#### PUT `/info-categories/{category_id}`
カテゴリ更新（`admin`）

（注）削除エンドポイントは実装されていません

---

### 8. 承認グループ (Approval Groups)

#### GET `/approval-groups/`
承認グループ一覧

#### GET `/approval-groups/{group_id}`
承認グループ取得

#### POST `/approval-groups/`
承認グループ作成（`admin`）

#### PUT `/approval-groups/{group_id}`
承認グループ更新（`admin`）

（注）削除およびメンバー一覧エンドポイントは実装されていません

---

### 9. 通知 (Notifications)

#### GET `/notifications/my-notifications`
自身の通知一覧

クエリ:
- `unread_only`: boolean（default: false）
- `skip`: integer（default: 0）
- `limit`: integer（default: 20, max: 100）

レスポンス（SimpleNotification 配列）:
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "revision_id": "uuid",
    "message": "string",
    "type": "string",
    "is_read": false,
    "created_at": "2024-01-01T00:00:00"
  }
]
```

#### PUT `/notifications/{notification_id}/read`
通知を既読にする（受信者または `admin`）

#### PUT `/notifications/read-all`
自身の通知を一括既読

レスポンス例: `{ "message": "N件の通知を既読にしました" }`

#### GET `/notifications/{user_id}`（レガシー, `admin`）
指定ユーザーの通知一覧（管理者のみ）

#### POST `/notifications/`（レガシー, `admin`）
通知作成（簡易通知）

（注）通知の削除/未読数取得/詳細取得エンドポイントは実装されていません

---

### 10. 差分 (Diffs)

#### GET `/diffs/{revision_id}`
改訂の差分取得（`RevisionDiff`）

レスポンス例（抜粋）:
```json
{
  "revision_id": "uuid",
  "target_article_id": "string",
  "proposer_name": "string",
  "reason": "string",
  "status": "submitted",
  "created_at": "2024-01-01T00:00:00",
  "field_diffs": [
    {
      "field_name": "title",
      "field_label": "タイトル",
      "change_type": "modified",
      "old_value": "Old Title",
      "new_value": "New Title",
      "is_critical": false
    }
  ],
  "total_changes": 3,
  "critical_changes": 1,
  "change_categories": ["content"],
  "impact_level": "medium"
}
```

権限: 提案者自身、承認者（`submitted` 等の条件下）、`admin`

#### GET `/diffs/{revision_id}/summary`
差分サマリー（`DiffSummary`）

#### GET `/diffs/article/{article_id}/snapshot`
記事の現行スナップショット（`ArticleSnapshot`）

#### GET `/diffs/article/{article_id}/history`
記事の差分履歴（最大50件）

（注）`/diffs/{revision_id}/formatted` および `/diffs/compare` は未実装です

---

### 11. システム (System)

#### GET `/system/health`
ヘルスチェック

レスポンス例:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "version": "0.1.0",
  "environment": "development",
  "database": "connected"
}
```

#### GET `/system/version`
バージョン情報

#### GET `/system/stats`
システム統計（`admin` のみ）

レスポンス例:
```json
{
  "users": { "total_users": 100, "by_role": {"admin": 2, "approver": 5, "user": 93} },
  "revisions": { "total_revisions": 1500, "by_status": {"draft": 10, "submitted": 20, "approved": 1460, "rejected": 10} },
  "notifications": { "total_notifications": 200, "unread_count": 12, "read_count": 188 },
  "system": { "database_status": "connected", "api_status": "operational", "last_updated": "2024-01-01T00:00:00" }
}
```

#### GET `/system/api-documentation`
APIエンドポイントの概要サマリ

---

## エラーレスポンス

標準形式:
```json
{ "detail": "エラーメッセージ" }
```

主なHTTPステータス:

| コード | 意味 |
|--------|------|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Unprocessable Entity |
| 500 | Internal Server Error |

---

## 開発環境での利用

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

トークン取得例:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login/json" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer {access_token}"
```

---

## 注意事項

1. JWTトークン有効期限: `ACCESS_TOKEN_EXPIRE_MINUTES` に依存
2. CORS: 開発環境では `localhost:3000`/`3001` を許可
3. レート制限: 本番環境での導入を推奨
4. データベース: 本番はPostgreSQL、テストはSQLite
5. 非同期処理: すべてのエンドポイントは非同期実装

## 付記（エイリアス）

- `GET /api/v1/health` は `GET /api/v1/system/health` のエイリアス
- `GET /api/v1/users/me` は `GET /api/v1/auth/me` のエイリアス
