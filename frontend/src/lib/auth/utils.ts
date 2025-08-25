/**
 * 認証関連のユーティリティ関数
 */

import { User, UserRole } from '@/types/user';

/**
 * ユーザーが特定のロールを持っているかチェック
 */
export function hasRole(user: User | null, role: UserRole | UserRole[]): boolean {
  if (!user) return false;
  
  const roles = Array.isArray(role) ? role : [role];
  return roles.includes(user.role);
}

/**
 * ユーザーが管理者かチェック
 */
export function isAdmin(user: User | null): boolean {
  return user?.role === 'admin';
}

/**
 * ユーザーが承認者かチェック（承認者または管理者）
 */
export function isApprover(user: User | null): boolean {
  return user?.role === 'approver' || user?.role === 'admin';
}

/**
 * ユーザーが一般ユーザーかチェック
 */
export function isUser(user: User | null): boolean {
  return user?.role === 'user';
}

/**
 * ユーザーがアクティブかチェック
 */
export function isActiveUser(user: User | null): boolean {
  return user?.is_active === true;
}

/**
 * ユーザーが承認グループに所属しているかチェック
 */
export function hasApprovalGroup(user: User | null): boolean {
  return !!user?.approval_group_id;
}

/**
 * ユーザーの表示名を取得（優先度: sweet_name > full_name > username）
 */
export function getUserDisplayName(user: User | null): string {
  if (!user) return 'Unknown User';
  
  return user.sweet_name || user.full_name || user.username;
}

/**
 * ユーザーのロール表示名を取得
 */
export function getRoleDisplayName(role: UserRole): string {
  const roleNames: Record<UserRole, string> = {
    admin: '管理者',
    approver: '承認者',
    user: 'ユーザー',
  };
  
  return roleNames[role] || role;
}

/**
 * 認証エラーメッセージを日本語に変換
 */
export function getAuthErrorMessage(error: any): string {
  if (error?.code) {
    const errorMessages: Record<string, string> = {
      'login_failed': 'ユーザー名またはパスワードが正しくありません',
      'network_error': 'ネットワークエラーが発生しました',
      'token_expired': 'セッションが期限切れです。再度ログインしてください',
      'unauthorized': '認証が必要です',
      'forbidden': 'この操作を実行する権限がありません',
      'user_info_failed': 'ユーザー情報の取得に失敗しました',
      'registration_failed': 'ユーザー登録に失敗しました',
    };
    
    return errorMessages[error.code] || error.message;
  }
  
  if (error?.status === 401) {
    return 'ユーザー名またはパスワードが正しくありません';
  }
  
  if (error?.status === 403) {
    return 'この操作を実行する権限がありません';
  }
  
  if (error?.status === 422) {
    return '入力内容に誤りがあります';
  }
  
  return error?.message || '予期しないエラーが発生しました';
}