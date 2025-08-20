// API Configuration
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
export const API_VERSION = process.env.NEXT_PUBLIC_API_VERSION || 'v1';
export const API_URL = `${API_BASE_URL}/api/${API_VERSION}`;

// Application Configuration
export const APP_NAME = process.env.NEXT_PUBLIC_APP_NAME || 'Knowledge Revision System';
export const APP_VERSION = process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0';

// JWT Configuration
export const JWT_SECRET = process.env.NEXT_PUBLIC_JWT_SECRET || 'default-secret';

// Debug Configuration
export const IS_DEBUG = process.env.NEXT_PUBLIC_DEBUG === 'true';

// Status options for revisions
export const REVISION_STATUSES = {
  DRAFT: 'draft',
  SUBMITTED: 'submitted',
  APPROVED: 'approved',
  REJECTED: 'rejected',
  DELETED: 'deleted',
} as const;

export type RevisionStatus = typeof REVISION_STATUSES[keyof typeof REVISION_STATUSES];

// User roles
export const USER_ROLES = {
  USER: 'user',
  APPROVER: 'approver',
  ADMIN: 'admin',
} as const;

export type UserRole = typeof USER_ROLES[keyof typeof USER_ROLES];