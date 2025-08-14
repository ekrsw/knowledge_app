import { AxiosError } from 'axios';

// Standard API error interface
export interface ApiErrorResponse {
  detail: string;
  error_code?: string;
  timestamp?: string;
}

// Custom error class for API errors
export class ApiError extends Error {
  public status: number;
  public errorCode?: string;
  public timestamp?: string;

  constructor(message: string, status: number, errorCode?: string, timestamp?: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.errorCode = errorCode;
    this.timestamp = timestamp;
  }
}

// Error handler utility
export class ErrorHandler {
  static handle(error: unknown): ApiError {
    if (error instanceof ApiError) {
      return error;
    }

    if (this.isAxiosError(error)) {
      return this.handleAxiosError(error);
    }

    if (error instanceof Error) {
      return new ApiError(error.message, 500);
    }

    return new ApiError('An unknown error occurred', 500);
  }

  private static isAxiosError(error: unknown): error is AxiosError<ApiErrorResponse> {
    return typeof error === 'object' && error !== null && 'isAxiosError' in error;
  }

  private static handleAxiosError(error: AxiosError<ApiErrorResponse>): ApiError {
    const status = error.response?.status || 500;
    const errorData = error.response?.data;

    if (errorData?.detail) {
      return new ApiError(
        errorData.detail,
        status,
        errorData.error_code,
        errorData.timestamp
      );
    }

    // Fallback error messages based on status codes
    const fallbackMessage = this.getFallbackMessage(status);
    return new ApiError(fallbackMessage, status);
  }

  private static getFallbackMessage(status: number): string {
    switch (status) {
      case 400:
        return 'Invalid request. Please check your input.';
      case 401:
        return 'Authentication required. Please log in.';
      case 403:
        return 'You do not have permission to perform this action.';
      case 404:
        return 'The requested resource was not found.';
      case 409:
        return 'Conflict with current state. Please refresh and try again.';
      case 422:
        return 'Invalid data provided. Please check your input.';
      case 500:
        return 'Internal server error. Please try again later.';
      case 503:
        return 'Service temporarily unavailable. Please try again later.';
      default:
        return `An error occurred (${status}). Please try again.`;
    }
  }
}

// Helper function to extract user-friendly error messages
export const getErrorMessage = (error: unknown): string => {
  const apiError = ErrorHandler.handle(error);
  return apiError.message;
};