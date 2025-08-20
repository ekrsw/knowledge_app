// Base API types
export interface BaseEntity {
  created_at: string;
  updated_at: string;
}

// Common enums and union types
export type UserRole = 'user' | 'approver' | 'admin';
export type RevisionStatus = 'draft' | 'submitted' | 'approved' | 'rejected' | 'deleted';
export type NotificationType = 'revision_submitted' | 'revision_approved' | 'revision_rejected' | 'revision_updated';
export type Priority = 'low' | 'medium' | 'high' | 'urgent';
export type ApprovalAction = 'approve' | 'reject' | 'request_changes' | 'defer';

// User types
export interface User extends BaseEntity {
  id: string;
  username: string;
  email: string;
  full_name: string;
  sweet_name?: string;
  ctstage_name?: string;
  role: UserRole;
  approval_group_id?: string;
  is_active: boolean;
}

// Approval Group types
export interface ApprovalGroup extends BaseEntity {
  group_id: string;
  group_name: string;
  description?: string;
  is_active: boolean;
}

// Info Category types
export interface InfoCategory extends BaseEntity {
  category_id: string;
  category_name: string;
  description?: string;
  display_order: number;
  is_active: boolean;
}

// Article types
export interface Article extends BaseEntity {
  article_id: string;
  title: string;
  info_category: string;
  keywords?: string;
  importance: boolean;
  publish_start?: string;
  publish_end?: string;
  target?: string;
  question?: string;
  answer?: string;
  additional_comment?: string;
  approval_group: string;
  is_active: boolean;
}

// Revision types
export interface Revision extends BaseEntity {
  revision_id: string;
  target_article_id: string;
  proposer_id: string;
  approver_id: string;
  after_title?: string;
  after_info_category?: string;
  after_keywords?: string;
  after_importance?: boolean;
  after_publish_start?: string;
  after_publish_end?: string;
  after_target?: string;
  after_question?: string;
  after_answer?: string;
  after_additional_comment?: string;
  reason: string;
  status: RevisionStatus;
  processed_at?: string;
}

// Notification types
export interface SimpleNotification extends BaseEntity {
  notification_id: string;
  user_id: string;
  revision_id: string;
  notification_type: string;
  title: string;
  message: string;
  is_read: boolean;
  read_at?: string;
}

// Auth types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  full_name: string;
  sweet_name?: string;
  ctstage_name?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: 'bearer';
}

// Revision Create/Update types
export interface RevisionCreate {
  target_article_id: string;
  approver_id: string;
  reason: string;
  after_title?: string;
  after_info_category?: string;
  after_keywords?: string;
  after_importance?: boolean;
  after_publish_start?: string;
  after_publish_end?: string;
  after_target?: string;
  after_question?: string;
  after_answer?: string;
  after_additional_comment?: string;
}

export interface RevisionUpdate {
  reason?: string;
  after_title?: string;
  after_info_category?: string;
  after_keywords?: string;
  after_importance?: boolean;
  after_publish_start?: string;
  after_publish_end?: string;
  after_target?: string;
  after_question?: string;
  after_answer?: string;
  after_additional_comment?: string;
}

// Approval types
export interface ApprovalDecision {
  action: 'approve' | 'reject' | 'request_changes' | 'defer';
  comment: string;
  priority?: 'low' | 'medium' | 'high' | 'urgent';
}

export interface ApprovalQueue {
  revision: Revision;
  days_pending: number;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  article_info?: Article;
}

export interface ApprovalMetrics {
  total_approved: number;
  total_rejected: number;
  average_processing_time: number;
  pending_count: number;
  efficiency_score: number;
}

// Diff types
export interface FieldDiff {
  field_name: string;
  current_value: any;
  proposed_value: any;
  change_type: 'added' | 'modified' | 'removed' | 'unchanged';
}

export interface RevisionDiff {
  revision_id: string;
  target_article_id: string;
  field_diffs: Record<string, FieldDiff>;
  summary: {
    total_changes: number;
    fields_changed: string[];
    impact_level: 'low' | 'medium' | 'high';
    estimated_review_time: number;
  };
}

// Statistics types
export interface ProposalStatistics {
  total_proposals: number;
  status_breakdown: {
    draft: number;
    submitted: number;
    approved: number;
    rejected: number;
    deleted: number;
  };
  recent_activity: {
    created_last_7_days: number;
    approved_last_7_days: number;
    rejected_last_7_days: number;
  };
}

export interface NotificationStats {
  total_notifications: number;
  unread_count: number;
  types_breakdown: Record<string, number>;
  recent_activity: {
    received_last_7_days: number;
    read_last_7_days: number;
  };
}

// Pagination types
export interface PaginationParams {
  skip?: number;
  limit?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Error types
export interface ApiErrorDetail {
  message: string;
  errors?: string[];
  warnings?: string[];
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

// System types
export interface HealthCheck {
  status: 'healthy' | 'unhealthy';
  timestamp: string;
  version: string;
  environment?: string;
  database?: string;
}

export interface SystemStats {
  users: {
    total: number;
    active: number;
    by_role: Record<string, number>;
  };
  revisions: {
    total: number;
    by_status: Record<string, number>;
  };
  notifications: {
    total: number;
    unread: number;
  };
}