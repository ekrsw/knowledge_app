/**
 * エラーハンドリング utilities
 */

import { ApiError, HttpError } from '@/types/api';

/**
 * API エラーを処理するカスタムエラークラス
 */
export class ApiRequestError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public apiError?: ApiError,
    public originalError?: Error
  ) {
    super(apiError?.detail || statusText || 'API request failed');
    this.name = 'ApiRequestError';
  }

  /**
   * エラーコードを取得
   */
  get errorCode(): string | undefined {
    return this.apiError?.error_code;
  }

  /**
   * バリデーションエラーを取得
   */
  get validationErrors() {
    return this.apiError?.validation_errors || [];
  }

  /**
   * ユーザー向けメッセージを取得
   */
  get userMessage(): string {
    if (this.apiError?.detail) {
      return this.apiError.detail;
    }
    
    // Standard HTTP status messages
    switch (this.status) {
      case 400:
        return '入力内容に問題があります。確認してください。';
      case 401:
        return 'ログインが必要です。';
      case 403:
        return '権限がありません。';
      case 404:
        return 'リソースが見つかりません。';
      case 409:
        return '競合が発生しました。再試行してください。';
      case 422:
        return '入力データの形式に問題があります。';
      case 429:
        return 'リクエストが多すぎます。しばらく待ってから再試行してください。';
      case 500:
        return 'サーバーエラーが発生しました。管理者に連絡してください。';
      case 502:
      case 503:
      case 504:
        return 'サービスが一時的に利用できません。しばらく待ってから再試行してください。';
      default:
        return 'エラーが発生しました。';
    }
  }

  /**
   * エラーが特定のタイプかチェック
   */
  isType(errorCode: string): boolean {
    return this.errorCode === errorCode;
  }

  /**
   * 認証エラーかチェック
   */
  get isAuthError(): boolean {
    return this.status === 401;
  }

  /**
   * 認可エラーかチェック
   */
  get isPermissionError(): boolean {
    return this.status === 403;
  }

  /**
   * バリデーションエラーかチェック
   */
  get isValidationError(): boolean {
    return this.status === 422 || (this.validationErrors && this.validationErrors.length > 0);
  }

  /**
   * ネットワークエラーかチェック
   */
  get isNetworkError(): boolean {
    return !this.status || this.status === 0;
  }

  /**
   * サーバーエラーかチェック
   */
  get isServerError(): boolean {
    return this.status >= 500;
  }
}

/**
 * ネットワークエラー用のカスタムクラス
 */
export class NetworkError extends Error {
  constructor(message = 'ネットワークエラーが発生しました') {
    super(message);
    this.name = 'NetworkError';
  }
}

/**
 * タイムアウトエラー用のカスタムクラス
 */
export class TimeoutError extends Error {
  constructor(message = 'リクエストがタイムアウトしました') {
    super(message);
    this.name = 'TimeoutError';
  }
}

/**
 * Fetch APIのレスポンスからAPIエラーを作成
 */
export async function createApiError(response: Response): Promise<ApiRequestError> {
  let apiError: ApiError | undefined;
  
  try {
    const responseText = await response.text();
    if (responseText) {
      apiError = JSON.parse(responseText);
    }
  } catch (e) {
    // JSON parse error - ignore
  }

  return new ApiRequestError(
    response.status,
    response.statusText,
    apiError
  );
}

/**
 * エラーをログに記録
 */
export function logError(error: Error, context?: string): void {
  const timestamp = new Date().toISOString();
  const prefix = context ? `[${context}]` : '';
  
  console.error(`${timestamp} ${prefix} ${error.name}: ${error.message}`);
  
  if (error instanceof ApiRequestError) {
    console.error('Status:', error.status);
    console.error('Error Code:', error.errorCode);
    console.error('Validation Errors:', error.validationErrors);
  }
  
  console.error('Stack:', error.stack);
}

/**
 * エラーハンドラーの型定義
 */
export type ErrorHandler = (error: Error) => void;

/**
 * 共通エラーハンドラー
 */
export function handleError(error: Error, context?: string): void {
  logError(error, context);
  
  // 開発モードでは詳細なエラー情報を表示
  if (process.env.NODE_ENV === 'development') {
    console.error('Detailed error info:', error);
  }
}

/**
 * 非同期関数のエラーを捕捉するラッパー
 */
export function withErrorHandling<T extends unknown[], R>(
  fn: (...args: T) => Promise<R>,
  errorHandler?: ErrorHandler
): (...args: T) => Promise<R> {
  return async (...args: T): Promise<R> => {
    try {
      return await fn(...args);
    } catch (error) {
      const err = error instanceof Error ? error : new Error(String(error));
      
      if (errorHandler) {
        errorHandler(err);
      } else {
        handleError(err, fn.name);
      }
      
      throw err;
    }
  };
}

/**
 * エラー境界で使用するエラー情報の取得
 */
export function getErrorInfo(error: Error): {
  message: string;
  userMessage: string;
  canRetry: boolean;
  shouldReload: boolean;
} {
  if (error instanceof ApiRequestError) {
    return {
      message: error.message,
      userMessage: error.userMessage,
      canRetry: !error.isPermissionError && !error.isValidationError,
      shouldReload: error.isAuthError
    };
  }
  
  if (error instanceof NetworkError || error instanceof TimeoutError) {
    return {
      message: error.message,
      userMessage: error.message,
      canRetry: true,
      shouldReload: false
    };
  }
  
  return {
    message: error.message,
    userMessage: '予期しないエラーが発生しました。',
    canRetry: true,
    shouldReload: false
  };
}

/**
 * エラーの種類を判定するヘルパー関数
 */
export function isApiError(error: unknown): error is ApiRequestError {
  return error instanceof ApiRequestError;
}

export function isNetworkError(error: unknown): error is NetworkError {
  return error instanceof NetworkError;
}

export function isTimeoutError(error: unknown): error is TimeoutError {
  return error instanceof TimeoutError;
}

/**
 * 特定のエラーコードかチェック
 */
export function isErrorCode(error: unknown, code: string): boolean {
  return isApiError(error) && error.isType(code);
}

/**
 * リトライ可能なエラーかチェック
 */
export function isRetryableError(error: unknown): boolean {
  if (isApiError(error)) {
    return error.isNetworkError || error.isServerError || error.status === 429;
  }
  
  return isNetworkError(error) || isTimeoutError(error);
}