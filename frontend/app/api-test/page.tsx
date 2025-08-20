'use client';

import { useState } from 'react';
import {
  testApiConnection,
  testHealthCheck,
  testApiEndpoints,
  logConnectionTestResult,
  type ConnectionTestResult,
  type ComprehensiveTestResult,
  getApiDebugInfo,
} from '@/lib/api/test-connection';

interface TestResults {
  basicConnection?: ConnectionTestResult;
  healthCheck?: ConnectionTestResult;
  comprehensive?: ComprehensiveTestResult;
  debugInfo?: Record<string, unknown>;
}

export default function ApiTestPage() {
  const [testResults, setTestResults] = useState<TestResults>({});
  const [isLoading, setIsLoading] = useState(false);
  const [activeTest, setActiveTest] = useState<string | null>(null);

  const runBasicConnectionTest = async () => {
    setIsLoading(true);
    setActiveTest('basic');

    try {
      const result = await testApiConnection();
      setTestResults((prev) => ({ ...prev, basicConnection: result }));
      logConnectionTestResult(result);
      console.log('🔗 Basic Connection Test Result:', result);
    } catch (error) {
      console.error('Basic connection test failed:', error);
    } finally {
      setIsLoading(false);
      setActiveTest(null);
    }
  };

  const runHealthCheckTest = async () => {
    setIsLoading(true);
    setActiveTest('health');

    try {
      const result = await testHealthCheck();
      setTestResults((prev) => ({ ...prev, healthCheck: result }));
      logConnectionTestResult(result);
      console.log('🏥 Health Check Test Result:', result);
    } catch (error) {
      console.error('Health check test failed:', error);
    } finally {
      setIsLoading(false);
      setActiveTest(null);
    }
  };

  const runComprehensiveTest = async () => {
    setIsLoading(true);
    setActiveTest('comprehensive');

    try {
      const result = await testApiEndpoints();
      setTestResults((prev) => ({ ...prev, comprehensive: result }));
      logConnectionTestResult(result);
      console.log('📊 Comprehensive Test Result:', result);
    } catch (error) {
      console.error('Comprehensive test failed:', error);
    } finally {
      setIsLoading(false);
      setActiveTest(null);
    }
  };

  const runDebugInfo = async () => {
    setIsLoading(true);
    setActiveTest('debug');

    try {
      const result = await getApiDebugInfo();
      setTestResults((prev) => ({ ...prev, debugInfo: result }));
      console.log('🐛 Debug Info:', result);
    } catch (error) {
      console.error('Debug info failed:', error);
    } finally {
      setIsLoading(false);
      setActiveTest(null);
    }
  };

  const clearResults = () => {
    setTestResults({});
    console.clear();
  };

  const renderConnectionResult = (result: ConnectionTestResult) => (
    <div
      className={`p-4 rounded-lg border-2 ${result.success ? 'border-green-500 bg-gray-800' : 'border-red-500 bg-gray-800'}`}
    >
      <div className="flex items-center gap-2 mb-2">
        <span className={`text-lg ${result.success ? 'text-green-400' : 'text-red-400'}`}>
          {result.success ? '✅' : '❌'}
        </span>
        <span className="font-semibold text-white">{result.message}</span>
      </div>
      <div className="text-sm text-gray-300 space-y-1">
        <div>URL: {result.details.baseUrl}</div>
        <div>Response Time: {result.details.responseTime}ms</div>
        {result.details.statusCode && <div>Status Code: {result.details.statusCode}</div>}
        {result.details.error && <div className="text-red-400">Error: {result.details.error}</div>}
        {result.details.systemInfo && (
          <div className="mt-2">
            <div className="font-medium text-blue-400">System Info:</div>
            <div className="ml-2 text-xs">
              <div>Version: {result.details.systemInfo.version}</div>
              <div>API Version: {result.details.systemInfo.api_version}</div>
              <div>Build Date: {result.details.systemInfo.build_date}</div>
              <div>Features: {result.details.systemInfo.features.join(', ')}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderComprehensiveResult = (result: ComprehensiveTestResult) => (
    <div className="space-y-4">
      <div
        className={`p-4 rounded-lg border-2 ${result.overall.success ? 'border-green-500 bg-gray-800' : 'border-yellow-500 bg-gray-800'}`}
      >
        <div className="flex items-center gap-2 mb-2">
          <span className="text-lg">{result.overall.success ? '✅' : '⚠️'}</span>
          <span className="font-semibold text-white">
            Overall: {result.overall.passedTests}/{result.overall.totalTests} tests passed
          </span>
        </div>
        <div className="text-sm text-gray-300">
          Average Response Time: {result.overall.averageResponseTime}ms
        </div>
      </div>

      <div className="grid gap-2">
        <h4 className="font-semibold text-white">Endpoint Results:</h4>
        {result.endpoints.map((endpoint, index) => (
          <div
            key={index}
            className={`p-3 rounded-lg border ${endpoint.success ? 'border-green-500 bg-gray-800' : 'border-red-500 bg-gray-800'}`}
          >
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-2">
                <span>{endpoint.success ? '✅' : '❌'}</span>
                <span className="font-mono text-sm text-gray-100">
                  {endpoint.method} {endpoint.endpoint}
                </span>
              </span>
              <span className="text-sm text-gray-300">{endpoint.responseTime}ms</span>
            </div>
            {endpoint.error && <div className="text-red-400 text-xs mt-1">{endpoint.error}</div>}
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      <div className="container mx-auto p-6 max-w-4xl">
        <h1 className="text-3xl font-bold mb-6 text-white">🔧 API接続テストツール</h1>

        <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 mb-6">
          <h2 className="text-lg font-semibold text-blue-400 mb-2">使用方法</h2>
          <ul className="text-gray-300 text-sm space-y-1">
            <li>• 各テストボタンをクリックして API 接続をテストします</li>
            <li>• 結果はこのページとブラウザのコンソール（F12）に表示されます</li>
            <li>• バックエンドサーバー（http://localhost:8000）が起動している必要があります</li>
          </ul>
        </div>

        <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 mb-6">
          <div className="flex flex-wrap gap-3">
          <button
            onClick={runBasicConnectionTest}
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed flex items-center gap-2 transition-colors duration-200"
          >
            {activeTest === 'basic' && <span className="animate-spin">⏳</span>}
            🔗 基本接続テスト
          </button>

          <button
            onClick={runHealthCheckTest}
            disabled={isLoading}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed flex items-center gap-2 transition-colors duration-200"
          >
            {activeTest === 'health' && <span className="animate-spin">⏳</span>}
            🏥 ヘルスチェック
          </button>

          <button
            onClick={runComprehensiveTest}
            disabled={isLoading}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed flex items-center gap-2 transition-colors duration-200"
          >
            {activeTest === 'comprehensive' && <span className="animate-spin">⏳</span>}
            📊 包括的テスト
          </button>

          <button
            onClick={runDebugInfo}
            disabled={isLoading}
            className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:bg-gray-600 disabled:cursor-not-allowed flex items-center gap-2 transition-colors duration-200"
          >
            {activeTest === 'debug' && <span className="animate-spin">⏳</span>}
            🐛 デバッグ情報
          </button>

          <button
            onClick={clearResults}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors duration-200"
          >
            🗑️ 結果クリア
          </button>
          </div>
        </div>

      <div className="space-y-6">
          {testResults.basicConnection && (
            <div>
              <h3 className="text-xl font-semibold mb-3 text-white">🔗 基本接続テスト結果</h3>
              {renderConnectionResult(testResults.basicConnection)}
            </div>
          )}

          {testResults.healthCheck && (
            <div>
              <h3 className="text-xl font-semibold mb-3 text-white">🏥 ヘルスチェック結果</h3>
              {renderConnectionResult(testResults.healthCheck)}
            </div>
          )}

          {testResults.comprehensive && (
            <div>
              <h3 className="text-xl font-semibold mb-3 text-white">📊 包括的テスト結果</h3>
              {renderComprehensiveResult(testResults.comprehensive)}
            </div>
          )}

          {testResults.debugInfo && (
            <div>
              <h3 className="text-xl font-semibold mb-3 text-white">🐛 デバッグ情報</h3>
              <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 overflow-x-auto">
                <pre className="text-sm text-gray-300">
                  {JSON.stringify(testResults.debugInfo, null, 2)}
                </pre>
              </div>
            </div>
          )}
      </div>

        <div className="mt-8 p-4 bg-gray-800 border border-gray-700 rounded-lg">
          <h3 className="font-semibold mb-2 text-green-400">📝 開発者向け情報</h3>
          <ul className="text-sm text-gray-300 space-y-1">
            <li>
              • API Base URL: {process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'}
            </li>
            <li>• Environment: {process.env.NODE_ENV}</li>
            <li>• Debug Mode: {process.env.NEXT_PUBLIC_DEBUG_MODE || 'false'}</li>
            <li>• 詳細なログはブラウザコンソールを確認してください（F12キー）</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
