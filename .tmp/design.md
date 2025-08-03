# 詳細設計書 - ナレッジの修正案を提出・承認する機能

## 1. アーキテクチャ概要

### 1.1 システム構成図

```
┌─────────────────────────────────────────────────────────────────┐
│                        フロントエンド                             │
├─────────────────────────────────────────────────────────────────┤
│  修正案管理UI    │   承認ワークフローUI   │   通知・ダッシュボード   │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ REST API
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      APIゲートウェイ層                            │
├─────────────────────────────────────────────────────────────────┤
│   認証・認可   │   レート制限   │   ロギング   │   エラーハンドリング  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                       ビジネスロジック層                          │
├─────────────────────────────────────────────────────────────────┤
│ ProposalService │ ApprovalService │ NotificationService │ DiffService │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                       データアクセス層                           │
├─────────────────────────────────────────────────────────────────┤
│ RevisionRepository │ UserRepository │ ArticleRepository │ NotificationRepository │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                         データ層                                │
├─────────────────────────────────────────────────────────────────┤
│   PostgreSQL 17   │   Redis 3.0.504   │   ファイルストレージ    │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 技術スタック

**バックエンド**:
- 言語: Python 3.12+
- フレームワーク: FastAPI 0.115.8
- ORM: SQLAlchemy 2.0.40（Mapped/mapped_column使用） + Alembic 1.14.1
- データベース: PostgreSQL 17 (asyncpg 0.30.0), Redis 3.0.504
- 認証: python-jose[cryptography] 3.4.0 + passlib 1.7.4 + bcrypt 3.2.2
- バックグラウンドタスク: APScheduler（定期処理）
- テスト: pytest 8.3.4 + pytest-asyncio 0.26.0 + fakeredis 2.20.1
- その他: 
  - pydantic 2.10.6 + pydantic_settings 2.8.1
  - uvicorn 0.34.0 (ASGI server)
  - ulid-py 1.1.0 (ID生成)

**フロントエンド**:
- 言語: TypeScript 5.0+
- フレームワーク: React 18+ with Next.js 14
- 認証: NextAuth.js
- UI: Tailwind CSS + Shadcn/ui
- 差分表示: react-diff-viewer
- 通知: Socket.io
- バリデーション: Zod
- テスト: Jest, React Testing Library, Playwright

**ツール**: ESLint, Prettier

## 2. コンポーネント設計

### 2.1 コンポーネント一覧

| コンポーネント名 | 責務 | 依存関係 |
|----------------|-----|---------|
| ProposalService | 修正案の作成・管理・検索・ライフサイクル管理 | RevisionRepository, ArticleRepository, NotificationService |
| ApprovalService | 承認ワークフローの管理・承認/却下処理 | RevisionRepository, UserRepository, NotificationService |
| DiffService | 修正差分の生成・表示・比較機能 | ArticleRepository, RevisionRepository |
| NotificationService | 通知・アラートの送信・管理 | UserRepository, SimpleNotificationRepository |
| UserService | ユーザー認証・認可・権限管理 | UserRepository |

### 2.2 各コンポーネントの詳細

#### ProposalService

- **目的**: 修正案のライフサイクル全体を管理
- **公開インターフェース**:
  ```python
  class ProposalService:
      async def create_proposal(self, db: AsyncSession, *, proposal_data: RevisionCreate, proposer: User) -> Revision:
      async def submit_proposal(self, db: AsyncSession, *, revision_id: UUID, proposer: User) -> Revision:
      async def withdraw_proposal(self, db: AsyncSession, *, revision_id: UUID, proposer: User) -> Revision:
      async def update_proposal(self, db: AsyncSession, *, revision_id: UUID, update_data: RevisionUpdate, proposer: User) -> Revision:
      async def delete_proposal(self, db: AsyncSession, *, revision_id: UUID, proposer: User) -> None:
      async def get_user_proposals(self, db: AsyncSession, *, user_id: UUID, status: Optional[str] = None) -> List[Revision]:
      async def get_proposals_for_approval(self, db: AsyncSession, *, approver: User) -> List[Revision]:
      async def validate_proposal_data(self, db: AsyncSession, *, proposal_data: RevisionCreate) -> dict:
  ```
- **内部実装方針**: 
  - After-only方式による修正案データ管理
  - 5段階ステータス（draft→submitted→approved/rejected/deleted）管理
  - 承認グループベースの権限制御

#### ApprovalService

- **目的**: 承認ワークフローの統制管理
- **公開インターフェース**:
  ```python
  class ApprovalService:
      async def approve_proposal(self, db: AsyncSession, *, revision_id: UUID, approver: User, comment: Optional[str] = None) -> Revision:
      async def reject_proposal(self, db: AsyncSession, *, revision_id: UUID, approver: User, reason: str) -> Revision:
      async def get_approval_status(self, db: AsyncSession, *, revision_id: UUID) -> dict:
      async def can_approve(self, db: AsyncSession, *, revision: Revision, user: User) -> bool:
      async def escalate_approval(self, db: AsyncSession, *, revision_id: UUID) -> None:
  ```
- **内部実装方針**:
  - 承認グループベースの権限管理
  - 単一承認者による承認・却下
  - 承認履歴の完全な記録

#### DiffService

- **目的**: 修正前後の差分生成と視覚化
- **公開インターフェース**:
  ```python
  class DiffService:
      async def generate_field_diff(self, db: AsyncSession, *, revision: Revision) -> dict:
      async def preview_changes(self, db: AsyncSession, *, revision_id: UUID) -> dict:
      async def validate_changes(self, revision: Revision) -> dict:
      async def get_change_summary(self, revision: Revision) -> dict:
  ```
- **内部実装方針**:
  - フィールド単位での差分比較
  - After-only方式に対応した差分表示
  - 構造化データの階層差分表示

#### NotificationService

- **目的**: システム内通知の管理
- **公開インターフェース**:
  ```python
  class NotificationService:
      async def notify_proposal_submitted(self, db: AsyncSession, *, revision: Revision, approvers: List[User]) -> None:
      async def notify_proposal_approved(self, db: AsyncSession, *, revision: Revision, proposer: User) -> None:
      async def notify_proposal_rejected(self, db: AsyncSession, *, revision: Revision, proposer: User, reason: str) -> None:
      async def get_user_notifications(self, db: AsyncSession, *, user_id: UUID, unread_only: bool = False) -> List[SimpleNotification]:
      async def mark_as_read(self, db: AsyncSession, *, notification_id: UUID, user: User) -> None:
  ```
- **内部実装方針**:
  - シンプルな通知システム（Redis 3.0.504制約対応）
  - データベースベースの通知履歴管理

## 3. データフロー

### 3.1 データフロー図

```
修正案提出フロー:
ユーザー → UI → ProposalService → RevisionRepository → PostgreSQL
                      ↓
               NotificationService → 承認者通知
                      ↓
                 Redis (キャッシュ)

承認フロー:
承認者 → UI → ApprovalService → RevisionRepository → PostgreSQL
                   ↓
            NotificationService → 提出者通知
                   ↓
              ProposalService → ステータス更新
```

### 3.2 データ変換

- **入力データ形式**: 
  - 修正案: After-onlyフィールド + メタデータ（JSON/Pydantic）
  - 承認データ: ステータス + コメント（JSON/Pydantic）
- **処理過程**: 
  - Pydanticによるデータバリデーション
  - SQLAlchemyによるORM変換
  - 承認ワークフロー状態の更新
- **出力データ形式**: 
  - フロントエンド向けJSON（Pydanticシリアライゼーション）
  - 通知用構造化データ
  - 差分表示用比較データ

## 4. APIインターフェース

### 4.1 内部API

```python
# 修正案API（既存実装済み）
POST   /api/v1/proposals/                    # 修正案作成
GET    /api/v1/proposals/{proposal_id}       # 修正案取得
PUT    /api/v1/proposals/{proposal_id}       # 修正案更新
DELETE /api/v1/proposals/{proposal_id}       # 修正案削除
POST   /api/v1/proposals/{proposal_id}/submit   # 修正案提出
POST   /api/v1/proposals/{proposal_id}/withdraw # 修正案撤回
GET    /api/v1/proposals/my-proposals        # 自分の修正案一覧
GET    /api/v1/proposals/for-approval        # 承認待ち修正案一覧
GET    /api/v1/proposals/statistics          # 修正案統計

# 承認API（新規実装必要）
POST   /api/v1/approvals/{proposal_id}/approve    # 承認
POST   /api/v1/approvals/{proposal_id}/reject     # 却下
GET    /api/v1/approvals/{proposal_id}/status     # 承認状況取得

# 差分API（新規実装必要）
GET    /api/v1/diffs/{proposal_id}           # 差分取得
GET    /api/v1/diffs/{proposal_id}/preview   # プレビュー

# 通知API（既存実装済み）
GET    /api/v1/notifications                 # 通知一覧
POST   /api/v1/notifications/{id}/read       # 既読マーク
```

### 4.2 データモデル

```python
# 修正案データモデル（既存）
class Revision(Base):
    revision_id: Mapped[UUID]
    target_article_id: Mapped[str]
    target_article_pk: Mapped[str]
    proposer_id: Mapped[UUID]
    after_title: Mapped[Optional[str]]  # After-onlyフィールド
    after_info_category: Mapped[Optional[str]]
    # ... 他のafterフィールド
    reason: Mapped[str]
    status: Mapped[str]  # draft/submitted/approved/rejected/deleted
    approver_id: Mapped[Optional[UUID]]
    processed_at: Mapped[Optional[datetime]]

# 承認結果データモデル（新規）
class ApprovalResult:
    proposal_id: UUID
    approver: User
    status: str  # approved/rejected
    comment: Optional[str]
    processed_at: datetime

# 差分表示データモデル（新規）
class FieldDiff:
    field_name: str
    current_value: Optional[str]
    proposed_value: Optional[str]
    change_type: str  # added/modified/deleted
```

## 5. エラーハンドリング

### 5.1 エラー分類

- **ProposalNotFoundError**: 修正案が見つからない → 404 Not Found
- **ProposalPermissionError**: 修正案操作権限なし → 403 Forbidden
- **ProposalStatusError**: 無効な状態遷移 → 400 Bad Request
- **ProposalValidationError**: 修正案データ不正 → 400 Bad Request
- **ArticleNotFoundError**: 対象記事が見つからない → 404 Not Found
- **ApprovalPermissionError**: 承認権限なし → 403 Forbidden

### 5.2 エラー通知

- **ユーザー向け**: 分かりやすいメッセージでUI表示
- **開発者向け**: 詳細なスタックトレースとコンテキスト情報をログ出力
- **監視**: 重要エラーは即座にアラート通知

## 6. セキュリティ設計

### 6.1 認証・認可

- **JWT トークンベース認証**: 既存実装済み
- **RBAC（Role-Based Access Control）**: user/approver/admin
- **修正案レベルでの細粒度アクセス制御**:
  - 提案者：自分の修正案のみ操作可能
  - 承認者：担当グループの修正案のみ承認可能
  - 管理者：全修正案の操作・閲覧可能

### 6.2 データ保護

- **入力データのサニタイゼーション**: XSS対策
- **SQLインジェクション対策**: SQLAlchemy ORM使用
- **CSRF対策**: トークンベース防止
- **機密レベル分類**: 修正案内容に応じた暗号化保存

## 7. テスト戦略

### 7.1 単体テスト

- **カバレッジ目標**: 90%以上
- **テストフレームワーク**: pytest 8.3.4 + pytest-asyncio 0.26.0
- **モックとスタブ**: fakeredis 2.20.1, freezegun 1.4.0
- **重点テスト項目**:
  - ProposalServiceの状態遷移ロジック
  - ApprovalServiceの権限制御
  - バリデーション機能の境界値テスト

### 7.2 統合テスト

- **APIエンドポイントテスト**: httpx 0.28.1 + pytest
- **データベース統合テスト**: aiosqlite 0.21.0 + alembic
- **シナリオテスト**: 修正案提出→承認→完了の完全フロー

## 8. パフォーマンス最適化

### 8.1 想定される負荷

- **同時ユーザー数**: 100人
- **修正案検索応答時間**: 3秒以内
- **差分表示時間**: 5秒以内（大容量対応）
- **データベース接続プール**: 20接続

### 8.2 最適化方針

- **Redis 3.0.504制約対応**:
  - 基本的なkey-value操作によるキャッシュ
  - セッション情報のキャッシュ
  - 通知カウントのキャッシュ
- **PostgreSQL 17活用**:
  - パーティションテーブル（時系列データ）
  - 並列クエリ実行
  - 適切なインデックス設計
- **大容量コンテンツ対応**:
  - 差分計算の非同期処理
  - ページネーション実装

## 9. デプロイメント

### 9.1 デプロイ構成

- **ターゲット環境**: Windows Server 2019
- **プロセス管理**: Windows Service または IIS統合
- **CI/CD**: GitHub Actions（Windows runners）
- **環境分離**: development / staging / production

### 9.2 設定管理

- **環境変数による設定外部化**: pydantic_settings使用
- **機密情報管理**: Windows資格情報マネージャーまたは環境変数
- **設定値バリデーション**: Pydanticスキーマ
- **ログローテーション**: Windows Event Log統合

## 10. 実装上の注意事項

### 10.1 Article IDの手入力対応
- **現状**: 既にarticle_idは手入力で設定可能（自動生成なし）
- **利点**: 既存システムとの連携で既存IDを使用可能
- **注意点**: 重複チェックの実装が必要（API側で実装済み）

### 10.2 Windows Server 2019固有対応
- **パスセパレータ**: 適切なクロスプラットフォーム対応
- **サービス化**: FastAPIアプリケーションのWindows Service化
- **ファイルロック**: Windows特有のファイルロック動作への対応

### 10.3 Redis 3.0.504制約
- **使用可能機能**: 基本操作（SET/GET/DEL/HSET/HGET等）
- **使用不可機能**: Streams、Modules、UNLINK等
- **キャッシュ戦略**: シンプルなkey-value中心の設計

### 10.4 SQLAlchemy 2.0対応
- **型安全性**: Mapped/mapped_columnによる静的型チェック
- **継承構造**: Baseクラスでのタイムスタンプ共通化
- **関係性定義**: 前方参照文字列の適切な使用

### 10.5 After-only設計
- **差分表示**: 現在値は元記事から、修正後値は修正案から取得
- **バリデーション**: at least one changeの検証
- **プレビュー**: 元記事データとの合成表示