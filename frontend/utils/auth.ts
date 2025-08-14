/**
 * 認証関連のユーティリティ
 * JWT トークン管理、セッション管理、認証状態チェック
 */

import { TokenPayload } from '@/types/api';

// トークンストレージのキー
const TOKEN_KEY = 'authToken';
const REFRESH_TOKEN_KEY = 'refreshToken';
const TOKEN_EXPIRES_KEY = 'tokenExpires';

/**
 * JWTトークン管理クラス
 */
export class TokenManager {
  /**
   * トークンを保存
   */
  static setToken(token: string, expiresIn?: number): void {
    if (typeof window === 'undefined') return;

    try {
      localStorage.setItem(TOKEN_KEY, token);
      
      if (expiresIn) {
        const expiresAt = Date.now() + expiresIn * 1000;
        localStorage.setItem(TOKEN_EXPIRES_KEY, expiresAt.toString());
      }
    } catch (error) {
      console.error('Failed to save token:', error);
    }
  }

  /**
   * トークンを取得
   */
  static getToken(): string | null {
    if (typeof window === 'undefined') return null;

    try {
      const token = localStorage.getItem(TOKEN_KEY);
      if (!token) return null;

      // 有効期限チェック
      if (this.isTokenExpired()) {
        this.clearToken();
        return null;
      }

      return token;
    } catch (error) {
      console.error('Failed to get token:', error);
      return null;
    }
  }

  /**
   * リフレッシュトークンを保存
   */
  static setRefreshToken(refreshToken: string): void {
    if (typeof window === 'undefined') return;

    try {
      localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    } catch (error) {
      console.error('Failed to save refresh token:', error);
    }
  }

  /**
   * リフレッシュトークンを取得
   */
  static getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null;

    try {
      return localStorage.getItem(REFRESH_TOKEN_KEY);
    } catch (error) {
      console.error('Failed to get refresh token:', error);
      return null;
    }
  }

  /**
   * すべてのトークンをクリア
   */
  static clearToken(): void {
    if (typeof window === 'undefined') return;

    try {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(REFRESH_TOKEN_KEY);
      localStorage.removeItem(TOKEN_EXPIRES_KEY);
    } catch (error) {
      console.error('Failed to clear tokens:', error);
    }
  }

  /**
   * トークンが期限切れかチェック
   */
  static isTokenExpired(): boolean {
    if (typeof window === 'undefined') return true;

    try {
      const expiresAt = localStorage.getItem(TOKEN_EXPIRES_KEY);
      if (!expiresAt) return false; // 有効期限情報がない場合は期限切れとみなさない

      return Date.now() >= parseInt(expiresAt);
    } catch (error) {
      console.error('Failed to check token expiration:', error);
      return true;
    }
  }

  /**
   * トークンが存在するかチェック
   */
  static hasValidToken(): boolean {
    const token = this.getToken();
    return token !== null && !this.isTokenExpired();
  }
}

/**
 * JWT ペイロードをデコード
 */
export function decodeToken(token: string): TokenPayload | null {
  try {
    // JWT は base64url エンコードされている
    const payload = token.split('.')[1];
    if (!payload) return null;

    // base64url to base64
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
    
    // パディング追加
    const padded = base64 + '='.repeat((4 - base64.length % 4) % 4);
    
    // デコード
    const decoded = JSON.parse(atob(padded));
    
    return decoded as TokenPayload;
  } catch (error) {
    console.error('Failed to decode token:', error);
    return null;
  }
}

/**
 * トークンの有効性をチェック
 */
export function isTokenValid(token: string): boolean {
  try {
    const payload = decodeToken(token);
    if (!payload) return false;

    // 有効期限チェック (exp は秒単位)
    const now = Math.floor(Date.now() / 1000);
    return payload.exp > now;
  } catch (error) {
    console.error('Failed to validate token:', error);
    return false;
  }
}

/**
 * セッション管理クラス
 */
export class SessionManager {
  /**
   * セッションを開始
   */
  static startSession(token: string, expiresIn?: number): void {
    TokenManager.setToken(token, expiresIn);
  }

  /**
   * セッションを終了
   */
  static endSession(): void {
    TokenManager.clearToken();
  }

  /**
   * セッションが有効かチェック
   */
  static isSessionValid(): boolean {
    return TokenManager.hasValidToken();
  }

  /**
   * セッション情報を取得
   */
  static getSessionInfo(): {
    isValid: boolean;
    token: string | null;
    payload: TokenPayload | null;
    expiresAt: Date | null;
  } {
    const token = TokenManager.getToken();
    const isValid = this.isSessionValid();
    const payload = token ? decodeToken(token) : null;
    
    let expiresAt: Date | null = null;
    if (payload?.exp) {
      expiresAt = new Date(payload.exp * 1000);
    }

    return {
      isValid,
      token,
      payload,
      expiresAt,
    };
  }
}

/**
 * 認証状態チェック関数
 */
export function checkAuthStatus(): {
  isAuthenticated: boolean;
  user: TokenPayload | null;
  needsRefresh: boolean;
} {
  const token = TokenManager.getToken();
  
  if (!token) {
    return {
      isAuthenticated: false,
      user: null,
      needsRefresh: false,
    };
  }

  const payload = decodeToken(token);
  if (!payload) {
    TokenManager.clearToken();
    return {
      isAuthenticated: false,
      user: null,
      needsRefresh: false,
    };
  }

  const now = Math.floor(Date.now() / 1000);
  const isExpired = payload.exp <= now;
  const needsRefresh = payload.exp - now < 300; // 5分以内に期限切れ

  if (isExpired) {
    TokenManager.clearToken();
    return {
      isAuthenticated: false,
      user: null,
      needsRefresh: true,
    };
  }

  return {
    isAuthenticated: true,
    user: payload,
    needsRefresh,
  };
}

/**
 * ログアウト処理
 */
export function logout(): void {
  SessionManager.endSession();
  
  // ページリロードまたはログインページにリダイレクト
  if (typeof window !== 'undefined') {
    window.location.href = '/login';
  }
}

/**
 * 認証が必要なページかチェック
 */
export function requiresAuth(pathname: string): boolean {
  const publicPaths = ['/login', '/register', '/'];
  return !publicPaths.includes(pathname);
}

/**
 * 管理者権限が必要な操作かチェック
 */
export function requiresAdmin(userRole?: string): boolean {
  return userRole === 'admin';
}

/**
 * 承認者権限が必要な操作かチェック
 */
export function requiresApprover(userRole?: string): boolean {
  return userRole === 'approver' || userRole === 'admin';
}