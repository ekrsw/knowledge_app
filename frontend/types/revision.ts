/**
 * 修正案関連の型定義
 * バックエンドの revision.py スキーマに対応
 */

export type RevisionStatus = 'draft' | 'submitted' | 'approved' | 'rejected' | 'deleted';

export interface RevisionBase {
  target_article_id: string;
  reason: string;
  // after_* フィールド (すべてオプショナル)
  after_title?: string | null;
  after_info_category?: string | null; // UUID string
  after_keywords?: string | null;
  after_importance?: boolean | null;
  after_publish_start?: string | null; // ISO date string
  after_publish_end?: string | null; // ISO date string
  after_target?: string | null;
  after_question?: string | null;
  after_answer?: string | null;
  after_additional_comment?: string | null;
}

export interface RevisionCreate extends RevisionBase {
  approver_id: string;
}

export interface RevisionUpdate {
  reason?: string;
  status?: RevisionStatus;
  processed_at?: string | null; // ISO datetime string
  approver_id?: string;
  // after_* フィールド
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

export interface RevisionStatusUpdate {
  status: Exclude<RevisionStatus, 'draft'>;
}

export interface Revision extends RevisionBase {
  revision_id: string;
  proposer_id: string;
  status: RevisionStatus;
  approver_id: string;
  processed_at?: string | null;
  created_at: string;
  updated_at: string;
}

// UI用の拡張型
export interface RevisionWithDetails extends Revision {
  proposer_name?: string;
  approver_name?: string;
  article_title?: string;
  category_name?: string;
}

// 一覧表示用の軽量な型
export interface RevisionSummary {
  revision_id: string;
  target_article_id: string;
  status: RevisionStatus;
  reason: string;
  proposer_id: string;
  proposer_name?: string;
  approver_id: string;
  approver_name?: string;
  created_at: string;
  updated_at: string;
}

// ステータスラベル
export const REVISION_STATUS_LABELS: Record<RevisionStatus, string> = {
  draft: '下書き',
  submitted: '提出済み',
  approved: '承認済み',
  rejected: '却下',
  deleted: '削除済み'
};

// ステータスの色分け用
export const REVISION_STATUS_COLORS: Record<RevisionStatus, 'gray' | 'blue' | 'green' | 'red' | 'slate'> = {
  draft: 'gray',
  submitted: 'blue',
  approved: 'green',
  rejected: 'red',
  deleted: 'slate'
};