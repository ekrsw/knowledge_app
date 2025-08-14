import { api } from './client';
import { API_ENDPOINTS } from './endpoints';
import { ErrorHandler } from './error-handler';

// API connection test interface
export interface ConnectionTestResult {
  success: boolean;
  message: string;
  status?: number;
  timestamp: string;
  endpoint: string;
}

// Test connection to the backend API
export class ApiConnectionTester {
  static async testConnection(): Promise<ConnectionTestResult> {
    const timestamp = new Date().toISOString();
    const endpoint = API_ENDPOINTS.SYSTEM.HEALTH;

    try {
      const response = await api.get<{ status: string; timestamp: string }>(endpoint);
      
      return {
        success: true,
        message: 'Successfully connected to the API',
        status: response.status,
        timestamp,
        endpoint,
      };
    } catch (error) {
      const apiError = ErrorHandler.handle(error);
      
      return {
        success: false,
        message: `Connection failed: ${apiError.message}`,
        status: apiError.status,
        timestamp,
        endpoint,
      };
    }
  }

  static async testAuthenticatedConnection(token?: string): Promise<ConnectionTestResult> {
    const timestamp = new Date().toISOString();
    const endpoint = API_ENDPOINTS.AUTH.ME;

    try {
      // Temporarily set token if provided
      if (token && typeof window !== 'undefined') {
        const originalToken = localStorage.getItem('authToken');
        localStorage.setItem('authToken', token);
        
        try {
          const response = await api.get<{ user: any }>(endpoint);
          
          return {
            success: true,
            message: 'Successfully authenticated with the API',
            status: response.status,
            timestamp,
            endpoint,
          };
        } finally {
          // Restore original token
          if (originalToken) {
            localStorage.setItem('authToken', originalToken);
          } else {
            localStorage.removeItem('authToken');
          }
        }
      } else {
        const response = await api.get<{ user: any }>(endpoint);
        
        return {
          success: true,
          message: 'Successfully authenticated with the API',
          status: response.status,
          timestamp,
          endpoint,
        };
      }
    } catch (error) {
      const apiError = ErrorHandler.handle(error);
      
      return {
        success: false,
        message: `Authentication test failed: ${apiError.message}`,
        status: apiError.status,
        timestamp,
        endpoint,
      };
    }
  }

  static async runBasicTests(): Promise<ConnectionTestResult[]> {
    const results: ConnectionTestResult[] = [];

    // Test system health
    const healthTest = await this.testConnection();
    results.push(healthTest);

    // Test system version endpoint
    try {
      const versionResponse = await api.get<{ version: string }>(API_ENDPOINTS.SYSTEM.VERSION);
      results.push({
        success: true,
        message: `API version: ${versionResponse.data.version}`,
        status: versionResponse.status,
        timestamp: new Date().toISOString(),
        endpoint: API_ENDPOINTS.SYSTEM.VERSION,
      });
    } catch (error) {
      const apiError = ErrorHandler.handle(error);
      results.push({
        success: false,
        message: `Version check failed: ${apiError.message}`,
        status: apiError.status,
        timestamp: new Date().toISOString(),
        endpoint: API_ENDPOINTS.SYSTEM.VERSION,
      });
    }

    return results;
  }
}

// Convenience function for quick connection test
export const testApiConnection = () => ApiConnectionTester.testConnection();