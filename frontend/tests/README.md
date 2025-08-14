# Tests Directory

このディレクトリにはテスト関連のファイルが含まれています。

## 構造

```
tests/
├── README.md                 # このファイル
├── auth-test.ts             # 認証システムのテスト・開発用ユーティリティ
└── api-connection/          # API接続テスト
    ├── README.md
    ├── final-verification-results.json
    ├── final-verification.js
    ├── node-test.js
    ├── run-tests.sh
    ├── test-results.json
    ├── typescript-test-results.json
    └── typescript-test.ts
```

## 使用方法

### 認証システムテスト

```typescript
import { runAuthTests, devAuthTest, createDummyAuthSession } from '@/tests/auth-test';

// 開発環境での認証テスト実行
await devAuthTest();

// ダミー認証セッション作成（開発用）
createDummyAuthSession();
```

### API接続テスト

```bash
cd tests/api-connection
./run-tests.sh
```

## 注意事項

- このディレクトリのファイルはプロダクションビルドには含まれません
- 開発・テスト用の機能のみ利用してください
- 本番環境での使用は避けてください