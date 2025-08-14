/**
 * ユーザー関連の型定義
 * バックエンドの user.py スキーマに対応
 */

export type UserRole = 'user' | 'approver' | 'admin';

export interface UserBase {
  username: string;
  email: string;
  full_name: string;
  sweet_name?: string | null;
  ctstage_name?: string | null;
  role: UserRole;
  approval_group_id?: string | null;
  is_active: boolean;
}

export interface UserCreate extends UserBase {
  password: string;
}

export interface UserUpdate {
  username?: string;
  email?: string;
  full_name?: string;
  sweet_name?: string | null;
  ctstage_name?: string | null;
  role?: UserRole;
  approval_group_id?: string | null;
  is_active?: boolean;
  password?: string;
}

export interface User extends UserBase {
  id: string;
  created_at: string;
  updated_at: string;
}

export interface CurrentUser extends User {
  // 現在のログインユーザーを表す際に使用
}

// ユーザー選択のための軽量な型
export interface UserOption {
  id: string;
  username: string;
  full_name: string;
  role: UserRole;
}