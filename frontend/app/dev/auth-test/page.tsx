'use client';

/**
 * 開発用認証テストページ
 * 本番環境では利用不可
 */

import { useState } from 'react';
import { runAuthTests, devAuthTest, createDummyAuthSession, clearAuthData, AuthTestResult } from '@/tests/auth-test';
import { useAuth } from '@/hooks/useAuth';

export default function AuthTestPage() {
  const auth = useAuth();
  const [testResults, setTestResults] = useState<AuthTestResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);

  // 開発環境チェック
  if (process.env.NODE_ENV !== 'development') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-slate-900 flex items-center justify-center">
        <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-8 shadow-2xl max-w-md mx-auto">
          <div className="text-center">
            <div className="text-6xl mb-4">🚫</div>
            <h1 className="text-2xl font-bold text-red-400 mb-4">アクセス拒否</h1>
            <p className="text-gray-300 mb-6">このページは開発環境でのみ利用可能です。</p>
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
              <p className="text-sm text-red-400">
                本番環境では認証テスト機能は無効化されています。
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const handleRunTests = async () => {
    setIsRunning(true);
    try {
      const results = await runAuthTests();
      setTestResults(results.tests);
      console.log('🔐 認証システムテスト結果:', results);
    } catch (error) {
      console.error('テスト実行エラー:', error);
    } finally {
      setIsRunning(false);
    }
  };

  const handleDevTest = async () => {
    await devAuthTest();
  };

  const handleCreateDummySession = () => {
    createDummyAuthSession();
    auth.refreshAuth(); // 認証状態をリフレッシュ
  };

  const handleClearAuth = () => {
    clearAuthData();
    auth.refreshAuth(); // 認証状態をリフレッシュ
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-slate-900">
      <div className="p-8 max-w-5xl mx-auto">
        <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-8 shadow-2xl">
          <h1 className="text-4xl font-bold mb-8 text-gray-100 flex items-center gap-3">
            <span className="text-blue-400">🔐</span>
            認証システムテスト
          </h1>
          
          {/* 現在の認証状態 */}
          <div className="bg-gray-700/60 border border-gray-600 p-6 rounded-lg mb-8 backdrop-blur-sm">
            <h2 className="text-xl font-semibold mb-4 text-gray-200 flex items-center gap-2">
              <span className="w-2 h-2 bg-blue-400 rounded-full"></span>
              現在の認証状態
            </h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <span className="text-gray-400 min-w-[80px]">認証済み:</span>
                  <span className={`px-2 py-1 rounded text-sm font-medium ${
                    auth.isAuthenticated 
                      ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                      : 'bg-red-500/20 text-red-400 border border-red-500/30'
                  }`}>
                    {auth.isAuthenticated ? '✅ はい' : '❌ いいえ'}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-gray-400 min-w-[80px]">ローディング:</span>
                  <span className={`px-2 py-1 rounded text-sm font-medium ${
                    auth.isLoading 
                      ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30' 
                      : 'bg-green-500/20 text-green-400 border border-green-500/30'
                  }`}>
                    {auth.isLoading ? '⏳ 読み込み中' : '✅ 完了'}
                  </span>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <span className="text-gray-400 min-w-[60px]">ユーザー:</span>
                  <span className="text-gray-200 font-mono text-sm">
                    {auth.user ? `${auth.user.username} (${auth.user.role})` : 'なし'}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-gray-400 min-w-[60px]">エラー:</span>
                  <span className={auth.error ? 'text-red-400' : 'text-gray-500'}>
                    {auth.error ? auth.error.message : 'なし'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* 操作ボタン */}
          <div className="grid grid-cols-2 gap-4 mb-8">
            <button
              onClick={handleRunTests}
              disabled={isRunning}
              className="bg-slate-700 hover:bg-slate-600 text-gray-100 px-6 py-3 rounded-lg font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed border border-slate-600 hover:border-slate-500 shadow-lg"
            >
              {isRunning ? '⏳ テスト実行中...' : '🧪 認証テスト実行'}
            </button>
            
            <button
              onClick={handleDevTest}
              className="bg-gray-700 hover:bg-gray-600 text-gray-100 px-6 py-3 rounded-lg font-medium transition-all duration-200 border border-gray-600 hover:border-gray-500 shadow-lg"
            >
              📝 コンソールテスト実行
            </button>
            
            <button
              onClick={handleCreateDummySession}
              className="bg-slate-600 hover:bg-slate-500 text-gray-100 px-6 py-3 rounded-lg font-medium transition-all duration-200 border border-slate-500 hover:border-slate-400 shadow-lg"
            >
              👤 ダミーユーザーログイン
            </button>
            
            <button
              onClick={handleClearAuth}
              className="bg-red-800/80 hover:bg-red-700/80 text-gray-100 px-6 py-3 rounded-lg font-medium transition-all duration-200 border border-red-700 hover:border-red-600 shadow-lg"
            >
              🧹 認証データクリア
            </button>
          </div>

          {/* テスト結果 */}
          {testResults.length > 0 && (
            <div className="bg-gray-700/60 border border-gray-600 rounded-lg p-6 backdrop-blur-sm mb-8">
              <h2 className="text-xl font-semibold mb-6 text-gray-200 flex items-center gap-2">
                <span className="w-2 h-2 bg-green-400 rounded-full"></span>
                テスト結果
              </h2>
              <div className="space-y-4">
                {testResults.map((result, index) => (
                  <div
                    key={index}
                    className={`p-4 rounded-lg border-l-4 backdrop-blur-sm ${
                      result.passed 
                        ? 'border-green-400 bg-green-500/10 border-r border-t border-b border-green-500/20' 
                        : 'border-red-400 bg-red-500/10 border-r border-t border-b border-red-500/20'
                    }`}
                  >
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-lg">{result.passed ? '✅' : '❌'}</span>
                      <strong className="text-gray-200">{result.test}</strong>
                    </div>
                    <p className="text-sm text-gray-300 ml-8">{result.message}</p>
                    {result.data && (
                      <details className="mt-3 ml-8">
                        <summary className="text-sm cursor-pointer text-blue-400 hover:text-blue-300 transition-colors">
                          データを表示
                        </summary>
                        <pre className="text-xs bg-gray-800/60 border border-gray-600 p-3 rounded mt-2 overflow-auto text-gray-300 font-mono">
                          {JSON.stringify(result.data, null, 2)}
                        </pre>
                      </details>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 使用方法 */}
          <div className="bg-slate-700/60 border border-slate-600 p-6 rounded-lg backdrop-blur-sm">
            <h2 className="text-lg font-semibold mb-4 text-gray-200 flex items-center gap-2">
              <span className="text-blue-400">📖</span>
              使用方法
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <span className="text-slate-400 mt-1">🧪</span>
                  <div>
                    <strong className="text-gray-200">認証テスト実行:</strong>
                    <p className="text-sm text-gray-400">TokenManager、JWT、セッション管理の包括的テスト</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <span className="text-slate-400 mt-1">📝</span>
                  <div>
                    <strong className="text-gray-200">コンソールテスト:</strong>
                    <p className="text-sm text-gray-400">ブラウザのDevToolsコンソールにテスト結果を出力</p>
                  </div>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <span className="text-slate-400 mt-1">👤</span>
                  <div>
                    <strong className="text-gray-200">ダミーユーザーログイン:</strong>
                    <p className="text-sm text-gray-400">開発用のadminユーザーでログイン</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <span className="text-slate-400 mt-1">🧹</span>
                  <div>
                    <strong className="text-gray-200">認証データクリア:</strong>
                    <p className="text-sm text-gray-400">localStorage内の認証情報をすべて削除</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}