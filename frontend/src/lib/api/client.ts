/**
 * AxiosベースのAPIクライアント
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { TokenStorage } from '@/lib/auth/token-storage';
import { API_CONFIG } from './index';

// APIクライアントのインスタンスを作成
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
  // プロキシを無効化
  proxy: false,
  // サーバーサイドの場合のみhttpアダプターを使用
  ...(typeof window === 'undefined' ? {
    adapter: 'http'
  } : {})
});

// リクエストインターセプター（JWTトークンを自動で付与）
apiClient.interceptors.request.use(
  (config) => {
    const token = TokenStorage.getToken();
    
    // デバッグ情報をコンソールに出力
    console.log('[API Client] Request URL:', config.baseURL + config.url);
    console.log('[API Client] Base URL:', config.baseURL);
    console.log('[API Client] Request Path:', config.url);
    
    if (token && TokenStorage.isTokenValid(token)) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// レスポンスインターセプター（エラーハンドリング）
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError) => {
    // 401エラー（認証エラー）の場合、トークンをクリア
    if (error.response?.status === 401) {
      TokenStorage.clear();
      
      // 現在のページをリロードして認証状態をリセット
      // ただし、ログインページや認証不要のページの場合は除く
      if (typeof window !== 'undefined') {
        const currentPath = window.location.pathname;
        if (!currentPath.includes('/login') && !currentPath.includes('/api-test')) {
          window.location.reload();
        }
      }
    }
    
    return Promise.reject(error);
  }
);

// APIレスポンスの型定義
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: number;
}

// APIエラーの型定義
export interface ApiErrorResponse {
  detail: string;
  error_code?: string;
  validation_errors?: Array<{
    field: string;
    message: string;
  }>;
}

// API呼び出し用のヘルパー関数
export class ApiClient {
  /**
   * GET リクエスト
   */
  static async get<T>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return apiClient.get<T>(url, config);
  }

  /**
   * POST リクエスト
   */
  static async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return apiClient.post<T>(url, data, config);
  }

  /**
   * PUT リクエスト
   */
  static async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return apiClient.put<T>(url, data, config);
  }

  /**
   * DELETE リクエスト
   */
  static async delete<T>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return apiClient.delete<T>(url, config);
  }

  /**
   * PATCH リクエスト
   */
  static async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return apiClient.patch<T>(url, data, config);
  }
}

export default apiClient;