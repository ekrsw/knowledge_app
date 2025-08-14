/**
 * 認証統合テスト
 * バックエンドAPIとの実際の認証テスト
 */

import { api } from '@/lib/api/client';
import { API_ENDPOINTS } from '@/lib/api/endpoints';
import { LoginRequest, LoginResponse } from '@/types';
import { TokenManager } from '@/utils/auth';
import { handleApiError } from '@/utils/error-handler';

export interface AuthIntegrationTestResult {
  test: string;
  passed: boolean;
  message: string;
  duration: number;
  data?: any;
}

/**
 * 認証APIの統合テスト
 */
export async function runAuthIntegrationTests(): Promise<{
  overall: boolean;
  tests: AuthIntegrationTestResult[];
  summary: {
    total: number;
    passed: number;
    failed: number;
    totalDuration: number;
  };
}> {
  const results: AuthIntegrationTestResult[] = [];
  let totalDuration = 0;

  // ヘルスチェックテスト
  const healthResult = await testHealthEndpoint();
  results.push(healthResult);
  totalDuration += healthResult.duration;

  // 認証が必要なエンドポイントテスト
  const protectedResult = await testProtectedEndpoint();
  results.push(protectedResult);
  totalDuration += protectedResult.duration;

  // 無効なトークンテスト
  const invalidTokenResult = await testInvalidToken();
  results.push(invalidTokenResult);
  totalDuration += invalidTokenResult.duration;

  const passed = results.filter(r => r.passed).length;
  const failed = results.filter(r => !r.passed).length;

  return {
    overall: failed === 0,
    tests: results,
    summary: {
      total: results.length,
      passed,
      failed,
      totalDuration,
    },
  };
}

/**
 * ヘルスチェックエンドポイントのテスト
 */
async function testHealthEndpoint(): Promise<AuthIntegrationTestResult> {
  const startTime = Date.now();
  
  try {
    const response = await api.get(API_ENDPOINTS.SYSTEM.HEALTH);
    const duration = Date.now() - startTime;
    
    return {
      test: 'システムヘルスチェック',
      passed: response.status === 200,
      message: `ヘルスチェックAPI応答: ${response.status}`,
      duration,
      data: response.data,
    };
  } catch (error) {
    const duration = Date.now() - startTime;
    const appError = handleApiError(error);
    
    return {
      test: 'システムヘルスチェック',
      passed: false,
      message: `ヘルスチェック失敗: ${appError.message}`,
      duration,
    };
  }
}

/**
 * 認証が必要なエンドポイントのテスト
 */
async function testProtectedEndpoint(): Promise<AuthIntegrationTestResult> {
  const startTime = Date.now();
  
  try {
    const response = await api.get(API_ENDPOINTS.AUTH.ME);
    const duration = Date.now() - startTime;
    
    // 認証されていない場合は401が返されるべき
    return {
      test: '認証保護エンドポイント',
      passed: false,
      message: `予期しない成功: ${response.status} (401が期待される)`,
      duration,
      data: response.data,
    };
  } catch (error) {
    const duration = Date.now() - startTime;
    const appError = handleApiError(error);
    
    // 401 Unauthorizedが期待される結果
    if (appError.statusCode === 401) {
      return {
        test: '認証保護エンドポイント',
        passed: true,
        message: '未認証アクセスで正しく401エラーが返された',
        duration,
      };
    } else {
      return {
        test: '認証保護エンドポイント',
        passed: false,
        message: `予期しないエラー: ${appError.message} (401が期待される)`,
        duration,
      };
    }
  }
}

/**
 * 無効なトークンでのテスト
 */
async function testInvalidToken(): Promise<AuthIntegrationTestResult> {
  const startTime = Date.now();
  
  // 現在のトークンを保存
  const originalToken = TokenManager.getToken();
  
  try {
    // 無効なトークンを設定
    TokenManager.setToken('invalid.token.here');
    
    const response = await api.get(API_ENDPOINTS.AUTH.ME);
    const duration = Date.now() - startTime;
    
    // 復元
    if (originalToken) {
      TokenManager.setToken(originalToken);
    } else {
      TokenManager.clearToken();
    }
    
    return {
      test: '無効トークン検証',
      passed: false,
      message: `無効トークンで予期しない成功: ${response.status}`,
      duration,
    };
  } catch (error) {
    const duration = Date.now() - startTime;
    const appError = handleApiError(error);
    
    // 復元
    if (originalToken) {
      TokenManager.setToken(originalToken);
    } else {
      TokenManager.clearToken();
    }
    
    // 401 Unauthorizedが期待される結果
    if (appError.statusCode === 401) {
      return {
        test: '無効トークン検証',
        passed: true,
        message: '無効トークンで正しく401エラーが返された',
        duration,
      };
    } else {
      return {
        test: '無効トークン検証',
        passed: false,
        message: `予期しないエラー: ${appError.message}`,
        duration,
      };
    }
  }
}

/**
 * 開発環境での認証統合テスト実行
 */
export async function devAuthIntegrationTest(): Promise<void> {
  if (process.env.NODE_ENV !== 'development') {
    console.warn('認証統合テストは開発環境でのみ実行できます');
    return;
  }

  console.group('🔗 認証統合テスト (API連携)');
  
  const results = await runAuthIntegrationTests();
  
  console.log(`📊 テスト結果: ${results.summary.passed}/${results.summary.total} 合格`);
  console.log(`⏱️ 総実行時間: ${results.summary.totalDuration}ms`);
  
  results.tests.forEach(test => {
    const icon = test.passed ? '✅' : '❌';
    console.log(`${icon} ${test.test}: ${test.message} (${test.duration}ms)`);
    
    if (test.data) {
      console.log('   データ:', test.data);
    }
  });
  
  if (results.overall) {
    console.log('🎉 すべての統合テストが合格しました');
  } else {
    console.warn('⚠️ 一部の統合テストが失敗しました');
  }
  
  console.groupEnd();
}

/**
 * 実際のログインフローのテスト（テスト用認証情報が必要）
 */
export async function testLoginFlow(credentials: LoginRequest): Promise<AuthIntegrationTestResult> {
  const startTime = Date.now();
  
  try {
    // 既存のトークンをクリア
    TokenManager.clearToken();
    
    // ログイン実行
    const response = await api.post<LoginResponse>(API_ENDPOINTS.AUTH.LOGIN, credentials);
    const duration = Date.now() - startTime;
    
    if (response.data?.access_token) {
      // トークンを設定
      TokenManager.setToken(response.data.access_token, response.data.expires_in);
      
      // ユーザー情報取得テスト
      const userResponse = await api.get(API_ENDPOINTS.AUTH.ME);
      const userData = userResponse.data as any;
      
      return {
        test: 'ログインフローテスト',
        passed: true,
        message: `ログイン成功: ${userData?.username || 'Unknown'}`,
        duration,
        data: {
          token: response.data.access_token,
          user: userData,
        },
      };
    } else {
      return {
        test: 'ログインフローテスト',
        passed: false,
        message: 'レスポンスにトークンが含まれていません',
        duration,
      };
    }
  } catch (error) {
    const duration = Date.now() - startTime;
    const appError = handleApiError(error);
    
    return {
      test: 'ログインフローテスト',
      passed: false,
      message: `ログイン失敗: ${appError.message}`,
      duration,
    };
  }
}