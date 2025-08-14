/**
 * TypeScript環境でのAPI接続テスト機能検証
 * lib/api/test-connection.ts の実際の動作を確認
 */

// 相対パスで必要なモジュールをインポート
import { ApiConnectionTester } from '../../lib/api/test-connection';
import { api } from '../../lib/api/client';
import { API_ENDPOINTS } from '../../lib/api/endpoints';

interface TestResult {
  testName: string;
  success: boolean;
  message: string;
  timestamp: string;
  details?: any;
}

class TypeScriptApiTester {
  private results: TestResult[] = [];

  private logResult(testName: string, success: boolean, message: string, details?: any): void {
    const result: TestResult = {
      testName,
      success,
      message,
      timestamp: new Date().toISOString(),
      details
    };
    
    this.results.push(result);
    
    const status = success ? '✅' : '❌';
    console.log(`${status} ${testName}: ${message}`);
    
    if (details && success) {
      console.log(`   詳細: ${JSON.stringify(details, null, 2)}`);
    }
  }

  async testBasicConnection(): Promise<boolean> {
    try {
      const result = await ApiConnectionTester.testConnection();
      
      if (result.success) {
        this.logResult('基本接続テスト', true, result.message, {
          status: result.status,
          endpoint: result.endpoint
        });
        return true;
      } else {
        this.logResult('基本接続テスト', false, result.message);
        return false;
      }
    } catch (error) {
      this.logResult('基本接続テスト', false, `例外発生: ${error}`);
      return false;
    }
  }

  async testAuthenticatedConnection(): Promise<boolean> {
    try {
      const result = await ApiConnectionTester.testAuthenticatedConnection();
      
      // 認証なしでは失敗が期待される
      if (!result.success && (result.status === 401 || result.status === 403)) {
        this.logResult('認証テスト', true, '認証が必要（期待される結果）', {
          status: result.status,
          endpoint: result.endpoint
        });
        return true;
      } else if (result.success) {
        this.logResult('認証テスト', true, '認証成功（トークンが存在）', {
          status: result.status,
          endpoint: result.endpoint
        });
        return true;
      } else {
        this.logResult('認証テスト', false, result.message);
        return false;
      }
    } catch (error) {
      this.logResult('認証テスト', false, `例外発生: ${error}`);
      return false;
    }
  }

  async testBasicTestSuite(): Promise<boolean> {
    try {
      const results = await ApiConnectionTester.runBasicTests();
      
      const allSuccess = results.every(r => r.success);
      
      this.logResult('基本テストスイート', allSuccess, 
        `${results.length}個のテスト実行 - ${allSuccess ? '全て成功' : '一部失敗'}`, {
        testCount: results.length,
        successCount: results.filter(r => r.success).length
      });
      
      return allSuccess;
    } catch (error) {
      this.logResult('基本テストスイート', false, `例外発生: ${error}`);
      return false;
    }
  }

  async testComprehensiveTests(): Promise<boolean> {
    try {
      const result = await ApiConnectionTester.runComprehensiveTests();
      
      this.logResult('包括的テスト', result.overall, 
        `総合テスト結果: ${result.summary.passed}/${result.summary.total} 成功`, {
        summary: result.summary,
        overall: result.overall
      });
      
      return result.overall;
    } catch (error) {
      this.logResult('包括的テスト', false, `例外発生: ${error}`);
      return false;
    }
  }

  async testIndividualEndpoint(): Promise<boolean> {
    try {
      const result = await ApiConnectionTester.testEndpoint(API_ENDPOINTS.SYSTEM.HEALTH, 'GET');
      
      if (result.success) {
        this.logResult('個別エンドポイントテスト', true, result.message, {
          status: result.status,
          endpoint: result.endpoint
        });
        return true;
      } else {
        this.logResult('個別エンドポイントテスト', false, result.message);
        return false;
      }
    } catch (error) {
      this.logResult('個別エンドポイントテスト', false, `例外発生: ${error}`);
      return false;
    }
  }

  async runAllTests(): Promise<void> {
    console.log('🧪 TypeScript環境でのAPI接続テスト機能検証開始...');
    console.log('');

    const tests = [
      { name: '基本接続テスト', test: () => this.testBasicConnection() },
      { name: '認証テスト', test: () => this.testAuthenticatedConnection() },
      { name: '基本テストスイート', test: () => this.testBasicTestSuite() },
      { name: '包括的テスト', test: () => this.testComprehensiveTests() },
      { name: '個別エンドポイントテスト', test: () => this.testIndividualEndpoint() },
    ];

    let passedCount = 0;

    for (const { name, test } of tests) {
      console.log(`🔍 ${name} 実行中...`);
      const success = await test();
      if (success) passedCount++;
      console.log('');
    }

    // 結果サマリー
    const totalTests = tests.length;
    const successRate = Math.round(passedCount / totalTests * 100);

    console.log('📊 TypeScriptテスト結果サマリー:');
    console.log(`   総テスト数: ${totalTests}`);
    console.log(`   成功: ${passedCount}`);
    console.log(`   失敗: ${totalTests - passedCount}`);
    console.log(`   成功率: ${successRate}%`);
    console.log('');

    if (passedCount === totalTests) {
      console.log('🎉 TypeScript環境でのAPI接続テスト機能は完全に動作しています！');
      console.log('✅ Task 1.3のAPI接続テスト機能実装は成功です。');
    } else {
      console.log('⚠️ 一部のテストが失敗しています。');
    }

    // 結果を JSON で出力（テストディレクトリに保存）
    const fs = require('fs');
    const path = require('path');
    const outputData = {
      testType: 'TypeScript API Connection Test',
      summary: {
        total: totalTests,
        passed: passedCount,
        failed: totalTests - passedCount,
        successRate
      },
      results: this.results,
      timestamp: new Date().toISOString()
    };

    // テストディレクトリのパスを取得
    const testDir = path.join(process.cwd(), 'tests', 'api-connection');
    const outputPath = path.join(testDir, 'typescript-test-results.json');
    
    try {
      fs.writeFileSync(outputPath, JSON.stringify(outputData, null, 2));
      console.log('📝 詳細結果: typescript-test-results.json に出力されました');
    } catch (error) {
      // フォールバック: カレントディレクトリに出力
      fs.writeFileSync('typescript-test-results.json', JSON.stringify(outputData, null, 2));
      console.log('📝 詳細結果: typescript-test-results.json にフォールバック出力されました');
    }
  }
}

// エクスポート用
export { TypeScriptApiTester };

// 直接実行された場合
if (require.main === module) {
  const tester = new TypeScriptApiTester();
  tester.runAllTests()
    .then(() => {
      console.log('✨ TypeScriptテスト完了');
      process.exit(0);
    })
    .catch((error) => {
      console.error('❌ TypeScriptテスト失敗:', error);
      process.exit(1);
    });
}