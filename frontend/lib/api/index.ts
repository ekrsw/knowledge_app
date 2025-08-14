// Export main API client
export { api, ApiClient, apiClient } from './client';
export type { ApiResponse, ApiError } from './client';

// Export API endpoints
export { API_ENDPOINTS } from './endpoints';
export type { ApiEndpoint } from './endpoints';

// Export error handling utilities
export { ErrorHandler, ApiError as CustomApiError, getErrorMessage } from './error-handler';
export type { ApiErrorResponse } from './error-handler';

// Export connection testing utilities
export { ApiConnectionTester, testApiConnection } from './test-connection';
export type { ConnectionTestResult } from './test-connection';