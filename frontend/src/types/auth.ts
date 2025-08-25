/**
 * 認証関連の型定義
 */

import { User } from './user';

export interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: User | null;
  token: string | null;
}

export interface AuthContextType {
  // 認証状態
  isAuthenticated: boolean;
  isLoading: boolean;
  user: User | null;
  token: string | null;
  
  // 認証操作
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUserInfo: () => Promise<void>;
  
  // ユーティリティ
  hasRole: (role: string | string[]) => boolean;
  isAdmin: boolean;
  isApprover: boolean;
}

export interface AuthError {
  message: string;
  code?: string;
  status?: number;
}

export class AuthenticationError extends Error {
  constructor(
    message: string,
    public code?: string,
    public status?: number
  ) {
    super(message);
    this.name = 'AuthenticationError';
  }
  
  toString(): string {
    return `${this.name}: ${this.message} (code: ${this.code || 'unknown'}, status: ${this.status || 'unknown'})`;
  }
}