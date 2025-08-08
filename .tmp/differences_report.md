# API設計書と実装の相違点調査レポート

## 調査概要

API設計書（`.tmp/api_design.md`）と実際のバックエンド実装の間に存在する相違点を徹底的に調査しました。
以下、カテゴリ別に相違点をまとめます。

## 1. エンドポイント構造の相違

### 設計書の想定構造
```
/api/v1/revisions/*     # 修正案管理
/api/v1/approvals/*     # 承認管理
/api/v1/diffs/*         # 差分表示
```

### 実際の実装構造
```
/api/v1/revisions/*     # 基本的な修正案CRUD
/api/v1/proposals/*     # 修正案のビジネスロジック（追加）
/api/v1/approvals/*     # 承認管理
/api/v1/diffs/*         # 差分表示
/api/v1/analytics/*     # 分析機能（追加）
```

**相違点**: 実装では`proposals`と`analytics`の2つの追加エンドポイントグループが存在。

## 2. 修正案管理エンドポイントの相違

### 設計書で定義されているが実装されていないエンドポイント

1. **修正案提出** (`POST /api/v1/revisions/{revision_id}/submit`)
   - 設計: revisionsエンドポイント内
   - 実装: proposalsエンドポイントに移動

2. **修正案撤回** (`POST /api/v1/revisions/{revision_id}/withdraw`)
   - 設計: revisionsエンドポイント内
   - 実装: proposalsエンドポイントに移動

### 実装で追加されているエンドポイント

1. **`GET /api/v1/revisions/by-proposer/{proposer_id}`**: 提案者別修正案取得
2. **`GET /api/v1/revisions/by-status/{status}`**: ステータス別修正案取得
3. **`PATCH /api/v1/revisions/{revision_id}/status`**: ステータス直接更新

## 3. 承認管理エンドポイントの拡張

### 設計書にない追加実装

1. **ワークロード管理**:
   - `GET /api/v1/approvals/workload`
   - `GET /api/v1/approvals/workload/{approver_id}`

2. **ダッシュボード機能**:
   - `GET /api/v1/approvals/statistics/dashboard`
   - `GET /api/v1/approvals/team-overview`

3. **ワークフロー最適化**:
   - `GET /api/v1/approvals/workflow/recommendations`
   - `GET /api/v1/approvals/workflow/checklist/{revision_id}`

4. **クイックアクション**:
   - `POST /api/v1/approvals/{revision_id}/quick-actions/{action}`

## 4. 差分表示エンドポイントの拡張

### 設計書にない追加機能

1. **記事スナップショット**: `GET /api/v1/diffs/article/{article_id}/snapshot`
2. **記事履歴**: `GET /api/v1/diffs/article/{article_id}/history`
3. **修正案比較**: `POST /api/v1/diffs/compare`
4. **フォーマット済み差分**: `GET /api/v1/diffs/{revision_id}/formatted`
5. **一括サマリー**: `POST /api/v1/diffs/bulk-summaries`
6. **統計情報**: `GET /api/v1/diffs/statistics/changes`

## 5. スキーマ定義の相違

### Revision関連スキーマ

**設計書のフィールド**:
```json
{
  "after_publish_start": "2024-01-01",
  "after_publish_end": "2024-12-31"
}
```

**実装のフィールド**:
- `RevisionUpdate`スキーマで`after_publish_start`と`after_publish_end`が`datetime`型に変更
- `RevisionBase`では`date`型を維持

### 追加されたスキーマ

1. **ApprovalAction** (Enum): approve, reject, request_changes, defer
2. **ApprovalWorkload**: 承認者のワークロード情報
3. **ApprovalMetrics**: 承認プロセスのメトリクス
4. **BulkApprovalRequest**: 一括承認リクエスト
5. **FieldDiff**: フィールド単位の差分情報
6. **ArticleSnapshot**: 記事のスナップショット

## 6. データベースモデルの相違

### User モデル

**追加フィールド**:
- `sweet_name`: Optional[str] - 追加の識別子
- `ctstage_name`: Optional[str] - 追加の識別子

### Article モデル

**設計書で言及されていない構造**:
- `article_number`: 記事番号フィールド
- `article_url`: 記事URLフィールド
- 実装は完全に独立したテーブルとして設計

### Revision モデル

**データ型の相違**:
- `after_publish_start`, `after_publish_end`: Date型で実装（設計書通り）
- すべてのafter_*フィールドがOptional（設計書通り）

## 7. レスポンス形式の相違

### 設計書の共通レスポンス形式
```json
{
  "data": { /* リソースデータ */ },
  "message": "操作が完了しました",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 実装のレスポンス形式
- 多くのエンドポイントで直接リソースデータを返す
- 設計書の共通ラッパー形式は実装されていない

## 8. 権限制御の実装差異

### 設計書の権限関数
```python
get_current_active_user()      # 認証済みアクティブユーザー
get_current_approver_user()    # 承認者権限チェック
get_current_admin_user()       # 管理者権限チェック
```

### 実装の権限制御
- 基本的な依存関数は実装済み
- エンドポイント内でロール別の細かな権限制御を実装
- 承認グループベースの権限制御が追加

## 9. 設計書で定義されているが未実装の機能

### レート制限
- 設計書: 詳細なレート制限仕様
- 実装: 確認できず

### キャッシュ戦略
- 設計書: Redis使用のキャッシュ戦略
- 実装: 明示的なキャッシュ実装は確認できず

### 承認グループ管理
- 設計書: `/api/v1/approval-groups/*`
- 実装: エンドポイントファイルは存在するが詳細未確認

## 10. 実装で大幅に拡張された機能

### 1. プロポーザル管理
- 実装では修正案提案のライフサイクル管理を独立したサービスとして実装
- バリデーション、状態遷移、通知の統合管理

### 2. 承認ワークフロー
- ワークロード分析
- チーム全体の承認状況監視
- ワークフロー最適化の提案機能

### 3. 差分分析
- 高度な差分比較機能
- 記事の変更履歴追跡
- 統計分析機能

## 11. アーキテクチャの相違

### 設計書の想定
- シンプルなRESTful API
- 基本的なCRUD操作中心

### 実装の構造
- レイヤードアーキテクチャ
- サービス層での複雑なビジネスロジック
- リポジトリパターンによるデータアクセス
- 包括的な例外処理システム

## 結論

実装は設計書の基本要件を満たしつつ、以下の方向で大幅に拡張されています：

1. **機能の分離**: 修正案の基本CRUD（revisions）とビジネスロジック（proposals）の分離
2. **運用機能**: 承認者のワークロード管理、統計分析、ダッシュボード機能
3. **ユーザビリティ**: 一括操作、クイックアクション、フォーマット済み表示
4. **分析機能**: 差分の詳細分析、変更統計、パフォーマンスメトリクス

この実装は設計書を基盤としつつ、実用的なエンタープライズシステムとして必要な機能を網羅的に実装していることが確認できます。