/**
 * エラーハンドリングutilities
 * API エラー、バリデーションエラー、アプリケーションエラーの処理
 */

import { ApiError } from '@/types/api';
import { ZodError } from 'zod';

// エラータイプの定義
export type AppError = {
  type: 'api' | 'validation' | 'network' | 'auth' | 'permission' | 'unknown';
  message: string;
  code?: string;
  field?: string;
  statusCode?: number;
  timestamp: string;
};

// HTTPステータスコードとエラータイプのマッピング
const STATUS_ERROR_TYPE_MAP: Record<number, AppError['type']> = {
  400: 'validation',
  401: 'auth',
  403: 'permission',
  404: 'api',
  422: 'validation',
  500: 'api',
};

// エラーメッセージの日本語化マッピング
const ERROR_MESSAGE_MAP: Record<string, string> = {
  'Invalid credentials': 'ユーザー名またはパスワードが正しくありません',
  'User not found': 'ユーザーが見つかりません',
  'Access denied': 'アクセスが拒否されました',
  'Token expired': 'セッションが期限切れです。再度ログインしてください',
  'Invalid token': '認証情報が無効です。再度ログインしてください',
  'Network Error': 'ネットワークエラーが発生しました。接続を確認してください',
  'Request timeout': 'リクエストがタイムアウトしました',
  'Server unavailable': 'サーバーに接続できません',
  'Bad Request': '不正なリクエストです',
  'Forbidden': 'この操作を実行する権限がありません',
  'Not Found': 'リソースが見つかりません',
  'Internal Server Error': 'サーバー内部エラーが発生しました',
};

/**
 * Axiosエラーを統一形式に変換
 */
export function handleApiError(error: any): AppError {
  const timestamp = new Date().toISOString();

  // ネットワークエラー
  if (!error.response) {
    return {
      type: 'network',
      message: ERROR_MESSAGE_MAP['Network Error'],
      timestamp,
    };
  }

  const { status, data } = error.response;
  const errorType = STATUS_ERROR_TYPE_MAP[status] || 'unknown';

  // バックエンドからの詳細エラー
  if (data && typeof data === 'object') {
    const apiError = data as ApiError;
    
    // Pydanticバリデーションエラー（422）の場合
    if (status === 422 && typeof apiError.detail === 'object') {
      const fieldErrors = Object.entries(apiError.detail);
      if (fieldErrors.length > 0) {
        const [fieldName, messages] = fieldErrors[0];
        return {
          type: 'validation',
          message: Array.isArray(messages) ? messages[0] : String(messages),
          field: fieldName,
          statusCode: status,
          timestamp,
        };
      }
    }

    // 通常のAPIエラー
    const message = typeof apiError.detail === 'string' 
      ? ERROR_MESSAGE_MAP[apiError.detail] || apiError.detail
      : 'エラーが発生しました';

    return {
      type: errorType,
      message,
      code: apiError.error_code,
      statusCode: status,
      timestamp,
    };
  }

  // フォールバック
  const defaultMessage = ERROR_MESSAGE_MAP[error.message] || 
    STATUS_CODE_MESSAGES[status] || 
    '予期しないエラーが発生しました';

  return {
    type: errorType,
    message: defaultMessage,
    statusCode: status,
    timestamp,
  };
}

/**
 * Zodバリデーションエラーを統一形式に変換
 */
export function handleValidationError(error: ZodError): AppError {
  const firstIssue = error.issues[0];
  
  return {
    type: 'validation',
    message: firstIssue.message,
    field: firstIssue.path.join('.'),
    timestamp: new Date().toISOString(),
  };
}

/**
 * 一般的なJavaScriptエラーを統一形式に変換
 */
export function handleUnknownError(error: unknown): AppError {
  const timestamp = new Date().toISOString();

  if (error instanceof Error) {
    return {
      type: 'unknown',
      message: error.message || '予期しないエラーが発生しました',
      timestamp,
    };
  }

  return {
    type: 'unknown',
    message: '予期しないエラーが発生しました',
    timestamp,
  };
}

/**
 * エラーの重要度を判定
 */
export function getErrorSeverity(error: AppError): 'low' | 'medium' | 'high' | 'critical' {
  switch (error.type) {
    case 'network':
    case 'api':
      return error.statusCode && error.statusCode >= 500 ? 'critical' : 'high';
    case 'auth':
      return 'high';
    case 'permission':
      return 'medium';
    case 'validation':
      return 'low';
    default:
      return 'medium';
  }
}

/**
 * エラーの表示色を取得
 */
export function getErrorColor(error: AppError): string {
  const severity = getErrorSeverity(error);
  const colorMap = {
    low: 'text-yellow-600 bg-yellow-50 border-yellow-200',
    medium: 'text-orange-600 bg-orange-50 border-orange-200',
    high: 'text-red-600 bg-red-50 border-red-200',
    critical: 'text-red-800 bg-red-100 border-red-300',
  };
  return colorMap[severity];
}

/**
 * エラーログを出力
 */
export function logError(error: AppError, context?: string): void {
  const logLevel = getErrorSeverity(error) === 'critical' ? 'error' : 'warn';
  const logData = {
    ...error,
    context,
    userAgent: typeof window !== 'undefined' ? window.navigator.userAgent : 'server',
    url: typeof window !== 'undefined' ? window.location.href : 'unknown',
  };

  console[logLevel]('Application Error:', logData);

  // 本番環境では外部ログサービスに送信
  if (process.env.NODE_ENV === 'production' && getErrorSeverity(error) === 'critical') {
    // TODO: 外部ログサービス（Sentry、LogRocket等）への送信実装
  }
}

/**
 * HTTPステータスコードのデフォルトメッセージ
 */
const STATUS_CODE_MESSAGES: Record<number, string> = {
  400: '不正なリクエストです',
  401: '認証が必要です',
  403: 'この操作を実行する権限がありません',
  404: 'リソースが見つかりません',
  422: '入力データに問題があります',
  429: 'リクエスト回数が制限を超えました',
  500: 'サーバー内部エラーが発生しました',
  502: 'サーバーに接続できません',
  503: 'サービスが一時的に利用できません',
  504: 'リクエストがタイムアウトしました',
};

/**
 * リトライ可能なエラーかどうかを判定
 */
export function isRetryableError(error: AppError): boolean {
  if (error.type === 'network') return true;
  if (error.statusCode && [502, 503, 504, 408].includes(error.statusCode)) return true;
  return false;
}

/**
 * ユーザーに表示すべきエラーかどうかを判定
 */
export function shouldDisplayError(error: AppError): boolean {
  // 認証エラーや権限エラーは表示しない（別途ハンドリング）
  return !['auth'].includes(error.type);
}

/**
 * エラー用のトースト通知メッセージを生成
 */
export function getToastMessage(error: AppError): { title: string; description: string } {
  const titles = {
    validation: '入力エラー',
    api: 'API エラー',
    network: '接続エラー',
    auth: '認証エラー',
    permission: '権限エラー',
    unknown: 'エラー',
  };

  return {
    title: titles[error.type],
    description: error.message,
  };
}