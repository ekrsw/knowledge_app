import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { API_URL } from './constants';

// API Response wrapper type
export interface ApiResponse<T = unknown> {
  data: T;
  message?: string;
  timestamp?: string;
}

// Error response type
export interface ApiError {
  detail: string | { message: string; errors?: string[]; warnings?: string[] };
  timestamp?: string;
  status?: number;
}

// API Client class
class ApiClient {
  private instance: AxiosInstance;

  constructor() {
    this.instance = axios.create({
      baseURL: API_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor - Add auth token
    this.instance.interceptors.request.use(
      (config) => {
        const token = this.getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor - Handle errors
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        return response;
      },
      (error) => {
        return Promise.reject(this.handleApiError(error));
      }
    );
  }

  private getAuthToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('access_token');
  }

  private handleApiError(error: unknown): ApiClientError {
    if (error && typeof error === 'object' && 'response' in error) {
      // Server responded with error status
      const { status, data } = error.response as { status: number; data?: unknown };
      const errorData = data && typeof data === 'object' && 'detail' in data 
        ? data as { detail: string } 
        : null;
      return new ApiClientError(
        errorData?.detail || `HTTP Error ${status}`,
        status,
        'server_error',
        data
      );
    } else if (error && typeof error === 'object' && 'request' in error) {
      // Network error
      return new ApiClientError(
        'Network error - please check your connection',
        0,
        'network_error',
        null
      );
    } else {
      // Other error
      const message = error instanceof Error ? error.message : 'Unknown error occurred';
      return new ApiClientError(
        message,
        0,
        'unknown_error',
        null
      );
    }
  }

  // HTTP methods
  async get<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.get<T>(url, config);
    return response.data;
  }

  async post<T = unknown>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response = await this.instance.post<T>(url, data, config);
    return response.data;
  }

  async put<T = unknown>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response = await this.instance.put<T>(url, data, config);
    return response.data;
  }

  async patch<T = unknown>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response = await this.instance.patch<T>(url, data, config);
    return response.data;
  }

  async delete<T = unknown>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response = await this.instance.delete<T>(url, config);
    return response.data;
  }

  // Auth token management
  setAuthToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token);
    }
  }

  removeAuthToken(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
    }
  }

  getAxiosInstance(): AxiosInstance {
    return this.instance;
  }
}

// Custom error class
export class ApiClientError extends Error {
  public readonly status: number;
  public readonly type: string;
  public readonly response: unknown;

  constructor(
    message: string,
    status: number = 0,
    type: string = 'api_error',
    response: unknown = null
  ) {
    super(message);
    this.name = 'ApiClientError';
    this.status = status;
    this.type = type;
    this.response = response;
  }

  isNetworkError(): boolean {
    return this.type === 'network_error';
  }

  isServerError(): boolean {
    return this.status >= 500;
  }

  isClientError(): boolean {
    return this.status >= 400 && this.status < 500;
  }

  isAuthError(): boolean {
    return this.status === 401;
  }

  isForbiddenError(): boolean {
    return this.status === 403;
  }

  isNotFoundError(): boolean {
    return this.status === 404;
  }

  isValidationError(): boolean {
    return this.status === 422;
  }
}

// Create singleton instance
const apiClient = new ApiClient();

export default apiClient;