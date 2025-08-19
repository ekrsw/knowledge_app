// User-related types
export type UserRole = 'user' | 'approver' | 'admin';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  approval_group_id: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  email: string;
  full_name: string;
  password: string;
  role?: UserRole;
  approval_group_id?: string | null;
}

export interface UserUpdate {
  email?: string;
  full_name?: string;
  role?: UserRole;
  approval_group_id?: string | null;
  is_active?: boolean;
}

// Revision-related types
export type RevisionStatus = 'draft' | 'submitted' | 'approved' | 'rejected' | 'deleted';

export interface Revision {
  id: string;
  target_article_id: string;
  proposer_id: string;
  approver_id: string;
  status: RevisionStatus;
  after_title: string | null;
  after_content: string | null;
  after_category_id: string | null;
  proposal_reason: string | null;
  approval_comment: string | null;
  created_at: string;
  updated_at: string;
  proposed_at: string | null;
  approved_at: string | null;
}

export interface RevisionCreate {
  target_article_id: string;
  approver_id: string;
  after_title?: string | null;
  after_content?: string | null;
  after_category_id?: string | null;
  proposal_reason?: string | null;
}

export interface RevisionUpdate {
  after_title?: string | null;
  after_content?: string | null;
  after_category_id?: string | null;
  proposal_reason?: string | null;
}

// Article-related types
export interface Article {
  id: string;
  title: string;
  content: string;
  category_id: string;
  approval_group_id: string;
  created_at: string;
  updated_at: string;
}

export interface ArticleCreate {
  id: string;
  title: string;
  content: string;
  category_id: string;
  approval_group_id: string;
}

export interface ArticleUpdate {
  title?: string;
  content?: string;
  category_id?: string;
  approval_group_id?: string;
}

// Category-related types
export interface InfoCategory {
  id: string;
  name: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface InfoCategoryCreate {
  name: string;
  description?: string | null;
}

export interface InfoCategoryUpdate {
  name?: string;
  description?: string | null;
  is_active?: boolean;
}

// Approval Group-related types
export interface ApprovalGroup {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface ApprovalGroupCreate {
  name: string;
  description?: string | null;
}

export interface ApprovalGroupUpdate {
  name?: string;
  description?: string | null;
}

// Authentication types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface TokenValidation {
  valid: boolean;
  user?: User;
}

// Notification types
export interface SimpleNotification {
  id: string;
  user_id: string;
  revision_id: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

// Approval types
export interface ApprovalDecision {
  decision: 'approved' | 'rejected';
  comment?: string;
}

export interface ApprovalWorkload {
  user_id: string;
  pending_count: number;
  total_processed: number;
  avg_processing_time_hours: number | null;
}

// Diff types
export interface DiffSummary {
  revision_id: string;
  changes_count: number;
  field_changes: {
    title: boolean;
    content: boolean;
    category: boolean;
  };
}

// Statistics types
export interface ProposalStatistics {
  total_proposals: number;
  by_status: Record<RevisionStatus, number>;
  by_proposer: Array<{
    proposer_id: string;
    proposer_name: string;
    count: number;
  }>;
}