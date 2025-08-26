# revisions と proposals の役割の違い

## 概要
このシステムでは、修正案管理を「データ層（revisions）」と「ビジネスロジック層（proposals）」に分離しています。

## **revisions（修正案データ層）**

### 責任範囲
修正案の**データそのもの**を扱うCRUD操作に特化

### 主な役割
- **基本的なデータ操作**: 修正案の作成・読取・更新・削除
- **データ保存**: 変更内容（after_*フィールド）の永続化
- **単純な取得**: フィルタリング、ソート、ページネーション
- **直接的なDB操作**: revisionsテーブルへの直接アクセス

### APIエンドポイント
```python
# シンプルなCRUD操作
GET    /api/v1/revisions/          # 一覧取得
POST   /api/v1/revisions/          # 新規作成
GET    /api/v1/revisions/{id}      # 詳細取得
PUT    /api/v1/revisions/{id}      # 更新（下書き編集）
DELETE /api/v1/revisions/{id}      # 削除
GET    /api/v1/revisions/by-article/{id}  # 特定記事の修正案一覧
```

### 使用場面
- 修正案の**作成・編集フォーム**でのデータ保存
- 修正案の**一覧表示**（単純なリスト）
- 修正案の**詳細表示**（データの表示）
- **下書きの削除**

## **proposals（提案ビジネスロジック層）**

### 責任範囲
修正案に対する**ビジネスアクション**とワークフロー管理

### 主な役割
- **状態遷移管理**: draft → submitted → approved/rejected のワークフロー
- **ビジネスルール適用**: 提出前バリデーション、権限チェック
- **ワークフロー制御**: 提出、撤回などのビジネスアクション
- **複雑なクエリ**: 「自分の提案」「承認待ち」など業務的な取得
- **副作用の処理**: 通知送信、承認キューへの追加など

### APIエンドポイント
```python
# ビジネスアクション
POST /api/v1/proposals/{id}/submit      # 提出（draft→submitted）
POST /api/v1/proposals/{id}/withdraw    # 撤回（submitted→draft）
GET  /api/v1/proposals/my-proposals     # 自分の提案一覧（ビジネスフィルター付き）
GET  /api/v1/proposals/for-approval     # 承認待ち一覧（承認者用）
GET  /api/v1/proposals/{id}/statistics  # 統計情報
```

### 使用場面
- **提出ボタン**のクリック処理
- **撤回ボタン**のクリック処理
- **マイページ**での自分の提案管理
- **ダッシュボード**での統計表示
- **承認者向け**の承認待ちキュー

## **具体的な使用例**

### 1. 修正案を作成する場合
```typescript
// ✅ revisions: 単純にデータを作成
const response = await api.post('/api/v1/revisions/', {
  target_article_id: 'article-001',
  approver_id: 'user-123',
  after_title: '新しいタイトル',
  reason: '誤字修正',
  status: 'draft'  // 下書きとして作成
});
```

### 2. 修正案を提出する場合
```typescript
// ✅ proposals: ビジネスロジックを実行
const response = await api.post('/api/v1/proposals/123/submit');
// 内部で実行される処理:
// → 必須フィールドのバリデーション
// → ステータスをsubmittedに変更
// → 承認者への通知を送信
// → 承認キューに追加
// → 提出履歴の記録
```

### 3. 修正案を編集する場合
```typescript
// ✅ revisions: 下書きの内容を更新
const response = await api.put('/api/v1/revisions/123', {
  after_title: '更新されたタイトル',
  after_content: '更新された内容'
});
```

### 4. 一覧を取得する場合の違い
```typescript
// revisions: 単純な一覧取得（機械的）
GET /api/v1/revisions/?status=submitted&limit=10
// → submittedステータスの修正案を10件取得

// proposals: ビジネスロジックを含む取得
GET /api/v1/proposals/my-proposals
// → ログインユーザーの修正案のみ
// → 関連データ（承認者名など）を含む
// → ビジネス的な優先度順で返却
```

## **アーキテクチャ上の位置づけ**

### レイヤー構造
```
┌─────────────────────────────────┐
│   Frontend (UI Layer)           │
│   - Forms, Lists, Buttons       │
├─────────────────────────────────┤
│   API Routes                    │
├─────────────────────────────────┤
│   proposals (Business Layer)    │ ← ビジネスロジック層
│   - ProposalService             │   ワークフロー、ルール
├─────────────────────────────────┤
│   revisions (Data Layer)        │ ← データアクセス層
│   - RevisionRepository          │   CRUD操作
├─────────────────────────────────┤
│   Database (PostgreSQL)         │
│   - revisions table             │
└─────────────────────────────────┘
```

### サービス層の実装例
```python
# ProposalService（ビジネスロジック）
class ProposalService:
    def submit_proposal(self, revision_id: str, user_id: str):
        # 1. revisionを取得（データ層）
        revision = revision_repository.get(revision_id)
        
        # 2. ビジネスルールチェック
        if not revision.after_title or not revision.reason:
            raise ValidationError("必須項目が入力されていません")
        
        if revision.proposer_id != user_id:
            raise PermissionError("他者の提案は提出できません")
        
        # 3. 状態遷移
        revision.status = "submitted"
        revision_repository.update(revision)
        
        # 4. 副作用の処理
        notification_service.notify_approver(revision.approver_id)
        audit_log.record("proposal_submitted", revision_id)
        
        return revision
```

## **フロントエンド実装での使い分けガイドライン**

| 画面/機能 | 使用するAPI | 理由 |
|-----------|------------|------|
| **修正案作成フォーム** | | |
| - 保存ボタン | `POST/PUT /revisions/` | 単純なデータ保存 |
| - 提出ボタン | `POST /proposals/{id}/submit` | ビジネスアクション |
| **修正案一覧画面** | | |
| - 全体一覧 | `GET /revisions/` | 単純なデータ取得 |
| - マイページ | `GET /proposals/my-proposals` | ユーザー固有のビュー |
| **修正案詳細画面** | | |
| - 詳細表示 | `GET /revisions/{id}` | データの取得 |
| - 撤回ボタン | `POST /proposals/{id}/withdraw` | ビジネスアクション |
| - 削除ボタン | `DELETE /revisions/{id}` | データの削除 |
| **ダッシュボード** | | |
| - 統計情報 | `GET /proposals/statistics` | 集計ロジック |
| - 承認待ち | `GET /proposals/for-approval` | 承認者向けビュー |

## **設計の利点**

### 1. 責任の分離
- **revisions**: データの永続化に専念
- **proposals**: ビジネスルールに専念

### 2. 再利用性
- revisions APIは汎用的で、様々な画面から利用可能
- proposals APIは特定の業務フローに特化

### 3. 保守性
- ビジネスルールが変更されても、データ層は影響なし
- 新しいワークフローの追加が容易

### 4. テスタビリティ
- データ操作とビジネスロジックを独立してテスト可能
- モックの作成が容易

## **まとめ**

### revisions（データ層）
- **責任**: 修正案データのCRUD操作
- **特徴**: シンプル、汎用的、状態を持たない
- **使用**: フォームの保存、一覧表示、詳細表示

### proposals（ビジネス層）
- **責任**: 修正案の提案・承認ワークフロー
- **特徴**: 複雑、業務特化、状態遷移を管理
- **使用**: 提出、撤回、承認フロー、統計

この分離により、シンプルなデータ操作と複雑なビジネスロジックを適切に管理し、保守性の高いシステムを実現しています。

## **実装時の判断基準**

新しい機能を実装する際の判断基準：

1. **単純なデータ操作か？** → revisions API
2. **状態遷移を伴うか？** → proposals API
3. **ビジネスルールがあるか？** → proposals API
4. **通知などの副作用があるか？** → proposals API
5. **特定ユーザー向けのフィルタリングか？** → proposals API
6. **単純な条件での取得か？** → revisions API