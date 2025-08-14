# API接続テスト

このディレクトリには、フロントエンドのAPI接続テスト機能の検証用ファイルが含まれています。

## ファイル構成

- `node-test.js` - Node.js環境でのAPI接続テスト
- `typescript-test.ts` - TypeScript環境でのテスト機能検証
- `final-verification.js` - 最終的な動作確認テスト
- `run-tests.sh` - すべてのテストを実行するスクリプト

## 使用方法

### 全テスト実行
```bash
cd tests/api-connection
bash run-tests.sh
```

### 個別テスト実行
```bash
# Node.jsテスト
node node-test.js

# TypeScriptテスト  
npx tsx typescript-test.ts

# 最終検証
node final-verification.js
```

## 注意事項

- バックエンドが `localhost:8000` で動作している必要があります
- 認証が必要なエンドポイントで 403/401 エラーが発生するのは正常な動作です
- テスト結果は `test-results.json` に出力されます

## Task 1.3 完了確認

これらのテストにより、Task 1.3「型定義ファイルの作成」における「API接続テスト機能の実装」が正常に動作することが確認されました。