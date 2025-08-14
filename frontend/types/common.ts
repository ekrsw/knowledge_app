/**
 * 共通の型定義
 * 承認グループ、情報カテゴリ、通知など
 */

// 承認グループ関連
export interface ApprovalGroupBase {
  group_name: string;
  description?: string | null;
  is_active: boolean;
}

export interface ApprovalGroupCreate extends ApprovalGroupBase {
  // 作成用（Baseと同じ）
}

export interface ApprovalGroupUpdate {
  group_name?: string;
  description?: string | null;
  is_active?: boolean;
}

export interface ApprovalGroup extends ApprovalGroupBase {
  group_id: string;
  created_at: string;
  updated_at: string;
}

// 情報カテゴリ関連
export interface InfoCategoryBase {
  category_name: string;
  description?: string | null;
  is_active: boolean;
}

export interface InfoCategoryCreate extends InfoCategoryBase {
  // 作成用（Baseと同じ）
}

export interface InfoCategoryUpdate {
  category_name?: string;
  description?: string | null;
  is_active?: boolean;
}

export interface InfoCategory extends InfoCategoryBase {
  category_id: string;
  created_at: string;
  updated_at: string;
}

// 通知関連
export interface NotificationBase {
  message: string;
  is_read: boolean;
  notification_type: string;
  revision_id?: string | null;
}

export interface NotificationCreate extends NotificationBase {
  user_id: string;
}

export interface Notification extends NotificationBase {
  notification_id: string;
  user_id: string;
  created_at: string;
  updated_at: string;
}

// 選択用の軽量な型
export interface ApprovalGroupOption {
  group_id: string;
  group_name: string;
  is_active: boolean;
}

export interface InfoCategoryOption {
  category_id: string;
  category_name: string;
  is_active: boolean;
}