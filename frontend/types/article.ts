/**
 * 記事関連の型定義
 * バックエンドの article.py スキーマに対応
 */

export interface ArticleBase {
  article_id: string;
  article_number: string;
  article_url?: string | null;
  approval_group?: string | null; // UUID string
  title?: string | null;
  info_category?: string | null; // UUID string
  keywords?: string | null;
  importance?: boolean | null;
  publish_start?: string | null; // ISO date string
  publish_end?: string | null; // ISO date string
  target?: string | null;
  question?: string | null;
  answer?: string | null;
  additional_comment?: string | null;
}

export interface ArticleCreate extends ArticleBase {
  // 記事作成用（BaseとCreateは同じ）
}

export interface ArticleUpdate {
  article_number?: string;
  article_url?: string | null;
  approval_group?: string | null;
  title?: string | null;
  info_category?: string | null;
  keywords?: string | null;
  importance?: boolean | null;
  publish_start?: string | null;
  publish_end?: string | null;
  target?: string | null;
  question?: string | null;
  answer?: string | null;
  additional_comment?: string | null;
}

export interface Article extends ArticleBase {
  created_at: string;
  updated_at: string;
}

// UI用の拡張型
export interface ArticleWithDetails extends Article {
  approval_group_name?: string;
  category_name?: string;
  revision_count?: number; // この記事に対する修正案の数
  last_revision_date?: string;
}

// 一覧表示用の軽量な型
export interface ArticleSummary {
  article_id: string;
  article_number: string;
  title?: string | null;
  approval_group?: string | null;
  approval_group_name?: string;
  category_name?: string;
  importance?: boolean | null;
  publish_start?: string | null;
  publish_end?: string | null;
  updated_at: string;
}

// 記事選択用の軽量な型
export interface ArticleOption {
  article_id: string;
  article_number: string;
  title?: string | null;
}