/**
 * API関連のユーティリティのエクスポート
 */

export * from './test-connection';
export { apiClient, ApiClient } from './client';
export type { ApiResponse, ApiErrorResponse } from './client';
export * from './revisions';

// APIクライアントの設定
export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1',
  TIMEOUT: parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '10000'),
  RETRY_ATTEMPTS: parseInt(process.env.NEXT_PUBLIC_API_RETRY_ATTEMPTS || '3'),
  RETRY_DELAY: parseInt(process.env.NEXT_PUBLIC_API_RETRY_DELAY || '1000')
};

/**
 * APIエンドポイントの定数
 */
export const API_ENDPOINTS = {
  // Auth
  LOGIN: '/auth/login/json',
  LOGOUT: '/auth/logout',
  REGISTER: '/auth/register',
  
  // Users
  USERS: '/users',
  USER_ME: '/users/me',
  USER_PASSWORD: '/users/me/password',
  
  // Revisions
  REVISIONS: '/revisions',
  REVISIONS_BY_ARTICLE: (articleId: string) => `/revisions/by-article/${articleId}`,
  
  // Proposals
  PROPOSALS: '/proposals',
  PROPOSAL_SUBMIT: (id: string) => `/proposals/${id}/submit`,
  PROPOSAL_WITHDRAW: (id: string) => `/proposals/${id}/withdraw`,
  PROPOSAL_APPROVED_UPDATE: (id: string) => `/proposals/${id}/approved-update`,
  
  // Approvals
  APPROVALS: '/approvals',
  APPROVAL_QUEUE: '/approvals/queue',
  APPROVAL_DECIDE: (id: string) => `/approvals/${id}/decide`,
  APPROVAL_METRICS: '/approvals/metrics',
  APPROVAL_BULK: '/approvals/bulk-process',
  
  // Articles
  ARTICLES: '/articles',
  
  // Info Categories
  INFO_CATEGORIES: '/info-categories',
  
  // Approval Groups
  APPROVAL_GROUPS: '/approval-groups',
  
  // Diffs
  DIFFS: (id: string) => `/diffs/${id}`,
  DIFF_COMPARE: '/diffs/compare',
  DIFF_PREVIEW: (id: string) => `/diffs/${id}/preview`,
  DIFF_HISTORY: (articleId: string) => `/diffs/history/${articleId}`,
  
  // Notifications
  NOTIFICATIONS: '/notifications',
  NOTIFICATIONS_MY: '/notifications/my-notifications',
  NOTIFICATIONS_MARK_READ: (id: string) => `/notifications/${id}/mark-read`,
  NOTIFICATIONS_MARK_ALL_READ: '/notifications/mark-all-read',
  NOTIFICATIONS_STATS: '/notifications/stats',
  
  // System
  SYSTEM_INFO: '/system/info',
  SYSTEM_HEALTH: '/system/health',
  SYSTEM_VERSION: '/system/version',
  
  // Analytics
  ANALYTICS_OVERVIEW: '/analytics/overview',
  ANALYTICS_USER_ACTIVITY: '/analytics/user-activity',
  ANALYTICS_APPROVAL_TRENDS: '/analytics/approval-trends'
} as const;

/**
 * 開発環境でのAPI接続チェック
 */
export async function checkApiConnection(): Promise<void> {
  if (process.env.NODE_ENV === 'development') {
    const { testApiConnection, logConnectionTestResult } = await import('./test-connection');
    
    try {
      const result = await testApiConnection();
      logConnectionTestResult(result);
      
      if (!result.success) {
        console.warn('⚠️ API connection failed. Please check if the backend server is running.');
      }
    } catch (error) {
      console.error('Failed to test API connection:', error);
    }
  }
}