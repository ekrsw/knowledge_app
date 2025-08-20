/**
 * 差分表示関連の型定義
 */

export type ChangeType = 'added' | 'modified' | 'removed' | 'unchanged';

export interface FieldDiff {
  field_name: string;
  field_label: string;
  current_value: any;
  proposed_value: any;
  change_type: ChangeType;
  is_significant: boolean;
}

export interface DiffSummary {
  revision_id: string;
  target_article_id: string;
  total_changes: number;
  significant_changes: number;
  fields: FieldDiff[];
  created_at: string;
  proposer_name: string;
  status: string;
}

export interface DiffComparison {
  revision_1: {
    revision_id: string;
    created_at: string;
    status: string;
    proposer_name: string;
  };
  revision_2: {
    revision_id: string;
    created_at: string;
    status: string;
    proposer_name: string;
  };
  differences: FieldDiff[];
  similarity_score: number;
}

export interface ArticleHistory {
  article_id: string;
  article_title: string;
  total_revisions: number;
  revisions: {
    revision_id: string;
    created_at: string;
    status: string;
    proposer_name: string;
    change_summary: string;
    total_changes: number;
  }[];
}

export interface TextDiff {
  original: string;
  modified: string;
  hunks: {
    old_start: number;
    old_lines: number;
    new_start: number;
    new_lines: number;
    lines: {
      type: 'add' | 'delete' | 'normal';
      content: string;
    }[];
  }[];
}