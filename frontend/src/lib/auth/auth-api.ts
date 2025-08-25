/**
 * 認証関連のAPI通信
 */

import { apiClient } from '../api';
import { LoginCredentials, AuthToken, User } from '@/types/user';
import { AuthenticationError } from '@/types/auth';

export class AuthAPI {
  /**
   * ログイン（JSON形式）
   */
  static async login(email: string, password: string): Promise<AuthToken> {
    try {
      const response = await apiClient.post<AuthToken>('/auth/login/json', {
        email,
        password
      });
      return response.data;
    } catch (error: any) {
      console.error('Login API Error:', error);
      
      // API エラーレスポンスをチェック
      if (error.response) {
        const { status, data } = error.response;
        console.error('Response Error:', { status, data });
        
        throw new AuthenticationError(
          data?.detail || 'ログインに失敗しました',
          data?.error_code || 'login_failed',
          status
        );
      }
      
      if (error.request) {
        console.error('Network Error - no response received:', error.request);
        throw new AuthenticationError(
          'サーバーに接続できません。バックエンドサーバーが起動しているか確認してください。',
          'network_error'
        );
      }
      
      console.error('Unknown Error:', error);
      throw new AuthenticationError(
        error.message || 'ネットワークエラーが発生しました',
        'network_error'
      );
    }
  }

  /**
   * 現在のユーザー情報を取得
   */
  static async getCurrentUser(): Promise<User> {
    try {
      const response = await apiClient.get<User>('/auth/me');
      return response.data;
    } catch (error: any) {
      console.error('Get Current User API Error:', error);
      
      if (error.response) {
        const { status, data } = error.response;
        console.error('Response Error:', { status, data });
        
        throw new AuthenticationError(
          data?.detail || 'ユーザー情報の取得に失敗しました',
          data?.error_code || 'user_info_failed',
          status
        );
      }
      
      if (error.request) {
        console.error('Network Error - no response received:', error.request);
        throw new AuthenticationError(
          'サーバーに接続できません。バックエンドサーバーが起動しているか確認してください。',
          'network_error'
        );
      }
      
      console.error('Unknown Error:', error);
      throw new AuthenticationError(
        error.message || 'ネットワークエラーが発生しました',
        'network_error'
      );
    }
  }

  /**
   * トークンのテスト（有効性確認）
   */
  static async testToken(): Promise<{ valid: boolean; message?: string }> {
    try {
      const response = await apiClient.post<{ message: string }>('/auth/test-token');
      return { 
        valid: true, 
        message: response.data.message 
      };
    } catch (error: any) {
      if (error.response) {
        const { status, data } = error.response;
        return {
          valid: false,
          message: data?.detail || 'トークンが無効です'
        };
      }
      
      return {
        valid: false,
        message: 'ネットワークエラーが発生しました'
      };
    }
  }

  /**
   * ユーザー登録
   */
  static async register(userData: {
    username: string;
    email: string;
    password: string;
    full_name: string;
    sweet_name?: string;
    ctstage_name?: string;
  }): Promise<User> {
    try {
      const response = await apiClient.post<User>('/auth/register', userData);
      return response.data;
    } catch (error: any) {
      if (error.response) {
        const { status, data } = error.response;
        throw new AuthenticationError(
          data?.detail || 'ユーザー登録に失敗しました',
          data?.error_code || 'registration_failed',
          status
        );
      }
      
      throw new AuthenticationError(
        'ネットワークエラーが発生しました',
        'network_error'
      );
    }
  }
}