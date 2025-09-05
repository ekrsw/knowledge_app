'use client';

import { useEffect, useState } from 'react';
import { checkApiConnection } from '@/lib/api';

/**
 * API接続チェックプロバイダー
 * 開発環境でのみAPI接続状態を自動チェックする
 */
export function ApiCheckProvider({ children }: { children: React.ReactNode }) {
  const [isChecking, setIsChecking] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'unknown' | 'connected' | 'failed'>(
    'unknown'
  );

  useEffect(() => {
    // 開発環境でのみ実行
    if (process.env.NODE_ENV === 'development' && typeof window !== 'undefined') {
      const performApiCheck = async () => {
        setIsChecking(true);
        try {
          await checkApiConnection();
          setConnectionStatus('connected');

          // 成功時のコンソール通知
          console.log(
            '%c✅ API Connection Check',
            'color: green; font-weight: bold',
            'Backend API is accessible'
          );
        } catch (error) {
          setConnectionStatus('failed');

          // 失敗時の詳細なガイダンス
          console.group('%c⚠️ API Connection Check Failed', 'color: orange; font-weight: bold');
          console.log('Backend API is not accessible. Please check:');
          console.log(
            '1. Backend server is running: uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000'
          );
          console.log(
            '2. API Base URL is correct:',
            process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'
          );
          console.log('3. No firewall or proxy issues');
          console.log('4. Visit /api-test page for detailed diagnostics');
          console.error('Error details:', error);
          console.groupEnd();
        } finally {
          setIsChecking(false);
        }
      };

      // 初回チェック
      performApiCheck();

      // 定期チェック（5分毎）- 開発時のみ
      const interval = setInterval(performApiCheck, 5 * 60 * 1000);

      return () => clearInterval(interval);
    }
  }, []);

  // 開発環境での接続状態表示（右下に小さく）
  if (process.env.NODE_ENV === 'development' && typeof window !== 'undefined') {
    const statusDisplay = (
      <div className="fixed bottom-4 right-4 z-50 pointer-events-none">
        <div
          className={`px-3 py-1 rounded-full text-xs font-medium ${
            isChecking
              ? 'bg-blue-100 text-blue-800'
              : connectionStatus === 'connected'
                ? 'bg-green-100 text-green-800'
                : connectionStatus === 'failed'
                  ? 'bg-red-100 text-red-800'
                  : 'bg-gray-100 text-gray-800'
          }`}
        >
          {isChecking && '⏳ Checking API...'}
          {!isChecking && connectionStatus === 'connected' && '✅ API OK'}
          {!isChecking && connectionStatus === 'failed' && '❌ API Down'}
          {!isChecking && connectionStatus === 'unknown' && '⚪ API Unknown'}
        </div>
      </div>
    );

    return (
      <>
        {children}
        {statusDisplay}
      </>
    );
  }

  return <>{children}</>;
}
