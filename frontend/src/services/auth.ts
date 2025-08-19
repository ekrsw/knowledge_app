import { apiClient } from '../lib/api-client';
import { LoginRequest, LoginResponse, User, TokenValidation } from '../types/models';
import { ApiResponse } from '../types/api';

export class AuthService {
  async login(credentials: LoginRequest): Promise<ApiResponse<LoginResponse>> {
    return apiClient.post<LoginResponse>('/auth/login', credentials);
  }

  async getCurrentUser(): Promise<ApiResponse<User>> {
    return apiClient.get<User>('/auth/me');
  }

  async testToken(): Promise<ApiResponse<TokenValidation>> {
    return apiClient.post<TokenValidation>('/auth/test-token');
  }

  setToken(token: string | null) {
    apiClient.setToken(token);
  }

  logout() {
    apiClient.setToken(null);
    localStorage.removeItem('token');
  }
}

export const authService = new AuthService();