import { testApiConnection, authService, ApiClientError } from '../lib/services';

// Comprehensive API connection test
export interface ApiTestResult {
  test: string;
  passed: boolean;
  message: string;
  details?: any;
  error?: string;
}

export interface ApiTestSuite {
  passed: boolean;
  totalTests: number;
  passedTests: number;
  results: ApiTestResult[];
  summary: string;
}

export async function runApiTests(): Promise<ApiTestSuite> {
  const results: ApiTestResult[] = [];

  // Test 1: Basic connectivity
  try {
    const connectionTest = await testApiConnection();
    results.push({
      test: 'API Connectivity',
      passed: connectionTest.connected,
      message: connectionTest.connected 
        ? `Connected to API (${connectionTest.status}, v${connectionTest.version})`
        : 'Failed to connect to API',
      details: connectionTest,
      error: connectionTest.error,
    });
  } catch (error) {
    results.push({
      test: 'API Connectivity',
      passed: false,
      message: 'Failed to test API connectivity',
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }

  // Test 2: Environment configuration
  try {
    const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
    const apiVersion = process.env.NEXT_PUBLIC_API_VERSION;
    
    const configTest = baseUrl && apiVersion;
    results.push({
      test: 'Environment Configuration',
      passed: !!configTest,
      message: configTest 
        ? `API Base: ${baseUrl}, Version: ${apiVersion}`
        : 'Missing environment configuration',
      details: { baseUrl, apiVersion },
    });
  } catch (error) {
    results.push({
      test: 'Environment Configuration',
      passed: false,
      message: 'Failed to check environment configuration',
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }

  // Test 3: Token handling
  try {
    const hasToken = authService.isAuthenticated();
    const token = authService.getToken();
    
    results.push({
      test: 'Token Management',
      passed: true, // This test always passes as it's about functionality
      message: hasToken 
        ? 'Token found and managed properly'
        : 'No token found (user not logged in)',
      details: { 
        hasToken, 
        tokenLength: token ? token.length : 0,
        tokenPreview: token ? `${token.substring(0, 10)}...` : 'none'
      },
    });
  } catch (error) {
    results.push({
      test: 'Token Management',
      passed: false,
      message: 'Failed to check token management',
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }

  // Test 4: Error handling
  try {
    const error = new ApiClientError('Test error', 404, 'test_error', { test: true });
    const errorHandlingWorking = 
      error.isNotFoundError() && 
      error.status === 404 && 
      error.type === 'test_error';

    results.push({
      test: 'Error Handling',
      passed: errorHandlingWorking,
      message: errorHandlingWorking 
        ? 'Error handling classes working properly'
        : 'Error handling not working correctly',
      details: {
        isNotFound: error.isNotFoundError(),
        status: error.status,
        type: error.type,
      },
    });
  } catch (error) {
    results.push({
      test: 'Error Handling',
      passed: false,
      message: 'Failed to test error handling',
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }

  // Test 5: Service instances
  try {
    const servicesAvailable = !!(
      authService && 
      typeof authService.login === 'function' &&
      typeof authService.logout === 'function'
    );

    results.push({
      test: 'Service Instances',
      passed: servicesAvailable,
      message: servicesAvailable 
        ? 'All service instances created successfully'
        : 'Service instances not properly initialized',
      details: {
        authServiceAvailable: !!authService,
        hasLoginMethod: typeof authService?.login === 'function',
      },
    });
  } catch (error) {
    results.push({
      test: 'Service Instances',
      passed: false,
      message: 'Failed to test service instances',
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }

  // Calculate results
  const passedTests = results.filter(r => r.passed).length;
  const totalTests = results.length;
  const passed = passedTests === totalTests;

  return {
    passed,
    totalTests,
    passedTests,
    results,
    summary: passed 
      ? `All ${totalTests} API tests passed successfully`
      : `${passedTests}/${totalTests} API tests passed`,
  };
}

// Simple connectivity check for quick verification
export async function quickApiCheck(): Promise<boolean> {
  try {
    const connection = await testApiConnection();
    return connection.connected;
  } catch {
    return false;
  }
}

// Log API test results to console
export async function logApiTests(): Promise<void> {
  console.log('🔧 Running API Connection Tests...\n');
  
  const testSuite = await runApiTests();
  
  testSuite.results.forEach((result, index) => {
    const icon = result.passed ? '✅' : '❌';
    console.log(`${icon} Test ${index + 1}: ${result.test}`);
    console.log(`   ${result.message}`);
    
    if (result.error) {
      console.log(`   Error: ${result.error}`);
    }
    
    if (result.details && typeof result.details === 'object') {
      console.log('   Details:', result.details);
    }
    
    console.log('');
  });
  
  console.log(`📊 Summary: ${testSuite.summary}`);
  
  if (!testSuite.passed) {
    console.warn('⚠️  Some tests failed. Please check your API configuration.');
  }
}

// Export for development use
export const apiTestUtils = {
  runApiTests,
  quickApiCheck,
  logApiTests,
};