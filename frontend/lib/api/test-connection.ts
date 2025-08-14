import { api } from './client';
import { API_ENDPOINTS } from './endpoints';
import { ErrorHandler } from './error-handler';
import { SystemStatus } from '@/types/api';
import { User } from '@/types/user';
import { handleApiError, AppError } from '@/utils/error-handler';

// API connection test interface
export interface ConnectionTestResult {
  success: boolean;
  message: string;
  status?: number;
  timestamp: string;
  endpoint: string;
  error?: AppError;
  data?: any;
}

// Test connection to the backend API
export class ApiConnectionTester {
  static async testConnection(): Promise<ConnectionTestResult> {
    const timestamp = new Date().toISOString();
    const endpoint = API_ENDPOINTS.SYSTEM.HEALTH;

    try {
      const response = await api.get<SystemStatus>(endpoint);
      
      return {
        success: true,
        message: 'API接続に成功しました',
        status: response.status,
        timestamp,
        endpoint,
        data: response.data,
      };
    } catch (error) {
      const appError = handleApiError(error);
      
      return {
        success: false,
        message: `API接続に失敗しました: ${appError.message}`,
        status: appError.statusCode,
        timestamp,
        endpoint,
        error: appError,
      };
    }
  }

  static async testAuthenticatedConnection(token?: string): Promise<ConnectionTestResult> {
    const timestamp = new Date().toISOString();
    const endpoint = API_ENDPOINTS.AUTH.ME;

    try {
      // Temporarily set token if provided
      if (token && typeof window !== 'undefined') {
        const originalToken = localStorage.getItem('authToken');
        localStorage.setItem('authToken', token);
        
        try {
          const response = await api.get<User>(endpoint);
          
          return {
            success: true,
            message: '認証付きAPI接続に成功しました',
            status: response.status,
            timestamp,
            endpoint,
            data: response.data,
          };
        } finally {
          // Restore original token
          if (originalToken) {
            localStorage.setItem('authToken', originalToken);
          } else {
            localStorage.removeItem('authToken');
          }
        }
      } else {
        const response = await api.get<User>(endpoint);
        
        return {
          success: true,
          message: '認証付きAPI接続に成功しました',
          status: response.status,
          timestamp,
          endpoint,
          data: response.data,
        };
      }
    } catch (error) {
      const appError = handleApiError(error);
      
      return {
        success: false,
        message: `認証テストに失敗しました: ${appError.message}`,
        status: appError.statusCode,
        timestamp,
        endpoint,
        error: appError,
      };
    }
  }

  static async runBasicTests(): Promise<ConnectionTestResult[]> {
    const results: ConnectionTestResult[] = [];

    // Test system health
    const healthTest = await this.testConnection();
    results.push(healthTest);

    // Test system version endpoint if available
    if (API_ENDPOINTS.SYSTEM?.VERSION) {
      try {
        const versionResponse = await api.get<{ version: string }>(API_ENDPOINTS.SYSTEM.VERSION);
        results.push({
          success: true,
          message: `APIバージョン: ${versionResponse.data.version}`,
          status: versionResponse.status,
          timestamp: new Date().toISOString(),
          endpoint: API_ENDPOINTS.SYSTEM.VERSION,
          data: versionResponse.data,
        });
      } catch (error) {
        const appError = handleApiError(error);
        results.push({
          success: false,
          message: `バージョン確認に失敗しました: ${appError.message}`,
          status: appError.statusCode,
          timestamp: new Date().toISOString(),
          endpoint: API_ENDPOINTS.SYSTEM.VERSION,
          error: appError,
        });
      }
    }

    return results;
  }

  /**
   * 主要なエンドポイントの接続テストを実行
   */
  static async runComprehensiveTests(): Promise<{
    overall: boolean;
    tests: ConnectionTestResult[];
    summary: {
      total: number;
      passed: number;
      failed: number;
    };
  }> {
    const results: ConnectionTestResult[] = [];

    // 基本テストを実行
    const basicTests = await this.runBasicTests();
    results.push(...basicTests);

    // 各エンティティの一覧エンドポイントをテスト（認証エラーは正常とみなす）
    const endpoints = [
      { name: 'ユーザー一覧', endpoint: API_ENDPOINTS.USERS.BASE, requiresAuth: true },
      { name: '記事一覧', endpoint: API_ENDPOINTS.ARTICLES.BASE, requiresAuth: false },
      { name: '修正案一覧', endpoint: API_ENDPOINTS.REVISIONS.BASE, requiresAuth: true },
      { name: '承認グループ一覧', endpoint: API_ENDPOINTS.APPROVAL_GROUPS.BASE, requiresAuth: false },
      { name: '情報カテゴリ一覧', endpoint: API_ENDPOINTS.INFO_CATEGORIES.BASE, requiresAuth: false },
    ];

    for (const { name, endpoint, requiresAuth } of endpoints) {
      try {
        const response = await api.get(endpoint);
        results.push({
          success: true,
          message: `${name}の取得に成功しました`,
          status: response.status,
          timestamp: new Date().toISOString(),
          endpoint,
          data: Array.isArray(response.data) ? { count: response.data.length } : response.data,
        });
      } catch (error) {
        const appError = handleApiError(error);
        
        // 認証が必要なエンドポイントで403/401エラーの場合は正常とみなす
        if (requiresAuth && (appError.statusCode === 403 || appError.statusCode === 401)) {
          results.push({
            success: true,
            message: `${name}: 認証が必要です（正常な動作）`,
            status: appError.statusCode,
            timestamp: new Date().toISOString(),
            endpoint,
          });
        } else {
          results.push({
            success: false,
            message: `${name}の取得に失敗しました: ${appError.message}`,
            status: appError.statusCode,
            timestamp: new Date().toISOString(),
            endpoint,
            error: appError,
          });
        }
      }
    }

    const passed = results.filter(r => r.success).length;
    const failed = results.filter(r => !r.success).length;

    return {
      overall: failed === 0,
      tests: results,
      summary: {
        total: results.length,
        passed,
        failed,
      },
    };
  }

  /**
   * 特定のエンドポイントをテスト
   */
  static async testEndpoint(
    endpoint: string,
    method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET',
    data?: any,
    params?: Record<string, any>
  ): Promise<ConnectionTestResult> {
    const timestamp = new Date().toISOString();

    try {
      let response;

      switch (method) {
        case 'GET':
          response = await api.get(endpoint, params);
          break;
        case 'POST':
          response = await api.post(endpoint, data);
          break;
        case 'PUT':
          response = await api.put(endpoint, data);
          break;
        case 'DELETE':
          response = await api.delete(endpoint);
          break;
      }

      return {
        success: true,
        message: `${method} ${endpoint} に成功しました`,
        status: response.status,
        timestamp,
        endpoint,
        data: response.data,
      };
    } catch (error) {
      const appError = handleApiError(error);

      return {
        success: false,
        message: `${method} ${endpoint} に失敗しました: ${appError.message}`,
        status: appError.statusCode,
        timestamp,
        endpoint,
        error: appError,
      };
    }
  }
}

// Convenience function for quick connection test
export const testApiConnection = () => ApiConnectionTester.testConnection();