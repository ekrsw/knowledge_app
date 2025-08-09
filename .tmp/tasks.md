# タスクリスト - APIエンドポイントテスト実装

## 概要

- 総タスク数: 28
- 推定作業時間: 4-5日
- 優先度: 高

## タスク一覧

### Phase 1: 準備・調査

#### Task 1.1: テスト環境セットアップ

- [x] テスト用フィクスチャの拡充（ユーザー、記事、修正案のサンプルデータ）
- [x] テスト用データベースの初期化スクリプト作成
- [x] 認証トークン生成ヘルパー関数の実装
- [x] テストユーティリティ関数の作成
- **完了条件**: テスト環境が完全に動作し、サンプルデータが生成可能
- **依存**: なし
- **推定時間**: 3時間

#### Task 1.2: テストデータファクトリー作成

- [x] UserFactory（user、approver、admin各ロール）
- [x] ApprovalGroupFactory（複数グループのサンプル）
- [x] ArticleFactory（様々なカテゴリ・内容の記事）
- [x] RevisionFactory（各ステータスの修正案）
- [x] NotificationFactory（通知サンプル）
- **完了条件**: 全エンティティのファクトリーが動作
- **依存**: Task 1.1
- **推定時間**: 2時間

### Phase 2: 認証・基盤APIテスト

#### Task 2.1: 認証API（/auth）テスト

- [ ] POST /auth/login - 正常ログイン
- [ ] POST /auth/login - 無効な認証情報
- [ ] POST /auth/register - ユーザー登録
- [ ] GET /auth/me - 現在のユーザー情報取得
- [ ] POST /auth/test-token - トークン検証
- **完了条件**: 全認証エンドポイントのテストがパス
- **依存**: Task 1.2
- **推定時間**: 2時間

#### Task 2.2: ユーザー管理API（/users）テスト

- [ ] GET /users/ - ユーザー一覧（管理者権限）
- [ ] POST /users/ - ユーザー作成（管理者権限）
- [ ] GET /users/{id} - ユーザー詳細（本人/管理者）
- [ ] PUT /users/{id} - ユーザー更新（権限チェック）
- [ ] DELETE /users/{id} - ユーザー削除（管理者権限）
- **完了条件**: 権限制御を含む全ユーザー管理機能のテスト完了
- **依存**: Task 2.1
- **推定時間**: 2時間

#### Task 2.3: マスタデータAPI（approval-groups, info-categories）テスト

- [ ] 承認グループCRUD操作テスト
- [ ] 情報カテゴリCRUD操作テスト
- [ ] アクティブ/非アクティブフィルタテスト
- [ ] 権限制御テスト
- **完了条件**: マスタデータ管理機能の完全テスト
- **依存**: Task 2.1
- **推定時間**: 2時間

### Phase 3: コア業務APIテスト

#### Task 3.1: 記事管理API（/articles）テスト

- [ ] GET /articles/ - 記事一覧取得
- [ ] POST /articles/ - 記事作成（管理者権限）
- [ ] GET /articles/{id} - 記事詳細
- [ ] PUT /articles/{id} - 記事更新（管理者権限）
- [ ] GET /articles/by-category/{id} - カテゴリ別一覧
- [ ] GET /articles/by-group/{id} - 承認グループ別一覧
- **完了条件**: 記事管理の全機能テスト完了
- **依存**: Task 2.3
- **推定時間**: 2時間

#### Task 3.2: 修正案基本API（/revisions）テスト

- [ ] GET /revisions/ - 修正案一覧（権限ベース）
- [ ] POST /revisions/ - 修正案作成
- [ ] GET /revisions/{id} - 修正案詳細（権限チェック）
- [ ] PUT /revisions/{id} - 修正案更新（draft状態のみ）
- [ ] DELETE /revisions/{id} - 修正案削除
- [ ] GET /revisions/by-status/{status} - ステータス別一覧
- [ ] PATCH /revisions/{id}/status - ステータス直接更新
- **完了条件**: 修正案CRUD操作の完全テスト
- **依存**: Task 3.1
- **推定時間**: 3時間

#### Task 3.3: 修正案提案API（/proposals）テスト

- [ ] POST /proposals/ - 提案作成（バリデーション含む）
- [ ] PUT /proposals/{id} - 提案更新（draft状態制約）
- [ ] POST /proposals/{id}/submit - 提案提出（状態遷移）
- [ ] POST /proposals/{id}/withdraw - 提案撤回（状態遷移）
- [ ] DELETE /proposals/{id} - 提案削除（draft制約）
- [ ] GET /proposals/my-proposals - 自分の提案一覧
- [ ] GET /proposals/for-approval - 承認待ち一覧
- [ ] GET /proposals/statistics - 統計情報
- **完了条件**: ビジネスロジックを含む提案管理の完全テスト
- **依存**: Task 3.2
- **推定時間**: 3時間

### Phase 4: ワークフロー・高度機能テスト

#### Task 4.1: 承認ワークフローAPI（/approvals）テスト

- [ ] POST /approvals/{id}/decide - 承認・却下処理
- [ ] GET /approvals/{id}/can-approve - 承認権限チェック
- [ ] GET /approvals/queue - 承認待ちキュー
- [ ] GET /approvals/metrics - 承認メトリクス
- [ ] GET /approvals/workload - ワークロード情報
- [ ] POST /approvals/bulk - 一括承認（最大20件制約）
- [ ] GET /approvals/history - 承認履歴
- [ ] GET /approvals/statistics/dashboard - ダッシュボード統計
- [ ] POST /approvals/{id}/quick-actions/{action} - クイックアクション
- **完了条件**: 承認ワークフロー全機能の動作確認
- **依存**: Task 3.3
- **推定時間**: 4時間

#### Task 4.2: 差分表示API（/diffs）テスト

- [ ] GET /diffs/{id} - 差分データ取得
- [ ] GET /diffs/article/{id}/snapshot - 記事スナップショット
- [ ] GET /diffs/article/{id}/history - 記事履歴
- [ ] POST /diffs/compare - 修正案比較
- [ ] GET /diffs/{id}/formatted - フォーマット済み差分
- [ ] GET /diffs/{id}/summary - 変更サマリー
- [ ] POST /diffs/bulk-summaries - 一括サマリー（最大50件）
- [ ] GET /diffs/statistics/changes - 変更統計
- **完了条件**: 差分表示機能の完全テスト
- **依存**: Task 3.3
- **推定時間**: 3時間

#### Task 4.3: 通知API（/notifications）テスト

- [ ] GET /notifications/my-notifications - 自分の通知一覧
- [ ] GET /notifications/statistics - 通知統計
- [ ] GET /notifications/digest - 通知ダイジェスト
- [ ] PUT /notifications/{id}/read - 既読化
- [ ] PUT /notifications/read-all - 全既読化
- [ ] POST /notifications/batch - 一括通知（最大100ユーザー）
- **完了条件**: 通知システムの完全テスト
- **依存**: Task 4.1
- **推定時間**: 2時間

#### Task 4.4: 分析・統計API（/analytics）テスト

- [ ] GET /analytics/overview - 分析概要
- [ ] GET /analytics/trends - トレンド分析
- [ ] GET /analytics/performance - パフォーマンスメトリクス
- [ ] GET /analytics/reports/summary - サマリーレポート
- [ ] GET /analytics/export/data - データエクスポート
- [ ] GET /analytics/dashboards/executive - エグゼクティブダッシュボード（管理者）
- **完了条件**: 分析機能の完全テスト
- **依存**: Task 4.1
- **推定時間**: 2時間

### Phase 5: シナリオテスト・統合テスト

#### Task 5.1: エンドツーエンドシナリオテスト

- [ ] 修正案作成→提出→承認の完全フロー
- [ ] 修正案作成→提出→却下→再提出フロー
- [ ] 修正案作成→提出→撤回→再編集フロー
- [ ] 一括承認シナリオ
- [ ] 通知配信シナリオ
- **完了条件**: 主要業務フローの完全動作確認
- **依存**: Task 4.1, 4.2, 4.3
- **推定時間**: 3時間

#### Task 5.2: 権限・セキュリティテスト

- [ ] 一般ユーザー権限境界テスト
- [ ] 承認者権限境界テスト
- [ ] 管理者権限テスト
- [ ] 不正なトークンでのアクセステスト
- [ ] SQLインジェクション対策確認
- [ ] 入力バリデーションテスト
- **完了条件**: セキュリティ要件の完全確認
- **依存**: Task 5.1
- **推定時間**: 3時間

#### Task 5.3: パフォーマンス・負荷テスト

- [ ] 大量データでの一覧取得性能
- [ ] 同時アクセステスト（100ユーザー想定）
- [ ] 大容量コンテンツの差分表示性能
- [ ] データベースクエリ最適化確認
- **完了条件**: パフォーマンス要件の達成確認
- **依存**: Task 5.1
- **推定時間**: 2時間

#### Task 5.4: エラーハンドリングテスト

- [ ] カスタム例外の適切な返却確認
- [ ] バリデーションエラーメッセージ確認
- [ ] 404/403/400エラーの適切な処理
- [ ] 状態遷移エラーの確認
- [ ] データベース接続エラー時の挙動
- **完了条件**: エラー処理の完全性確認
- **依存**: Task 5.1
- **推定時間**: 2時間

### Phase 6: 検証・仕上げ

#### Task 6.1: テストカバレッジ確認

- [ ] カバレッジレポート生成
- [ ] 未テスト部分の特定
- [ ] 追加テストの実装
- [ ] カバレッジ80%以上の達成
- **完了条件**: 十分なテストカバレッジの確保
- **依存**: Phase 5完了
- **推定時間**: 2時間

#### Task 6.2: システムAPI（/system）テスト

- [ ] GET /system/health - ヘルスチェック
- [ ] GET /system/version - バージョン情報
- [ ] GET /system/stats - システム統計（管理者）
- [ ] GET /system/config - システム設定（管理者）
- [ ] POST /system/maintenance - メンテナンスタスク（管理者）
- [ ] GET /system/api-documentation - API文書
- **完了条件**: システム管理機能の完全テスト
- **依存**: なし
- **推定時間**: 1時間

#### Task 6.3: テスト結果レポート作成

- [ ] テスト実行結果の集計
- [ ] 問題点・改善点の整理
- [ ] パフォーマンス測定結果のまとめ
- [ ] 次ステップへの推奨事項作成
- **完了条件**: 包括的なテストレポートの完成
- **依存**: Task 6.1, 6.2
- **推定時間**: 2時間

## 実装順序

1. Phase 1（準備）を最初に実行
2. Phase 2-3は並行実行可能（担当者を分けて実施）
3. Phase 4はPhase 3完了後に実施
4. Phase 5はPhase 4完了後に実施
5. Phase 6で全体の検証と仕上げ

## リスクと対策

- **テストデータの一貫性**: ファクトリーパターンで統一的に管理
- **権限テストの複雑性**: ロール別のテストケースを明確に分離
- **非同期処理のテスト**: pytest-asyncioを活用した適切な非同期テスト
- **外部依存（Redis）**: FakeRedisでモック化して独立性を確保

## 注意事項

- 各テストは独立して実行可能にする
- テストデータは各テスト終了時にクリーンアップ
- エラーケースも必ずテストする
- レスポンス形式とステータスコードを厳密に検証

## 実装開始ガイド

1. このタスクリストに従って順次実装を進めてください
2. 各タスクの開始時にTodoWriteでin_progressに更新
3. 完了時はcompletedに更新
4. 問題発生時は速やかに報告してください
5. テスト実行コマンド: `uv run pytest -v --cov=app backend/tests/`