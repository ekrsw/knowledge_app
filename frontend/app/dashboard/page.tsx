'use client';

import { useRequireAuth } from '@/hooks/useRequireAuth';
import { MainLayout } from '@/components/layout';

/**
 * ダッシュボードページ（認証が必要）
 */
export default function DashboardPage() {
  const { user, isLoading, hasPermission } = useRequireAuth();

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
    <MainLayout>
      <div className="text-white">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">ダッシュボード</h1>
          <p className="text-gray-400 mt-2">システムの概要と最新の活動を確認できます</p>
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
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">修正案</h3>
              <svg className="w-8 h-8 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p className="text-3xl font-bold text-blue-400 mt-2">0</p>
            <p className="text-gray-400 text-sm">作成した修正案</p>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">承認待ち</h3>
              <svg className="w-8 h-8 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-3xl font-bold text-yellow-400 mt-2">0</p>
            <p className="text-gray-400 text-sm">承認待ちの修正案</p>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">承認済み</h3>
              <svg className="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-3xl font-bold text-green-400 mt-2">0</p>
            <p className="text-gray-400 text-sm">承認された修正案</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">最近の活動</h3>
            <div className="space-y-3">
              <div className="flex items-center space-x-3 text-sm">
                <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                <span className="text-gray-300">まだ活動はありません</span>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">クイックアクション</h3>
            <div className="space-y-3">
              <button className="w-full text-left px-4 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors">
                <div className="flex items-center space-x-3">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  <span>新しい修正案を作成</span>
                </div>
              </button>
              <button className="w-full text-left px-4 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">
                <div className="flex items-center space-x-3">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span>修正案一覧を見る</span>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}