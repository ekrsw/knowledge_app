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

        {/* 統計サマリー */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <div className="bg-gray-800 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-gray-400">下書き</h3>
              <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </div>
            <p className="text-2xl font-bold text-white mt-2">0</p>
            <p className="text-gray-500 text-xs">下書き中の修正案</p>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-gray-400">承認待ち</h3>
              <svg className="w-6 h-6 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-2xl font-bold text-yellow-400 mt-2">0</p>
            <p className="text-gray-500 text-xs">承認待ち</p>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-gray-400">承認済み</h3>
              <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-2xl font-bold text-green-400 mt-2">0</p>
            <p className="text-gray-500 text-xs">承認済み</p>
          </div>

          <div className="bg-gray-800 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-gray-400">却下</h3>
              <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-2xl font-bold text-red-400 mt-2">0</p>
            <p className="text-gray-500 text-xs">却下された修正案</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 承認が必要な修正案 */}
          {user?.role === 'approver' || user?.role === 'admin' ? (
            <div className="bg-gray-800 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">承認が必要な修正案</h3>
                <span className="text-xs text-yellow-400 bg-yellow-400/10 px-2 py-1 rounded">要対応</span>
              </div>
              <div className="space-y-3">
                <div className="text-gray-400 text-sm">
                  現在承認待ちの修正案はありません
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">自分の修正案</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-400">下書き</span>
                  <span className="text-white">0件</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-400">提出済み</span>
                  <span className="text-yellow-400">0件</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-400">承認済み</span>
                  <span className="text-green-400">0件</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-400">却下済み</span>
                  <span className="text-red-400">0件</span>
                </div>
              </div>
            </div>
          )}

          {/* 最近の通知 */}
          <div className="bg-gray-800 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">最近の通知</h3>
              <button className="text-xs text-blue-400 hover:text-blue-300">すべて表示</button>
            </div>
            <div className="space-y-3">
              <div className="text-gray-400 text-sm">
                新しい通知はありません
              </div>
            </div>
          </div>
        </div>

        {/* クイックアクション */}
        <div className="mt-6">
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">クイックアクション</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              <button 
                onClick={() => window.location.href = '/revisions/new'}
                className="flex items-center justify-center space-x-2 px-4 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                <span>新しい修正案を作成</span>
              </button>
              
              <button 
                onClick={() => window.location.href = '/revisions'}
                className="flex items-center justify-center space-x-2 px-4 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span>修正案一覧</span>
              </button>

              {(user?.role === 'approver' || user?.role === 'admin') && (
                <button 
                  onClick={() => window.location.href = '/approvals'}
                  className="flex items-center justify-center space-x-2 px-4 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                  </svg>
                  <span>承認キュー</span>
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}