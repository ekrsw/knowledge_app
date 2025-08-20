// Import services
import { authService } from './auth';
import { revisionsService } from './revisions';
import { proposalsService } from './proposals';
import { approvalsService } from './approvals';
import { diffsService } from './diffs';
import { notificationsService } from './notifications';

// Export all services
export { AuthService, authService } from './auth';
export { RevisionsService, revisionsService } from './revisions';
export { ProposalsService, proposalsService } from './proposals';
export { ApprovalsService, approvalsService } from './approvals';
export { DiffsService, diffsService } from './diffs';
export { NotificationsService, notificationsService } from './notifications';

// Export API client
export { default as apiClient, ApiClientError } from '../api';

// Main services object for convenient access
export const services = {
  auth: authService,
  revisions: revisionsService,
  proposals: proposalsService,
  approvals: approvalsService,
  diffs: diffsService,
  notifications: notificationsService,
};

// API connection test utility
export async function testApiConnection(): Promise<{
  connected: boolean;
  status: string;
  version?: string;
  environment?: string;
  error?: string;
}> {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/health`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const healthData = await response.json();
    
    return {
      connected: true,
      status: healthData.status || 'unknown',
      version: healthData.version,
      environment: healthData.environment,
    };
  } catch (error) {
    return {
      connected: false,
      status: 'error',
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

// Type exports for convenience
export type {
  User,
  Revision,
  Article,
  ApprovalGroup,
  InfoCategory,
  SimpleNotification,
  RevisionCreate,
  RevisionUpdate,
  ApprovalDecision,
  RevisionDiff,
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  PaginationParams,
  UserRole,
  RevisionStatus,
  Priority,
  ApprovalAction,
} from '../../types/api';

// API client types
export type { ApiResponse, ApiError } from '../api';