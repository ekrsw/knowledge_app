/**
 * 通知関連の型定義
 */

export type NotificationType = 
  | 'revision_submitted'
  | 'revision_approved'
  | 'revision_rejected'
  | 'revision_withdrawn'
  | 'revision_updated'
  | 'comment_added'
  | 'mention';

export interface SimpleNotification {
  notification_id: string;  // UUID
  user_id: string;  // UUID
  revision_id?: string | null;  // UUID
  notification_type: NotificationType;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;  // ISO 8601 datetime
  read_at?: string | null;  // ISO 8601 datetime
  
  // Relations (populated in some endpoints)
  revision?: any;  // Revision object
}

export interface NotificationCreate {
  user_id: string;
  revision_id?: string | null;
  notification_type: NotificationType;
  title: string;
  message: string;
}

export interface NotificationBatchCreate {
  user_ids: string[];
  notification_type: NotificationType;
  title: string;
  message: string;
  revision_id?: string | null;
}

export interface NotificationStats {
  total_count: number;
  unread_count: number;
  by_type: Record<NotificationType, number>;
}