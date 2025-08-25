/**
 * JWTトークンのローカルストレージ管理
 */

const TOKEN_KEY = 'knowledge_app_token';
const USER_KEY = 'knowledge_app_user';

export class TokenStorage {
  /**
   * トークンを保存
   */
  static setToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem(TOKEN_KEY, token);
    }
  }

  /**
   * トークンを取得
   */
  static getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(TOKEN_KEY);
    }
    return null;
  }

  /**
   * トークンを削除
   */
  static removeToken(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(TOKEN_KEY);
    }
  }

  /**
   * ユーザー情報を保存
   */
  static setUser(user: any): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    }
  }

  /**
   * ユーザー情報を取得
   */
  static getUser(): any | null {
    if (typeof window !== 'undefined') {
      const userStr = localStorage.getItem(USER_KEY);
      if (userStr) {
        try {
          return JSON.parse(userStr);
        } catch (error) {
          console.error('Failed to parse user data:', error);
          TokenStorage.removeUser();
        }
      }
    }
    return null;
  }

  /**
   * ユーザー情報を削除
   */
  static removeUser(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(USER_KEY);
    }
  }

  /**
   * 全ての認証データをクリア
   */
  static clear(): void {
    TokenStorage.removeToken();
    TokenStorage.removeUser();
  }

  /**
   * トークンの有効性を簡単にチェック
   * 注意: これは基本的なチェックのみで、サーバー側での検証が必要
   */
  static isTokenValid(token?: string): boolean {
    const tokenToCheck = token || TokenStorage.getToken();
    
    if (!tokenToCheck) {
      return false;
    }

    try {
      // JWTの基本構造チェック（3つの部分に分かれているか）
      const parts = tokenToCheck.split('.');
      if (parts.length !== 3) {
        return false;
      }

      // ペイロードをデコードして有効期限をチェック
      const payload = JSON.parse(atob(parts[1]));
      const currentTime = Math.floor(Date.now() / 1000);
      
      // expフィールドがあり、現在時刻より後であることをチェック
      if (payload.exp && payload.exp < currentTime) {
        return false;
      }

      return true;
    } catch (error) {
      console.error('Token validation error:', error);
      return false;
    }
  }

  /**
   * トークンから有効期限を取得
   */
  static getTokenExpiration(token?: string): Date | null {
    const tokenToCheck = token || TokenStorage.getToken();
    
    if (!tokenToCheck) {
      return null;
    }

    try {
      const parts = tokenToCheck.split('.');
      if (parts.length !== 3) {
        return null;
      }

      const payload = JSON.parse(atob(parts[1]));
      if (payload.exp) {
        return new Date(payload.exp * 1000);
      }

      return null;
    } catch (error) {
      console.error('Failed to get token expiration:', error);
      return null;
    }
  }
}