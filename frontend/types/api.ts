/**
 * API関連の型定義
 * レスポンス、リクエスト、エラーハンドリング用
 */

// 基本的なAPIレスポンス
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  success: boolean;
}

// ページネーション付きレスポンス
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// エラーレスポンス
export interface ApiError {
  detail: string | { [key: string]: string[] };
  error_code?: string;
  timestamp?: string;
}

// 認証関連
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in?: number;
}

export interface TokenPayload {
  user_id: string;
  username: string;
  role: string;
  exp: number;
  iat: number;
}

// フィルター・ソートパラメータ
export interface QueryParams {
  skip?: number;
  limit?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface RevisionQueryParams extends QueryParams {
  status?: string;
  proposer_id?: string;
  approver_id?: string;
  target_article_id?: string;
}

export interface UserQueryParams extends QueryParams {
  role?: string;
  is_active?: boolean;
  approval_group_id?: string;
}

export interface ArticleQueryParams extends QueryParams {
  approval_group?: string;
  info_category?: string;
  importance?: boolean;
}

// 統計・ダッシュボード関連
export interface DashboardStats {
  total_revisions: number;
  pending_approvals: number;
  my_drafts: number;
  my_submitted: number;
  recent_activity_count: number;
}

export interface ApprovalQueueStats {
  total_pending: number;
  high_priority: number;
  overdue: number;
  average_processing_time: number;
}

// 差分表示関連
export interface FieldDiff {
  field_name: string;
  field_label: string;
  before_value: any;
  after_value: any;
  has_change: boolean;
}

export interface DiffResponse {
  revision_id: string;
  target_article_id: string;
  fields: FieldDiff[];
  summary: {
    total_fields: number;
    changed_fields: number;
    change_percentage: number;
  };
}

// システム情報
export interface SystemStatus {
  status: 'healthy' | 'degraded' | 'down';
  database: boolean;
  cache: boolean;
  external_apis: boolean;
  last_check: string;
}

// バルク操作
export interface BulkOperation<T = any> {
  items: T[];
  operation: 'update' | 'delete' | 'approve' | 'reject';
  reason?: string;
}

export interface BulkOperationResult {
  success_count: number;
  error_count: number;
  errors: Array<{
    item_id: string;
    error: string;
  }>;
}

// HTTP メソッド型
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

// API エンドポイント設定
export interface ApiEndpoint {
  method: HttpMethod;
  path: string;
  requiresAuth: boolean;
  role?: string[];
}