/**
 * 認証関連モジュールのエクスポート
 */

// API
export { AuthAPI } from './auth-api';

// ストレージ
export { TokenStorage } from './token-storage';

// ユーティリティ
export {
  hasRole,
  isAdmin,
  isApprover,
  isUser,
  isActiveUser,
  hasApprovalGroup,
  getUserDisplayName,
  getRoleDisplayName,
  getAuthErrorMessage,
} from './utils';

// 型定義
export type {
  AuthState,
  AuthContextType,
  AuthError,
} from '@/types/auth';

export { AuthenticationError } from '@/types/auth';