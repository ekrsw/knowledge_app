/**
 * API共通の型定義
 */

/**
 * ページネーションパラメータ
 */
export interface PaginationParams {
  skip?: number;
  limit?: number;
}

/**
 * ソートパラメータ
 */
export interface SortParams {
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

/**
 * APIレスポンスの基本型
 */
export interface ApiResponse<T> {
  data: T;
  message?: string;
  timestamp?: string;
}

/**
 * ページネーション付きレスポンス
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
}

/**
 * APIエラーレスポンス
 */
export interface ApiError {
  detail: string;
  error_code?: string;
  timestamp?: string;
  validation_errors?: ValidationError[];
}

/**
 * バリデーションエラー
 */
export interface ValidationError {
  field: string;
  message: string;
  type: string;
}

/**
 * HTTPエラー
 */
export class HttpError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public error?: ApiError
  ) {
    super(error?.detail || statusText);
    this.name = 'HttpError';
  }
}

/**
 * 一括操作結果
 */
export interface BulkOperationResult {
  success_count: number;
  failure_count: number;
  total_count: number;
  failed_ids?: string[];
  errors?: Array<{
    id: string;
    error: string;
  }>;
}

/**
 * システム情報
 */
export interface SystemInfo {
  version: string;
  environment: string;
  debug: boolean;
  database_connected: boolean;
  redis_connected: boolean;
  uptime_seconds: number;
}

/**
 * ヘルスチェック
 */
export interface HealthCheck {
  status: 'healthy' | 'degraded' | 'unhealthy';
  checks: {
    database: boolean;
    redis: boolean;
    api: boolean;
  };
  timestamp: string;
}

/**
 * 統計情報の基本型
 */
export interface Statistics {
  period_start: string;
  period_end: string;
  generated_at: string;
}

/**
 * フィルタパラメータ
 */
export interface FilterParams {
  status?: string | string[];
  user_id?: string;
  approver_id?: string;
  approval_group_id?: string;
  article_id?: string;
  date_from?: string;
  date_to?: string;
  is_active?: boolean;
}

/**
 * 検索パラメータ
 */
export interface SearchParams {
  q?: string;  // Search query
  fields?: string[];  // Fields to search in
}