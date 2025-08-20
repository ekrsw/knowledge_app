import apiClient from '../api';
import {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  User,
} from '../../types/api';

export class AuthService {
  // Login with JSON body
  async login(credentials: LoginRequest): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>(
      '/auth/login/json',
      credentials
    );
    
    // Store token in client
    apiClient.setAuthToken(response.access_token);
    
    return response;
  }

  // Register new user
  async register(userData: RegisterRequest): Promise<User> {
    return apiClient.post<User>('/auth/register', userData);
  }

  // Get current user info
  async getCurrentUser(): Promise<User> {
    return apiClient.get<User>('/auth/me');
  }

  // Test token validity
  async testToken(): Promise<{ valid: boolean; user?: User }> {
    try {
      const user = await this.getCurrentUser();
      return { valid: true, user };
    } catch {
      return { valid: false };
    }
  }

  // Logout
  logout(): void {
    apiClient.removeAuthToken();
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    if (typeof window === 'undefined') return false;
    const token = localStorage.getItem('access_token');
    return !!token;
  }

  // Get stored token
  getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('access_token');
  }
}

export const authService = new AuthService();