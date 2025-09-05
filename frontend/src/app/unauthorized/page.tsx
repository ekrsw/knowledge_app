'use client';

import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';

/**
 * 権限不足エラーページ
 */
export default function UnauthorizedPage() {
  const router = useRouter();
  const { user, logout } = useAuth();

  const handleGoBack = () => {
    router.back();
  };

  const handleGoHome = () => {
    router.push('/');
  };

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center">
        {/* エラーアイコン */}
        <div className="mb-6">
          <svg
            className="mx-auto h-24 w-24 text-red-500"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.5"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>

        {/* エラーメッセージ */}
        <h1 className="text-3xl font-bold text-white mb-2">
          アクセス権限がありません
        </h1>
        <p className="text-gray-400 mb-8">
          このページにアクセスするための権限が不足しています。
          {user && (
            <span className="block mt-2">
              現在のロール: <span className="text-blue-400">{user.role}</span>
            </span>
          )}
        </p>

        {/* アクションボタン */}
        <div className="space-y-3">
          <button
            onClick={handleGoBack}
            className="w-full px-4 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
          >
            前のページに戻る
          </button>
          
          <button
            onClick={handleGoHome}
            className="w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            ホームに戻る
          </button>

          <button
            onClick={handleLogout}
            className="w-full px-4 py-3 bg-transparent hover:bg-gray-800 text-gray-400 hover:text-white border border-gray-700 rounded-lg transition-colors"
          >
            別のアカウントでログイン
          </button>
        </div>

        {/* ヘルプテキスト */}
        <div className="mt-8 p-4 bg-gray-800 rounded-lg">
          <p className="text-sm text-gray-400">
            権限についてお困りの場合は、システム管理者にお問い合わせください。
          </p>
        </div>
      </div>
    </div>
  );
}