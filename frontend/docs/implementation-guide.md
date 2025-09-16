# KSAP フロントエンド 実装ガイド

## 🚀 開発環境セットアップ

### 前提条件
```bash
# 必要なツール
Node.js 20+ (推奨: 20.11.0)
npm 10+
Git

# 開発ツール (推奨)
VS Code
Chrome DevTools
```

### プロジェクト初期化
```bash
# 依存関係インストール
cd frontend
npm install

# 開発サーバー起動
npm run dev

# 型チェック
npm run type-check

# リンター実行
npm run lint

# ビルド確認
npm run build
```

### VS Code 推奨設定
```json
// .vscode/settings.json
{
  "typescript.preferences.includePackageJsonAutoImports": "on",
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "tailwindCSS.includeLanguages": {
    "typescript": "javascript",
    "typescriptreact": "javascript"
  },
  "editor.inlineSuggest.enabled": true
}

// .vscode/extensions.json
{
  "recommendations": [
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint",
    "ms-vscode.vscode-typescript-next"
  ]
}
```

## 📁 ファイル・フォルダ構成

### ディレクトリ構造
```
frontend/
├── app/                          # Next.js App Router
│   ├── globals.css              # グローバルスタイル
│   ├── layout.tsx               # Root Layout
│   ├── page.tsx                 # Home (ダッシュボードリダイレクト)
│   ├── login/
│   │   └── page.tsx
│   ├── dashboard/
│   │   └── page.tsx
│   ├── approvals/               # 承認関連ページ ⭐最重要
│   │   ├── queue/page.tsx
│   │   ├── review/[id]/page.tsx
│   │   └── history/page.tsx
│   ├── proposals/               # メンテナンス提案関連ページ
│   │   ├── new/page.tsx
│   │   ├── my/page.tsx
│   │   └── edit/[id]/page.tsx
│   └── admin/                   # 管理者ページ
│       ├── users/page.tsx
│       └── stats/page.tsx
├── components/                   # React コンポーネント
│   ├── auth/                    # 認証関連
│   ├── approvals/               # 承認関連 ⭐最重要
│   ├── proposals/               # メンテナンス提案関連
│   ├── admin/                   # 管理機能
│   ├── common/                  # 共通コンポーネント
│   └── ui/                      # 基本UIコンポーネント
├── lib/                         # ユーティリティとAPI
│   ├── api.ts                   # APIクライアント
│   ├── auth.ts                  # 認証ヘルパー
│   ├── types.ts                 # 型定義
│   └── utils.ts                 # 共通ユーティリティ
├── hooks/                       # カスタムフック
├── contexts/                    # React Context
├── styles/                      # 追加スタイル
├── public/                      # 静的ファイル
├── docs/                        # 設計文書
└── __tests__/                   # テストファイル
```

## 🏗️ 実装順序とマイルストーン

### フェーズ1: 基盤構築 (Week 1-2)

#### 1.1 プロジェクト初期設定
```bash
# パッケージ追加
npm install clsx react-diff-viewer-continued

# 型定義ファイル作成
touch lib/types.ts
touch lib/api.ts
```

#### 1.2 サイドバーナビゲーション + レイアウト実装
```typescript
// app/layout.tsx の実装例
import { AuthProvider } from '@/contexts/AuthContext';
import { Sidebar } from '@/components/common/Sidebar';

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ja">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <AuthProvider>
          <div className="flex h-screen bg-gray-50">
            <Sidebar />
            <main className="flex-1 flex flex-col overflow-hidden">
              {children}
            </main>
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}
```

##### サイドバーコンポーネント実装順序
```bash
# 実装優先順位
1. components/common/Sidebar.tsx → メインサイドバー構造
2. components/common/SidebarNavigation.tsx → ナビゲーションメニュー
3. components/common/UserProfile.tsx → ユーザープロファイル
4. hooks/useSidebar.ts → サイドバー状態管理
5. contexts/SidebarContext.tsx → グローバル状態
```

#### 1.3 認証システム実装
```typescript
// 実装優先順位
1. lib/api.ts → APIクライアント基盤
2. contexts/AuthContext.tsx → 認証状態管理
3. components/auth/LoginForm.tsx → ログインフォーム
4. components/auth/AuthGuard.tsx → ページ保護
5. app/login/page.tsx → ログインページ
```

#### 1.4 サイドバーナビゲーション実装
```typescript
// components/common/Sidebar.tsx
export function Sidebar() {
  const { user } = useAuth();
  const { isCollapsed, toggle } = useSidebar();

  return (
    <aside className={clsx(
      'bg-white border-r border-gray-200 flex-shrink-0 flex flex-col transition-all duration-200',
      isCollapsed ? 'w-16' : 'w-220px'
    )}>
      <SidebarHeader user={user} isCollapsed={isCollapsed} />
      <SidebarNavigation user={user} isCollapsed={isCollapsed} />
      <SidebarFooter isCollapsed={isCollapsed} />
    </aside>
  );
}

// components/common/SidebarNavigation.tsx
export function SidebarNavigation({ user, isCollapsed }: SidebarNavigationProps) {
  const navigationGroups = [
    {
      title: 'メイン',
      items: [
        { href: '/dashboard', label: 'ダッシュボード', icon: HomeIcon },
      ]
    },
    ...(user?.role === 'approver' || user?.role === 'admin' ? [{
      title: '承認作業',
      items: [
        { href: '/maintenance/new', label: '新規メンテナンス', icon: PlusIcon },
        { href: '/maintenance', label: 'メンテナンス一覧', icon: DocumentTextIcon },
        { href: '/approvals/pending', label: '承認待ち', icon: ClockIcon },
      ]
    }] : []),
    {
      title: 'メンテナンス提案管理',
      items: [
        { href: '/proposals/new', label: '新規作成', icon: PlusIcon },
        { href: '/proposals/my', label: '自分のメンテナンス提案', icon: DocumentTextIcon },
      ]
    },
    ...(user?.role === 'admin' ? [{
      title: '管理機能',
      items: [
        { href: '/admin/users', label: 'ユーザー管理', icon: UsersIcon },
        { href: '/admin/stats', label: 'システム統計', icon: ChartBarIcon },
      ]
    }] : [])
  ];

  return (
    <nav className="flex-1 px-2 py-4 space-y-6 overflow-y-auto">
      {navigationGroups.map(group => (
        <NavigationGroup
          key={group.title}
          group={group}
          isCollapsed={isCollapsed}
        />
      ))}
    </nav>
  );
}
```

### フェーズ2: 承認ワークフロー (Week 3-4) ⭐最重要

#### 2.1 承認待ちページ
```bash
# ファイル作成順序
1. app/approvals/queue/page.tsx
2. components/approvals/ApprovalQueue.tsx
3. components/approvals/QueueItem.tsx
4. hooks/useApprovalQueue.ts
```

#### 2.2 承認レビューページ (最重要)
```bash
# コンポーネント実装順序 (サイドバーナビゲーション対応)
1. app/approvals/review/[id]/page.tsx → ページレイアウト (2カラム: 左60% + 右40%)
2. components/approvals/ProposalSummary.tsx → メンテナンス提案情報表示 (左カラム)
3. components/approvals/DiffViewer.tsx → 差分表示 (左カラム、基本版)
4. components/approvals/FieldDiffItem.tsx → 個別差分項目
5. components/approvals/ApprovalActions.tsx → 判定ボタン (右カラム)
6. components/approvals/ApprovalHistory.tsx → 承認履歴 (右カラム)
7. components/common/PageHeader.tsx → パンくずナビ + タイトル
8. hooks/useApprovalReview.ts → データ取得・状態管理
9. hooks/useApprovalNavigation.ts → 次/前ナビゲーション (右カラム)
```

##### 承認レビューページレイアウト構造
```typescript
// app/approvals/review/[id]/page.tsx
export default function ApprovalReviewPage({ params }: { params: { id: string } }) {
  return (
    <div className="flex flex-col h-full">
      {/* ページヘッダー */}
      <PageHeader 
        breadcrumbs={[
          { label: 'ダッシュボード', href: '/dashboard' },
          { label: '承認待ち', href: '/approvals/pending' },
          { label: `案件 #${revision.article_number}`, href: '#' }
        ]}
        title={revision.after_title}
      />

      {/* メインコンテンツエリア (2カラム) */}
      <div className="flex flex-1 gap-6 p-6 overflow-hidden">
        {/* 左カラム 60% (メンテナンス提案サマリー + 差分ビューア) */}
        <div className="flex-[3] flex flex-col gap-4 overflow-hidden">
          <ProposalSummary revision={revision} />
          <DiffViewer diff={diff} />
        </div>

        {/* 右カラム 40% (判定アクション + 履歴 + ナビゲーション) */}
        <div className="flex-[2] flex flex-col gap-4">
          <ApprovalActions revisionId={params.id} onDecision={handleDecision} />
          <ApprovalHistory revisionId={params.id} />
          <ApprovalNavigation 
            currentId={params.id}
            onNavigate={handleNavigate}
          />
        </div>
      </div>
    </div>
  );
}
```

#### 2.3 左カラム差分表示実装詳細 (サイドバー対応)
```typescript
// components/approvals/DiffViewer.tsx の実装手順

// Step 1: 基本構造 (左カラムに最適化)
export function DiffViewer({ diff, loading }: DiffViewerProps) {
  return (
    <Card className="flex-1 overflow-hidden flex flex-col">
      <DiffHeader diff={diff} />
      <DiffContent diff={diff} loading={loading} />
    </Card>
  );
}

// Step 2: ヘッダー実装 (コンパクト化)
function DiffHeader({ diff }: { diff: RevisionDiff }) {
  return (
    <div className="flex-shrink-0 p-4 border-b bg-gray-50">
      <ChangeSummaryIndicator diff={diff} />
    </div>
  );
}

// Step 3: メインコンテンツ (左カラムの高さを最大活用)
function DiffContent({ diff, loading }: { diff: RevisionDiff; loading: boolean }) {
  if (loading) return <DiffSkeleton />;

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="space-y-4 p-4">
        {diff.field_diffs.map((fieldDiff, index) => (
          <FieldDiffItem key={index} fieldDiff={fieldDiff} />
        ))}
      </div>
    </div>
  );
}

// Step 4: レスポンシブ対応 (タブレット・モバイル)
// タブレット・モバイルでは縦積みレイアウトに自動調整
@media (max-width: 1023px) {
  .diff-viewer {
    @apply flex-none h-96; /* 固定高さで表示 */
  }
}
```

### フェーズ3: メンテナンス提案管理 (Week 5-6)

#### 3.1 メンテナンス提案作成機能
```bash
# 実装順序
1. app/proposals/new/page.tsx
2. components/proposals/ProposalForm.tsx
3. components/proposals/ArticleSelector.tsx
4. components/proposals/ApproverSelector.tsx
5. hooks/useProposalCreation.ts
```

#### 3.2 メンテナンス提案管理機能
```bash
# 実装順序
1. app/proposals/my/page.tsx
2. components/proposals/ProposalList.tsx
3. components/proposals/ProposalCard.tsx
4. app/proposals/edit/[id]/page.tsx
5. hooks/useMyProposals.ts
```

### フェーズ4: 管理・最適化 (Week 7-8)

#### 4.1 管理機能
```bash
# Admin機能実装
1. app/admin/users/page.tsx
2. app/admin/stats/page.tsx
3. components/admin/UserManagement.tsx
4. components/admin/SystemStats.tsx
```

#### 4.2 通知機能
```bash
# 通知システム実装
1. contexts/NotificationContext.tsx
2. components/common/NotificationBanner.tsx
3. hooks/useNotifications.ts
```

## 🎯 重要な実装ガイドライン

### コンポーネント作成パターン (サイドバーレイアウト対応)
```typescript
// 1. 型定義を最初に行う
interface ComponentProps {
  // props definition
}

// 2. デフォルトpropsは分離
const defaultProps = {
  // defaults
};

// 3. メインコンポーネント (レスポンシブレイアウト考慮)
export function Component({ prop1, prop2, ...props }: ComponentProps) {
  // 4. hooks を最初に配置
  const [state, setState] = useState();
  const { isCollapsed } = useSidebar(); // サイドバー状態
  const customHook = useCustomHook();

  // 5. イベントハンドラー
  const handleEvent = useCallback(() => {
    // handler logic
  }, [dependencies]);

  // 6. 条件分岐による早期return
  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay error={error} />;

  // 7. メインレンダリング (レスポンシブクラス適用)
  return (
    <div className={clsx(
      'component-base-class',
      'lg:flex lg:gap-6', // デスクトップ: フレックスレイアウト
      'flex-col md:flex-col', // モバイル・タブレット: 縦積み
      isCollapsed && 'sidebar-collapsed'
    )}>
      {/* JSX */}
    </div>
  );
}

// 8. displayName設定 (開発時のデバッグ用)
Component.displayName = 'Component';
```

### サイドバーレイアウト専用パターン
```typescript
// ページレベルコンポーネントの標準パターン
export function StandardPage({ title, breadcrumbs, children }: StandardPageProps) {
  return (
    <div className="flex flex-col h-full">
      {/* ページヘッダー (固定) */}
      <PageHeader breadcrumbs={breadcrumbs} title={title} />
      
      {/* メインコンテンツ (可変) */}
      <div className="flex-1 overflow-hidden">
        {children}
      </div>
    </div>
  );
}

// 2カラムレイアウトパターン (承認レビューページ用)
export function TwoColumnLayout({ 
  leftContent, 
  rightContent, 
  leftRatio = 3, 
  rightRatio = 2 
}: TwoColumnLayoutProps) {
  return (
    <div className={clsx(
      // デスクトップ: 2カラム
      'lg:flex lg:gap-6 lg:p-6 lg:h-full',
      // タブレット・モバイル: 縦積み
      'flex flex-col gap-4 p-4 md:p-4'
    )}>
      <div className={clsx(
        `lg:flex-[${leftRatio}]`,
        'flex flex-col gap-4 lg:overflow-hidden'
      )}>
        {leftContent}
      </div>
      <div className={clsx(
        `lg:flex-[${rightRatio}]`,
        'flex flex-col gap-4'
      )}>
        {rightContent}
      </div>
    </div>
  );
}
```

### APIクライアント使用パターン
```typescript
// Good: カスタムフックでの使用
function useRevisionData(revisionId: string) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const fetchData = async () => {
      try {
        const result = await api.approval.getRevision(revisionId);
        if (!cancelled) {
          setData(result);
        }
      } catch (error) {
        if (!cancelled) {
          // error handling
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      cancelled = true;
    };
  }, [revisionId]);

  return { data, loading };
}

// Bad: コンポーネント内での直接使用
function Component() {
  const [data, setData] = useState(null);

  useEffect(() => {
    api.approval.getRevision('id').then(setData); // ❌ エラーハンドリングなし
  }, []);

  return <div>{data?.title}</div>;
}
```

### スタイリングガイドライン
```typescript
// 1. clsx を使用した条件付きスタイル
import clsx from 'clsx';

function Button({ variant, disabled, children }: ButtonProps) {
  return (
    <button
      className={clsx(
        'px-4 py-2 rounded-md font-medium transition-colors',
        {
          'bg-blue-600 text-white hover:bg-blue-700': variant === 'primary',
          'bg-gray-600 text-white hover:bg-gray-700': variant === 'secondary',
          'opacity-50 cursor-not-allowed': disabled,
        }
      )}
      disabled={disabled}
    >
      {children}
    </button>
  );
}

// 2. Tailwind カスタムクラス定義
// globals.css
@layer components {
  .btn-primary {
    @apply px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50;
  }
}
```

## 🧪 テスト実装ガイドライン

### テストファイル作成パターン
```bash
# テストファイル構成
__tests__/
├── components/
│   ├── auth/
│   │   └── LoginForm.test.tsx
│   └── approvals/
│       ├── ApprovalActions.test.tsx
│       └── DiffViewer.test.tsx
├── hooks/
│   ├── useAuth.test.ts
│   └── useApprovalReview.test.ts
├── lib/
│   └── api.test.ts
└── integration/
    └── approval-flow.test.tsx
```

### テスト実装例
```typescript
// __tests__/components/approvals/ApprovalActions.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ApprovalActions } from '@/components/approvals/ApprovalActions';

// モックの設定
const mockOnDecision = jest.fn();

describe('ApprovalActions', () => {
  beforeEach(() => {
    mockOnDecision.mockClear();
  });

  it('renders all action buttons', () => {
    render(
      <ApprovalActions
        revisionId="test-id"
        onDecision={mockOnDecision}
      />
    );

    expect(screen.getByRole('button', { name: /承認/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /却下/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /変更要求/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /保留/i })).toBeInTheDocument();
  });

  it('handles keyboard shortcuts', () => {
    render(
      <ApprovalActions
        revisionId="test-id"
        onDecision={mockOnDecision}
      />
    );

    fireEvent.keyDown(document, { key: 'a', code: 'KeyA' });

    expect(mockOnDecision).toHaveBeenCalledWith({
      action: 'approve',
      comment: undefined
    });
  });
});
```

## 📊 デバッグとパフォーマンス監視

### 開発ツール設定
```typescript
// lib/debug.ts (開発環境のみ)
if (process.env.NODE_ENV === 'development') {
  // React DevTools Profiler 有効化
  window.__REACT_DEVTOOLS_GLOBAL_HOOK__.settings.profiler = true;

  // パフォーマンス監視
  const observer = new PerformanceObserver((list) => {
    for (const entry of list.getEntries()) {
      if (entry.entryType === 'navigation') {
        console.log(`Page Load Time: ${entry.duration}ms`);
      }
    }
  });

  observer.observe({ entryTypes: ['navigation', 'paint'] });

  // API呼び出しログ
  const originalFetch = window.fetch;
  window.fetch = async (...args) => {
    const start = performance.now();
    const response = await originalFetch(...args);
    const duration = performance.now() - start;

    console.log(`API Call: ${args[0]} - ${duration.toFixed(2)}ms`);
    return response;
  };
}
```

### パフォーマンス監視
```typescript
// components/common/PerformanceMonitor.tsx (開発時)
export function PerformanceMonitor({ children }: { children: ReactNode }) {
  useEffect(() => {
    // Core Web Vitals 監視
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        console.log(`${entry.name}: ${entry.value}`);
      }
    });

    observer.observe({ entryTypes: ['measure'] });

    return () => observer.disconnect();
  }, []);

  return <>{children}</>;
}

// 使用例: 承認レビューページでの監視
export function ApprovalReviewPage({ params }: { params: { id: string } }) {
  return (
    <PerformanceMonitor>
      {/* ページコンテンツ */}
    </PerformanceMonitor>
  );
}
```

## 🚀 デプロイメント

### 本番デプロイ前チェックリスト
```bash
# 1. コード品質チェック
npm run lint
npm run type-check
npm run test

# 2. ビルド確認
npm run build
npm start

# 3. セキュリティチェック
npm audit
npm run security-check

# 4. パフォーマンステスト
npm run lighthouse
npm run bundle-analyze

# 5. E2Eテスト
npm run test:e2e
```

### 環境変数設定
```bash
# .env.production
NEXT_PUBLIC_API_URL=https://api.ksap.company.com/api/v1
NEXT_PUBLIC_APP_ENV=production
NEXTAUTH_SECRET=your-production-secret
NEXTAUTH_URL=https://ksap.company.com
```

この実装ガイドに従って開発を進めることで、確実で効率的なMVPフロントエンドを構築できます。各フェーズでの成果物を確認しながら、段階的に機能を積み上げていくことが重要です。