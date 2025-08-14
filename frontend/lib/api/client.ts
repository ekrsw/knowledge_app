import axios from 'axios';
import type { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

// API Response wrapper type
export interface ApiResponse<T = any> {
  data: T;
  status: number;
  message?: string;
}

// Error response type
export interface ApiError {
  detail: string;
  error_code?: string;
  timestamp?: string;
}

// Create axios instance with base configuration
const createAxiosInstance = (): AxiosInstance => {
  const instance = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1',
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json',
    },
    // Remove proxy setting as it's not needed for modern axios
  });

  // Request interceptor for adding auth token
  instance.interceptors.request.use(
    (config) => {
      // Get token from localStorage if available
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('authToken');
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor for handling errors
  instance.interceptors.response.use(
    (response: AxiosResponse) => {
      return response;
    },
    (error: AxiosError<ApiError>) => {
      // Handle common error cases
      if (error.response?.status === 401) {
        // Unauthorized - redirect to login
        if (typeof window !== 'undefined') {
          localStorage.removeItem('authToken');
          window.location.href = '/login';
        }
      }
      
      return Promise.reject(error);
    }
  );

  return instance;
};

// Create and export the API client instance
export const apiClient = createAxiosInstance();

// Generic API methods
export class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = apiClient;
  }

  async get<T>(url: string, params?: Record<string, any>): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.get<T>(url, { params });
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async post<T>(url: string, data?: any): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.post<T>(url, data);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async put<T>(url: string, data?: any): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.put<T>(url, data);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async delete<T>(url: string): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.delete<T>(url);
      return {
        data: response.data,
        status: response.status,
      };
    } catch (error) {
      throw this.handleError(error);
    }
  }

  private handleError(error: any): Error {
    if (axios.isAxiosError(error)) {
      const apiError = error.response?.data as ApiError;
      if (apiError?.detail) {
        return new Error(apiError.detail);
      }
      return new Error(error.message || 'An unknown error occurred');
    }
    return error;
  }
}

// Export singleton instance
export const api = new ApiClient();