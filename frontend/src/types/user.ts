/**
 * ユーザー関連の型定義
 */

export type UserRole = 'user' | 'approver' | 'admin';

export interface User {
  id: string;  // UUID
  username: string;
  email: string;
  full_name: string;
  sweet_name?: string | null;
  ctstage_name?: string | null;
  role: UserRole;
  approval_group_id?: string | null;  // UUID
  is_active: boolean;
  created_at: string;  // ISO 8601 datetime
  updated_at: string;  // ISO 8601 datetime
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
  full_name: string;
  sweet_name?: string | null;
  ctstage_name?: string | null;
  role?: UserRole;
  approval_group_id?: string | null;
}

export interface UserUpdate {
  email?: string;
  full_name?: string;
  sweet_name?: string | null;
  ctstage_name?: string | null;
  role?: UserRole;
  approval_group_id?: string | null;
  is_active?: boolean;
}

export interface UserPasswordUpdate {
  current_password: string;
  new_password: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}