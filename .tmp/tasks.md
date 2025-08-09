# タスクリスト - 失敗テストの修正とテストカバレッジ完成

## 概要

- **総タスク数**: 15
- **推定作業時間**: 8-12時間
- **優先度**: 高（現在5つのテストが失敗中）
- **目的**: 失敗テストの修正とテストカバレッジ完成

## 失敗テスト分析

現在の失敗テスト:
- `tests/integration/test_users_api.py::TestUserCreate::test_create_user_as_admin` - assert 400 == 201
- `tests/test_factory_smoke.py::test_all_factories_basic_smoke` - AssertionError: assert 'Technology 24' == 'Technology'
- `tests/unit/test_approval_group_repository.py::TestApprovalGroupRepository::test_delete_approval_group` - AttributeError: ApprovalGroup has no 'id'
- `tests/unit/test_approval_group_repository.py::TestApprovalGroupRepository::test_get_by_name` - AttributeError: get_by_name not found
- `tests/unit/test_approval_group_repository.py::TestApprovalGroupRepository::test_get_by_name_not_found` - AttributeError: get_by_name not found

## タスク一覧

### Phase 1: 失敗テストの原因調査

#### Task 1.1: ユーザーAPI失敗テストの調査

- [ ] `tests/integration/test_users_api.py::TestUserCreate::test_create_user_as_admin`の詳細確認
- [ ] API実装(`app/api/v1/endpoints/users.py`)とテストの期待値の照合
- [ ] バリデーションエラーの原因特定
- [ ] リクエストデータとスキーマの検証
- **完了条件**: 失敗原因が特定され、修正方針が決定
- **依存**: なし
- **推定時間**: 30分

#### Task 1.2: ファクトリーテスト失敗の調査

- [ ] `tests/test_factory_smoke.py`のテストロジック確認
- [ ] ファクトリー実装(`tests/factories/`)のデータ生成ロジック確認
- [ ] 期待値'Technology'と実際の値'Technology 24'の差異分析
- [ ] カウンター機能やユニーク制約の影響確認
- **完了条件**: ファクトリーのデータ生成ロジックが理解され、修正方針決定
- **依存**: なし
- **推定時間**: 20分

#### Task 1.3: ApprovalGroupリポジトリ失敗の調査

- [ ] `app/models/approval_group.py`のモデル定義確認
- [ ] `app/repositories/approval_group.py`の実装確認
- [ ] `id`属性の存在確認（`group_id`との関係）
- [ ] `get_by_name`メソッドの実装状況確認
- [ ] 単体テスト期待値とリポジトリ実装の整合性確認
- **完了条件**: モデル属性とリポジトリメソッドの不整合が特定
- **依存**: なし
- **推定時間**: 20分

### Phase 2: 失敗テストの修正

#### Task 2.1: ユーザーAPI修正

- [ ] API実装の修正（バリデーションエラー対応）
- [ ] テスト期待値の妥当性確認・修正
- [ ] リクエストデータ形式の調整
- [ ] 修正後の動作確認
- **完了条件**: `test_create_user_as_admin`テストがパス
- **依存**: Task 1.1
- **推定時間**: 45分

#### Task 2.2: ファクトリーテスト修正

- [ ] ファクトリーのデータ生成ロジック修正
- [ ] テストの期待値調整（'Technology 24'対応または生成ロジック修正）
- [ ] ユニーク制約対応の改善
- [ ] 他のファクトリーへの影響確認
- **完了条件**: `test_all_factories_basic_smoke`テストがパス
- **依存**: Task 1.2
- **推定時間**: 30分

#### Task 2.3: ApprovalGroupモデル・リポジトリ修正

- [ ] ApprovalGroupモデルの`id`属性問題解決（プロパティ追加またはテスト修正）
- [ ] ApprovalGroupRepositoryに`get_by_name`メソッド実装
- [ ] 既存の`get_by_group_name`との整合性確保
- [ ] 単体テストの修正・調整
- **完了条件**: ApprovalGroupリポジトリの全テストがパス
- **依存**: Task 1.3
- **推定時間**: 45分

### Phase 3: テストカバレッジの強化

#### Task 3.1: カバレッジ分析実行

- [ ] `pytest --cov=app --cov-report=html`でカバレッジ取得
- [ ] 現在のカバレッジ率確認
- [ ] カバレッジ不足領域の特定
- [ ] 80%カバレッジ目標に向けた計画策定
- **完了条件**: カバレッジレポートと改善計画が完成
- **依存**: Phase 2完了
- **推定時間**: 20分

#### Task 3.2: 未テストAPIエンドポイントの特定

- [ ] api_design.mdと実際のテストファイルの比較
- [ ] 未実装のテストケース特定
- [ ] 優先度別のテスト追加計画作成
- **完了条件**: 追加すべきテストの一覧と優先度が明確化
- **依存**: Task 3.1
- **推定時間**: 30分

#### Task 3.3: 権限制御テストの強化

- [ ] ロールベースアクセス制御の包括的テスト追加
- [ ] 権限境界テストケースの実装
- [ ] 不正アクセステストの追加
- [ ] セキュリティテストの強化
- **完了条件**: 権限制御が網羅的にテストされる
- **依存**: Task 3.2
- **推定時間**: 60分

#### Task 3.4: エラーハンドリングテストの強化

- [ ] カスタム例外のテストケース追加
- [ ] バリデーションエラーの境界値テスト
- [ ] エラーレスポンス形式の一貫性テスト
- [ ] 異常系シナリオの網羅的テスト
- **完了条件**: エラーハンドリングが包括的にテストされる
- **依存**: Task 3.3
- **推定時間**: 45分

### Phase 4: パフォーマンス・統合テスト

#### Task 4.1: パフォーマンステスト実装

- [ ] 大量データでの応答時間テスト（3秒以内要件）
- [ ] 同時接続100ユーザーのテスト
- [ ] 10MBコンテンツでの差分表示テスト
- [ ] ページネーション性能テスト
- **完了条件**: パフォーマンス要件を満たすことが検証される
- **依存**: Task 3.4
- **推定時間**: 90分

#### Task 4.2: E2E統合テストの強化

- [ ] 修正案の完全ワークフローテスト（作成→提出→承認）
- [ ] 通知システムの統合テスト
- [ ] 差分表示の統合テスト
- [ ] ユーザー認証フローの統合テスト
- **完了条件**: 主要ビジネスフローが完全にテストされる
- **依存**: Task 4.1
- **推定時間**: 75分

#### Task 4.3: CI/CD統合とテスト環境整備

- [ ] GitHub Actionsでの自動テスト実行確認
- [ ] Windows環境でのテスト実行確認
- [ ] テストレポート生成とカバレッジ取得の自動化
- [ ] テスト失敗時の通知設定
- **完了条件**: CI/CDでテストが自動実行され、結果が報告される
- **依存**: Task 4.2
- **推定時間**: 45分

### Phase 5: 最終検証・文書化

#### Task 5.1: 全テストの実行・検証

- [ ] 全テストスイートの実行
- [ ] パフォーマンステストの実行
- [ ] カバレッジ80%以上の達成確認
- [ ] テスト実行時間の測定・最適化
- **完了条件**: 全テストがパスし、カバレッジ目標を達成
- **依存**: Task 4.3
- **推定時間**: 30分

#### Task 5.2: テストドキュメントの更新

- [ ] test_design.mdの実装状況反映
- [ ] テスト実行手順書の更新
- [ ] カバレッジレポートの作成
- [ ] 今後のテスト保守ガイドライン作成
- **完了条件**: テスト関連ドキュメントが完全に更新される
- **依存**: Task 5.1
- **推定時間**: 30分

## 実装順序

1. **Phase 1-2**: 失敗テストの修正（並行実行可能）
2. **Phase 3**: テストカバレッジの強化（順次実行）
3. **Phase 4**: パフォーマンス・統合テスト（順次実行）
4. **Phase 5**: 最終検証・文書化（順次実行）

## リスクと対策

- **モデル設計変更のリスク**: ApprovalGroup.id問題 → プロパティ追加で最小限の変更
- **テスト実行時間の増加**: パフォーマンステスト追加 → 並列実行とマーク分離で対策
- **CI/CDでの失敗**: Windows環境特有の問題 → ローカル検証を徹底

## 注意事項

- 各タスクはコミット単位で完結させる
- 失敗テスト修正後は必ず全テストを実行して副作用確認
- パフォーマンステストは専用マーク(`@pytest.mark.performance`)で分離
- カバレッジ測定は除外パターン(tests/, migrations/)を適切に設定

## 実装開始ガイド

1. このタスクリストに従って順次実装を進めてください
2. 各タスクの開始時にTodoWriteでin_progressに更新
3. 完了時はcompletedに更新
4. 問題発生時は速やかに報告してください

## コマンド参考

```bash
# 失敗テストのみ実行
uv run pytest tests/integration/test_users_api.py::TestUserCreate::test_create_user_as_admin -v

# カバレッジ付き全テスト実行
uv run pytest --cov=app --cov-report=html --cov-report=term

# 特定マークのテスト実行
uv run pytest -m "not performance" -v

# パフォーマンステストのみ実行
uv run pytest -m performance -v
```