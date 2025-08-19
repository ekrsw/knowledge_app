import { ApiResponse, ApiError } from '../types/api';

export class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
  }

  setToken(token: string | null) {
    this.token = token;
  }

  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    return headers;
  }

  private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
    try {
      const data = await response.json();

      if (!response.ok) {
        const error: ApiError = {
          status: response.status,
          message: data.detail || data.message || `HTTP ${response.status}`,
          code: data.code,
        };
        return { success: false, error };
      }

      return { success: true, data };
    } catch {
      const apiError: ApiError = {
        status: response.status,
        message: 'Failed to parse response',
        code: 'PARSE_ERROR',
      };
      return { success: false, error: apiError };
    }
  }

  async get<T>(endpoint: string, params?: Record<string, unknown>): Promise<ApiResponse<T>> {
    try {
      const url = new URL(`${this.baseUrl}${endpoint}`);
      if (params) {
        Object.entries(params).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            url.searchParams.append(key, String(value));
          }
        });
      }

      const response = await fetch(url.toString(), {
        method: 'GET',
        headers: this.getHeaders(),
      });

      return this.handleResponse<T>(response);
    } catch {
      return {
        success: false,
        error: {
          status: 0,
          message: 'Network error',
          code: 'NETWORK_ERROR',
        },
      };
    }
  }

  async post<T>(endpoint: string, data?: unknown): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: data ? JSON.stringify(data) : undefined,
      });

      return this.handleResponse<T>(response);
    } catch {
      return {
        success: false,
        error: {
          status: 0,
          message: 'Network error',
          code: 'NETWORK_ERROR',
        },
      };
    }
  }

  async put<T>(endpoint: string, data?: unknown): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'PUT',
        headers: this.getHeaders(),
        body: data ? JSON.stringify(data) : undefined,
      });

      return this.handleResponse<T>(response);
    } catch {
      return {
        success: false,
        error: {
          status: 0,
          message: 'Network error',
          code: 'NETWORK_ERROR',
        },
      };
    }
  }

  async patch<T>(endpoint: string, data?: unknown): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'PATCH',
        headers: this.getHeaders(),
        body: data ? JSON.stringify(data) : undefined,
      });

      return this.handleResponse<T>(response);
    } catch {
      return {
        success: false,
        error: {
          status: 0,
          message: 'Network error',
          code: 'NETWORK_ERROR',
        },
      };
    }
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'DELETE',
        headers: this.getHeaders(),
      });

      return this.handleResponse<T>(response);
    } catch {
      return {
        success: false,
        error: {
          status: 0,
          message: 'Network error',
          code: 'NETWORK_ERROR',
        },
      };
    }
  }
}

export const apiClient = new ApiClient();