/**
 * API接続テスト機能
 */

import { SystemInfo, HealthCheck } from '@/types/api';
import { ApiRequestError, NetworkError, TimeoutError } from '@/lib/errors';

/**
 * API接続テストの結果
 */
export interface ConnectionTestResult {
  success: boolean;
  message: string;
  details: {
    baseUrl: string;
    responseTime: number;
    statusCode?: number;
    systemInfo?: SystemInfo;
    healthCheck?: HealthCheck;
    error?: string;
  };
  timestamp: string;
}

/**
 * APIエンドポイントのテスト結果
 */
export interface EndpointTestResult {
  endpoint: string;
  method: string;
  success: boolean;
  statusCode?: number;
  responseTime: number;
  error?: string;
}

/**
 * 包括的なAPI接続テスト結果
 */
export interface ComprehensiveTestResult {
  overall: {
    success: boolean;
    totalTests: number;
    passedTests: number;
    failedTests: number;
    averageResponseTime: number;
  };
  baseConnection: ConnectionTestResult;
  endpoints: EndpointTestResult[];
  timestamp: string;
}

/**
 * APIベースURLを取得
 */
function getApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';
}

/**
 * HTTP リクエストのタイムアウト付き実行
 */
async function fetchWithTimeout(
  url: string,
  options: RequestInit = {},
  timeoutMs: number = 5000
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new TimeoutError(`Request timeout after ${timeoutMs}ms`);
      }
      throw new NetworkError(`Network error: ${error.message}`);
    }
    throw error;
  }
}

/**
 * 基本的なAPI接続をテスト
 */
export async function testApiConnection(): Promise<ConnectionTestResult> {
  const baseUrl = getApiBaseUrl();
  const startTime = Date.now();
  const timestamp = new Date().toISOString();
  
  try {
    // システムバージョンエンドポイントをテスト
    const response = await fetchWithTimeout(`${baseUrl}/system/version`);
    const responseTime = Date.now() - startTime;
    
    if (!response.ok) {
      throw new ApiRequestError(response.status, response.statusText);
    }
    
    const systemInfo: SystemInfo = await response.json();
    
    return {
      success: true,
      message: 'API connection successful',
      details: {
        baseUrl,
        responseTime,
        statusCode: response.status,
        systemInfo
      },
      timestamp
    };
  } catch (error) {
    const responseTime = Date.now() - startTime;
    let errorMessage = 'Unknown error';
    let statusCode: number | undefined;
    
    if (error instanceof ApiRequestError) {
      errorMessage = error.userMessage;
      statusCode = error.status;
    } else if (error instanceof NetworkError) {
      errorMessage = 'Network connection failed';
    } else if (error instanceof TimeoutError) {
      errorMessage = 'Connection timeout';
    } else if (error instanceof Error) {
      errorMessage = error.message;
    }
    
    return {
      success: false,
      message: 'API connection failed',
      details: {
        baseUrl,
        responseTime,
        statusCode,
        error: errorMessage
      },
      timestamp
    };
  }
}

/**
 * ヘルスチェックエンドポイントをテスト
 */
export async function testHealthCheck(): Promise<ConnectionTestResult> {
  const baseUrl = getApiBaseUrl();
  const startTime = Date.now();
  const timestamp = new Date().toISOString();
  
  try {
    const response = await fetchWithTimeout(`${baseUrl}/system/health`);
    const responseTime = Date.now() - startTime;
    
    if (!response.ok) {
      throw new ApiRequestError(response.status, response.statusText);
    }
    
    const healthCheck: HealthCheck = await response.json();
    const isHealthy = healthCheck.status === 'healthy';
    
    return {
      success: isHealthy,
      message: isHealthy ? 'System is healthy' : `System status: ${healthCheck.status}`,
      details: {
        baseUrl,
        responseTime,
        statusCode: response.status,
        healthCheck
      },
      timestamp
    };
  } catch (error) {
    const responseTime = Date.now() - startTime;
    let errorMessage = 'Unknown error';
    
    if (error instanceof Error) {
      errorMessage = error.message;
    }
    
    return {
      success: false,
      message: 'Health check failed',
      details: {
        baseUrl,
        responseTime,
        error: errorMessage
      },
      timestamp
    };
  }
}

/**
 * 特定のエンドポイントをテスト
 */
export async function testEndpoint(
  endpoint: string,
  method: string = 'GET',
  headers: Record<string, string> = {},
  body?: any
): Promise<EndpointTestResult> {
  const baseUrl = getApiBaseUrl();
  const url = `${baseUrl}${endpoint}`;
  const startTime = Date.now();
  
  try {
    const options: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...headers
      }
    };
    
    if (body && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
      options.body = JSON.stringify(body);
    }
    
    const response = await fetchWithTimeout(url, options);
    const responseTime = Date.now() - startTime;
    
    return {
      endpoint,
      method,
      success: response.ok,
      statusCode: response.status,
      responseTime,
      error: response.ok ? undefined : response.statusText
    };
  } catch (error) {
    const responseTime = Date.now() - startTime;
    
    return {
      endpoint,
      method,
      success: false,
      responseTime,
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}

/**
 * 複数のエンドポイントを包括的にテスト
 */
export async function testApiEndpoints(authToken?: string): Promise<ComprehensiveTestResult> {
  const timestamp = new Date().toISOString();
  const headers: Record<string, string> = authToken ? { Authorization: `Bearer ${authToken}` } : {};
  
  // テスト対象のエンドポイント
  const testEndpoints = [
    { endpoint: '/system/version', method: 'GET' },
    { endpoint: '/system/health', method: 'GET' },
    { endpoint: '/users/me', method: 'GET' }, // 認証が必要
    { endpoint: '/revisions/', method: 'GET' }, // 認証が必要
    { endpoint: '/articles/', method: 'GET' }, // 認証が必要
    { endpoint: '/info-categories/', method: 'GET' },
    { endpoint: '/approval-groups/', method: 'GET' }
  ];
  
  // 基本接続テスト
  const baseConnection = await testApiConnection();
  
  // 各エンドポイントをテスト
  const endpointResults = await Promise.all(
    testEndpoints.map(({ endpoint, method }) =>
      testEndpoint(endpoint, method, headers)
    )
  );
  
  // 統計を計算
  const totalTests = endpointResults.length + 1; // +1 for base connection
  const passedTests = endpointResults.filter(r => r.success).length + (baseConnection.success ? 1 : 0);
  const failedTests = totalTests - passedTests;
  const averageResponseTime = endpointResults.reduce((sum, r) => sum + r.responseTime, 0) / endpointResults.length;
  
  return {
    overall: {
      success: passedTests === totalTests,
      totalTests,
      passedTests,
      failedTests,
      averageResponseTime: Math.round(averageResponseTime)
    },
    baseConnection,
    endpoints: endpointResults,
    timestamp
  };
}

/**
 * デバッグ用のAPI情報を取得
 */
export async function getApiDebugInfo(): Promise<{
  baseUrl: string;
  environment: string;
  timestamp: string;
  userAgent: string;
  systemInfo?: SystemInfo;
  connectionTest: ConnectionTestResult;
}> {
  const baseUrl = getApiBaseUrl();
  const environment = process.env.NODE_ENV || 'unknown';
  const timestamp = new Date().toISOString();
  const userAgent = typeof window !== 'undefined' ? window.navigator.userAgent : 'Server-side';
  
  const connectionTest = await testApiConnection();
  
  return {
    baseUrl,
    environment,
    timestamp,
    userAgent,
    systemInfo: connectionTest.details.systemInfo,
    connectionTest
  };
}

/**
 * 接続テスト結果をコンソールに出力
 */
export function logConnectionTestResult(result: ConnectionTestResult | ComprehensiveTestResult): void {
  if ('overall' in result) {
    // Comprehensive test result
    console.group(`🔍 API Connection Test Results - ${result.timestamp}`);
    console.log(`Overall: ${result.overall.success ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`Tests: ${result.overall.passedTests}/${result.overall.totalTests} passed`);
    console.log(`Average Response Time: ${result.overall.averageResponseTime}ms`);
    
    console.group('📡 Base Connection');
    console.log(`Status: ${result.baseConnection.success ? '✅' : '❌'}`);
    console.log(`Response Time: ${result.baseConnection.details.responseTime}ms`);
    if (result.baseConnection.details.error) {
      console.error(`Error: ${result.baseConnection.details.error}`);
    }
    console.groupEnd();
    
    console.group('🎯 Endpoint Tests');
    result.endpoints.forEach(endpoint => {
      console.log(`${endpoint.success ? '✅' : '❌'} ${endpoint.method} ${endpoint.endpoint} (${endpoint.responseTime}ms)`);
      if (endpoint.error) {
        console.error(`  Error: ${endpoint.error}`);
      }
    });
    console.groupEnd();
    
    console.groupEnd();
  } else {
    // Simple connection test result
    console.group(`🔗 API Connection Test - ${result.timestamp}`);
    console.log(`Status: ${result.success ? '✅ CONNECTED' : '❌ FAILED'}`);
    console.log(`URL: ${result.details.baseUrl}`);
    console.log(`Response Time: ${result.details.responseTime}ms`);
    if (result.details.systemInfo) {
      console.log(`API Version: ${result.details.systemInfo.version}`);
      console.log(`Environment: ${result.details.systemInfo.environment}`);
    }
    if (result.details.error) {
      console.error(`Error: ${result.details.error}`);
    }
    console.groupEnd();
  }
}