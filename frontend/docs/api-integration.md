# KSAP フロントエンド API統合仕様

## 🔌 API統合アーキテクチャ

### 基本方針
- **RESTful API**: FastAPI バックエンド (`http://localhost:8000/api/v1`)
- **認証方式**: JWT Bearer Token
- **エラーハンドリング**: 統一的なエラー処理と回復戦略
- **型安全性**: TypeScript完全対応

## 🏗️ APIクライアント設計

### 基本クライアント (lib/api.ts)
```typescript
interface ApiClientConfig {
  baseURL: string;
  timeout: number;
}

class ApiClient {
  private config: ApiClientConfig;
  private token: string | null = null;

  constructor(config: ApiClientConfig) {
    this.config = config;
    this.loadTokenFromStorage();
  }

  // JWT Token管理
  setToken(token: string): void {
    this.token = token;
    localStorage.setItem('ksap_token', token);
  }

  getToken(): string | null {
    return this.token || localStorage.getItem('ksap_token');
  }

  clearToken(): void {
    this.token = null;
    localStorage.removeItem('ksap_token');
  }

  private loadTokenFromStorage(): void {
    this.token = localStorage.getItem('ksap_token');
  }

  // 共通リクエスト処理
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.config.baseURL}${endpoint}`;
    const token = this.getToken();

    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
    };

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

      const response = await fetch(url, {
        ...config,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        await this.handleErrorResponse(response);
      }

      return await response.json();
    } catch (error) {
      throw this.transformError(error);
    }
  }

  // エラー処理
  private async handleErrorResponse(response: Response): Promise<never> {
    const errorBody = await response.json().catch(() => ({ detail: 'Unknown error' }));

    switch (response.status) {
      case 401:
        this.clearToken();
        window.location.href = '/login';
        throw new ApiError('認証が必要です', 401);
      case 403:
        throw new ApiError('アクセス権限がありません', 403);
      case 404:
        throw new ApiError('リソースが見つかりません', 404);
      case 422:
        throw new ValidationError('入力データが不正です', errorBody.detail);
      default:
        throw new ApiError(errorBody.detail || 'サーバーエラー', response.status);
    }
  }

  private transformError(error: any): Error {
    if (error.name === 'AbortError') {
      return new ApiError('リクエストがタイムアウトしました', 408);
    }
    if (error instanceof ApiError) {
      return error;
    }
    return new ApiError('ネットワークエラーが発生しました', 0);
  }
}

// カスタムエラークラス
class ApiError extends Error {
  constructor(public message: string, public status: number) {
    super(message);
    this.name = 'ApiError';
  }
}

class ValidationError extends ApiError {
  constructor(message: string, public details: any) {
    super(message, 422);
    this.name = 'ValidationError';
  }
}
```

### 認証API (lib/auth-api.ts)
```typescript
export class AuthApi {
  constructor(private client: ApiClient) {}

  // ログイン (JSON形式)
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    return this.client.request('/auth/login/json', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  // 現在のユーザー情報取得
  async getCurrentUser(): Promise<User> {
    return this.client.request('/auth/me');
  }

  // トークン検証
  async verifyToken(): Promise<TokenVerificationResponse> {
    return this.client.request('/auth/verify');
  }

  // ログアウト
  async logout(): Promise<LogoutResponse> {
    const response = await this.client.request('/auth/logout', {
      method: 'POST',
    });
    this.client.clearToken();
    return response;
  }

  // ユーザー登録
  async register(userData: UserRegistration): Promise<User> {
    return this.client.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }
}
```

### 承認API (lib/approval-api.ts) ⭐最重要
```typescript
export class ApprovalApi {
  constructor(private client: ApiClient) {}

  // 改訂取得 (基本情報)
  async getRevision(revisionId: string): Promise<RevisionWithNames> {
    return this.client.request(`/revisions/${revisionId}`);
  }

  // 差分取得
  async getRevisionDiff(revisionId: string): Promise<RevisionDiff> {
    return this.client.request(`/diffs/${revisionId}`);
  }

  // 並列データ取得 (最適化)
  async getRevisionWithDiff(revisionId: string): Promise<{
    revision: RevisionWithNames;
    diff: RevisionDiff;
  }> {
    const [revision, diff] = await Promise.all([
      this.getRevision(revisionId),
      this.getRevisionDiff(revisionId),
    ]);

    return { revision, diff };
  }

  // 承認判定送信
  async submitDecision(
    revisionId: string,
    decision: ApprovalDecision
  ): Promise<void> {
    return this.client.request(`/approvals/${revisionId}/decide`, {
      method: 'POST',
      body: JSON.stringify({
        action: decision.action,
        comment: decision.comment,
      }),
    });
  }

  // 承認キュー取得
  async getApprovalQueue(filters?: ApprovalQueueFilters): Promise<RevisionWithNames[]> {
    const params = new URLSearchParams();
    if (filters?.priority) params.append('priority', filters.priority);
    if (filters?.limit) params.append('limit', filters.limit.toString());

    const endpoint = params.toString()
      ? `/approvals/queue?${params}`
      : '/approvals/queue';

    return this.client.request(endpoint);
  }

  // 承認履歴取得
  async getApprovalHistory(): Promise<RevisionWithNames[]> {
    return this.client.request('/approvals/history');
  }

  // 承認可能性確認
  async canApproveRevision(revisionId: string): Promise<{ can_approve: boolean }> {
    return this.client.request(`/approvals/${revisionId}/can-approve`);
  }

  // ワークロード取得
  async getApprovalWorkload(): Promise<ApprovalWorkload> {
    return this.client.request('/approvals/workload');
  }

  // クイック承認アクション
  async quickAction(
    revisionId: string,
    action: 'approve' | 'reject'
  ): Promise<void> {
    return this.client.request(`/approvals/${revisionId}/quick-actions/${action}`, {
      method: 'POST',
    });
  }
}
```

### 提案API (lib/proposal-api.ts)
```typescript
export class ProposalApi {
  constructor(private client: ApiClient) {}

  // 自分の提案一覧
  async getMyProposals(params?: {
    status?: string;
    skip?: number;
    limit?: number;
  }): Promise<RevisionWithNames[]> {
    const searchParams = new URLSearchParams();
    if (params?.status) searchParams.append('status', params.status);
    if (params?.skip) searchParams.append('skip', params.skip.toString());
    if (params?.limit) searchParams.append('limit', params.limit.toString());

    const endpoint = searchParams.toString()
      ? `/proposals/my-proposals?${searchParams}`
      : '/proposals/my-proposals';

    return this.client.request(endpoint);
  }

  // 新規提案作成
  async createProposal(proposal: ProposalCreate): Promise<RevisionWithNames> {
    return this.client.request('/revisions/', {
      method: 'POST',
      body: JSON.stringify(proposal),
    });
  }

  // 提案更新
  async updateProposal(
    revisionId: string,
    proposal: ProposalUpdate
  ): Promise<RevisionWithNames> {
    return this.client.request(`/proposals/${revisionId}`, {
      method: 'PUT',
      body: JSON.stringify(proposal),
    });
  }

  // 提案提出
  async submitProposal(revisionId: string): Promise<void> {
    return this.client.request(`/proposals/${revisionId}/submit`, {
      method: 'POST',
    });
  }

  // 提案取り下げ
  async withdrawProposal(revisionId: string): Promise<void> {
    return this.client.request(`/proposals/${revisionId}/withdraw`, {
      method: 'POST',
    });
  }

  // 提案削除
  async deleteProposal(revisionId: string): Promise<void> {
    return this.client.request(`/proposals/${revisionId}`, {
      method: 'DELETE',
    });
  }

  // 提案統計
  async getProposalStatistics(userId?: string): Promise<ProposalStatistics> {
    const endpoint = userId
      ? `/proposals/statistics?user_id=${userId}`
      : '/proposals/statistics';

    return this.client.request(endpoint);
  }
}
```

## 📊 データ型定義 (lib/types.ts)

### API応答型
```typescript
// 認証関連
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: 'bearer';
}

export interface User {
  user_id: string;
  username: string;
  email: string;
  full_name: string;
  sweet_name: string;
  ctstage_name: string;
  role: 'user' | 'approver' | 'admin';
  is_active: boolean;
  approval_group_id?: string;
  created_at: string;
  updated_at: string;
}

export interface TokenVerificationResponse {
  valid: boolean;
  user: User;
  token_type: 'bearer';
}

// 改訂・提案関連
export interface RevisionWithNames {
  revision_id: string;
  article_number: string;
  reason: string;
  after_title: string;
  after_info_category: string;
  after_keywords: string;
  after_importance: boolean;
  after_publish_start: string;
  after_publish_end: string;
  after_target: string;
  after_question: string;
  after_answer: string;
  after_additional_comment: string;
  status: 'draft' | 'submitted' | 'approved' | 'rejected';
  processed_at: string | null;
  created_at: string;
  updated_at: string;
  proposer_name: string;
  approver_name: string | null;
}

export interface RevisionDiff {
  revision_id: string;
  target_article_id: string;
  proposer_name: string;
  reason: string;
  status: string;
  created_at: string;
  field_diffs: FieldDiff[];
  total_changes: number;
  critical_changes: number;
  change_categories: string[];
  impact_level: 'low' | 'medium' | 'high';
}

export interface FieldDiff {
  field_name: string;
  field_label: string;
  change_type: 'added' | 'modified' | 'removed';
  old_value: string | null;
  new_value: string | null;
  is_critical: boolean;
}

// 承認関連
export interface ApprovalDecision {
  action: 'approve' | 'reject' | 'request_changes' | 'defer';
  comment?: string;
}

export interface ApprovalQueueFilters {
  priority?: 'high' | 'medium' | 'low';
  limit?: number;
}

export interface ApprovalWorkload {
  pending_count: number;
  this_week_count: number;
  average_time_minutes: number;
  categories: Array<{
    category_name: string;
    count: number;
  }>;
}

// 提案作成・更新
export interface ProposalCreate {
  target_article_id: string;
  reason: string;
  approver_id: string;
  after_title?: string;
  after_info_category?: string;
  after_keywords?: string;
  after_importance?: boolean;
  after_publish_start?: string;
  after_publish_end?: string;
  after_target?: string;
  after_question?: string;
  after_answer?: string;
  after_additional_comment?: string;
}

export interface ProposalUpdate extends Partial<ProposalCreate> {}

export interface ProposalStatistics {
  total_proposals: number;
  by_status: Record<string, number>;
  this_month: number;
  approval_rate: number;
  average_processing_days: number;
}
```

## 🔄 データフェッチングパターン

### 基本的なデータ取得
```typescript
// hooks/useApiData.ts
export function useApiData<T>(
  fetchFn: () => Promise<T>,
  deps: any[] = []
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await fetchFn();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : '不明なエラー');
    } finally {
      setLoading(false);
    }
  }, deps);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { data, loading, error, refetch };
}
```

### 承認レビューデータの取得 (最適化版)
```typescript
// hooks/useApprovalReviewData.ts
export function useApprovalReviewData(revisionId: string) {
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

  useEffect(() => {
    let isCancelled = false;

    const fetchData = async () => {
      try {
        setState(prev => ({ ...prev, loading: true, error: null }));

        // 並列取得で高速化
        const { revision, diff } = await apiClient.approval.getRevisionWithDiff(revisionId);

        if (!isCancelled) {
          setState({
            revision,
            diff,
            loading: false,
            error: null,
          });
        }
      } catch (error) {
        if (!isCancelled) {
          setState(prev => ({
            ...prev,
            loading: false,
            error: error instanceof Error ? error.message : '読み込みエラー',
          }));
        }
      }
    };

    fetchData();

    return () => {
      isCancelled = true;
    };
  }, [revisionId]);

  return state;
}
```

## 🚦 エラーハンドリング戦略

### 自動リトライ機能
```typescript
// utils/retry.ts
export async function withRetry<T>(
  fn: () => Promise<T>,
  maxAttempts: number = 3,
  delayMs: number = 1000
): Promise<T> {
  let lastError: Error;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error('Unknown error');

      if (attempt === maxAttempts) {
        throw lastError;
      }

      // 指数バックオフでリトライ間隔を増加
      await new Promise(resolve =>
        setTimeout(resolve, delayMs * Math.pow(2, attempt - 1))
      );
    }
  }

  throw lastError!;
}

// 使用例
const revisionData = await withRetry(() =>
  apiClient.approval.getRevision(revisionId)
);
```

### オフライン対応
```typescript
// hooks/useOnlineStatus.ts
export function useOnlineStatus() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline;
}
```

## 🔧 APIクライアントインスタンス

### シングルトンパターン
```typescript
// lib/api-client.ts
const apiClient = new ApiClient({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 10000, // 10秒
});

export const api = {
  auth: new AuthApi(apiClient),
  approval: new ApprovalApi(apiClient),
  proposal: new ProposalApi(apiClient),
  user: new UserApi(apiClient),
  system: new SystemApi(apiClient),
  notification: new NotificationApi(apiClient),
};

export default api;
```

### 環境設定
```typescript
// lib/config.ts
export const API_CONFIG = {
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  timeout: parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '10000'),
  retryAttempts: parseInt(process.env.NEXT_PUBLIC_API_RETRY_ATTEMPTS || '3'),
};
```

## 🧪 API統合テスト戦略

### モックAPI (開発・テスト用)
```typescript
// lib/mock-api.ts (開発・テスト環境)
export class MockApprovalApi implements ApprovalApi {
  async getRevision(revisionId: string): Promise<RevisionWithNames> {
    // モックデータ返却
    return {
      revision_id: revisionId,
      article_number: 'ART001',
      reason: 'テスト用の提案理由です',
      after_title: 'テスト記事タイトル',
      // ... その他のモックデータ
    };
  }

  // その他のメソッドも実装
}

// 環境に応じたAPI選択
export const createApiClient = () => {
  if (process.env.NODE_ENV === 'test' || process.env.NEXT_PUBLIC_USE_MOCK_API) {
    return new MockApiClient();
  }
  return new RealApiClient();
};
```