# テストユーザー情報

バックエンド開発・テスト用のユーザーアカウント情報

## 管理者 (Admin)
- **Username**: testadmin
- **Email**: testadmin@example.com
- **Password**: password
- **Role**: admin
- **権限**: 全修正案の操作・閲覧可能

## 承認者 (Approver)
- **Username**: testapprover
- **Email**: testapprover@example.com
- **Password**: password
- **Role**: approver
- **権限**: 担当グループの修正案承認可能 + 自分の修正案操作

## 一般ユーザー (User)
- **Username**: testuser
- **Email**: testuser@example.com
- **Password**: password
- **Role**: user
- **権限**: 自分の修正案のみ操作可能

## バックエンドAPI接続情報
- **Base URL**: http://localhost:8000
- **API Path**: /api/v1/
- **認証方式**: JWT Bearer Token
- **ログインエンドポイント**: POST /api/v1/auth/login