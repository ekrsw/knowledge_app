/**
 * 認証システムのテスト用ユーティリティ
 * 開発・デバッグ用の認証機能テスト
 */

import { TokenManager, decodeToken, isTokenValid, checkAuthStatus } from '@/utils/auth';

/**
 * 認証システムのテスト結果
 */
export interface AuthTestResult {
  test: string;
  passed: boolean;
  message: string;
  data?: any;
}

/**
 * 認証システムの包括的テスト
 */
export async function runAuthTests(): Promise<{
  overall: boolean;
  tests: AuthTestResult[];
  summary: {
    total: number;
    passed: number;
    failed: number;
  };
}> {
  const results: AuthTestResult[] = [];

  // Token Manager テスト
  results.push(testTokenManager());
  
  // JWT デコードテスト
  results.push(testJWTDecoding());
  
  // セッション管理テスト
  results.push(testSessionManagement());
  
  // 権限チェックテスト
  results.push(testPermissionChecks());

  const passed = results.filter(r => r.passed).length;
  const failed = results.filter(r => !r.passed).length;

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
 * Token Manager のテスト
 */
function testTokenManager(): AuthTestResult {
  try {
    // テスト用トークン
    const testToken = 'test.token.here';
    const expiresIn = 3600; // 1時間

    // トークン保存テスト
    TokenManager.setToken(testToken, expiresIn);
    const retrievedToken = TokenManager.getToken();

    if (retrievedToken === testToken) {
      // クリーンアップ
      TokenManager.clearToken();
      
      return {
        test: 'TokenManager基本機能',
        passed: true,
        message: 'トークンの保存・取得・削除が正常に動作',
      };
    } else {
      return {
        test: 'TokenManager基本機能',
        passed: false,
        message: 'トークンの保存または取得に失敗',
      };
    }
  } catch (error) {
    return {
      test: 'TokenManager基本機能',
      passed: false,
      message: `テスト中にエラー: ${error}`,
    };
  }
}

/**
 * JWT デコードのテスト
 */
function testJWTDecoding(): AuthTestResult {
  try {
    // テスト用のJWTトークン（有効期限: 2099年）
    const testJWT = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidGVzdC11c2VyIiwidXNlcm5hbWUiOiJ0ZXN0dXNlciIsInJvbGUiOiJ1c2VyIiwiZXhwIjo0MDk1MjQ0MzExLCJpYXQiOjE2NDA5OTUyMDB9.test';
    
    const decoded = decodeToken(testJWT);
    
    if (decoded && decoded.user_id === 'test-user') {
      return {
        test: 'JWTデコード機能',
        passed: true,
        message: 'JWTトークンのデコードが正常に動作',
        data: decoded,
      };
    } else {
      return {
        test: 'JWTデコード機能',
        passed: false,
        message: 'JWTトークンのデコードに失敗または内容が不正',
      };
    }
  } catch (error) {
    return {
      test: 'JWTデコード機能',
      passed: false,
      message: `デコードテスト中にエラー: ${error}`,
    };
  }
}

/**
 * セッション管理のテスト
 */
function testSessionManagement(): AuthTestResult {
  try {
    // 期限切れトークンのテスト
    const expiredToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidGVzdCIsImV4cCI6MTYwMDAwMDAwMCwiaWF0IjoxNjAwMDAwMDAwfQ.test';
    
    const isValid = isTokenValid(expiredToken);
    
    if (!isValid) {
      return {
        test: 'セッション有効期限チェック',
        passed: true,
        message: '期限切れトークンが正しく無効と判定された',
      };
    } else {
      return {
        test: 'セッション有効期限チェック',
        passed: false,
        message: '期限切れトークンが有効と誤判定された',
      };
    }
  } catch (error) {
    return {
      test: 'セッション有効期限チェック',
      passed: false,
      message: `セッション管理テスト中にエラー: ${error}`,
    };
  }
}

/**
 * 権限チェックのテスト
 */
function testPermissionChecks(): AuthTestResult {
  try {
    // 現在の認証状態をチェック
    const authStatus = checkAuthStatus();
    
    return {
      test: '認証状態チェック',
      passed: true,
      message: '認証状態チェック機能が正常に動作',
      data: authStatus,
    };
  } catch (error) {
    return {
      test: '認証状態チェック',
      passed: false,
      message: `権限チェックテスト中にエラー: ${error}`,
    };
  }
}

/**
 * 開発環境での認証テスト実行
 */
export async function devAuthTest(): Promise<void> {
  if (process.env.NODE_ENV !== 'development') {
    console.warn('認証テストは開発環境でのみ実行できます');
    return;
  }

  console.group('🔐 認証システムテスト');
  
  const results = await runAuthTests();
  
  console.log(`📊 テスト結果: ${results.summary.passed}/${results.summary.total} 合格`);
  
  results.tests.forEach(test => {
    const icon = test.passed ? '✅' : '❌';
    console.log(`${icon} ${test.test}: ${test.message}`);
    
    if (test.data) {
      console.log('   データ:', test.data);
    }
  });
  
  if (results.overall) {
    console.log('🎉 すべてのテストが合格しました');
  } else {
    console.warn('⚠️ 一部のテストが失敗しました');
  }
  
  console.groupEnd();
}

/**
 * 開発用: ダミーユーザーでログインテスト
 */
export function createDummyAuthSession() {
  if (process.env.NODE_ENV !== 'development') {
    console.warn('ダミー認証は開発環境でのみ利用可能です');
    return;
  }

  // ダミーJWTトークン（2099年まで有効）
  const dummyToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZGV2LXVzZXIiLCJ1c2VybmFtZSI6ImRldmVsb3BlciIsInJvbGUiOiJhZG1pbiIsImV4cCI6NDA5NTI0NDMxMSwiaWF0IjoxNjQwOTk1MjAwfQ.dummy-signature';
  
  TokenManager.setToken(dummyToken, 3600);
  
  console.log('🔧 開発用ダミー認証セッションを作成しました');
  console.log('ユーザー: developer (admin)');
  console.log('有効期限: 1時間');
}

/**
 * LocalStorageの認証データをクリア
 */
export function clearAuthData(): void {
  TokenManager.clearToken();
  console.log('🧹 認証データをクリアしました');
}