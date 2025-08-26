'use client';

import { useRouter } from 'next/navigation';
import { useRequireAuth } from '@/hooks/useRequireAuth';
import { useAuth } from '@/hooks/useAuth';

/**
 * ダッシュボードページ（認証が必要）
 */
export default function DashboardPage() {
  const router = useRouter();
  const { user, isLoading, hasPermission } = useRequireAuth();
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          <p className="mt-4 text-gray-400">読み込み中...</p>
        </div>
      </div>
    );
  }

  if (!hasPermission) {
    return null; // リダイレクト処理中
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">ダッシュボード</h1>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors font-medium"
          >
            ログアウト
          </button>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">ユーザー情報</h2>
          <div className="space-y-2">
            <p>
              <span className="text-gray-400">名前:</span>{' '}
              <span className="text-white">{user?.full_name}</span>
            </p>
            <p>
              <span className="text-gray-400">ユーザー名:</span>{' '}
              <span className="text-white">{user?.username}</span>
            </p>
            <p>
              <span className="text-gray-400">メール:</span>{' '}
              <span className="text-white">{user?.email}</span>
            </p>
            <p>
              <span className="text-gray-400">ロール:</span>{' '}
              <span className="text-blue-400">{user?.role}</span>
            </p>
            <p>
              <span className="text-gray-400">承認グループ:</span>{' '}
              <span className="text-white">{user?.approval_group_id || 'なし'}</span>
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-2">修正案</h3>
            <p className="text-3xl font-bold text-blue-400">0</p>
            <p className="text-gray-400 text-sm">作成した修正案</p>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-2">承認待ち</h3>
            <p className="text-3xl font-bold text-yellow-400">0</p>
            <p className="text-gray-400 text-sm">承認待ちの修正案</p>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-2">承認済み</h3>
            <p className="text-3xl font-bold text-green-400">0</p>
            <p className="text-gray-400 text-sm">承認された修正案</p>
          </div>
        </div>
      </div>
    </div>
  );
}