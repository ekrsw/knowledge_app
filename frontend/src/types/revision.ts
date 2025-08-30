/**
 * 修正案関連の型定義
 */

export type RevisionStatus = 'draft' | 'submitted' | 'approved' | 'rejected' | 'deleted';

export interface Revision {
  revision_id: string;  // UUID
  target_article_id: string;
  proposer_id: string;  // UUID
  approver_id: string;  // UUID (required)
  
  // After-only fields (all nullable)
  after_title?: string | null;
  after_info_category?: string | null;  // UUID
  after_keywords?: string | null;
  after_importance?: boolean | null;
  after_publish_start?: string | null;  // ISO 8601 date
  after_publish_end?: string | null;    // ISO 8601 date
  after_target?: string | null;
  after_question?: string | null;
  after_answer?: string | null;
  after_additional_comment?: string | null;
  
  // Metadata
  reason: string;
  status: RevisionStatus;
  processed_at?: string | null;  // ISO 8601 datetime
  created_at: string;  // ISO 8601 datetime
  updated_at: string;  // ISO 8601 datetime
  
  // Names populated from relations (in list views)
  proposer_name?: string;
  approver_name?: string;
  
  // Relations (populated in some endpoints)
  proposer?: unknown;  // User object
  approver?: unknown;  // User object
  article?: unknown;   // Article object
}

export interface RevisionCreate {
  target_article_id: string;
  approver_id: string;  // Required
  reason: string;
  
  // At least one after_* field must be provided
  after_title?: string | null;
  after_info_category?: string | null;
  after_keywords?: string | null;
  after_importance?: boolean | null;
  after_publish_start?: string | null;
  after_publish_end?: string | null;
  after_target?: string | null;
  after_question?: string | null;
  after_answer?: string | null;
  after_additional_comment?: string | null;
}

export interface RevisionUpdate {
  approver_id?: string;
  reason?: string;
  after_title?: string | null;
  after_info_category?: string | null;
  after_keywords?: string | null;
  after_importance?: boolean | null;
  after_publish_start?: string | null;
  after_publish_end?: string | null;
  after_target?: string | null;
  after_question?: string | null;
  after_answer?: string | null;
  after_additional_comment?: string | null;
}

export interface ApprovalDecision {
  action: 'approve' | 'reject' | 'request_changes' | 'defer';
  comment: string;
  priority?: 'low' | 'medium' | 'high' | 'urgent';
}

export interface RevisionStatistics {
  total_count: number;
  by_status: {
    draft: number;
    submitted: number;
    approved: number;
    rejected: number;
    deleted: number;
  };
  recent_submissions: number;
  approval_rate: number;
  average_processing_time_hours?: number;
}