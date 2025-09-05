'use client';

/**
 * ホームページ
 */

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { getUserDisplayName, getRoleDisplayName } from '@/lib/auth/utils';

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated, isLoading, user, logout } = useAuth();

  // 認証済みユーザーはダッシュボードへリダイレクト
  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white">認証状態を確認しています...</div>
      </div>
    );
  }

  // 認証済みの場合はリダイレクト処理中
  if (isAuthenticated) {
    return null;
  }

  // 未認証ユーザー向けのランディングページ
  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <div className="max-w-md text-center">
        <h1 className="text-3xl font-bold text-white mb-4">
          KSAP - Knowledge System Approval Platform
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
        <div className="mt-8">
          <a
            href="/api-test"
            className="text-gray-400 hover:text-gray-300 text-sm underline"
          >
            API接続テスト
          </a>
        </div>
      </div>
    </div>
  );

}
