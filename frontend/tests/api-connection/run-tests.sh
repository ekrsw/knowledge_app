#!/bin/bash

# API接続テスト実行スクリプト
# Task 1.3のAPI接続テスト機能の総合検証

echo "🚀 API接続テスト実行スクリプト開始"
echo "=================================="
echo ""

# 現在のディレクトリを保存
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📁 実行ディレクトリ: $SCRIPT_DIR"
echo ""

# バックエンドの動作確認
echo "🔍 バックエンド動作確認..."
if curl -s -f http://localhost:8000/api/v1/system/health > /dev/null; then
    echo "✅ バックエンドが動作しています (localhost:8000)"
else
    echo "❌ バックエンドに接続できません (localhost:8000)"
    echo "💡 バックエンドを起動してから再度実行してください"
    exit 1
fi
echo ""

# 既存の結果ファイルをクリーンアップ
echo "🧹 既存の結果ファイルをクリーンアップ..."
rm -f test-results.json typescript-test-results.json final-verification-results.json
echo ""

# テスト実行結果を格納する変数
declare -a test_results
total_tests=0
passed_tests=0

# 1. Node.jsテストを実行
echo "1️⃣ Node.jsテスト実行中..."
echo "-------------------------"
if node node-test.js; then
    echo "✅ Node.jsテスト: 成功"
    test_results+=("Node.js Test: PASS")
    ((passed_tests++))
else
    echo "❌ Node.jsテスト: 失敗"
    test_results+=("Node.js Test: FAIL")
fi
((total_tests++))
echo ""

# 2. TypeScriptテストを実行 (フロントエンドディレクトリから実行)
echo "2️⃣ TypeScriptテスト実行中..."
echo "----------------------------"
cd ../../  # フロントエンドルートに移動
if npx tsx tests/api-connection/typescript-test.ts; then
    echo "✅ TypeScriptテスト: 成功"
    test_results+=("TypeScript Test: PASS")
    ((passed_tests++))
else
    echo "❌ TypeScriptテスト: 失敗"
    test_results+=("TypeScript Test: FAIL")
fi
((total_tests++))

# 元のディレクトリに戻る
cd "$SCRIPT_DIR"
echo ""

# 3. 最終検証を実行
echo "3️⃣ 最終検証実行中..."
echo "-------------------"
if node final-verification.js; then
    echo "✅ 最終検証: 成功"
    test_results+=("Final Verification: PASS")
    ((passed_tests++))
else
    echo "❌ 最終検証: 失敗"
    test_results+=("Final Verification: FAIL")
fi
((total_tests++))
echo ""

# 総合結果の表示
echo "📊 総合テスト結果"
echo "=================="
echo "実行時刻: $(date)"
echo "総テスト数: $total_tests"
echo "成功: $passed_tests"
echo "失敗: $((total_tests - passed_tests))"

if [ $total_tests -gt 0 ]; then
    success_rate=$((passed_tests * 100 / total_tests))
    echo "成功率: ${success_rate}%"
else
    echo "成功率: 0%"
fi

echo ""
echo "詳細結果:"
for result in "${test_results[@]}"; do
    echo "  • $result"
done
echo ""

# 結果ファイルの確認（複数の場所をチェック）
echo "📝 生成された結果ファイル:"

# test-results.json
if [ -f "test-results.json" ]; then
    echo "  ✅ test-results.json"
else
    echo "  ❌ test-results.json (生成されませんでした)"
fi

# typescript-test-results.json（テストディレクトリとフロントエンドルートをチェック）
if [ -f "typescript-test-results.json" ]; then
    echo "  ✅ typescript-test-results.json (テストディレクトリ)"
elif [ -f "../../typescript-test-results.json" ]; then
    echo "  ✅ typescript-test-results.json (フロントエンドルート)"
    # テストディレクトリに移動
    mv "../../typescript-test-results.json" "typescript-test-results.json" 2>/dev/null || true
else
    echo "  ❌ typescript-test-results.json (生成されませんでした)"
fi

# final-verification-results.json
if [ -f "final-verification-results.json" ]; then
    echo "  ✅ final-verification-results.json"
else
    echo "  ❌ final-verification-results.json (生成されませんでした)"
fi

echo ""

# Task 1.3 完了判定
if [ $passed_tests -eq $total_tests ]; then
    echo "🎉 すべてのテストが成功しました！"
    echo "✅ Task 1.3「型定義ファイルの作成」のAPI接続テスト機能は完了しています。"
    echo ""
    echo "🔧 確認された機能:"
    echo "  • API接続テスト機能の実装 (lib/api/test-connection.ts)"
    echo "  • Node.js環境での動作確認"
    echo "  • TypeScript環境での動作確認"
    echo "  • エラーハンドリングの正常動作"
    echo "  • 認証制御の正常動作"
    echo "  • 各種エンドポイントの動作確認"
    exit 0
else
    echo "⚠️ 一部のテストが失敗しました。"
    echo "❌ Task 1.3の完了条件を満たしていません。"
    echo ""
    echo "🔍 以下を確認してください:"
    echo "  • バックエンドが正常に動作しているか"
    echo "  • ネットワーク接続に問題がないか"
    echo "  • 依存関係が正しくインストールされているか"
    exit 1
fi