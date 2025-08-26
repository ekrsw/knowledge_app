'use client';

import { useRequireAuth } from '@/hooks/useRequireAuth';

/**
 * 承認ページ（承認者または管理者権限が必要）
 */
export default function ApprovalsPage() {
  const { user, isLoading, hasPermission } = useRequireAuth({ 
    requiredRole: ['approver', 'admin'] 
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
        <h1 className="text-3xl font-bold mb-8">承認管理</h1>
        
        <div className="bg-gray-800 rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">承認者情報</h2>
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
              <span className="text-green-400 font-semibold">{user?.role}</span>
            </p>
            <p>
              <span className="text-gray-400">承認グループ:</span>{' '}
              <span className="text-white">{user?.approval_group_id || 'なし'}</span>
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-2">承認待ち</h3>
            <p className="text-3xl font-bold text-yellow-400">0</p>
            <p className="text-gray-400 text-sm">承認が必要な修正案</p>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-2">承認済み</h3>
            <p className="text-3xl font-bold text-green-400">0</p>
            <p className="text-gray-400 text-sm">今月承認した件数</p>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-2">却下</h3>
            <p className="text-3xl font-bold text-red-400">0</p>
            <p className="text-gray-400 text-sm">今月却下した件数</p>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-2">保留中</h3>
            <p className="text-3xl font-bold text-gray-400">0</p>
            <p className="text-gray-400 text-sm">確認中の修正案</p>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-xl font-semibold mb-4">承認待ちリスト</h3>
          <div className="text-center py-8 text-gray-400">
            <p>現在、承認待ちの修正案はありません</p>
          </div>
        </div>
      </div>
    </div>
  );
}