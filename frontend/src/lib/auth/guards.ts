import { User, UserRole } from '@/types/user';

/**
 * ロールベースのアクセス制御ユーティリティ
 */

/**
 * ユーザーが指定されたロールを持っているかチェック
 */
export function hasRole(user: User | null, role: UserRole | UserRole[]): boolean {
  if (!user) return false;
  
  const roles = Array.isArray(role) ? role : [role];
  return roles.includes(user.role);
}

/**
 * ユーザーが管理者かどうかチェック
 */
export function isAdmin(user: User | null): boolean {
  return user?.role === 'admin';
}

/**
 * ユーザーが承認者かどうかチェック（承認者または管理者）
 */
export function isApprover(user: User | null): boolean {
  return user?.role === 'approver' || user?.role === 'admin';
}

/**
 * ユーザーが一般ユーザーかどうかチェック
 */
export function isUser(user: User | null): boolean {
  return user?.role === 'user';
}

/**
 * ユーザーが特定のリソースの所有者かどうかチェック
 */
export function isOwner(user: User | null, ownerId: string): boolean {
  return user?.id === ownerId;
}

/**
 * ユーザーがリソースにアクセスできるかチェック（所有者または管理者）
 */
export function canAccessResource(user: User | null, ownerId: string): boolean {
  return isOwner(user, ownerId) || isAdmin(user);
}

/**
 * パスに対するアクセス権限をチェック
 */
export function canAccessPath(user: User | null, path: string): boolean {
  // 公開パス
  const publicPaths = ['/login', '/api-test', '/'];
  if (publicPaths.some(p => path === p || path.startsWith(`${p}/`))) {
    return true;
  }

  // 認証が必要
  if (!user) return false;

  // 管理者専用パス
  const adminPaths = ['/admin', '/users'];
  if (adminPaths.some(p => path.startsWith(p))) {
    return isAdmin(user);
  }

  // 承認者専用パス
  const approverPaths = ['/approvals', '/approval-queue'];
  if (approverPaths.some(p => path.startsWith(p))) {
    return isApprover(user);
  }

  // その他の認証済みユーザーがアクセス可能なパス
  return true;
}

/**
 * 権限不足エラーメッセージを生成
 */
export function getPermissionErrorMessage(requiredRole?: UserRole | UserRole[]): string {
  if (!requiredRole) {
    return 'このページへのアクセス権限がありません。';
  }

  const roles = Array.isArray(requiredRole) ? requiredRole : [requiredRole];
  const roleLabels = roles.map(r => getRoleLabel(r)).join('または');
  
  return `このページには${roleLabels}権限が必要です。`;
}

/**
 * ロールのラベルを取得
 */
export function getRoleLabel(role: UserRole): string {
  const roleLabels: Record<UserRole, string> = {
    admin: '管理者',
    approver: '承認者',
    user: 'ユーザー'
  };
  
  return roleLabels[role] || role;
}

/**
 * ロールの優先順位を取得（権限の強さ）
 */
export function getRolePriority(role: UserRole): number {
  const priorities: Record<UserRole, number> = {
    admin: 3,
    approver: 2,
    user: 1
  };
  
  return priorities[role] || 0;
}

/**
 * より強い権限を持っているかチェック
 */
export function hasHigherRole(userRole: UserRole, requiredRole: UserRole): boolean {
  return getRolePriority(userRole) >= getRolePriority(requiredRole);
}