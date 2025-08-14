/**
 * 認証関連の便利なフック
 */

import { useAuth as useAuthContext } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

/**
 * 基本的な認証フック（useAuthContextのエイリアス）
 */
export const useAuth = useAuthContext;

/**
 * 認証が完了するまで待機するフック
 */
export function useAuthReady() {
  const auth = useAuth();
  return !auth.isLoading;
}

/**
 * 認証が必要なページ用のフック
 * 未認証の場合はログインページにリダイレクト
 */
export function useRequireAuth() {
  const auth = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!auth.isLoading && !auth.isAuthenticated) {
      router.push('/login');
    }
  }, [auth.isLoading, auth.isAuthenticated, router]);

  return auth;
}

/**
 * 特定のロールが必要なページ用のフック
 */
export function useRequireRole(requiredRole: string | string[]) {
  const auth = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!auth.isLoading) {
      if (!auth.isAuthenticated) {
        router.push('/login');
      } else if (!auth.hasRole(requiredRole)) {
        router.push('/unauthorized');
      }
    }
  }, [auth.isLoading, auth.isAuthenticated, auth.hasRole, requiredRole, router]);

  return auth;
}

/**
 * 管理者権限が必要なページ用のフック
 */
export function useRequireAdmin() {
  return useRequireRole('admin');
}

/**
 * 承認者権限が必要なページ用のフック
 */
export function useRequireApprover() {
  return useRequireRole(['approver', 'admin']);
}

/**
 * ログイン状態を監視するフック
 */
export function useAuthStatus() {
  const auth = useAuth();
  
  return {
    isAuthenticated: auth.isAuthenticated,
    isLoading: auth.isLoading,
    user: auth.user,
    hasError: !!auth.error,
    error: auth.error,
  };
}

/**
 * ユーザーの権限情報を取得するフック
 */
export function useUserPermissions() {
  const auth = useAuth();
  
  return {
    isAdmin: auth.isAdmin(),
    isApprover: auth.isApprover(),
    canViewAllRevisions: auth.hasPermission('view_all_revisions'),
    canApproveRevisions: auth.hasPermission('approve_revisions'),
    canManageUsers: auth.hasPermission('manage_users'),
    hasRole: auth.hasRole,
    hasPermission: auth.hasPermission,
  };
}