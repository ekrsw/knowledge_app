# ログインシーケンス図

## 概要

Knowledge Revision Approval Systemのログイン処理のシーケンス図です。
システムはNext.js (Frontend) + FastAPI (Backend) + PostgreSQL (Database)の構成で、NextAuth.jsとJWT認証を使用しています。

## ログインシーケンス

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant Frontend as Frontend<br/>(Next.js + NextAuth)
    participant Backend as Backend<br/>(FastAPI)
    participant DB as Database<br/>(PostgreSQL)
    participant Session as Session Store<br/>(NextAuth JWT)

    Note over User,Session: ログイン開始
    User->>Frontend: 1. ログインページにアクセス (/auth/signin)
    Frontend->>User: 2. ログインフォーム表示

    Note over User,Session: 認証情報送信
    User->>Frontend: 3. username, password 入力・送信
    Frontend->>Frontend: 4. NextAuth credentials provider実行

    Note over User,Session: バックエンド認証
    Frontend->>Backend: 5. POST /api/v1/auth/login/json<br/>{username, password}
    Backend->>Backend: 6. user_repository.authenticate() 実行
    Backend->>DB: 7. SELECT user WHERE username = ?
    DB->>Backend: 8. ユーザー情報返却
    Backend->>Backend: 9. verify_password(plain, hash) でパスワード検証
    
    alt 認証成功
        Backend->>Backend: 10. create_access_token() でJWT生成<br/>(expire: ACCESS_TOKEN_EXPIRE_MINUTES)
        Backend->>Frontend: 11. {access_token, token_type: "bearer"}
        
        Note over User,Session: セッション作成
        Frontend->>Session: 12. NextAuth JWT token作成<br/>(user info + access_token)
        Frontend->>User: 13. ログイン成功・ダッシュボードリダイレクト
        
    else 認証失敗
        Backend->>Frontend: 11. HTTP 401 Unauthorized
        Frontend->>User: 13. ログインエラー表示
    end

    Note over User,Session: 後続リクエスト（認証が必要なページ）
    User->>Frontend: 14. 保護されたページアクセス
    Frontend->>Frontend: 15. useAuth() hook でセッション確認
    Frontend->>Session: 16. NextAuth session取得
    Session->>Frontend: 17. user情報 + accessToken
    
    alt セッション有効
        Frontend->>Backend: 18. API呼び出し<br/>Authorization: Bearer {access_token}
        Backend->>Backend: 19. HTTPBearer security dependency
        Backend->>Backend: 20. verify_token(token) でJWT検証
        Backend->>DB: 21. SELECT user WHERE id = ?
        DB->>Backend: 22. ユーザー情報返却
        Backend->>Backend: 23. get_current_active_user() で権限確認
        Backend->>Frontend: 24. API レスポンス
        Frontend->>User: 25. ページ表示
        
    else セッション無効/期限切れ
        Frontend->>User: 18. ログインページリダイレクト (/auth/signin)
    end
```

## 主要コンポーネント

### Frontend (Next.js + NextAuth)
- **NextAuth Configuration** (`/app/api/auth/[...nextauth]/route.ts`)
  - CredentialsProvider でユーザー名・パスワード認証
  - JWT戦略でセッション管理
  - バックエンドAPI(`/api/v1/auth/login`)への認証要求

- **Authentication Hook** (`/src/hooks/use-auth.ts`)
  - `useSession()`をラップしたカスタムフック
  - ユーザー情報、認証状態、アクセストークンを提供

- **Protected Route** (`/src/components/auth/protected-route.tsx`)
  - 認証状態チェック
  - 役割ベースアクセス制御 (RBAC)
  - 承認グループベースアクセス制御

### Backend (FastAPI)
- **Auth Endpoints** (`/app/api/v1/endpoints/auth.py`)
  - `POST /login`: OAuth2形式ログイン (form-data)
  - `POST /login/json`: JSON形式ログイン
  - `GET /me`: 現在のユーザー情報取得
  - `POST /test-token`: トークン検証

- **Security Module** (`/app/core/security.py`)
  - `create_access_token()`: JWT生成
  - `verify_token()`: JWT検証
  - `verify_password()`: bcryptパスワード検証
  - `get_password_hash()`: パスワードハッシュ化

- **Dependencies** (`/app/api/dependencies.py`)
  - `get_current_user()`: JWTからユーザー取得
  - `get_current_active_user()`: アクティブユーザー確認
  - `get_current_approver_user()`: 承認者権限確認
  - `get_current_admin_user()`: 管理者権限確認

- **User Repository** (`/app/repositories/user.py`)
  - `authenticate()`: ユーザー名・パスワード認証
  - `create_with_password()`: パスワードハッシュ化してユーザー作成

### Database (PostgreSQL)
- **users テーブル**
  - id (UUID, Primary Key)
  - username (Unique)
  - email (Unique)
  - password_hash (bcrypt)
  - role (user/approver/admin)
  - approval_group_id (Foreign Key)
  - is_active (Boolean)

## 認証フロー特徴

1. **ハイブリッド認証**: NextAuth (Frontend) + JWT (Backend)
2. **役割ベースアクセス制御**: user, approver, admin の3つの役割
3. **承認グループベースアクセス制御**: 承認グループ単位でのアクセス制限
4. **セキュア実装**: bcrypt + JWT + HTTPSのみアクセス
5. **セッション管理**: NextAuth JWT戦略でステートレス
6. **トークン期限**: 設定可能 (ACCESS_TOKEN_EXPIRE_MINUTES)

## エラーハンドリング

- **401 Unauthorized**: 認証情報が無効
- **400 Bad Request**: 非アクティブユーザー
- **403 Forbidden**: 権限不足
- 自動的にログインページリダイレクト