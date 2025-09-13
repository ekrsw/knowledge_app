# フロントエンド詳細設計書

## 1. 実装状況分析

### 1.1 現在の実装状況（2025年1月時点）

**✅ 完了済み（Phase 1-3.2）**:
- **基盤構築**: Next.js 15.4.6、TypeScript、API クライアント
- **型定義システム**: 全APIエンティティの型定義完了
- **認証システム**: JWT ベースの認証・認可システム完全実装
- **API接続テスト**: プロフェッショナルなテストツール実装済み
- **基本UIコンポーネント**: 汎用コンポーネント一式完成
- **データテーブル**: 高機能なデータテーブルコンポーネント実装済み

**🔄 Phase 3.3以降（未実装）**:
- 修正案管理機能（CRUD、ステータス操作）
- 承認ワークフロー（承認キュー、承認・却下）
- 差分表示機能（フィールド差分、統合ビューアー）
- ダッシュボード（概要表示、通知）

### 1.2 技術基盤の評価

**強み**:
- ✅ **最新技術スタック**: Next.js 15.4.6 + React 19.1.0
- ✅ **型安全性**: TypeScript完全対応、Zodバリデーション
- ✅ **認証基盤**: JWT + ロールベースアクセス制御
- ✅ **UI一貫性**: Tailwind CSS + 統一コンポーネント
- ✅ **開発効率**: API接続テストツール、開発用ユーティリティ

**今後強化すべき領域**:
- 🔄 **業務ロジック実装**: 修正案・承認フローの実装
- 🔄 **UX最適化**: ユーザビリティとパフォーマンス向上
- 🔄 **エラーハンドリング**: 統一されたエラー処理システム

## 2. コンポーネント設計詳細

### 2.1 修正案関連コンポーネント（未実装）

#### 2.1.1 RevisionList コンポーネント

**用途**: 修正案一覧表示  
**ファイルパス**: `/src/components/revision/RevisionList.tsx`

```typescript
interface RevisionListProps {
  // データソース
  revisions: Revision[];
  loading: boolean;
  error?: ApiError | null;
  
  // ページネーション
  pagination: {
    page: number;
    limit: number;
    total: number;
    onPageChange: (page: number) => void;
  };
  
  // フィルタリング・ソート
  filters: {
    status?: RevisionStatus[];
    approver?: string;
    proposer?: string;
    dateRange?: { start: Date; end: Date };
  };
  onFiltersChange: (filters: Partial<RevisionListProps['filters']>) => void;
  
  // ユーザー操作
  onRevisionClick: (revision: Revision) => void;
  onQuickApprove?: (revisionId: string) => void; // 承認者のみ
  onQuickReject?: (revisionId: string) => void;  // 承認者のみ
  
  // UI設定
  showQuickActions?: boolean; // 承認者向けクイックアクション
  compact?: boolean;          // コンパクト表示モード
}
```

**実装要件**:
- **混合アクセス制御**: 承認済み・提出中（全ユーザー）+ 自分の下書き・却下（作成者のみ）
- **リアルタイム更新**: ステータス変更時の自動リフレッシュ
- **パフォーマンス**: 仮想スクロール（1000件以上の場合）
- **アクセシビリティ**: キーボードナビゲーション、スクリーンリーダー対応

#### 2.1.2 RevisionForm コンポーネント

**用途**: 修正案作成・編集フォーム  
**ファイルパス**: `/src/components/revision/RevisionForm.tsx`

```typescript
interface RevisionFormProps {
  // データ
  revision?: Revision; // 編集時のみ
  targetArticle: Article;
  
  // 操作モード
  mode: 'create' | 'edit' | 'view';
  
  // コールバック
  onSubmit: (data: RevisionCreate | RevisionUpdate) => Promise<void>;
  onCancel: () => void;
  onDelete?: (revisionId: string) => Promise<void>; // 編集モードのみ
  
  // 状態
  loading: boolean;
  error?: ApiError | null;
  
  // 設定
  showPreview?: boolean;      // プレビュー表示
  autoSave?: boolean;         // 自動保存（下書き）
  validationMode?: 'onChange' | 'onBlur' | 'onSubmit';
}
```

**特徴的な実装**:
- **After-only設計**: 変更されたフィールドのみ送信
- **リアルタイムプレビュー**: 入力と同時に差分表示
- **承認者必須指定**: approver_id の選択必須
- **段階的バリデーション**: フィールド毎の即座フィードバック

#### 2.1.3 RevisionDetail コンポーネント

**用途**: 修正案詳細表示・操作  
**ファイルパス**: `/src/components/revision/RevisionDetail.tsx`

```typescript
interface RevisionDetailProps {
  revision: Revision;
  targetArticle: Article;
  
  // 権限制御
  currentUser: User;
  canEdit: boolean;
  canApprove: boolean;
  canDelete: boolean;
  
  // アクション
  onEdit?: () => void;
  onSubmit?: () => Promise<void>;       // draft → submitted
  onWithdraw?: () => Promise<void>;     // submitted → draft
  onApprove?: (comment?: string) => Promise<void>;
  onReject?: (comment: string) => Promise<void>;
  onDelete?: () => Promise<void>;
  
  // 表示設定
  showDiff?: boolean;         // 差分表示
  showHistory?: boolean;      // 履歴表示
  showComments?: boolean;     // コメント表示
}
```

**UX要件**:
- **ステータス別UI**: ステータスに応じたアクションボタン表示
- **権限制御**: ユーザーロールに基づく操作制限
- **確認ダイアログ**: 重要操作前の確認プロンプト
- **楽観的更新**: UI反応性向上のための先行表示

### 2.2 承認ワークフロー コンポーネント（未実装）

#### 2.2.1 ApprovalQueue コンポーネント

**用途**: 承認待ち案件の一覧と管理  
**ファイルパス**: `/src/components/approval/ApprovalQueue.tsx`

```typescript
interface ApprovalQueueProps {
  // データ
  approvals: Revision[];
  metrics: ApprovalMetrics;
  loading: boolean;
  
  // フィルタリング
  filters: {
    priority?: 'high' | 'medium' | 'low';
    age?: 'new' | 'old' | 'overdue';
    category?: string;
  };
  onFiltersChange: (filters: Partial<ApprovalQueueProps['filters']>) => void;
  
  // 一括操作
  selectedRevisions: string[];
  onSelectionChange: (revisionIds: string[]) => void;
  onBulkApprove: (revisionIds: string[], comment?: string) => Promise<void>;
  onBulkReject: (revisionIds: string[], comment: string) => Promise<void>;
  
  // 個別操作
  onRevisionClick: (revision: Revision) => void;
  onQuickDecision: (revisionId: string, decision: 'approve' | 'reject', comment?: string) => Promise<void>;
}
```

**機能要件**:
- **優先度表示**: 緊急度に基づく色分け・ソート
- **一括処理**: 複数案件の同時承認・却下
- **SLA管理**: 承認期限の視覚的表示
- **通知統合**: 新着案件のリアルタイム通知

#### 2.2.2 ApprovalForm コンポーネント

**用途**: 承認・却下の詳細フォーム  
**ファイルパス**: `/src/components/approval/ApprovalForm.tsx`

```typescript
interface ApprovalFormProps {
  revision: Revision;
  targetArticle: Article;
  
  // モード設定
  mode: 'approve' | 'reject' | 'view';
  
  // コールバック
  onSubmit: (decision: ApprovalDecision) => Promise<void>;
  onCancel: () => void;
  
  // UI設定
  showDiff: boolean;
  showComments: boolean;
  requiredComment?: boolean; // 却下時はコメント必須
}

interface ApprovalDecision {
  action: 'approve' | 'reject';
  comment?: string;
  conditions?: string[]; // 条件付き承認
  priority?: 'low' | 'medium' | 'high';
}
```

**UX設計**:
- **差分統合表示**: 承認判断のための明確な差分表示
- **テンプレート**: よく使用されるコメントテンプレート
- **段階的承認**: 条件付き承認のサポート
- **履歴表示**: 過去の承認履歴参照

### 2.3 差分表示コンポーネント（未実装）

#### 2.3.1 DiffViewer コンポーネント

**用途**: 統合差分ビューアー  
**ファイルパス**: `/src/components/diff/DiffViewer.tsx`

```typescript
interface DiffViewerProps {
  // データ
  revision: Revision;
  targetArticle: Article;
  fieldDiffs: Record<string, FieldDiff>;
  
  // 表示設定
  viewMode: 'side-by-side' | 'unified' | 'compact';
  showUnchanged?: boolean;
  highlightLevel?: 'none' | 'word' | 'character';
  
  // フィルタリング
  visibleFields?: string[];
  hideEmpty?: boolean;
  
  // インタラクション
  onFieldFocus?: (fieldName: string) => void;
  onToggleField?: (fieldName: string) => void;
}
```

**技術実装**:
- **react-diff-viewer**: テキスト差分の高度な表示
- **フィールド別表示**: 構造化データの差分表示
- **パフォーマンス最適化**: 大きなテキストの効率的レンダリング
- **カスタムハイライト**: 業務ルールに基づく重要度表示

#### 2.3.2 FieldDiff コンポーネント

**用途**: 個別フィールドの差分表示  
**ファイルパス**: `/src/components/diff/FieldDiff.tsx`

```typescript
interface FieldDiffProps {
  fieldName: string;
  fieldDiff: FieldDiff;
  
  // 表示設定
  layout: 'horizontal' | 'vertical';
  showLabels?: boolean;
  compact?: boolean;
  
  // カスタマイズ
  formatValue?: (value: unknown, fieldName: string) => React.ReactNode;
  highlightChanges?: boolean;
}

interface FieldDiff {
  field_name: string;
  current_value: unknown;
  proposed_value: unknown;
  change_type: 'added' | 'modified' | 'deleted' | 'unchanged';
  field_type: 'text' | 'date' | 'boolean' | 'select' | 'number';
}
```

**表示ロジック**:
- **型別レンダリング**: データ型に応じた最適な表示
- **変更タイプ表示**: 追加・修正・削除の視覚的区別
- **コンテキスト情報**: フィールドの業務的意味の説明

#### 2.3.3 ChangeSummary コンポーネント

**用途**: 変更内容のサマリー表示  
**ファイルパス**: `/src/components/diff/ChangeSummary.tsx`

```typescript
interface ChangeSummaryProps {
  revision: Revision;
  fieldDiffs: Record<string, FieldDiff>;
  
  // 表示設定
  format: 'list' | 'table' | 'timeline';
  groupBy?: 'type' | 'category' | 'importance';
  
  // インタラクション
  onFieldClick?: (fieldName: string) => void;
  expandable?: boolean;
}
```

**情報設計**:
- **変更統計**: 追加・修正・削除の件数
- **影響度分析**: 変更の業務的重要度
- **関連情報**: 変更理由と背景の表示

## 3. 技術的実装方針

### 3.1 Next.js 15.4.6 活用戦略

#### 3.1.1 App Router最適化

```typescript
// /src/app/(dashboard)/revisions/page.tsx
export default function RevisionsPage() {
  return <RevisionListContainer />;
}

// /src/app/(dashboard)/revisions/[id]/page.tsx
interface RevisionPageProps {
  params: { id: string };
}

export default function RevisionPage({ params }: RevisionPageProps) {
  return <RevisionDetailContainer revisionId={params.id} />;
}
```

**メリット**:
- **ファイルベースルーティング**: 直感的なURL構造
- **レイアウト共有**: 認証・ナビゲーションの自動適用
- **並列データ取得**: 複数APIの同時読み込み

#### 3.1.2 React 19.1.0新機能活用

```typescript
// React 19のuse()フックを活用したデータ取得
import { use } from 'react';

function RevisionDetail({ revisionPromise }: { revisionPromise: Promise<Revision> }) {
  const revision = use(revisionPromise);
  return <div>{revision.reason}</div>;
}

// Server Actionsを活用したフォーム送信
async function submitRevision(formData: FormData) {
  'use server';
  
  const revisionData = {
    reason: formData.get('reason'),
    after_title: formData.get('after_title'),
  };
  
  await apiClient.post('/revisions', revisionData);
}
```

### 3.2 Tailwind CSS 4.x + Shadcn/ui実装

#### 3.2.1 デザインシステム

```typescript
// /src/components/ui/theme.ts
export const theme = {
  colors: {
    primary: {
      50: '#eff6ff',
      500: '#3b82f6',
      900: '#1e3a8a',
    },
    status: {
      draft: '#64748b',      // グレー
      submitted: '#f59e0b',  // オレンジ
      approved: '#10b981',   // グリーン
      rejected: '#ef4444',   // レッド
      deleted: '#6b7280',    // ダークグレー
    },
  },
  components: {
    button: {
      base: 'px-4 py-2 rounded-lg font-medium transition-colors',
      variants: {
        primary: 'bg-blue-600 text-white hover:bg-blue-700',
        secondary: 'bg-gray-600 text-white hover:bg-gray-700',
        danger: 'bg-red-600 text-white hover:bg-red-700',
      },
    },
  },
};
```

#### 3.2.2 レスポンシブデザイン戦略

```css
/* モバイルファースト設計 */
.revision-list {
  @apply grid grid-cols-1 gap-4;
  
  /* タブレット */
  @apply md:grid-cols-2;
  
  /* デスクトップ */
  @apply lg:grid-cols-3;
  
  /* 大画面 */
  @apply xl:grid-cols-4;
}

/* コンテナクエリ対応 */
.revision-card {
  @apply container:w-full container:p-4;
  
  /* カードサイズに応じた適応的レイアウト */
  @apply container[200px]:text-sm;
  @apply container[400px]:text-base;
}
```

### 3.3 react-diff-viewer統合

#### 3.3.1 差分表示設定

```typescript
// /src/components/diff/TextDiffViewer.tsx
import ReactDiffViewer, { DiffMethod } from 'react-diff-viewer';

interface TextDiffViewerProps {
  oldValue: string;
  newValue: string;
  fieldName: string;
  language?: string;
}

export function TextDiffViewer({ oldValue, newValue, fieldName, language }: TextDiffViewerProps) {
  const diffStyles = {
    variables: {
      dark: {
        diffViewerBackground: '#1f2937',
        diffViewerColor: '#f9fafb',
        addedBackground: '#065f46',
        addedColor: '#d1fae5',
        removedBackground: '#7f1d1d',
        removedColor: '#fee2e2',
        wordAddedBackground: '#047857',
        wordRemovedBackground: '#991b1b',
        addedGutterBackground: '#064e3b',
        removedGutterBackground: '#7c2d12',
        gutterBackground: '#374151',
        gutterBackgroundDark: '#1f2937',
        highlightBackground: '#374151',
        highlightGutterBackground: '#4b5563',
      },
    },
  };

  return (
    <div className="diff-viewer-container">
      <ReactDiffViewer
        oldValue={oldValue}
        newValue={newValue}
        splitView={true}
        compareMethod={DiffMethod.WORDS}
        styles={diffStyles}
        showDiffOnly={false}
        useDarkTheme={true}
        leftTitle={`現在の${fieldName}`}
        rightTitle={`修正後の${fieldName}`}
        hideLineNumbers={false}
      />
    </div>
  );
}
```

### 3.4 JWT認証・ロールベースアクセス制御

#### 3.4.1 権限チェックシステム

```typescript
// /src/hooks/usePermissions.ts
interface PermissionConfig {
  revision: Revision;
  currentUser: User;
}

export function useRevisionPermissions({ revision, currentUser }: PermissionConfig) {
  const permissions = useMemo(() => {
    const isAdmin = currentUser.role === 'admin';
    const isProposer = revision.proposer_id === currentUser.id;
    const isApprover = revision.approver_id === currentUser.id;
    const isPublicRevision = ['submitted', 'approved'].includes(revision.status);
    
    return {
      canView: isAdmin || isProposer || isApprover || isPublicRevision,
      canEdit: isAdmin || (isProposer && revision.status === 'draft'),
      canSubmit: isAdmin || (isProposer && revision.status === 'draft'),
      canWithdraw: isAdmin || (isProposer && revision.status === 'submitted'),
      canApprove: isAdmin || (isApprover && revision.status === 'submitted'),
      canReject: isAdmin || (isApprover && revision.status === 'submitted'),
      canDelete: isAdmin || (isProposer && ['draft', 'rejected'].includes(revision.status)),
    };
  }, [revision, currentUser]);

  return permissions;
}
```

#### 3.4.2 認証ガードコンポーネント

```typescript
// /src/components/auth/PermissionGuard.tsx
interface PermissionGuardProps {
  children: React.ReactNode;
  requiredPermission: keyof ReturnType<typeof useRevisionPermissions>;
  revision: Revision;
  fallback?: React.ReactNode;
}

export function PermissionGuard({ 
  children, 
  requiredPermission, 
  revision, 
  fallback = null 
}: PermissionGuardProps) {
  const { user } = useAuth();
  const permissions = useRevisionPermissions({ revision, currentUser: user! });
  
  if (!permissions[requiredPermission]) {
    return <>{fallback}</>;
  }
  
  return <>{children}</>;
}

// 使用例
<PermissionGuard 
  requiredPermission="canApprove" 
  revision={revision}
  fallback={<div className="text-gray-500">承認権限がありません</div>}
>
  <ApprovalButtons revision={revision} />
</PermissionGuard>
```

## 4. 状態管理とデータフロー

### 4.1 React Query活用（推奨）

```typescript
// /src/hooks/api/useRevisions.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export function useRevisions(params: PaginationParams & FilterParams) {
  return useQuery({
    queryKey: ['revisions', params],
    queryFn: () => revisionAPI.getRevisions(params),
    staleTime: 30000, // 30秒
    refetchOnWindowFocus: true,
  });
}

export function useRevisionMutations() {
  const queryClient = useQueryClient();
  
  const createRevision = useMutation({
    mutationFn: revisionAPI.createRevision,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['revisions'] });
    },
  });
  
  const submitRevision = useMutation({
    mutationFn: ({ id, ...data }: { id: string } & RevisionUpdate) =>
      proposalAPI.submitProposal(id),
    onSuccess: (data) => {
      // 楽観的更新
      queryClient.setQueryData(['revisions', data.revision_id], data);
      queryClient.invalidateQueries({ queryKey: ['revisions'] });
    },
  });
  
  return { createRevision, submitRevision };
}
```

### 4.2 リアルタイム更新（WebSocket）

```typescript
// /src/hooks/useRealtimeRevisions.ts
export function useRealtimeRevisions() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  
  useEffect(() => {
    if (!user) return;
    
    const ws = new WebSocket(`${process.env.NEXT_PUBLIC_WS_URL}/revisions`);
    
    ws.onmessage = (event) => {
      const update = JSON.parse(event.data);
      
      if (update.type === 'revision_updated') {
        // リアルタイムでキャッシュを更新
        queryClient.setQueryData(
          ['revisions', update.revision_id], 
          update.revision
        );
        queryClient.invalidateQueries({ queryKey: ['revisions'] });
      }
    };
    
    return () => ws.close();
  }, [user, queryClient]);
}
```

## 5. パフォーマンス最適化

### 5.1 コード分割とLazy Loading

```typescript
// /src/app/(dashboard)/revisions/page.tsx
import { lazy, Suspense } from 'react';

const RevisionList = lazy(() => import('@/components/revision/RevisionList'));
const ApprovalQueue = lazy(() => import('@/components/approval/ApprovalQueue'));

export default function RevisionsPage() {
  return (
    <div>
      <Suspense fallback={<div>読み込み中...</div>}>
        <RevisionList />
      </Suspense>
      
      <Suspense fallback={<div>承認キュー読み込み中...</div>}>
        <ApprovalQueue />
      </Suspense>
    </div>
  );
}
```

### 5.2 仮想化とパフォーマンス

```typescript
// /src/components/revision/VirtualizedRevisionList.tsx
import { FixedSizeList as List } from 'react-window';

interface VirtualizedRevisionListProps {
  revisions: Revision[];
  height: number;
  itemHeight: number;
}

export function VirtualizedRevisionList({ 
  revisions, 
  height, 
  itemHeight 
}: VirtualizedRevisionListProps) {
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => (
    <div style={style}>
      <RevisionCard revision={revisions[index]} />
    </div>
  );
  
  return (
    <List
      height={height}
      itemCount={revisions.length}
      itemSize={itemHeight}
      width="100%"
    >
      {Row}
    </List>
  );
}
```

## 6. エラーハンドリングとUX

### 6.1 エラーバウンダリ

```typescript
// /src/components/error/ErrorBoundary.tsx
interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<
  React.PropsWithChildren<{}>,
  ErrorBoundaryState
> {
  constructor(props: React.PropsWithChildren<{}>) {
    super(props);
    this.state = { hasError: false };
  }
  
  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }
  
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>問題が発生しました</h2>
          <button onClick={() => window.location.reload()}>
            ページを再読み込み
          </button>
        </div>
      );
    }
    
    return this.props.children;
  }
}
```

### 6.2 楽観的更新

```typescript
// /src/hooks/useOptimisticRevisions.ts
export function useOptimisticRevisions() {
  const [revisions, setRevisions] = useState<Revision[]>([]);
  const { submitRevision } = useRevisionMutations();
  
  const optimisticSubmit = async (revisionId: string) => {
    // UIを即座に更新
    setRevisions(prev => 
      prev.map(r => 
        r.revision_id === revisionId 
          ? { ...r, status: 'submitted' as RevisionStatus }
          : r
      )
    );
    
    try {
      await submitRevision.mutateAsync(revisionId);
    } catch (error) {
      // エラー時は元に戻す
      setRevisions(prev => 
        prev.map(r => 
          r.revision_id === revisionId 
            ? { ...r, status: 'draft' as RevisionStatus }
            : r
        )
      );
      throw error;
    }
  };
  
  return { revisions, optimisticSubmit };
}
```

## 7. テスト戦略

### 7.1 コンポーネントテスト

```typescript
// /src/components/revision/__tests__/RevisionList.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RevisionList } from '../RevisionList';

describe('RevisionList', () => {
  let queryClient: QueryClient;
  
  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
  });
  
  it('renders revision list correctly', () => {
    const mockRevisions = [
      { revision_id: '1', status: 'draft', reason: 'Test revision' }
    ];
    
    render(
      <QueryClientProvider client={queryClient}>
        <RevisionList 
          revisions={mockRevisions}
          loading={false}
          onRevisionClick={jest.fn()}
        />
      </QueryClientProvider>
    );
    
    expect(screen.getByText('Test revision')).toBeInTheDocument();
  });
  
  it('handles revision click correctly', () => {
    const handleClick = jest.fn();
    const mockRevisions = [
      { revision_id: '1', status: 'draft', reason: 'Test revision' }
    ];
    
    render(
      <QueryClientProvider client={queryClient}>
        <RevisionList 
          revisions={mockRevisions}
          loading={false}
          onRevisionClick={handleClick}
        />
      </QueryClientProvider>
    );
    
    fireEvent.click(screen.getByText('Test revision'));
    expect(handleClick).toHaveBeenCalledWith(mockRevisions[0]);
  });
});
```

### 7.2 統合テスト

```typescript
// /src/__tests__/integration/revision-workflow.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { setupServer } from 'msw/node';
import { rest } from 'msw';

const server = setupServer(
  rest.post('/api/v1/revisions', (req, res, ctx) => {
    return res(ctx.json({ revision_id: '1', status: 'draft' }));
  }),
  rest.post('/api/v1/proposals/:id/submit', (req, res, ctx) => {
    return res(ctx.json({ revision_id: '1', status: 'submitted' }));
  })
);

describe('Revision Workflow Integration', () => {
  beforeAll(() => server.listen());
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());
  
  it('completes create-to-submit workflow', async () => {
    render(<RevisionWorkflowApp />);
    
    // 修正案作成
    fireEvent.click(screen.getByText('新規修正案'));
    fireEvent.change(screen.getByLabelText('修正理由'), {
      target: { value: 'テスト修正' }
    });
    fireEvent.click(screen.getByText('下書き保存'));
    
    await waitFor(() => {
      expect(screen.getByText('下書きを保存しました')).toBeInTheDocument();
    });
    
    // 修正案提出
    fireEvent.click(screen.getByText('提出'));
    
    await waitFor(() => {
      expect(screen.getByText('修正案を提出しました')).toBeInTheDocument();
    });
  });
});
```

## 8. 実装ロードマップ

### 8.1 Phase 4: 修正案管理機能（推定18時間）

**Week 1**:
- [ ] **Task 4.1**: RevisionList実装（6時間）
  - データテーブル統合
  - フィルタリング機能
  - ページネーション
  - 権限ベース表示
  
- [ ] **Task 4.2**: RevisionDetail実装（6時間）
  - 詳細表示UI
  - 権限ベースアクション
  - ステータス表示
  
- [ ] **Task 4.3**: RevisionForm基本実装（6時間）
  - フォームバリデーション
  - API連携
  - エラーハンドリング

**Week 2**:
- [ ] **Task 4.4**: RevisionForm全機能（6時間）
  - 全フィールド対応
  - プレビュー機能
  - 自動保存
  
- [ ] **Task 4.5**: ステータス操作（4時間）
  - 提出・撤回・削除
  - 確認ダイアログ
  - 楽観的更新

### 8.2 Phase 5: 承認ワークフロー（推定12時間）

**Week 3**:
- [ ] **Task 5.1**: ApprovalQueue実装（6時間）
  - 承認待ち一覧
  - 優先度表示
  - 一括操作UI
  
- [ ] **Task 5.2**: 承認・却下機能（6時間）
  - ApprovalForm実装
  - 決定処理
  - 通知連携

### 8.3 Phase 6: 差分表示機能（推定16時間）

**Week 4**:
- [ ] **Task 6.1**: 基本差分表示（8時間）
  - FieldDiff実装
  - DiffViewer基本機能
  - API連携
  
- [ ] **Task 6.2**: 高度差分表示（8時間）
  - react-diff-viewer統合
  - ChangeSummary実装
  - カスタムスタイリング

### 8.4 Phase 7-8: ダッシュボード・品質向上（推定12時間）

**Week 5**:
- [ ] **Task 7.1**: ダッシュボード（6時間）
  - 概要表示
  - 統計情報
  - クイックアクセス
  
- [ ] **Task 7.2**: 通知機能（3時間）
  - リアルタイム通知
  - 既読管理
  
- [ ] **Task 8.1-8.3**: 品質向上（3時間）
  - エラーハンドリング
  - パフォーマンス最適化
  - レスポンシブ対応

## 9. 結論

この詳細設計書は、現在の堅実な技術基盤（Phase 1-3.2完了）の上に、残りの業務機能を効率的に構築するための具体的な実装指針を提供しています。

**主要な成功要因**:
1. **既存基盤の活用**: 完成済みの認証・UI基盤の効果的活用
2. **段階的実装**: リスクを最小化する段階的な機能追加
3. **UX重視**: ユーザビリティを重視した実装
4. **技術的優位性**: 最新技術スタックの効果的活用

この設計に従って実装を進めることで、高品質で保守性の高いフロントエンドシステムの完成が期待できます。