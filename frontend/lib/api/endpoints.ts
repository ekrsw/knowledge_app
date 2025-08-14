// API endpoint constants based on backend API design
export const API_ENDPOINTS = {
  // Authentication
  AUTH: {
    LOGIN: '/auth/login/json',
    LOGOUT: '/auth/logout',
    ME: '/auth/me',
    REGISTER: '/auth/register',
  },

  // Users
  USERS: {
    BASE: '/users',
    BY_ID: (id: string) => `/users/${id}`,
    CURRENT: '/users/me',
    UPDATE_CURRENT: '/users/me',
  },

  // Revisions (Basic CRUD)
  REVISIONS: {
    BASE: '/revisions',
    BY_ID: (id: string) => `/revisions/${id}`,
    BY_ARTICLE: (articleId: string) => `/revisions/by-article/${articleId}`,
    BY_STATUS: (status: string) => `/revisions/by-status/${status}`,
  },

  // Proposals (Business Logic)
  PROPOSALS: {
    BASE: '/proposals',
    BY_ID: (id: string) => `/proposals/${id}`,
    SUBMIT: (id: string) => `/proposals/${id}/submit`,
    WITHDRAW: (id: string) => `/proposals/${id}/withdraw`,
    VALIDATE: '/proposals/validate',
  },

  // Approvals
  APPROVALS: {
    QUEUE: '/approvals/queue',
    DECIDE: (id: string) => `/approvals/${id}/decide`,
    STATUS: (id: string) => `/approvals/${id}/status`,
    METRICS: '/approvals/metrics',
    BULK: '/approvals/bulk',
  },

  // Diffs
  DIFFS: {
    BY_ID: (id: string) => `/diffs/${id}`,
    PREVIEW: (id: string) => `/diffs/${id}/preview`,
    COMPARE: '/diffs/compare',
    ARTICLE_HISTORY: (articleId: string) => `/diffs/article/${articleId}/history`,
  },

  // Articles
  ARTICLES: {
    BASE: '/articles',
    BY_ID: (id: string) => `/articles/${id}`,
    BY_GROUP: (groupId: string) => `/articles/by-group/${groupId}`,
    SEARCH: '/articles/search',
  },

  // Info Categories
  INFO_CATEGORIES: {
    BASE: '/info-categories',
    BY_ID: (id: string) => `/info-categories/${id}`,
    ACTIVE: '/info-categories/active',
  },

  // Approval Groups
  APPROVAL_GROUPS: {
    BASE: '/approval-groups',
    BY_ID: (id: string) => `/approval-groups/${id}`,
    ACTIVE: '/approval-groups/active',
    MEMBERS: (id: string) => `/approval-groups/${id}/members`,
  },

  // Notifications
  NOTIFICATIONS: {
    MY_NOTIFICATIONS: '/notifications/my-notifications',
    BY_ID: (id: string) => `/notifications/${id}`,
    MARK_READ: (id: string) => `/notifications/${id}/read`,
    UNREAD_COUNT: '/notifications/unread-count',
    MARK_ALL_READ: '/notifications/mark-all-read',
  },

  // System
  SYSTEM: {
    HEALTH: '/system/health',
    VERSION: '/system/version',
    STATUS: '/system/status',
  },

  // Analytics
  ANALYTICS: {
    DASHBOARD: '/analytics/dashboard',
    REVISION_STATS: '/analytics/revision-stats',
    USER_ACTIVITY: '/analytics/user-activity',
  },
} as const;

// Export type for endpoint keys
export type ApiEndpoint = typeof API_ENDPOINTS;