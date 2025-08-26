'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from './useAuth';
import { UserRole } from '@/types/user';

interface UseRequireAuthOptions {
  requiredRole?: UserRole | UserRole[];
  redirectTo?: string;
  fallbackUrl?: string;
}

/**
 * 認証が必要なページで使用するカスタムフック
 * 
 * @param options - 認証要件のオプション
 * @returns 認証状態とユーザー情報
 */
export function useRequireAuth(options: UseRequireAuthOptions = {}) {
  const router = useRouter();
  const { isAuthenticated, isLoading, user, hasRole } = useAuth();
  const { requiredRole, redirectTo = '/login', fallbackUrl = '/unauthorized' } = options;

  useEffect(() => {
    // ローディング中は何もしない
    if (isLoading) {
      return;
    }

    // 未認証の場合
    if (!isAuthenticated) {
      const returnUrl = encodeURIComponent(window.location.pathname);
      router.replace(`${redirectTo}?returnUrl=${returnUrl}`);
      return;
    }

    // ロールチェック
    if (requiredRole) {
      const roles = Array.isArray(requiredRole) ? requiredRole : [requiredRole];
      
      if (!hasRole(roles)) {
        router.replace(fallbackUrl);
      }
    }
  }, [isAuthenticated, isLoading, user, requiredRole, router, hasRole, redirectTo, fallbackUrl]);

  return {
    isAuthenticated,
    isLoading,
    user,
    hasRole,
    // 権限チェックの結果
    hasPermission: !requiredRole || (requiredRole && hasRole(requiredRole))
  };
}