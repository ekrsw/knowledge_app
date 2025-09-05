'use client';

import { useRequireAuth } from '@/hooks/useRequireAuth';

/**
 * 管理者ページ（管理者権限が必要）
 */
export default function AdminPage() {
  const { user, isLoading, hasPermission } = useRequireAuth({ 
    requiredRole: 'admin' 
  });

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
        <h1 className="text-3xl font-bold mb-8">管理者ダッシュボード</h1>
        
        <div className="bg-gray-800 rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">管理者情報</h2>
          <div className="space-y-2">
            <p>
              <span className="text-gray-400">名前:</span>{' '}
              <span className="text-white">{user?.full_name}</span>
            </p>
            <p>
              <span className="text-gray-400">メール:</span>{' '}
              <span className="text-white">{user?.email}</span>
            </p>
            <p>
              <span className="text-gray-400">ロール:</span>{' '}
              <span className="text-red-400 font-semibold">{user?.role}</span>
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-gray-800 rounded-lg p-6 hover:bg-gray-700 cursor-pointer transition-colors">
            <h3 className="text-lg font-semibold mb-2">ユーザー管理</h3>
            <p className="text-gray-400">システムユーザーの管理</p>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-6 hover:bg-gray-700 cursor-pointer transition-colors">
            <h3 className="text-lg font-semibold mb-2">承認グループ管理</h3>
            <p className="text-gray-400">承認グループの設定</p>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-6 hover:bg-gray-700 cursor-pointer transition-colors">
            <h3 className="text-lg font-semibold mb-2">システム設定</h3>
            <p className="text-gray-400">システム全体の設定</p>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-6 hover:bg-gray-700 cursor-pointer transition-colors">
            <h3 className="text-lg font-semibold mb-2">監査ログ</h3>
            <p className="text-gray-400">システムの操作履歴</p>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-6 hover:bg-gray-700 cursor-pointer transition-colors">
            <h3 className="text-lg font-semibold mb-2">統計情報</h3>
            <p className="text-gray-400">システム利用統計</p>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-6 hover:bg-gray-700 cursor-pointer transition-colors">
            <h3 className="text-lg font-semibold mb-2">バックアップ</h3>
            <p className="text-gray-400">データのバックアップ管理</p>
          </div>
        </div>
      </div>
    </div>
  );
}