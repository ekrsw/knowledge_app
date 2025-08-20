/**
 * 記事関連の型定義
 */

export interface Article {
  article_id: string;
  title: string;
  info_category?: string | null;  // UUID
  keywords?: string | null;
  importance: boolean;
  publish_start?: string | null;  // ISO 8601 date
  publish_end?: string | null;    // ISO 8601 date
  target?: string | null;
  question?: string | null;
  answer?: string | null;
  additional_comment?: string | null;
  approval_group?: string | null;  // UUID
  is_active: boolean;
  created_at: string;  // ISO 8601 datetime
  updated_at: string;  // ISO 8601 datetime
  
  // Relations (populated in some endpoints)
  category?: InfoCategory;
  group?: ApprovalGroup;
}

export interface ArticleCreate {
  article_id: string;  // User-defined ID
  title: string;
  info_category?: string | null;
  keywords?: string | null;
  importance?: boolean;
  publish_start?: string | null;
  publish_end?: string | null;
  target?: string | null;
  question?: string | null;
  answer?: string | null;
  additional_comment?: string | null;
  approval_group?: string | null;
}

export interface ArticleUpdate {
  title?: string;
  info_category?: string | null;
  keywords?: string | null;
  importance?: boolean;
  publish_start?: string | null;
  publish_end?: string | null;
  target?: string | null;
  question?: string | null;
  answer?: string | null;
  additional_comment?: string | null;
  approval_group?: string | null;
  is_active?: boolean;
}

export interface InfoCategory {
  category_id: string;  // UUID
  category_name: string;
  description?: string | null;
  display_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface InfoCategoryCreate {
  category_name: string;
  description?: string | null;
  display_order?: number;
}

export interface InfoCategoryUpdate {
  category_name?: string;
  description?: string | null;
  display_order?: number;
  is_active?: boolean;
}

export interface ApprovalGroup {
  group_id: string;  // UUID
  group_name: string;
  description?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ApprovalGroupCreate {
  group_name: string;
  description?: string | null;
}

export interface ApprovalGroupUpdate {
  group_name?: string;
  description?: string | null;
  is_active?: boolean;
}