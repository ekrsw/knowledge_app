'use client';

/**
 * ホームページ（一時的な実装）
 */

import React from 'react';
import { useAuth } from '@/hooks/useAuth';
import { getUserDisplayName, getRoleDisplayName } from '@/lib/auth/utils';

export default function HomePage() {
  const { isAuthenticated, isLoading, user, logout } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white">認証状態を確認しています...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="max-w-md text-center">
          <h1 className="text-3xl font-bold text-white mb-4">
            ナレッジ改訂システム
          </h1>
          <p className="text-gray-300 mb-8">
            このシステムを利用するにはログインが必要です。
          </p>
          <a
            href="/login"
            className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-lg transition-colors"
          >
            ログインページへ
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-white">
            ナレッジ改訂システム
          </h1>
          <button
            onClick={logout}
            className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
          >
            ログアウト
          </button>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-white mb-4">
            ユーザー情報
          </h2>
          {user && (
            <div className="space-y-2 text-gray-300">
              <p><strong>表示名:</strong> {getUserDisplayName(user)}</p>
              <p><strong>ユーザー名:</strong> {user.username}</p>
              <p><strong>ロール:</strong> {getRoleDisplayName(user.role)}</p>
              <p><strong>メール:</strong> {user.email}</p>
              {user.approval_group_id && (
                <p><strong>承認グループ:</strong> {user.approval_group_id}</p>
              )}
            </div>
          )}
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-4">
            利用可能な機能
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="bg-gray-700 rounded-lg p-4">
              <h3 className="font-medium text-white mb-2">改訂提案</h3>
              <p className="text-gray-300 text-sm">
                ナレッジの改訂を提案する
              </p>
            </div>
            <div className="bg-gray-700 rounded-lg p-4">
              <h3 className="font-medium text-white mb-2">承認管理</h3>
              <p className="text-gray-300 text-sm">
                改訂提案を承認・却下する
              </p>
            </div>
            <div className="bg-gray-700 rounded-lg p-4">
              <h3 className="font-medium text-white mb-2">履歴確認</h3>
              <p className="text-gray-300 text-sm">
                改訂履歴を確認する
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
