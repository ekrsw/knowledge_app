'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { UserRole } from '@/types/user';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: UserRole | UserRole[];
  fallbackUrl?: string;
}

/**
 * 認証が必要なルートを保護するコンポーネント
 * 
 * @param children - 保護されるコンテンツ
 * @param requiredRole - アクセスに必要なロール（単一または複数）
 * @param fallbackUrl - アクセス拒否時のリダイレクト先
 */
export function ProtectedRoute({ 
  children, 
  requiredRole,
  fallbackUrl = '/unauthorized'
}: ProtectedRouteProps) {
  const router = useRouter();
  const { isAuthenticated, isLoading, user, hasRole } = useAuth();

  useEffect(() => {
    // ローディング中は何もしない
    if (isLoading) {
      return;
    }

    // 未認証の場合はログインページへ
    if (!isAuthenticated) {
      router.replace(`/login?returnUrl=${encodeURIComponent(window.location.pathname)}`);
      return;
    }

    // ロールチェック
    if (requiredRole) {
      const roles = Array.isArray(requiredRole) ? requiredRole : [requiredRole];
      
      if (!hasRole(roles)) {
        // 権限がない場合はfallbackUrlへリダイレクト
        router.replace(fallbackUrl);
      }
    }
  }, [isAuthenticated, isLoading, user, requiredRole, router, hasRole, fallbackUrl]);

  // ローディング中の表示
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

  // 未認証の場合は何も表示しない（リダイレクト処理中）
  if (!isAuthenticated) {
    return null;
  }

  // ロールチェック
  if (requiredRole) {
    const roles = Array.isArray(requiredRole) ? requiredRole : [requiredRole];
    if (!hasRole(roles)) {
      return null; // リダイレクト処理中
    }
  }

  // 認証済みかつ権限がある場合は子要素を表示
  return <>{children}</>;
}