#!/usr/bin/env node

/**
 * Node.js環境でのAPI接続テスト
 * Task 1.3のAPI接続テスト機能の動作確認用
 */

const axios = require('axios');
const fs = require('fs');

// テスト設定
const BASE_URL = 'http://localhost:8000/api/v1';
const TEST_TIMEOUT = 10000;

// テスト結果を記録
const testResults = [];

// テスト実行用のAPIクライアント
const testClient = axios.create({
  baseURL: BASE_URL,
  timeout: TEST_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  }
});

// テスト用ヘルパー関数
function logTest(testName, success, message, data = null) {
  const result = {
    test: testName,
    success,
    message,
    timestamp: new Date().toISOString(),
    data: data ? JSON.stringify(data, null, 2) : null
  };
  
  testResults.push(result);
  
  const status = success ? '✅ PASS' : '❌ FAIL';
  console.log(`${status} ${testName}: ${message}`);
  
  if (data && success) {
    console.log(`   Data: ${JSON.stringify(data)}`);
  }
}

// 基本的なヘルスチェックテスト
async function testHealthCheck() {
  try {
    const response = await testClient.get('/system/health');
    const data = response.data;
    
    if (response.status === 200 && data.status === 'healthy') {
      logTest('Health Check', true, `API健全性確認成功 (${data.status})`, {
        version: data.version,
        environment: data.environment,
        database: data.database
      });
      return true;
    } else {
      logTest('Health Check', false, `予期しないレスポンス: status=${response.status}, data=${JSON.stringify(data)}`);
      return false;
    }
  } catch (error) {
    logTest('Health Check', false, `接続エラー: ${error.message}`);
    return false;
  }
}

// システムバージョンテスト
async function testVersionEndpoint() {
  try {
    const response = await testClient.get('/system/version');
    const data = response.data;
    
    if (response.status === 200) {
      logTest('Version Check', true, 'バージョン情報取得成功', data);
      return true;
    } else {
      logTest('Version Check', false, `予期しないステータス: ${response.status}`);
      return false;
    }
  } catch (error) {
    logTest('Version Check', false, `バージョン確認エラー: ${error.message}`);
    return false;
  }
}

// 各エンティティエンドポイントのテスト（認証制御確認）
async function testEntityEndpoints() {
  const endpoints = [
    { name: 'Users List', endpoint: '/users', requiresAuth: true },
    { name: 'Articles List', endpoint: '/articles', requiresAuth: false },
    { name: 'Revisions List', endpoint: '/revisions', requiresAuth: true },
    { name: 'Approval Groups List', endpoint: '/approval-groups', requiresAuth: false },
    { name: 'Info Categories List', endpoint: '/info-categories', requiresAuth: false },
  ];

  let successCount = 0;
  
  for (const { name, endpoint, requiresAuth } of endpoints) {
    try {
      const response = await testClient.get(endpoint);
      
      if (response.status === 200) {
        const message = `データ取得成功 (${Array.isArray(response.data) ? response.data.length : 'N/A'} items)`;
        logTest(name, true, message);
        successCount++;
      } else {
        logTest(name, false, `予期しないステータス: ${response.status}`);
      }
    } catch (error) {
      const isAuthError = error.response?.status === 401 || error.response?.status === 403;
      if (requiresAuth && isAuthError) {
        logTest(name, true, '認証が必要 (正常)');
        successCount++;
      } else if (!requiresAuth) {
        logTest(name, false, `エラー: ${error.message}`);
      } else {
        logTest(name, false, `予期しないエラー: ${error.message}`);
      }
    }
  }
  
  return successCount;
}

// メイン実行関数
async function runNodeApiTests() {
  console.log('🚀 Node.js環境API接続テスト開始...');
  console.log(`📡 テスト対象: ${BASE_URL}`);
  console.log(`⏰ タイムアウト: ${TEST_TIMEOUT}ms`);
  console.log('');
  
  let totalTests = 0;
  let passedTests = 0;
  
  // 1. ヘルスチェックテスト
  totalTests++;
  if (await testHealthCheck()) passedTests++;
  
  // 2. バージョンエンドポイントテスト
  totalTests++;
  if (await testVersionEndpoint()) passedTests++;
  
  // 3. エンティティエンドポイントテスト
  const entityEndpointCount = 5;
  const entitySuccessCount = await testEntityEndpoints();
  totalTests += entityEndpointCount;
  passedTests += entitySuccessCount;
  
  // 結果サマリー
  console.log('');
  console.log('📊 テスト結果サマリー:');
  console.log(`   総テスト数: ${totalTests}`);
  console.log(`   成功: ${passedTests}`);
  console.log(`   失敗: ${totalTests - passedTests}`);
  console.log(`   成功率: ${Math.round(passedTests / totalTests * 100)}%`);
  
  const allPassed = passedTests === totalTests;
  console.log('');
  console.log(allPassed 
    ? '🎉 すべてのテストが成功しました！'
    : '⚠️ 一部のテストが失敗しました。詳細を確認してください。'
  );
  
  // テスト結果をファイルに出力
  const resultData = {
    testType: 'Node.js API Connection Test',
    summary: {
      total: totalTests,
      passed: passedTests,
      failed: totalTests - passedTests,
      successRate: Math.round(passedTests / totalTests * 100)
    },
    tests: testResults,
    timestamp: new Date().toISOString()
  };
  
  fs.writeFileSync('test-results.json', JSON.stringify(resultData, null, 2));
  console.log('📝 詳細結果: test-results.json に出力されました');
  
  return allPassed;
}

// スクリプト実行
if (require.main === module) {
  runNodeApiTests()
    .then(success => process.exit(success ? 0 : 1))
    .catch(error => {
      console.error('💥 テスト実行中に予期しないエラーが発生しました:', error);
      process.exit(1);
    });
}