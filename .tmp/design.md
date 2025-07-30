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
│ 修正案サービス  │ 承認サービス │ 通知サービス  │ 差分表示サービス    │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                       データアクセス層                           │
├─────────────────────────────────────────────────────────────────┤
│   修正案Repository │ ユーザーRepository │ 承認Repository         │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                         データ層                                │
├─────────────────────────────────────────────────────────────────┤
│   修正案DB    │   ユーザーDB    │   承認DB    │   通知キュー        │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 技術スタック

**バックエンド**:
- 言語: Python 3.12+
- フレームワーク: FastAPI 0.115.8
- ORM: SQLAlchemy 2.0.40 + Alembic 1.14.1
- データベース: PostgreSQL 17 (asyncpg 0.30.0), Redis 3.0.504
- 認証: python-jose[cryptography] 3.4.0 + passlib 1.7.4 + bcrypt 3.2.2
- バックグラウンドタスク: APScheduler (定期処理)
- テスト: pytest 8.3.4 + pytest-asyncio 0.26.0 + fakeredis 2.20.1
- その他: 
  - pydantic 2.10.6 + pydantic_settings 2.8.1
  - uvicorn 0.34.0 (ASGI server)
  - ulid-py 1.1.0 (ID生成)
  - sqladmin 0.20.1 (管理画面)

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
| ProposalService | 修正案の作成・管理・検索 | ProposalRepository, NotificationService |
| ApprovalService | 承認ワークフローの管理 | ApprovalRepository, UserService, NotificationService |
| DiffService | 修正差分の生成・表示 | ProposalRepository |
| NotificationService | 通知・アラートの送信 | UserService, EmailService, WebSocketService |
| UserService | ユーザー認証・認可・権限管理 | UserRepository |

### 2.2 各コンポーネントの詳細

#### ProposalService

- **目的**: 修正案のライフサイクル管理
- **公開インターフェース**:
  ```python
  class ProposalService:
      async def create_proposal(self, proposal: CreateProposalDto) -> Proposal:
      async def get_proposal_by_id(self, proposal_id: str) -> Optional[Proposal]:
      async def update_proposal(self, proposal_id: str, updates: UpdateProposalDto) -> Proposal:
      async def search_proposals(self, criteria: SearchCriteria) -> PaginatedResult[Proposal]:
      async def delete_proposal(self, proposal_id: str) -> None:
      async def get_proposals_by_status(self, status: ProposalStatus) -> List[Proposal]:
  ```
- **内部実装方針**: 
  - SQLAlchemyによるORM活用とasync/await対応
  - Pydanticモデルによるデータバリデーション
  - SQLAlchemyの楽観的ロックによる同時編集制御

#### ApprovalService

- **目的**: 承認ワークフローの統制管理
- **公開インターフェース**:
  ```python
  class ApprovalService:
      async def assign_approvers(self, proposal_id: str, approvers: List[str]) -> None:
      async def submit_for_approval(self, proposal_id: str) -> ApprovalWorkflow:
      async def approve(self, workflow_id: str, approver_id: str, comment: Optional[str] = None) -> None:
      async def reject(self, workflow_id: str, approver_id: str, reason: str) -> None:
      async def get_approval_status(self, proposal_id: str) -> ApprovalStatus:
      async def escalate_approval(self, workflow_id: str) -> None:
  ```
- **内部実装方針**:
  - Enumベースのステートマシンパターンによる状態管理
  - 承認者の自動割り当てアルゴリズム
  - APSchedulerによる定期的なタイムアウト処理とエスカレーション

#### DiffService

- **目的**: 修正前後の差分生成と視覚化
- **公開インターフェース**:
  ```python
  class DiffService:
      async def generate_diff(self, original_content: str, modified_content: str) -> DiffResult:
      async def generate_structured_diff(self, original: KnowledgeStructure, modified: KnowledgeStructure) -> StructuredDiff:
      async def preview_changes(self, proposal_id: str) -> ChangePreview:
      async def validate_changes(self, diff: DiffResult) -> ValidationResult:
  ```
- **内部実装方針**:
  - Pythonの`difflib`ライブラリによる効率的な差分アルゴリズム
  - 大容量コンテンツの非同期分割処理
  - 構造化データの階層差分表示

## 3. データフロー

### 3.1 データフロー図

```
修正案提出フロー:
ユーザー → UI → ProposalService → ProposalRepository → DB
                      ↓
               NotificationService → 承認者

承認フロー:
承認者 → UI → ApprovalService → ApprovalRepository → DB
                   ↓
            NotificationService → 提出者
                   ↓
              ProposalService → 修正案ステータス更新
```

### 3.2 データ変換

- **入力データ形式**: 
  - 修正案: HTML/Markdown + メタデータ (JSON)
  - 承認データ: ステータス + コメント (JSON)
- **処理過程**: 
  - コンテンツの正規化・サニタイゼーション
  - 差分計算とハッシュ生成
  - 承認ワークフロー状態の更新
- **出力データ形式**: 
  - 差分表示用JSON
  - 通知用構造化データ
  - 承認済み修正案データ

## 4. APIインターフェース

### 4.1 内部API

```python
# FastAPI エンドポイント定義
# 修正案API
POST   /api/v1/proposals
GET    /api/v1/proposals/{proposal_id}
PUT    /api/v1/proposals/{proposal_id}
DELETE /api/v1/proposals/{proposal_id}
GET    /api/v1/proposals?status=pending&page=1&limit=20

# 承認API
POST   /api/v1/proposals/{proposal_id}/approve
POST   /api/v1/proposals/{proposal_id}/reject
GET    /api/v1/proposals/{proposal_id}/approval-status
POST   /api/v1/proposals/{proposal_id}/assign-approvers

# 差分API
GET    /api/v1/proposals/{proposal_id}/diff
GET    /api/v1/proposals/{proposal_id}/preview

# 通知API
GET    /api/v1/notifications
POST   /api/v1/notifications/mark-read
```

### 4.2 データモデル

```python
# 修正案データモデル
class Proposal:
    id: str
    title: str
    original_content: str
    modified_content: str
    reason: str
    category: ProposalCategory
    status: ProposalStatus
    submitter_id: str
    created_at: datetime
    updated_at: datetime

# 承認ワークフローデータモデル
class ApprovalWorkflow:
    id: str
    proposal_id: str
    approver_id: str
    status: ApprovalStatus
    comment: Optional[str]
    approved_at: Optional[datetime]
```

## 5. エラーハンドリング

### 5.1 エラー分類

- **ValidationError**: 入力データの形式エラー → 400 Bad Request
- **AuthorizationError**: 権限不足エラー → 403 Forbidden
- **NotFoundError**: リソース未存在エラー → 404 Not Found
- **ConflictError**: 競合状態エラー → 409 Conflict
- **SystemError**: システム内部エラー → 500 Internal Server Error

### 5.2 エラー通知

- ユーザー向け: 分かりやすいメッセージでUI表示
- 開発者向け: 詳細なスタックトレースとコンテキスト情報をログ出力
- 監視: 重要エラーは即座にSlack/メール通知

## 6. セキュリティ設計

### 6.1 認証・認可

- JWT トークンベースの認証
- RBAC (Role-Based Access Control) による権限管理
- 修正案レベルでの細粒度アクセス制御
- セッション管理とトークンの自動更新

### 6.2 データ保護

- 機密レベル分類に基づく暗号化保存
- 修正案内容のサニタイゼーション（XSS対策）
- SQL インジェクション対策（Prisma ORM使用）
- CSRF トークンによる不正リクエスト防止

## 7. テスト戦略

### 7.1 単体テスト

**バックエンド**:
- カバレッジ目標: 90%以上
- テストフレームワーク: pytest 8.3.4 + pytest-asyncio 0.26.0
- モックとスタブ: fakeredis 2.20.1, freezegun 1.4.0
- テストデータファクトリーパターンの採用

**フロントエンド**:
- テストフレームワーク: Jest + React Testing Library
- モックとスタブを活用した独立テスト

### 7.2 統合テスト

**バックエンド**:
- API エンドポイントのテスト (httpx 0.28.1 + pytest)
- データベース統合テスト (aiosqlite 0.21.0 + alembic)
- 外部システム連携テスト (モックサーバー使用)

**フロントエンド**:
- E2Eテスト (Playwright)

## 8. パフォーマンス最適化

### 8.1 想定される負荷

- 同時ユーザー数: 100人
- 修正案検索応答時間: 3秒以内
- 大容量差分表示時間: 5秒以内
- データベース接続プール: 20接続

### 8.2 最適化方針

- **Redis 3.0.504制約対応**:
  - Lua スクリプトの活用（Redis 3.0で安定化）
  - SET/GET操作中心のシンプルなキャッシュ戦略
  - Redis Streams は使用不可（Redis 5.0以降の機能）
  - HyperLogLog、Sorted Sets の基本機能のみ使用
- PostgreSQL 17 の新機能活用:
  - パーティションテーブルによる大容量データ対応
  - 並列クエリ実行による高速化
  - インデックスの最適化（BRIN、GINインデックス活用）
- 大容量コンテンツの遅延読み込み
- Windows Server環境での静的リソース最適化

## 9. デプロイメント

### 9.1 デプロイ構成

- **ターゲット環境**: Windows Server 2019
- **プロセス管理**: Windows Service または IIS 統合
- **CI/CD**: GitHub Actions (Windows runners)
- **環境分離**: development / staging / production
- **依存サービス**:
  - PostgreSQL 17 (Windows Service)
  - Redis 3.0.504 (Windows Service)

### 9.2 設定管理

- **Windows環境での設定管理**:
  - 環境変数による設定の外部化
  - Windows レジストリまたは設定ファイルでの機密情報管理
  - pydantic_settings による設定値バリデーション
  - 設定ファイルの動的リロード対応
- **サービス管理**:
  - Windows Service Manager による自動起動設定
  - ログローテーション（Windows Event Log統合）

## 10. 実装上の注意事項

### 10.1 Windows Server 2019 固有の考慮事項

- **Windows Service化**: FastAPIアプリケーションのWindows Service化
- **IIS統合**: reverse proxy としてのIIS設定（オプション）
- **Windows認証**: Active Directory統合の可能性を考慮
- **ファイルパス**: Windows パス区切り文字の適切な処理
- **プロセス管理**: APScheduler による定期処理（承認タイムアウト等）

### 10.2 Redis 3.0.504 制約対応

- **使用可能機能**:
  - 基本的なkey-value操作 (SET, GET, DEL等)
  - Hash操作 (HSET, HGET等)
  - List操作 (LPUSH, RPOP等)
  - Set操作 (SADD, SMEMBERS等)
  - Sorted Set操作 (ZADD, ZRANGE等)
  - Lua スクリプト (EVAL, EVALSHA)
- **使用不可機能**:
  - Redis Streams (Redis 5.0以降)
  - Modules (Redis 4.0以降)
  - Memory usage コマンド (Redis 4.0以降)
  - UNLINK コマンド (Redis 4.0以降)

### 10.3 一般的な実装注意事項

- **データ整合性**: SQLAlchemyの楽観的ロックによる同時編集制御
- **スケーラビリティ**: Windows環境でのマルチプロセス対応
- **監査要件**: Windows Event Log への重要操作記録
- **段階的リリース**: 設定ファイルベースのフィーチャーフラグ
- **バックアップ戦略**: PostgreSQL + Redis の Windows 環境での自動バックアップ