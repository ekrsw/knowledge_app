# KSAP フロントエンド コンポーネント設計仕様

## 🧩 コンポーネント階層構造

```
app/
├── layout.tsx (Root Layout + サイドバーナビゲーション)
├── page.tsx (Dashboard Redirect)
├── login/page.tsx (認証ページのみ、サイドバーなし)
├── approvals/review/[id]/page.tsx ⭐最重要
└── (other pages...)

components/
├── layout/
│   ├── Sidebar.tsx ⭐新規追加 (220px固定幅)
│   ├── SidebarNavigation.tsx
│   ├── UserProfile.tsx
│   ├── QuickActions.tsx
│   └── MobileNavigation.tsx (ハンバーガーメニュー)
├── auth/
│   ├── AuthGuard.tsx
│   └── LoginForm.tsx
├── approvals/ ⭐承認関連 (最重要)
│   ├── ApprovalReviewPage.tsx (左60% + 右40%レイアウト)
│   ├── ProposalSummary.tsx
│   ├── DiffViewer.tsx
│   ├── ApprovalActions.tsx
│   └── ApprovalQueue.tsx
├── common/
│   ├── PageHeader.tsx (パンくずナビ + タイトル)
│   ├── LoadingSpinner.tsx
│   └── ErrorBoundary.tsx
└── ui/
    ├── Button.tsx
    ├── Card.tsx
    ├── Input.tsx
    └── NavigationItem.tsx

hooks/
├── useAuth.ts
├── useApprovalReview.ts
├── useSidebar.ts ⭐新規追加
└── useApprovalNavigation.ts
```

## 🏗️ レイアウト関連コンポーネント

### Root Layout (app/layout.tsx)
```tsx
export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ja">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <AuthProvider>
          <div className="flex h-screen bg-gray-50">
            {/* サイドバーナビゲーション - 認証後のみ表示 */}
            <ConditionalSidebar />

            {/* メインコンテンツエリア */}
            <main className="flex-1 flex flex-col overflow-hidden">
              {children}
            </main>
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}

function ConditionalSidebar() {
  const { user, isAuthenticated } = useAuth();
  const pathname = usePathname();

  // ログインページではサイドバーを表示しない
  if (!isAuthenticated || pathname === '/login') {
    return null;
  }

  return <Sidebar user={user} />;
}
```

### Sidebar Component
```tsx
interface SidebarProps {
  user: User;
}

export function Sidebar({ user }: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useSidebar();

  return (
    <aside className={clsx(
      "bg-white border-r border-gray-200 flex flex-col transition-all duration-200",
      isCollapsed ? "w-16" : "w-56"
    )}>
      {/* ユーザー情報 */}
      <UserProfile user={user} isCollapsed={isCollapsed} />

      {/* メインナビゲーション */}
      <SidebarNavigation isCollapsed={isCollapsed} />

      {/* クイックアクション */}
      <QuickActions user={user} isCollapsed={isCollapsed} />

      {/* 折りたたみトグル */}
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="p-3 border-t border-gray-200 hover:bg-gray-50"
      >
        {isCollapsed ? <ChevronRightIcon className="w-5 h-5" /> : <ChevronLeftIcon className="w-5 h-5" />}
      </button>
    </aside>
  );
}
```

### UserProfile Component
```tsx
interface UserProfileProps {
  user: User;
  isCollapsed: boolean;
}

export function UserProfile({ user, isCollapsed }: UserProfileProps) {
  return (
    <div className={clsx(
      "p-4 border-b border-gray-200",
      isCollapsed && "px-2"
    )}>
      <div className="flex items-center gap-3">
        <Avatar
          src={user.avatar_url}
          alt={user.name}
          size={isCollapsed ? "sm" : "md"}
        />
        {!isCollapsed && (
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">
              {user.name}
            </p>
            <p className="text-xs text-gray-500 truncate">
              {getRoleLabel(user.role)}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
```

### SidebarNavigation Component
```tsx
interface NavigationItem {
  label: string;
  href: string;
  icon: ComponentType<{ className?: string }>;
  badge?: string | number;
  children?: NavigationItem[];
  roles?: UserRole[];
}

const navigationItems: NavigationItem[] = [
  {
    label: 'ダッシュボード',
    href: '/dashboard',
    icon: HomeIcon,
  },
  {
    label: '新規メンテナンス',
    href: '/maintenance/new',
    icon: PlusIcon,
  },
  {
    label: 'メンテナンス一覧',
    href: '/maintenance',
    icon: DocumentTextIcon,
    children: [
      {
        label: '検索・フィルター',
        href: '/maintenance/search',
        icon: MagnifyingGlassIcon,
      },
      {
        label: '集計機能',
        href: '/maintenance/analytics',
        icon: ChartBarIcon,
      },
    ],
  },
  {
    label: '承認待ち',
    href: '/approvals/pending',
    icon: ClockIcon,
    roles: ['approver', 'admin'],
    badge: 'pendingCount', // 動的バッジ
  },
  {
    label: '管理機能',
    href: '/admin',
    icon: Cog6ToothIcon,
    roles: ['admin'],
    children: [
      {
        label: 'ユーザー管理',
        href: '/admin/users',
        icon: UsersIcon,
      },
      {
        label: 'システム統計',
        href: '/admin/stats',
        icon: ChartBarIcon,
      },
    ],
  },
];

export function SidebarNavigation({ isCollapsed }: { isCollapsed: boolean }) {
  const { user } = useAuth();
  const pathname = usePathname();

  const filteredItems = navigationItems.filter(item =>
    !item.roles || item.roles.includes(user.role)
  );

  return (
    <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
      {filteredItems.map((item) => (
        <NavigationItem
          key={item.href}
          item={item}
          pathname={pathname}
          isCollapsed={isCollapsed}
        />
      ))}
    </nav>
  );
}
```

## 🎯 承認レビューページ (最重要コンポーネント)

### ApprovalReviewPage
```tsx
// app/approvals/review/[id]/page.tsx
interface ApprovalReviewPageProps {
  params: { id: string }
}

export default function ApprovalReviewPage({ params }: ApprovalReviewPageProps) {
  const { revision, diff, loading, error, submitDecision } = useApprovalReview(params.id);
  const { nextId, previousId, navigateNext, navigatePrevious } = useApprovalNavigation(params.id);

  if (loading) return <LoadingSkeleton />;
  if (error) return <ErrorBoundary error={error} />;

  return (
    <div className="flex flex-col h-full">
      {/* ページヘッダー */}
      <PageHeader
        breadcrumbs={[
          { label: 'ダッシュボード', href: '/dashboard' },
          { label: '承認キュー', href: '/approvals/queue' },
          { label: `案件 #${revision.article_number}`, current: true }
        ]}
        title={revision.after_title}
        actions={
          <div className="flex gap-2">
            <Button
              onClick={navigatePrevious}
              disabled={!previousId}
              variant="secondary"
              size="sm"
            >
              ← 前の案件
            </Button>
            <Button
              onClick={navigateNext}
              disabled={!nextId}
              variant="secondary"
              size="sm"
            >
              次の案件 →
            </Button>
          </div>
        }
      />

      {/* メインコンテンツ: 左60% + 右40% */}
      <div className="flex flex-1 gap-6 p-6 overflow-hidden">
        {/* 左カラム: 記事情報 + 差分表示 */}
        <div className="flex-[3] flex flex-col gap-4 overflow-hidden">
          <ProposalSummary revision={revision} className="flex-shrink-0" />
          <DiffViewer diff={diff} className="flex-1 overflow-hidden" />
        </div>

        {/* 右カラム: 判定アクション + 履歴 */}
        <div className="flex-[2] flex flex-col gap-4">
          <ApprovalActions
            revisionId={params.id}
            onDecision={submitDecision}
            className="flex-shrink-0"
          />

          {/* 判定履歴 (必要に応じて) */}
          <ApprovalHistory revisionId={params.id} className="flex-1" />
        </div>
      </div>
    </div>
  );
}
```

### ProposalSummary
```tsx
interface ProposalSummaryProps {
  revision: RevisionWithNames;
  className?: string;
}

export function ProposalSummary({ revision, className }: ProposalSummaryProps) {
  return (
    <Card className={clsx("p-4 overflow-y-auto", className)}>
      {/* 基本情報 */}
      <div className="space-y-4">
        <div>
          <h3 className="font-semibold text-lg">{revision.after_title}</h3>
          <p className="text-sm text-gray-600">記事番号: {revision.article_number}</p>
        </div>

        {/* 提案者情報 */}
        <div>
          <label className="text-sm font-medium">提案者</label>
          <p>{revision.proposer_name}</p>
        </div>

        {/* メンテナンス理由 */}
        <div>
          <label className="text-sm font-medium">メンテナンス理由</label>
          <p className="mt-1 text-sm">{revision.reason}</p>
        </div>

        {/* ステータス・日時 */}
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div>
            <label className="font-medium">ステータス</label>
            <StatusBadge status={revision.status} />
          </div>
          <div>
            <label className="font-medium">作成日時</label>
            <p>{formatDateTime(revision.created_at)}</p>
          </div>
        </div>

        {/* 重要度 */}
        {revision.after_importance && (
          <ImportanceIndicator className="bg-orange-100 text-orange-800" />
        )}
      </div>
    </Card>
  );
}
```

### DiffViewer
```tsx
interface DiffViewerProps {
  diff: RevisionDiff;
  className?: string;
  loading?: boolean;
}

export function DiffViewer({ diff, className, loading }: DiffViewerProps) {
  return (
    <Card className={clsx("overflow-hidden", className)}>
      {/* ヘッダー: 変更サマリー */}
      <div className="p-4 border-b bg-gray-50">
        <div className="flex justify-between items-center">
          <h3 className="font-semibold">変更内容</h3>
          <div className="flex gap-4 text-sm">
            <span>全変更: {diff.total_changes}件</span>
            <span className="text-orange-600">重要: {diff.critical_changes}件</span>
            <ImpactBadge level={diff.impact_level} />
          </div>
        </div>
      </div>

      {/* 差分表示エリア */}
      <div className="overflow-y-auto max-h-[calc(100vh-200px)]">
        {loading ? (
          <DiffSkeleton />
        ) : (
          <div className="space-y-4 p-4">
            {diff.field_diffs.map((fieldDiff, index) => (
              <FieldDiffItem
                key={index}
                fieldDiff={fieldDiff}
                isExpanded={fieldDiff.is_critical}
              />
            ))}
          </div>
        )}
      </div>
    </Card>
  );
}
```

### FieldDiffItem (差分表示の核心)
```tsx
interface FieldDiffItemProps {
  fieldDiff: FieldDiff;
  isExpanded?: boolean;
}

export function FieldDiffItem({ fieldDiff, isExpanded = false }: FieldDiffItemProps) {
  const [expanded, setExpanded] = useState(isExpanded);

  const getBorderColor = () => {
    switch (fieldDiff.change_type) {
      case 'added': return 'border-l-green-500 bg-green-50';
      case 'removed': return 'border-l-red-500 bg-red-50';
      case 'modified': return 'border-l-yellow-500 bg-yellow-50';
      default: return 'border-l-gray-300';
    }
  };

  return (
    <div className={clsx(
      "border-l-4 p-3 rounded-r",
      getBorderColor(),
      fieldDiff.is_critical && "ring-2 ring-orange-500"
    )}>
      {/* フィールド名とトグル */}
      <div className="flex justify-between items-center mb-2">
        <div className="flex items-center gap-2">
          <h4 className="font-medium">{fieldDiff.field_label}</h4>
          <ChangeTypeBadge type={fieldDiff.change_type} />
          {fieldDiff.is_critical && <CriticalIndicator />}
        </div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-sm text-gray-600 hover:text-gray-800"
        >
          {expanded ? 'たたむ' : '展開'}
        </button>
      </div>

      {/* 差分内容 */}
      <div className={clsx(!expanded && "max-h-20 overflow-hidden")}>
        {fieldDiff.change_type === 'modified' ? (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-medium text-gray-600">変更前</label>
              <div className="mt-1 p-2 bg-red-100 rounded text-sm">
                {fieldDiff.old_value || '(なし)'}
              </div>
            </div>
            <div>
              <label className="text-xs font-medium text-gray-600">変更後</label>
              <div className="mt-1 p-2 bg-green-100 rounded text-sm">
                {fieldDiff.new_value || '(なし)'}
              </div>
            </div>
          </div>
        ) : fieldDiff.change_type === 'added' ? (
          <div className="p-2 bg-green-100 rounded text-sm">
            <label className="text-xs font-medium text-gray-600">追加内容</label>
            <div>{fieldDiff.new_value}</div>
          </div>
        ) : (
          <div className="p-2 bg-red-100 rounded text-sm">
            <label className="text-xs font-medium text-gray-600">削除内容</label>
            <div>{fieldDiff.old_value}</div>
          </div>
        )}
      </div>
    </div>
  );
}
```

### ApprovalActions
```tsx
interface ApprovalActionsProps {
  revisionId: string;
  onDecision: (decision: ApprovalDecision) => Promise<void>;
  className?: string;
}

export function ApprovalActions({ revisionId, onDecision, className }: ApprovalActionsProps) {
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleDecision = async (action: ApprovalDecision['action']) => {
    setIsSubmitting(true);
    try {
      await onDecision({ action, comment: comment.trim() || undefined });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card className={clsx("p-4 flex flex-col gap-4", className)}>
      {/* 判定ボタン群 */}
      <div className="space-y-3">
        <h3 className="font-semibold">判定アクション</h3>

        <ActionButton
          action="approve"
          label="[A]承認する"
          variant="success"
          onClick={() => handleDecision('approve')}
          disabled={isSubmitting}
        />

        <ActionButton
          action="reject"
          label="[R]却下する"
          variant="danger"
          onClick={() => handleDecision('reject')}
          disabled={isSubmitting}
        />

        <ActionButton
          action="request_changes"
          label="[C]変更要求"
          variant="warning"
          onClick={() => handleDecision('request_changes')}
          disabled={isSubmitting}
        />

        <ActionButton
          action="defer"
          label="[D]保留する"
          variant="secondary"
          onClick={() => handleDecision('defer')}
          disabled={isSubmitting}
        />
      </div>

      {/* コメント入力 */}
      <div>
        <label htmlFor="comment" className="block text-sm font-medium mb-2">
          コメント (任意)
        </label>
        <textarea
          id="comment"
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="判定理由やフィードバックを記入..."
          rows={4}
          className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* 操作ガイド */}
      <OperationGuide />
    </Card>
  );
}
```

## 📚 カスタムフック仕様

### useApprovalReview
```tsx
export function useApprovalReview(revisionId: string) {
  const [state, setState] = useState<{
    revision: RevisionWithNames | null;
    diff: RevisionDiff | null;
    loading: boolean;
    error: string | null;
  }>({
    revision: null,
    diff: null,
    loading: true,
    error: null,
  });

  // データ取得 (並列実行)
  useEffect(() => {
    const fetchData = async () => {
      try {
        setState(prev => ({ ...prev, loading: true, error: null }));

        const [revisionData, diffData] = await Promise.all([
          apiClient.getRevision(revisionId),
          apiClient.getRevisionDiff(revisionId),
        ]);

        setState({
          revision: revisionData,
          diff: diffData,
          loading: false,
          error: null,
        });
      } catch (error) {
        setState(prev => ({
          ...prev,
          loading: false,
          error: error.message || '読み込みエラー',
        }));
      }
    };

    fetchData();
  }, [revisionId]);

  // 判定送信
  const submitDecision = async (decision: ApprovalDecision) => {
    try {
      await apiClient.submitDecision(revisionId, decision);
      // 成功時の処理 (通知、ナビゲーション等)
    } catch (error) {
      // エラーハンドリング
      throw error;
    }
  };

  return {
    ...state,
    submitDecision,
  };
}
```

### useSidebar
```tsx
export function useSidebar() {
  const [isCollapsed, setIsCollapsed] = useState(() => {
    // ローカルストレージから設定を復元
    if (typeof window !== 'undefined') {
      return localStorage.getItem('sidebar-collapsed') === 'true';
    }
    return false;
  });

  // 設定をローカルストレージに保存
  useEffect(() => {
    localStorage.setItem('sidebar-collapsed', String(isCollapsed));
  }, [isCollapsed]);

  // モバイル画面では自動的に折りたたみ
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) {
        setIsCollapsed(true);
      }
    };

    window.addEventListener('resize', handleResize);
    handleResize(); // 初回実行

    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return [isCollapsed, setIsCollapsed] as const;
}
```

### useApprovalQueue
```tsx
export function useApprovalQueue() {
  const [queue, setQueue] = useState<ApprovalQueueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [pendingCount, setPendingCount] = useState(0);

  const fetchQueue = useCallback(async () => {
    try {
      setLoading(true);
      const data = await apiClient.getApprovalQueue();
      setQueue(data.items);
      setPendingCount(data.pending_count);
    } catch (error) {
      console.error('Failed to fetch approval queue:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchQueue();

    // 30秒ごとに自動更新
    const interval = setInterval(fetchQueue, 30000);
    return () => clearInterval(interval);
  }, [fetchQueue]);

  return {
    queue,
    loading,
    pendingCount,
    refetch: fetchQueue,
  };
}
```

## 🎨 共通UIコンポーネント

### ActionButton (判定ボタン)
```tsx
interface ActionButtonProps {
  action: ApprovalDecision['action'];
  label: string;
  variant: 'success' | 'danger' | 'warning' | 'secondary';
  onClick: () => void;
  disabled?: boolean;
}

export function ActionButton({ action, label, variant, onClick, disabled }: ActionButtonProps) {
  const variants = {
    success: 'bg-green-600 hover:bg-green-700 text-white',
    danger: 'bg-red-600 hover:bg-red-700 text-white',
    warning: 'bg-yellow-600 hover:bg-yellow-700 text-white',
    secondary: 'bg-gray-600 hover:bg-gray-700 text-white',
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={clsx(
        'w-full py-3 px-6 rounded-md font-medium transition-colors',
        'focus:ring-2 focus:ring-offset-2',
        variants[variant],
        disabled && 'opacity-50 cursor-not-allowed'
      )}
      aria-label={`このメンテナンス提案を${action}する`}
    >
      {disabled ? <LoadingSpinner size="sm" /> : label}
    </button>
  );
}
```

## 🔄 状態管理パターン

### Context Provider構成
```tsx
// contexts/AuthContext.tsx
export const AuthProvider = ({ children }) => {
  // JWT認証状態管理
};

// contexts/ApprovalQueueContext.tsx
export const ApprovalQueueProvider = ({ children }) => {
  // 承認キューの共有状態
  // 承認完了時の自動更新
};

// Root Layout での Provider Nesting
export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <AuthProvider>
          <ApprovalQueueProvider>
            {children}
          </ApprovalQueueProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
```

## 🚦 エラーバウンダリー

```tsx
// components/common/ErrorBoundary.tsx
interface ErrorBoundaryProps {
  error: Error;
  reset?: () => void;
}

export function ErrorBoundary({ error, reset }: ErrorBoundaryProps) {
  return (
    <Card className="p-6 text-center">
      <div className="text-red-600 mb-4">
        <ExclamationCircleIcon className="w-12 h-12 mx-auto" />
      </div>
      <h3 className="text-lg font-medium mb-2">エラーが発生しました</h3>
      <p className="text-gray-600 mb-4">{error.message}</p>
      {reset && (
        <Button onClick={reset} variant="primary">
          再試行
        </Button>
      )}
    </Card>
  );
}
```