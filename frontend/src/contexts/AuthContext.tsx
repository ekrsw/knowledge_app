'use client';

import { createContext, useContext, useEffect, useReducer, ReactNode } from 'react';
import { AuthContextType, AuthState, AuthenticationError } from '@/types/auth';
import { User, UserRole } from '@/types/user';
import { TokenStorage } from '@/lib/auth/token-storage';
import { AuthAPI } from '@/lib/auth/auth-api';

// 認証状態のアクション定義
type AuthAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_AUTHENTICATED'; payload: { user: User; token: string } }
  | { type: 'SET_USER'; payload: User }
  | { type: 'LOGOUT' }
  | { type: 'INIT_FROM_STORAGE'; payload: { user: User | null; token: string | null } };

// 認証状態の初期値
const initialAuthState: AuthState = {
  isAuthenticated: false,
  isLoading: true,
  user: null,
  token: null,
};

// 認証状態のリデューサー
function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    
    case 'SET_AUTHENTICATED':
      return {
        isAuthenticated: true,
        isLoading: false,
        user: action.payload.user,
        token: action.payload.token,
      };
    
    case 'SET_USER':
      return {
        ...state,
        user: action.payload,
      };
    
    case 'LOGOUT':
      return {
        isAuthenticated: false,
        isLoading: false,
        user: null,
        token: null,
      };
    
    case 'INIT_FROM_STORAGE':
      return {
        isAuthenticated: !!action.payload.token && !!action.payload.user,
        isLoading: false,
        user: action.payload.user,
        token: action.payload.token,
      };
    
    default:
      return state;
  }
}

// 認証コンテキストの作成
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// 認証プロバイダーのProps
interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [state, dispatch] = useReducer(authReducer, initialAuthState);

  // 初期化時にストレージから認証情報を復元
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const token = TokenStorage.getToken();
        const storedUser = TokenStorage.getUser();

        if (token && TokenStorage.isTokenValid(token)) {
          if (storedUser) {
            dispatch({
              type: 'INIT_FROM_STORAGE',
              payload: { user: storedUser, token }
            });
          } else {
            // トークンがあるがユーザー情報がない場合、APIから取得
            try {
              const user = await AuthAPI.getCurrentUser();
              TokenStorage.setUser(user);
              dispatch({
                type: 'SET_AUTHENTICATED',
                payload: { user, token }
              });
            } catch (error) {
              // API から取得できない場合はログアウト
              TokenStorage.clear();
              dispatch({ type: 'LOGOUT' });
            }
          }
        } else {
          // 無効なトークンの場合はクリア
          TokenStorage.clear();
          dispatch({ type: 'LOGOUT' });
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        TokenStorage.clear();
        dispatch({ type: 'LOGOUT' });
      }
    };

    initializeAuth();
  }, []);

  // ログイン処理
  const login = async (email: string, password: string): Promise<void> => {
    dispatch({ type: 'SET_LOADING', payload: true });

    try {
      // ログインAPIを呼び出し
      const tokenResponse = await AuthAPI.login(email, password);
      
      // トークンを保存
      TokenStorage.setToken(tokenResponse.access_token);
      
      // ユーザー情報を取得
      const user = await AuthAPI.getCurrentUser();
      
      // ユーザー情報を保存
      TokenStorage.setUser(user);
      
      // 状態を更新
      dispatch({
        type: 'SET_AUTHENTICATED',
        payload: { user, token: tokenResponse.access_token }
      });
    } catch (error) {
      dispatch({ type: 'SET_LOADING', payload: false });
      throw error;
    }
  };

  // ログアウト処理
  const logout = (): void => {
    TokenStorage.clear();
    dispatch({ type: 'LOGOUT' });
  };

  // ユーザー情報の再取得
  const refreshUserInfo = async (): Promise<void> => {
    if (!state.token) {
      throw new AuthenticationError('認証されていません');
    }

    try {
      const user = await AuthAPI.getCurrentUser();
      TokenStorage.setUser(user);
      dispatch({ type: 'SET_USER', payload: user });
    } catch (error) {
      // ユーザー情報の取得に失敗した場合はログアウト
      logout();
      throw error;
    }
  };

  // ロールチェック関数
  const hasRole = (role: string | string[]): boolean => {
    if (!state.user) return false;
    
    const roles = Array.isArray(role) ? role : [role];
    return roles.includes(state.user.role);
  };

  // 管理者かどうかを判定
  const isAdmin = state.user?.role === 'admin';

  // 承認者かどうかを判定（承認者または管理者）
  const isApprover = state.user?.role === 'approver' || state.user?.role === 'admin';

  const contextValue: AuthContextType = {
    // 認証状態
    isAuthenticated: state.isAuthenticated,
    isLoading: state.isLoading,
    user: state.user,
    token: state.token,
    
    // 認証操作
    login,
    logout,
    refreshUserInfo,
    
    // ユーティリティ
    hasRole,
    isAdmin,
    isApprover,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

// 認証コンテキストを使用するカスタムフック
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}