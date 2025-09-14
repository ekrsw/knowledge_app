# KSAP フロントエンド アーキテクチャ設計

## 🎯 設計方針とMVP戦略

### ビジネス要件
- **年間処理件数**: 10,000件の改訂提案
- **重要課題**: 承認作業の効率化
- **優先機能**: 差分理解 + 判定速度の両立

### MVP方針
- **基本的だが確実に動作**する機能セット
- 軽量版差分表示機能
- 将来の高機能化への拡張性を保持

## 🏗️ システムアーキテクチャ

### 技術スタック
```
Frontend Stack:
├── Next.js 15 (App Router + Turbopack)
├── React 19
├── TailwindCSS v4
├── TypeScript (strict mode)
└── react-diff-viewer-continued (差分表示)

Backend Integration:
├── FastAPI REST API (localhost:8000/api/v1)
├── JWT Bearer Authentication
└── PostgreSQL データベース
```

### ページ構成とルーティング
```
app/
├── layout.tsx (Root Layout + 認証)
├── page.tsx (Dashboard Redirect)
├── login/page.tsx
├── dashboard/page.tsx (ロール別分岐)
├── approvals/
│   ├── queue/page.tsx (承認キュー)
│   ├── review/[id]/page.tsx (承認レビュー ⭐最重要)
│   └── history/page.tsx (承認履歴)
├── proposals/
│   ├── new/page.tsx (新規提案)
│   ├── my/page.tsx (自分の提案)
│   └── edit/[id]/page.tsx (提案編集)
└── admin/
    ├── users/page.tsx (ユーザー管理)
    └── stats/page.tsx (システム統計)
```

## 🎨 承認レビューページ設計 (核心機能)

### レイアウト構成
```
┌─────────────┬─────────────────────┬─────────────┐
│ Summary     │ DiffViewer         │ Actions     │
│ (1/4 width) │ (2/4 width)       │ (1/4 width) │
│             │                   │             │
│ ・記事情報   │ ・Before/After    │ ・判定ボタン │
│ ・提案者    │ ・変更ハイライト   │ ・コメント欄 │
│ ・重要度    │ ・フィールド別表示 │ ・操作ガイド    │
│ ・変更統計  │ ・critical強調    │ ・ナビゲーション │
└─────────────┴─────────────────────┴─────────────┘

レスポンシブ対応:
- Desktop (1024px+): 3列グリッド
- Tablet (768px+): 2列グリッド (Diff+Actions | Summary)
- Mobile (~768px): 縦スタック
```

### データフロー

#### ページ読み込み処理
```mermaid
graph TD
    A[承認レビューページ<br/>アクセス] --> B[GET /revisions/{revision_id}]
    B --> C[RevisionWithNames<br/>データ取得]
    B --> D[GET /diffs/{revision_id}]
    D --> E[RevisionDiff<br/>データ取得]
    C --> F[並列レンダリング<br/>Summary + Diff + Actions]
    E --> F
    F --> G[承認レビューページ<br/>表示完了]
```

#### 判定処理フロー
```mermaid
graph TD
    H[ユーザー判定<br/>A/R/C/D + コメント] --> I[POST /approvals/{id}/decide]
    I --> J{API応答}
    J -->|成功| K[判定完了<br/>Success通知]
    J -->|エラー| L[エラー表示<br/>再試行可能]
    K --> M{次のアクション}
    M -->|Next Available| N[次の案件へ<br/>ナビゲーション]
    M -->|No More Items| O[承認キューへ<br/>戻る]
    L --> H
```

## 🚀 開発フェーズ計画

### Phase 1: 認証・ナビゲーション基盤 (Week 1-2)
- JWT認証システム
- ロール別ダッシュボード
- 基本ナビゲーション・レイアウト
- AuthGuard実装

### Phase 2: 承認ワークフロー (Week 3-4) ⭐最重要
- 承認キュー画面
- 承認レビューページ (3列レイアウト)
- 差分表示コンポーネント (基本版)
- 判定アクション機能
- Next/Previous ナビゲーション

### Phase 3: 提案管理機能 (Week 5-6)
- 提案作成フォーム
- 提案一覧・編集機能
- 自分の提案管理

### Phase 4: 管理機能・最適化 (Week 7-8)
- 通知システム
- 管理者機能
- パフォーマンス最適化
- エラーハンドリング強化

## 📊 ユーザーロール別機能マトリクス

| 機能 | 一般ユーザー | 承認者 | 管理者 |
|------|-------------|-------|-------|
| 提案作成・編集 | ✅ | ❌ | ✅ |
| 承認キュー | ❌ | ✅ | ✅ |
| 承認レビュー | ❌ | ✅ | ✅ |
| 全提案閲覧 | ❌ | △(担当分) | ✅ |
| ユーザー管理 | ❌ | ❌ | ✅ |
| システム統計 | ❌ | △(限定) | ✅ |

## 🔧 技術的制約・前提条件

### パフォーマンス要件
- 承認レビューページの初期表示: 3秒以内
- 判定処理: 1秒以内
- UI操作応答: 100ms以内

### ブラウザサポート
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### アクセシビリティ
- WCAG 2.1 AA準拠
- キーボードナビゲーション完全対応
- スクリーンリーダー対応

## 📈 将来の拡張性

### 高機能化への道筋
- **差分表示**: Monaco Editor統合、セマンティック差分
- **判定支援**: 機械学習判定支援、予測入力
- **リアルタイム**: WebSocket通知、協調編集
- **分析機能**: 承認パターン分析、効率性メトリクス

### スケーラビリティ
- **フロントエンド**: React Query導入、仮想スクロール
- **状態管理**: Zustand/Redux Toolkit移行検討
- **キャッシュ**: Service Worker、オフライン対応