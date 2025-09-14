# KSAP フロントエンド 技術仕様

## 🛠️ 技術スタック詳細

### コア技術
```json
{
  "framework": {
    "nextjs": "15.5.3",
    "react": "19.1.0",
    "typescript": "^5.0.0"
  },
  "styling": {
    "tailwindcss": "^4.0.0",
    "@tailwindcss/postcss": "^4.0.0"
  },
  "development": {
    "eslint": "^9.0.0",
    "eslint-config-next": "15.5.3",
    "@eslint/eslintrc": "^3.0.0"
  },
  "additional": {
    "react-diff-viewer-continued": "^3.3.0",
    "clsx": "^2.1.0"
  }
}
```

### Next.js 15 設定
```typescript
// next.config.ts
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  // Turbopack for development
  experimental: {
    turbo: {
      rules: {
        '*.svg': {
          loaders: ['@svgr/webpack'],
          as: '*.js',
        },
      },
    },
  },

  // TypeScript configuration
  typescript: {
    tsconfigPath: './tsconfig.json',
  },

  // Environment variables
  env: {
    API_BASE_URL: process.env.API_BASE_URL || 'http://localhost:8000/api/v1',
    JWT_SECRET_KEY: process.env.JWT_SECRET_KEY || 'dev-secret-key',
  },

  // Build optimization
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },

  // Headers for security
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ];
  },
};

export default nextConfig;
```

### TypeScript 設定
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "es6"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"],
      "@/components/*": ["./components/*"],
      "@/lib/*": ["./lib/*"],
      "@/hooks/*": ["./hooks/*"],
      "@/types/*": ["./types/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

## 🏗️ 状態管理アーキテクチャ

### React Context パターン
```typescript
// contexts/AuthContext.tsx
interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<{
    user: User | null;
    token: string | null;
    isLoading: boolean;
  }>({
    user: null,
    token: null,
    isLoading: true,
  });

  // JWT自動更新
  useEffect(() => {
    const token = localStorage.getItem('ksap_token');
    if (token) {
      validateAndRefreshToken(token);
    } else {
      setState(prev => ({ ...prev, isLoading: false }));
    }
  }, []);

  const login = async (credentials: LoginCredentials) => {
    const response = await api.auth.login(credentials);
    const userData = await api.auth.getCurrentUser();

    setState({
      user: userData,
      token: response.access_token,
      isLoading: false,
    });

    localStorage.setItem('ksap_token', response.access_token);
    api.setToken(response.access_token);
  };

  const logout = async () => {
    await api.auth.logout();
    setState({ user: null, token: null, isLoading: false });
    localStorage.removeItem('ksap_token');
    api.clearToken();
  };

  return (
    <AuthContext.Provider value={{
      ...state,
      isAuthenticated: !!state.user && !!state.token,
      login,
      logout,
      refreshToken: () => validateAndRefreshToken(state.token),
    }}>
      {children}
    </AuthContext.Provider>
  );
}
```

### 承認キュー管理 Context
```typescript
// contexts/ApprovalQueueContext.tsx
interface ApprovalQueueContextType {
  queue: RevisionWithNames[];
  currentIndex: number;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  navigateToNext: () => string | null;
  navigateToPrevious: () => string | null;
  markAsProcessed: (revisionId: string) => void;
}

export function ApprovalQueueProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<{
    queue: RevisionWithNames[];
    currentIndex: number;
    loading: boolean;
    error: string | null;
  }>({
    queue: [],
    currentIndex: 0,
    loading: true,
    error: null,
  });

  const refresh = async () => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      const queue = await api.approval.getApprovalQueue();
      setState(prev => ({ ...prev, queue, loading: false }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'キューの取得に失敗',
      }));
    }
  };

  const navigateToNext = (): string | null => {
    const nextIndex = state.currentIndex + 1;
    if (nextIndex < state.queue.length) {
      setState(prev => ({ ...prev, currentIndex: nextIndex }));
      return state.queue[nextIndex].revision_id;
    }
    return null;
  };

  const navigateToPrevious = (): string | null => {
    const prevIndex = state.currentIndex - 1;
    if (prevIndex >= 0) {
      setState(prev => ({ ...prev, currentIndex: prevIndex }));
      return state.queue[prevIndex].revision_id;
    }
    return null;
  };

  const markAsProcessed = (revisionId: string) => {
    setState(prev => ({
      ...prev,
      queue: prev.queue.filter(item => item.revision_id !== revisionId),
    }));
  };

  return (
    <ApprovalQueueContext.Provider value={{
      ...state,
      refresh,
      navigateToNext,
      navigateToPrevious,
      markAsProcessed,
    }}>
      {children}
    </ApprovalQueueContext.Provider>
  );
}
```

## ⚡ パフォーマンス最適化

### コードスプリッティング
```typescript
// Dynamic imports for non-critical components
const AdminPanel = dynamic(() => import('@/components/admin/AdminPanel'), {
  ssr: false,
  loading: () => <LoadingSpinner />,
});

const DiffViewer = dynamic(() => import('@/components/approvals/DiffViewer'), {
  ssr: false,
  loading: () => <DiffSkeleton />,
});

// Route-level code splitting
const ProposalCreation = lazy(() => import('@/components/proposals/ProposalCreation'));
```

### メモ化戦略
```typescript
// hooks/useApprovalReview.ts (最適化版)
export function useApprovalReview(revisionId: string) {
  // データのメモ化
  const revisionData = useMemo(() => {
    return revisionCache.get(revisionId);
  }, [revisionId]);

  // API呼び出しの最適化
  const { data: revision, error: revisionError } = useSWR(
    `/revisions/${revisionId}`,
    () => api.approval.getRevision(revisionId),
    {
      revalidateOnFocus: false,
      dedupingInterval: 5000,
    }
  );

  // 差分データの並列取得
  const { data: diff, error: diffError } = useSWR(
    `/diffs/${revisionId}`,
    () => api.approval.getRevisionDiff(revisionId),
    {
      revalidateOnFocus: false,
      dedupingInterval: 5000,
    }
  );

  // 判定送信の最適化
  const submitDecision = useCallback(async (decision: ApprovalDecision) => {
    // 楽観的更新
    mutate(`/revisions/${revisionId}`,
      { ...revision, status: decision.action === 'approve' ? 'approved' : 'rejected' },
      false
    );

    try {
      await api.approval.submitDecision(revisionId, decision);
      // 成功時にキューを更新
      mutate('/approvals/queue');
    } catch (error) {
      // エラー時に元の状態に戻す
      mutate(`/revisions/${revisionId}`);
      throw error;
    }
  }, [revisionId, revision]);

  return {
    revision,
    diff,
    loading: !revision || !diff,
    error: revisionError || diffError,
    submitDecision,
  };
}
```

### 仮想スクロール (大量データ対応)
```typescript
// components/approvals/VirtualizedQueue.tsx (将来拡張用)
import { FixedSizeList as List } from 'react-window';

interface VirtualizedQueueProps {
  items: RevisionWithNames[];
  onItemClick: (item: RevisionWithNames) => void;
}

export function VirtualizedQueue({ items, onItemClick }: VirtualizedQueueProps) {
  const Row = ({ index, style }: { index: number; style: CSSProperties }) => (
    <div style={style}>
      <QueueItem
        item={items[index]}
        onClick={() => onItemClick(items[index])}
      />
    </div>
  );

  return (
    <List
      height={600}
      itemCount={items.length}
      itemSize={80}
      width="100%"
    >
      {Row}
    </List>
  );
}
```

## 🚦 エラーハンドリング戦略

### グローバルエラーバウンダリー
```typescript
// components/ErrorBoundary.tsx
interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class GlobalErrorBoundary extends Component<
  PropsWithChildren<{}>,
  ErrorBoundaryState
> {
  constructor(props: PropsWithChildren<{}>) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error, errorInfo: null };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ error, errorInfo });

    // エラーレポーティング (本番環境)
    if (process.env.NODE_ENV === 'production') {
      this.reportError(error, errorInfo);
    }
  }

  private reportError(error: Error, errorInfo: ErrorInfo) {
    // エラーレポーティングサービスに送信
    console.error('Global Error:', error, errorInfo);
  }

  private handleRetry = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
            <div className="flex items-center mb-4">
              <ExclamationTriangleIcon className="h-8 w-8 text-red-500 mr-3" />
              <h1 className="text-xl font-semibold text-gray-900">
                システムエラー
              </h1>
            </div>

            <p className="text-gray-600 mb-6">
              予期しないエラーが発生しました。ページを再読み込みして再試行してください。
            </p>

            <div className="flex space-x-4">
              <button
                onClick={this.handleRetry}
                className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
              >
                再試行
              </button>
              <button
                onClick={() => window.location.reload()}
                className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700"
              >
                ページ再読み込み
              </button>
            </div>

            {process.env.NODE_ENV === 'development' && (
              <details className="mt-6">
                <summary className="cursor-pointer text-sm text-gray-500">
                  エラー詳細 (開発環境のみ)
                </summary>
                <pre className="mt-2 text-xs bg-gray-100 p-2 rounded overflow-auto">
                  {this.state.error?.stack}
                </pre>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### ネットワークエラー処理
```typescript
// utils/error-handling.ts
export class ErrorHandler {
  static async handleApiError(error: unknown): Promise<never> {
    if (error instanceof ApiError) {
      switch (error.status) {
        case 401:
          // 認証エラー: ログインページへリダイレクト
          window.location.href = '/login';
          throw error;

        case 403:
          // 権限エラー: エラーメッセージを表示
          toast.error('この操作を実行する権限がありません');
          throw error;

        case 404:
          // リソース未発見: 適切なエラーページへ
          throw new Error('要求されたリソースが見つかりません');

        case 422:
          // バリデーションエラー: フィールドエラーを表示
          if (error instanceof ValidationError) {
            this.handleValidationError(error.details);
          }
          throw error;

        case 500:
          // サーバーエラー: 一般的なエラーメッセージ
          toast.error('サーバーでエラーが発生しました。しばらくしてから再試行してください');
          throw error;

        default:
          toast.error(error.message || '不明なエラーが発生しました');
          throw error;
      }
    }

    // ネットワークエラー等
    if (error instanceof TypeError && error.message.includes('fetch')) {
      toast.error('ネットワーク接続を確認してください');
      throw new Error('ネットワークエラー');
    }

    // その他のエラー
    toast.error('予期しないエラーが発生しました');
    throw error;
  }

  private static handleValidationError(details: any) {
    if (Array.isArray(details)) {
      details.forEach(detail => {
        toast.error(`${detail.field}: ${detail.message}`);
      });
    } else {
      toast.error('入力内容に問題があります');
    }
  }
}
```

## 🔐 セキュリティ対策

### JWT セキュリティ
```typescript
// utils/jwt-security.ts
export class JWTManager {
  private static readonly TOKEN_KEY = 'ksap_token';
  private static readonly REFRESH_THRESHOLD = 5 * 60 * 1000; // 5分前

  static setToken(token: string): void {
    // HttpOnly cookieへの保存 (セキュア)
    document.cookie = `${this.TOKEN_KEY}=${token}; secure; samesite=strict; max-age=604800`; // 7日

    // localStorage は fallback のみ
    localStorage.setItem(this.TOKEN_KEY, token);
  }

  static getToken(): string | null {
    // Cookie優先、fallback でlocalStorage
    const cookieToken = this.getTokenFromCookie();
    if (cookieToken) return cookieToken;

    return localStorage.getItem(this.TOKEN_KEY);
  }

  static clearToken(): void {
    document.cookie = `${this.TOKEN_KEY}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
    localStorage.removeItem(this.TOKEN_KEY);
  }

  private static getTokenFromCookie(): string | null {
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === this.TOKEN_KEY) {
        return value;
      }
    }
    return null;
  }

  static isTokenExpiringSoon(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const exp = payload.exp * 1000; // Convert to milliseconds
      return Date.now() + this.REFRESH_THRESHOLD > exp;
    } catch {
      return true; // Invalid token
    }
  }

  // XSS対策: script実行前のtoken検証
  static validateTokenIntegrity(token: string): boolean {
    const parts = token.split('.');
    if (parts.length !== 3) return false;

    try {
      const payload = JSON.parse(atob(parts[1]));
      return typeof payload.sub === 'string' && typeof payload.exp === 'number';
    } catch {
      return false;
    }
  }
}
```

### CSRF対策
```typescript
// utils/csrf-protection.ts
export class CSRFProtection {
  private static readonly CSRF_TOKEN_KEY = 'ksap_csrf_token';

  static generateCSRFToken(): string {
    const token = crypto.randomUUID();
    sessionStorage.setItem(this.CSRF_TOKEN_KEY, token);
    return token;
  }

  static getCSRFToken(): string | null {
    return sessionStorage.getItem(this.CSRF_TOKEN_KEY);
  }

  static validateCSRFToken(receivedToken: string): boolean {
    const storedToken = this.getCSRFToken();
    return storedToken === receivedToken;
  }

  // APIリクエストにCSRFトークンを自動付与
  static addCSRFHeader(headers: HeadersInit = {}): HeadersInit {
    const token = this.getCSRFToken();
    if (token) {
      return {
        ...headers,
        'X-CSRF-Token': token,
      };
    }
    return headers;
  }
}
```

## 🧪 テスト戦略

### Unit Testing (Jest + React Testing Library)
```typescript
// __tests__/components/ApprovalActions.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ApprovalActions } from '@/components/approvals/ApprovalActions';

const mockOnDecision = jest.fn();

describe('ApprovalActions', () => {
  beforeEach(() => {
    mockOnDecision.mockClear();
  });

  it('should render all action buttons', () => {
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

  it('should call onDecision with correct parameters when approve button is clicked', async () => {
    render(
      <ApprovalActions
        revisionId="test-id"
        onDecision={mockOnDecision}
      />
    );

    const approveButton = screen.getByRole('button', { name: /承認/i });
    fireEvent.click(approveButton);

    await waitFor(() => {
      expect(mockOnDecision).toHaveBeenCalledWith({
        action: 'approve',
        comment: undefined
      });
    });
  });

  it('should include comment when provided', async () => {
    render(
      <ApprovalActions
        revisionId="test-id"
        onDecision={mockOnDecision}
      />
    );

    const commentInput = screen.getByRole('textbox', { name: /コメント/i });
    const approveButton = screen.getByRole('button', { name: /承認/i });

    fireEvent.change(commentInput, { target: { value: 'テストコメント' } });
    fireEvent.click(approveButton);

    await waitFor(() => {
      expect(mockOnDecision).toHaveBeenCalledWith({
        action: 'approve',
        comment: 'テストコメント'
      });
    });
  });
});
```

### Integration Testing
```typescript
// __tests__/integration/approval-flow.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { server } from '__mocks__/server';
import { ApprovalReviewPage } from '@/app/approvals/review/[id]/page';

describe('Approval Flow Integration', () => {
  beforeAll(() => server.listen());
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());

  it('should complete full approval workflow', async () => {
    render(<ApprovalReviewPage params={{ id: 'test-revision-id' }} />);

    // データ読み込み待機
    await waitFor(() => {
      expect(screen.getByText('テスト記事タイトル')).toBeInTheDocument();
    });

    // 差分表示確認
    expect(screen.getByText('変更内容')).toBeInTheDocument();

    // 承認処理
    const approveButton = screen.getByRole('button', { name: /承認/i });
    fireEvent.click(approveButton);

    // 成功メッセージ確認
    await waitFor(() => {
      expect(screen.getByText('判定完了')).toBeInTheDocument();
    });
  });
});
```

### Performance Testing
```typescript
// __tests__/performance/rendering.test.tsx
import { render } from '@testing-library/react';
import { performance } from 'perf_hooks';
import { ApprovalReviewPage } from '@/app/approvals/review/[id]/page';

describe('Performance Tests', () => {
  it('should render approval review page within acceptable time', async () => {
    const startTime = performance.now();

    render(<ApprovalReviewPage params={{ id: 'test-id' }} />);

    const endTime = performance.now();
    const renderTime = endTime - startTime;

    // 100ms以内でのレンダリングを期待
    expect(renderTime).toBeLessThan(100);
  });

  it('should handle large diff data efficiently', async () => {
    const largeDiff = {
      revision_id: 'test',
      field_diffs: Array(1000).fill({
        field_name: 'test_field',
        field_label: 'テストフィールド',
        change_type: 'modified',
        old_value: 'old'.repeat(100),
        new_value: 'new'.repeat(100),
        is_critical: false,
      }),
      total_changes: 1000,
      critical_changes: 10,
      impact_level: 'high' as const,
    };

    const startTime = performance.now();

    render(<DiffViewer diff={largeDiff} />);

    const endTime = performance.now();
    const renderTime = endTime - startTime;

    // 大量データでも200ms以内
    expect(renderTime).toBeLessThan(200);
  });
});
```

## 📦 ビルド・デプロイ設定

### 本番ビルド最適化
```javascript
// next.config.js (本番環境)
const nextConfig = {
  // Bundle分析
  analyzeBundle: process.env.ANALYZE === 'true',

  // 圧縮設定
  compress: true,

  // 画像最適化
  images: {
    formats: ['image/webp', 'image/avif'],
    minimumCacheTTL: 60,
  },

  // PWA設定 (将来拡張)
  pwa: {
    dest: 'public',
    disable: process.env.NODE_ENV === 'development',
  },

  // セキュリティヘッダー
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'X-XSS-Protection', value: '1; mode=block' },
          {
            key: 'Content-Security-Policy',
            value: "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
          },
        ],
      },
    ];
  },
};
```

### Dockerfile (本番デプロイ用)
```dockerfile
# Multi-stage build for production
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production

FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT 3000

CMD ["node", "server.js"]
```