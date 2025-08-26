'use client';

import { useRequireAuth } from '@/hooks/useRequireAuth';
import { MainLayout } from '@/components/layout';

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
    <MainLayout>
      <div className="text-white">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">承認管理</h1>
          <p className="text-gray-400 mt-2">承認待ちの修正案を確認し、承認または却下を行います</p>
        </div>
        
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
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">承認待ち</h3>
              <svg className="w-8 h-8 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-3xl font-bold text-yellow-400 mt-2">0</p>
            <p className="text-gray-400 text-sm">承認が必要な修正案</p>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">承認済み</h3>
              <svg className="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-3xl font-bold text-green-400 mt-2">0</p>
            <p className="text-gray-400 text-sm">今月承認した件数</p>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">却下</h3>
              <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <p className="text-3xl font-bold text-red-400 mt-2">0</p>
            <p className="text-gray-400 text-sm">今月却下した件数</p>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">保留中</h3>
              <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-3xl font-bold text-gray-400 mt-2">0</p>
            <p className="text-gray-400 text-sm">確認中の修正案</p>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-xl font-semibold mb-4">承認待ちリスト</h3>
          <div className="text-center py-12 text-gray-400">
            <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="text-lg">現在、承認待ちの修正案はありません</p>
            <p className="text-sm mt-2">新しい修正案が提出されると、ここに表示されます</p>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}