'use client';

/**
 * 認証コンテキスト
 * アプリケーション全体で認証状態を管理
 */

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { User, LoginRequest, LoginResponse, TokenPayload } from '@/types';
import { api } from '@/lib/api/client';
import { API_ENDPOINTS } from '@/lib/api/endpoints';
import { TokenManager, SessionManager, checkAuthStatus, decodeToken } from '@/utils/auth';
import { handleApiError, AppError } from '@/utils/error-handler';

// 認証状態の型定義
interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: User | null;
  token: string | null;
  error: AppError | null;
}

// 認証コンテキストの型定義
export interface AuthContextType extends AuthState {
  // 認証アクション
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => void;
  refreshAuth: () => Promise<void>;
  clearError: () => void;
  
  // ユーザー情報更新
  updateUser: (userData: Partial<User>) => void;
  
  // 権限チェック
  hasRole: (role: string | string[]) => boolean;
  hasPermission: (permission: string) => boolean;
  isAdmin: () => boolean;
  isApprover: () => boolean;
}

// 初期状態
const initialState: AuthState = {
  isAuthenticated: false,
  isLoading: true,
  user: null,
  token: null,
  error: null,
};

// コンテキスト作成
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// プロバイダープロパティ
interface AuthProviderProps {
  children: React.ReactNode;
}

/**
 * 認証プロバイダー
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const [state, setState] = useState<AuthState>(initialState);

  /**
   * 認証状態を更新
   */
  const updateAuthState = useCallback((updates: Partial<AuthState>) => {
    setState(prev => ({ ...prev, ...updates }));
  }, []);

  /**
   * エラーをクリア
   */
  const clearError = useCallback(() => {
    updateAuthState({ error: null });
  }, [updateAuthState]);

  /**
   * ユーザー情報を取得
   */
  const fetchUser = useCallback(async (token: string): Promise<User | null> => {
    try {
      const response = await api.get<User>(API_ENDPOINTS.AUTH.ME);
      return response.data;
    } catch (error) {
      const appError = handleApiError(error);
      console.error('Failed to fetch user:', appError);
      
      // 認証エラーの場合はトークンをクリア
      if (appError.statusCode === 401 || appError.statusCode === 403) {
        TokenManager.clearToken();
      }
      
      return null;
    }
  }, []);

  /**
   * 認証状態を初期化
   */
  const initializeAuth = useCallback(async () => {
    updateAuthState({ isLoading: true, error: null });

    try {
      const authStatus = checkAuthStatus();
      
      if (!authStatus.isAuthenticated) {
        updateAuthState({
          isAuthenticated: false,
          isLoading: false,
          user: null,
          token: null,
        });
        return;
      }

      // ユーザー情報を取得
      const user = await fetchUser(authStatus.user?.user_id || '');
      
      if (user) {
        updateAuthState({
          isAuthenticated: true,
          isLoading: false,
          user,
          token: TokenManager.getToken(),
          error: null,
        });
      } else {
        // ユーザー情報取得に失敗した場合はログアウト
        TokenManager.clearToken();
        updateAuthState({
          isAuthenticated: false,
          isLoading: false,
          user: null,
          token: null,
        });
      }
    } catch (error) {
      const appError = handleApiError(error);
      updateAuthState({
        isAuthenticated: false,
        isLoading: false,
        user: null,
        token: null,
        error: appError,
      });
    }
  }, [updateAuthState, fetchUser]);

  /**
   * ログイン
   */
  const login = useCallback(async (credentials: LoginRequest) => {
    updateAuthState({ isLoading: true, error: null });

    try {
      const response = await api.post<LoginResponse>(API_ENDPOINTS.AUTH.LOGIN, credentials);
      const { access_token, expires_in } = response.data;

      // トークンを保存
      TokenManager.setToken(access_token, expires_in);

      // ユーザー情報を取得
      const user = await fetchUser(access_token);
      
      if (user) {
        updateAuthState({
          isAuthenticated: true,
          isLoading: false,
          user,
          token: access_token,
          error: null,
        });
      } else {
        throw new Error('ユーザー情報の取得に失敗しました');
      }
    } catch (error) {
      const appError = handleApiError(error);
      TokenManager.clearToken();
      updateAuthState({
        isAuthenticated: false,
        isLoading: false,
        user: null,
        token: null,
        error: appError,
      });
      throw appError;
    }
  }, [updateAuthState, fetchUser]);

  /**
   * ログアウト
   */
  const logout = useCallback(() => {
    TokenManager.clearToken();
    updateAuthState({
      isAuthenticated: false,
      isLoading: false,
      user: null,
      token: null,
      error: null,
    });

    // ログインページにリダイレクト
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  }, [updateAuthState]);

  /**
   * 認証状態をリフレッシュ
   */
  const refreshAuth = useCallback(async () => {
    await initializeAuth();
  }, [initializeAuth]);

  /**
   * ユーザー情報を更新
   */
  const updateUser = useCallback((userData: Partial<User>) => {
    if (state.user) {
      const updatedUser = { ...state.user, ...userData };
      updateAuthState({ user: updatedUser });
    }
  }, [state.user, updateAuthState]);

  /**
   * ロールチェック
   */
  const hasRole = useCallback((role: string | string[]): boolean => {
    if (!state.user) return false;
    
    const userRole = state.user.role;
    if (Array.isArray(role)) {
      return role.some(r => r === userRole);
    }
    return userRole === role;
  }, [state.user]);

  /**
   * 権限チェック（将来的な拡張用）
   */
  const hasPermission = useCallback((permission: string): boolean => {
    if (!state.user) return false;
    
    const userRole = state.user.role;
    
    // 権限システムの実装（将来的に拡張）
    switch (permission) {
      case 'view_all_revisions':
        return userRole === 'admin' || userRole === 'approver';
      case 'approve_revisions':
        return userRole === 'admin' || userRole === 'approver';
      case 'manage_users':
        return userRole === 'admin';
      default:
        return false;
    }
  }, [state.user]);

  /**
   * 管理者かチェック
   */
  const isAdmin = useCallback((): boolean => {
    return hasRole('admin');
  }, [hasRole]);

  /**
   * 承認者かチェック
   */
  const isApprover = useCallback((): boolean => {
    if (!state.user) return false;
    return state.user.role === 'approver' || state.user.role === 'admin';
  }, [state.user]);

  // 初期化
  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  // トークン期限チェック（5分ごと）
  useEffect(() => {
    if (!state.isAuthenticated) return;

    const interval = setInterval(() => {
      const authStatus = checkAuthStatus();
      
      if (!authStatus.isAuthenticated) {
        logout();
      } else if (authStatus.needsRefresh) {
        // トークンリフレッシュの実装（将来的に追加）
        console.warn('Token needs refresh');
      }
    }, 5 * 60 * 1000); // 5分

    return () => clearInterval(interval);
  }, [state.isAuthenticated, logout]);

  const contextValue: AuthContextType = {
    ...state,
    login,
    logout,
    refreshAuth,
    clearError,
    updateUser,
    hasRole,
    hasPermission,
    isAdmin,
    isApprover,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * 認証コンテキストを使用するフック
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}

/**
 * 認証が必要なコンポーネント用のフック
 */
export function useRequireAuth() {
  const auth = useAuth();
  
  useEffect(() => {
    if (!auth.isLoading && !auth.isAuthenticated) {
      auth.logout();
    }
  }, [auth]);
  
  return auth;
}

/**
 * 特定のロールが必要なコンポーネント用のフック
 */
export function useRequireRole(requiredRole: string | string[]) {
  const auth = useAuth();
  
  useEffect(() => {
    if (!auth.isLoading && auth.isAuthenticated && !auth.hasRole(requiredRole)) {
      console.warn(`Access denied: Required role ${requiredRole}, but user has ${auth.user?.role}`);
      // 権限不足の場合の処理（エラーページへリダイレクトなど）
    }
  }, [auth, requiredRole]);
  
  return auth;
}