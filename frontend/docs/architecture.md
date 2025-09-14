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

#### フロントエンドスタック
```mermaid
graph TD
    A[Frontend Stack] --> B[Next.js 15<br/>App Router + Turbopack]
    A --> C[React 19]
    A --> D[TailwindCSS v4]
    A --> E[TypeScript<br/>strict mode]
    A --> F[react-diff-viewer-continued<br/>差分表示]
```

#### バックエンド統合
```mermaid
graph TD
    G[Backend Integration] --> H[FastAPI REST API<br/>localhost:8000/api/v1]
    G --> I[JWT Bearer Authentication]
    G --> J[PostgreSQL データベース]
```

### ページ構成とルーティング

```mermaid
graph TD
    A[app/] --> B[layout.tsx<br/>Root Layout + サイドバーナビ]
    A --> C[page.tsx<br/>Dashboard Redirect]
    A --> D[login/page.tsx<br/>認証ページのみ]

    B --> E[サイドバーナビゲーション]
    E --> F[メインコンテンツエリア]

    F --> G[dashboard/page.tsx<br/>ロール別ダッシュボード]

    F --> H[approvals/]
    H --> I[queue/page.tsx<br/>承認キュー]
    H --> J["review/[id]/page.tsx<br/>承認レビュー ⭐最重要"]
    H --> K[history/page.tsx<br/>承認履歴]

    F --> L[proposals/]
    L --> M[new/page.tsx<br/>新規提案]
    L --> N[my/page.tsx<br/>自分の提案]
    L --> O["edit/[id]/page.tsx<br/>提案編集"]

    F --> P[admin/]
    P --> Q[users/page.tsx<br/>ユーザー管理]
    P --> R[stats/page.tsx<br/>システム統計]
```

#### サイドバーナビゲーション構成
```mermaid
graph TD
    S[サイドバー 220px] --> T[ユーザー情報<br/>・アバター<br/>・名前<br/>・ロール]
    S --> U[メインメニュー]
    S --> V[クイックアクション]

    U --> W[ダッシュボード<br/>📊 Overview]
    U --> X[承認関連<br/>📋 Approvals]
    U --> Y[提案関連<br/>📝 Proposals]
    U --> Z[管理機能<br/>⚙️ Admin]

    X --> AA[承認キュー<br/>✅ Queue]
    X --> BB[承認履歴<br/>📈 History]

    Y --> CC[新規作成<br/>➕ Create New]
    Y --> DD[自分の提案<br/>📄 My Proposals]

    Z --> EE[ユーザー管理<br/>👥 Users]
    Z --> FF[システム統計<br/>📊 Statistics]
```

## 🎨 承認レビューページ設計 (核心機能)

### レイアウト構成

#### サイドバーナビゲーション + メインコンテンツ
```mermaid
flowchart LR
    A[サイドバー<br/>220px fixed<br/>・ナビゲーション<br/>・ユーザー情報<br/>・メニュー<br/>・クイックアクション] --- B[メインコンテンツ<br/>flex-1<br/>・承認レビューページ<br/>・承認キュー<br/>・提案管理<br/>・システム統計]

    B --> C[承認レビュー詳細<br/>・Summary Panel<br/>・DiffViewer<br/>・Action Panel]
```

#### 承認レビューページ内部構成
```mermaid
flowchart TD
    D[承認レビューページ] --> E[ヘッダー<br/>・パンくずナビ<br/>・案件番号<br/>・進捗表示]
    D --> F[メインエリア<br/>2列レイアウト]

    F --> G[左カラム 60%<br/>・記事情報Summary<br/>・DiffViewer]
    F --> H[右カラム 40%<br/>・判定Actions<br/>・コメント欄<br/>・Next/Previous<br/>・履歴表示]
```

#### レスポンシブ対応
```mermaid
graph TD
    I[画面サイズ] --> J[Desktop 1024px+]
    I --> K[Tablet 768px+]
    I --> L[Mobile ~768px]

    J --> M["サイドバー(220px) + メインコンテンツ<br/>承認レビュー: 左60% + 右40%"]
    K --> N["サイドバー(180px) + メインコンテンツ<br/>承認レビュー: 縦積み表示"]
    L --> O["ハンバーガーメニュー<br/>承認レビュー: 単一カラム<br/>タブ切り替え形式"]
```

### データフロー

#### ページ読み込み処理
```mermaid
graph TD
    A[承認レビューページ<br/>アクセス] --> B["GET /revisions/{revision_id}"]
    B --> C[RevisionWithNames<br/>データ取得]
    B --> D["GET /diffs/{revision_id}"]
    D --> E[RevisionDiff<br/>データ取得]
    C --> F[並列レンダリング<br/>Summary + Diff + Actions]
    E --> F
    F --> G[承認レビューページ<br/>表示完了]
```

#### 判定処理フロー
```mermaid
graph TD
    H[ユーザー判定<br/>A/R/C/D + コメント] --> I["POST /approvals/{id}/decide"]
    I --> J{API応答}
    J -->|成功| K[判定完了<br/>Success通知]
    J -->|エラー| L[エラー表示<br/>再試行可能]
    K --> M{次のアクション}
    M -->|Next Available| N[次の案件へ<br/>ナビゲーション]
    M -->|No More Items| O[承認キューへ<br/>戻る]
    L --> H
```

## 🚀 開発フェーズ計画

### 開発タイムライン
```mermaid
gantt
    title KSAP フロントエンド開発スケジュール
    dateFormat X
    axisFormat %s
    
    section Phase 1: 基盤
    JWT認証システム           :done, p1a, 0, 3d
    ロール別ダッシュボード      :done, p1b, after p1a, 2d
    基本ナビゲーション         :done, p1c, after p1b, 2d
    AuthGuard実装            :done, p1d, after p1c, 1d
    
    section Phase 2: 承認ワークフロー ⭐
    承認キュー画面            :active, p2a, after p1d, 3d
    承認レビューページ         :p2b, after p2a, 4d
    差分表示コンポーネント      :p2c, after p2b, 3d
    判定アクション機能         :p2d, after p2c, 2d
    ナビゲーション機能         :p2e, after p2d, 2d
    
    section Phase 3: 提案管理
    提案作成フォーム          :p3a, after p2e, 4d
    提案一覧・編集機能         :p3b, after p3a, 3d
    自分の提案管理            :p3c, after p3b, 2d
    
    section Phase 4: 管理・最適化
    通知システム              :p4a, after p3c, 2d
    管理者機能               :p4b, after p4a, 3d
    パフォーマンス最適化       :p4c, after p4b, 2d
    エラーハンドリング強化     :p4d, after p4c, 1d
```

### フェーズ詳細

#### Phase 1: 認証・ナビゲーション基盤 (Week 1-2)
```mermaid
graph TD
    A[Phase 1: 基盤構築] --> B[JWT認証システム]
    A --> C[ロール別ダッシュボード]
    A --> D[基本ナビゲーション・レイアウト]
    A --> E[AuthGuard実装]
    
    B --> F[認証完了]
    C --> F
    D --> F
    E --> F
    F --> G[Phase 2開始可能]
```

#### Phase 2: 承認ワークフロー (Week 3-4) ⭐最重要
```mermaid
graph TD
    H[Phase 2: 承認ワークフロー] --> I[承認キュー画面]
    H --> J[承認レビューページ<br/>3列レイアウト]
    H --> K[差分表示コンポーネント<br/>基本版]
    H --> L[判定アクション機能]
    H --> M[Next/Previous ナビゲーション]
    
    I --> N[承認システム完成]
    J --> N
    K --> N
    L --> N
    M --> N
    N --> O[MVP完成]
```

## 📊 ユーザーロール別機能マトリクス

### 機能アクセス権限図
```mermaid
graph TD
    A[KSAP システム] --> B[一般ユーザー]
    A --> C[承認者]
    A --> D[管理者]
    
    B --> E[提案作成・編集 ✅]
    
    C --> F[承認キュー ✅]
    C --> G[承認レビュー ✅]
    C --> H[全提案閲覧 △<br/>担当分のみ]
    C --> I[システム統計 △<br/>限定表示]
    
    D --> J[提案作成・編集 ✅]
    D --> K[承認キュー ✅]
    D --> L[承認レビュー ✅]
    D --> M[全提案閲覧 ✅]
    D --> N[ユーザー管理 ✅]
    D --> O[システム統計 ✅]
```

### 権限マトリクス表
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

### 高機能化ロードマップ
```mermaid
graph TD
    A[現在のMVP] --> B[Phase 1: 基本機能強化]
    B --> C[Phase 2: AI・分析機能]
    C --> D[Phase 3: リアルタイム協調]
    
    B --> E[差分表示強化<br/>Monaco Editor統合<br/>セマンティック差分]
    
    C --> F[判定支援AI<br/>機械学習判定支援<br/>予測入力]
    C --> G[分析機能<br/>承認パターン分析<br/>効率性メトリクス]
    
    D --> H[リアルタイム機能<br/>WebSocket通知<br/>協調編集]
```

### 技術スケーラビリティ
```mermaid
graph TD
    I[現在の技術スタック] --> J[パフォーマンス最適化]
    I --> K[状態管理強化]
    I --> L[キャッシュ戦略]
    
    J --> M[React Query導入<br/>データ取得最適化]
    J --> N[仮想スクロール<br/>大量データ対応]
    
    K --> O[Zustand導入<br/>軽量状態管理]
    K --> P[Redux Toolkit<br/>複雑状態管理]
    
    L --> Q[Service Worker<br/>オフライン対応]
    L --> R[ブラウザキャッシュ<br/>高速化]
```