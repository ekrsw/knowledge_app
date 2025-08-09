# 未テストAPIエンドポイント分析結果

## 概要

API設計書と実際のテストファイルを比較分析し、テストカバレッジのギャップを特定しました。
現在のテストカバレッジは**48%**で、目標の**80%**まで**32%不足**しています。

## テスト済みエンドポイント ✅

### 1. 認証管理 (/api/v1/auth) 
**ファイル**: `tests/integration/test_auth_api.py` ✅ **包括的テスト完了**
- ログイン (OAuth2, JSON) - 成功/失敗ケース
- ユーザー登録 - バリデーション、重複チェック
- 現在のユーザー情報 - 認証確認
- トークンテスト - 有効性確認
- 統合テスト - フルワークフロー

### 2. ユーザー管理 (/api/v1/users)
**ファイル**: `tests/integration/test_users_api.py` ✅ **基本CRUD + 権限テスト完了**
- 基本CRUD操作（一覧、作成、詳細、更新、削除）
- 権限マトリクステスト（管理者、承認者、一般ユーザー）
- ページネーション
- バリデーション（重複、不正データ）

### 3. 承認グループ管理 (/api/v1/approval-groups)
**ファイル**: `tests/integration/test_approval_groups_api.py` ✅ **基本CRUD + エッジケーステスト完了**
- 基本CRUD操作
- ページネーション
- エッジケース（特殊文字、Unicode、空白処理）

### 4. 情報カテゴリ管理 (/api/v1/info-categories)
**ファイル**: `tests/integration/test_info_categories_api.py` ✅ **CRUD + アクティブフィルタリングテスト完了**
- 基本CRUD操作
- アクティブカテゴリ一覧（`/active` エンドポイント）
- 表示順序テスト
- エッジケース

## 未テストエンドポイント ❌

### 1. 修正案管理 (/api/v1/revisions) - **高優先度**
**実装ファイル**: `app/api/v1/endpoints/revisions.py`
**テストファイル**: 未作成 ❌
**エンドポイント数**: 6個

| エンドポイント | HTTP | 説明 | 権限要件 | 優先度 |
|---|---|---|---|---|
| `/api/v1/revisions/` | GET | 修正案一覧取得 | 認証済み（権限別フィルタ） | 🔴 高 |
| `/api/v1/revisions/{id}` | GET | 修正案詳細取得 | 関係者のみ | 🔴 高 |
| `/api/v1/revisions/` | POST | 修正案作成 | 認証済み | 🔴 高 |
| `/api/v1/revisions/{id}` | PUT | 修正案更新 | 提出者（draft時のみ） | 🟡 中 |
| `/api/v1/revisions/by-proposer/{id}` | GET | 提案者別一覧 | 管理者/本人 | 🟡 中 |
| `/api/v1/revisions/by-status/{status}` | GET | ステータス別一覧 | 認証済み | 🟡 中 |
| `/api/v1/revisions/{id}/status` | PATCH | ステータス更新 | 承認者/管理者 | 🔴 高 |

### 2. 修正案提案管理 (/api/v1/proposals) - **高優先度**
**実装ファイル**: `app/api/v1/endpoints/proposals.py`
**テストファイル**: 未作成 ❌
**エンドポイント数**: 8個

| エンドポイント | HTTP | 説明 | 権限要件 | 優先度 |
|---|---|---|---|---|
| `/api/v1/proposals/` | POST | 修正案提案作成 | 認証済み | 🔴 高 |
| `/api/v1/proposals/{id}` | PUT | 修正案提案更新 | 提案者（draft時のみ） | 🔴 高 |
| `/api/v1/proposals/{id}/submit` | POST | 修正案提出 | 提案者 | 🔴 高 |
| `/api/v1/proposals/{id}/withdraw` | POST | 修正案撤回 | 提案者 | 🟡 中 |
| `/api/v1/proposals/{id}` | DELETE | 修正案削除 | 提案者（draft時のみ） | 🟡 中 |
| `/api/v1/proposals/my-proposals` | GET | 自分の提案一覧 | 認証済み | 🔴 高 |
| `/api/v1/proposals/for-approval` | GET | 承認待ち一覧 | 承認者 | 🔴 高 |
| `/api/v1/proposals/statistics` | GET | 提案統計 | 認証済み | 🟢 低 |
| `/api/v1/proposals/{id}` | GET | 提案詳細取得 | 関係者のみ | 🔴 高 |

### 3. 承認管理 (/api/v1/approvals) - **最高優先度**
**実装ファイル**: `app/api/v1/endpoints/approvals.py`
**テストファイル**: 未作成 ❌
**エンドポイント数**: 13個

| エンドポイント | HTTP | 説明 | 権限要件 | 優先度 |
|---|---|---|---|---|
| `/api/v1/approvals/{id}/decide` | POST | 承認・却下処理 | 指定承認者 | 🚨 最高 |
| `/api/v1/approvals/{id}/can-approve` | GET | 承認権限チェック | 認証済み | 🔴 高 |
| `/api/v1/approvals/queue` | GET | 承認待ち一覧 | 承認者 | 🚨 最高 |
| `/api/v1/approvals/metrics` | GET | 承認統計・メトリクス | 承認者/管理者 | 🟡 中 |
| `/api/v1/approvals/workload` | GET | ワークロード管理 | 承認者 | 🟡 中 |
| `/api/v1/approvals/workload/{id}` | GET | 特定承認者ワークロード | 管理者 | 🟢 低 |
| `/api/v1/approvals/bulk` | POST | 一括承認・却下 | 承認者 | 🟡 中 |
| `/api/v1/approvals/history` | GET | 承認履歴 | 認証済み | 🟡 中 |
| `/api/v1/approvals/statistics/dashboard` | GET | ダッシュボード統計 | 承認者 | 🟢 低 |
| `/api/v1/approvals/team-overview` | GET | チーム概要 | 管理者 | 🟢 低 |
| `/api/v1/approvals/{id}/quick-actions/{action}` | POST | クイックアクション | 承認者 | 🟡 中 |
| `/api/v1/approvals/workflow/recommendations` | GET | ワークフロー推奨事項 | 承認者 | 🟢 低 |
| `/api/v1/approvals/workflow/checklist/{id}` | GET | 承認チェックリスト | 承認者 | 🟢 低 |

### 4. 差分表示 (/api/v1/diffs) - **高優先度**
**実装ファイル**: `app/api/v1/endpoints/diffs.py`
**テストファイル**: 未作成 ❌
**エンドポイント数**: 8個

| エンドポイント | HTTP | 説明 | 権限要件 | 優先度 |
|---|---|---|---|---|
| `/api/v1/diffs/{id}` | GET | 差分データ取得 | 関係者のみ | 🔴 高 |
| `/api/v1/diffs/article/{id}/snapshot` | GET | 記事スナップショット | 認証済み | 🔴 高 |
| `/api/v1/diffs/article/{id}/history` | GET | 記事履歴 | 認証済み | 🟡 中 |
| `/api/v1/diffs/compare` | POST | 修正案比較 | 承認者/管理者 | 🟡 中 |
| `/api/v1/diffs/{id}/formatted` | GET | フォーマット済み差分 | 関係者のみ | 🟡 中 |
| `/api/v1/diffs/{id}/summary` | GET | 変更サマリー | 関係者のみ | 🔴 高 |
| `/api/v1/diffs/bulk-summaries` | POST | 一括サマリー | 認証済み | 🟡 中 |
| `/api/v1/diffs/statistics/changes` | GET | 変更統計 | 認証済み | 🟢 低 |

### 5. 記事管理 (/api/v1/articles) - **中優先度**
**実装ファイル**: `app/api/v1/endpoints/articles.py`
**テストファイル**: 未作成 ❌
**エンドポイント数**: 6個

| エンドポイント | HTTP | 説明 | 権限要件 | 優先度 |
|---|---|---|---|---|
| `/api/v1/articles/` | GET | 記事一覧取得 | 認証済み | 🟡 中 |
| `/api/v1/articles/{id}` | GET | 記事詳細取得 | 認証済み | 🟡 中 |
| `/api/v1/articles/` | POST | 記事作成 | 管理者 | 🟡 中 |
| `/api/v1/articles/by-category/{id}` | GET | カテゴリ別記事一覧 | 認証済み | 🟢 低 |
| `/api/v1/articles/by-group/{id}` | GET | 承認グループ別記事一覧 | 認証済み | 🟢 低 |
| `/api/v1/articles/{id}` | PUT | 記事更新 | 管理者 | 🟡 中 |

### 6. 通知管理 (/api/v1/notifications) - **中優先度**
**実装ファイル**: `app/api/v1/endpoints/notifications.py`
**テストファイル**: 未作成 ❌
**エンドポイント数**: 8個

| エンドポイント | HTTP | 説明 | 権限要件 | 優先度 |
|---|---|---|---|---|
| `/api/v1/notifications/my-notifications` | GET | 自分の通知一覧 | 認証済み | 🟡 中 |
| `/api/v1/notifications/statistics` | GET | 通知統計 | 認証済み | 🟢 低 |
| `/api/v1/notifications/digest` | GET | 通知ダイジェスト | 認証済み | 🟢 低 |
| `/api/v1/notifications/{id}/read` | PUT | 通知既読化 | 受信者/管理者 | 🟡 中 |
| `/api/v1/notifications/read-all` | PUT | 全通知既読化 | 認証済み | 🟡 中 |
| `/api/v1/notifications/batch` | POST | 一括通知作成 | 管理者 | 🟢 低 |
| `/api/v1/notifications/{id}` | GET | レガシーエンドポイント | 管理者 | 🟢 低 |
| `/api/v1/notifications/` | POST | レガシーエンドポイント | 管理者 | 🟢 低 |

### 7. 分析・統計 (/api/v1/analytics) - **低優先度**
**実装ファイル**: `app/api/v1/endpoints/analytics.py`
**テストファイル**: 未作成 ❌
**エンドポイント数**: 6個

| エンドポイント | HTTP | 説明 | 権限要件 | 優先度 |
|---|---|---|---|---|
| `/api/v1/analytics/overview` | GET | 分析概要 | 認証済み | 🟢 低 |
| `/api/v1/analytics/trends` | GET | トレンド分析 | 認証済み | 🟢 低 |
| `/api/v1/analytics/performance` | GET | パフォーマンスメトリクス | 承認者 | 🟢 低 |
| `/api/v1/analytics/reports/summary` | GET | サマリーレポート | 認証済み | 🟢 低 |
| `/api/v1/analytics/export/data` | GET | データエクスポート | 認証済み | 🟢 低 |
| `/api/v1/analytics/dashboards/executive` | GET | エグゼクティブダッシュボード | 管理者 | 🟢 低 |

### 8. システム情報 (/api/v1/system) - **低優先度**
**実装ファイル**: `app/api/v1/endpoints/system.py`
**テストファイル**: 未作成 ❌
**エンドポイント数**: 6個

| エンドポイント | HTTP | 説明 | 権限要件 | 優先度 |
|---|---|---|---|---|
| `/api/v1/system/health` | GET | ヘルスチェック | 公開 | 🟢 低 |
| `/api/v1/system/version` | GET | バージョン情報 | 公開 | 🟢 低 |
| `/api/v1/system/stats` | GET | システム統計 | 管理者 | 🟢 低 |
| `/api/v1/system/config` | GET | システム設定 | 管理者 | 🟢 低 |
| `/api/v1/system/maintenance` | POST | メンテナンスタスク | 管理者 | 🟢 低 |
| `/api/v1/system/api-documentation` | GET | API文書 | 公開 | 🟢 低 |

## 優先度別実装推奨順序

### Phase A: コアビジネスロジック（最高優先度）🚨
1. **承認管理**: `/decide`, `/queue` エンドポイント
2. **修正案管理**: 基本CRUD、ステータス管理
3. **修正案提案管理**: 提案作成、提出、承認待ち一覧

### Phase B: 重要機能（高優先度）🔴  
4. **差分表示**: 差分取得、スナップショット、サマリー
5. **修正案管理**: 提案者別、ステータス別一覧
6. **承認管理**: 権限チェック、履歴

### Phase C: 補助機能（中優先度）🟡
7. **記事管理**: 基本CRUD操作
8. **通知管理**: 通知一覧、既読化
9. **承認管理**: ワークロード、メトリクス

### Phase D: 分析・システム（低優先度）🟢
10. **分析・統計**: 各種レポート機能
11. **システム情報**: ヘルスチェック、統計

## 推定作業時間

| 優先度 | エンドポイント数 | 推定時間 | 説明 |
|---|---|---|---|
| 🚨 最高 | 9個 | 4-5時間 | コアビジネスロジック |
| 🔴 高 | 15個 | 6-7時間 | 重要機能、複雑な権限制御 |
| 🟡 中 | 18個 | 4-5時間 | 標準的なCRUD操作 |
| 🟢 低 | 13個 | 2-3時間 | 単純な取得操作 |
| **合計** | **55個** | **16-20時間** | 全未テストエンドポイント |

## テストカバレッジ向上への影響

現在**48%**のカバレッジを**80%**に向上させるには、以下の実装が必要：

1. **Phase A (最高優先度)**: 約15%向上 → **63%**
2. **Phase B (高優先度)**: 約12%向上 → **75%** 
3. **Phase C (中優先度)**: 約7%向上 → **82%** ✅ **目標達成**

**結論**: Phase A-C（42個のエンドポイント）をテストすることで目標の80%カバレッジを達成できる見込みです。

## 権限制御テスト強化が必要な領域

現在の権限テストは基本的なものに留まっているため、以下の強化が必要：

1. **承認グループベースの権限制御**
2. **修正案の関係者権限（提出者・承認者・管理者）**
3. **ステータスベースの操作制限**
4. **データレベルの権限制御（own vs. others）**
5. **API境界での権限チェック**

## エラーハンドリングテスト強化が必要な領域

1. **カスタム例外**: ProposalError, ApprovalError系の例外処理
2. **バリデーションエラー**: 複雑なビジネスルール検証
3. **ステータス競合エラー**: 同時実行時の状態競合
4. **データ整合性エラー**: 外部キー制約違反など
5. **システムエラー**: データベース接続エラー、サービス層エラー

## 次のアクション

Task 3.2 完了。次は Task 3.3（権限制御テスト強化）と Task 3.4（エラーハンドリングテスト強化）の計画を立て、まずは**Phase A**の最高優先度エンドポイントからテストを実装する。