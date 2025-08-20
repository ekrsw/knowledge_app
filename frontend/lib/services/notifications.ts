import apiClient from '../api';
import { SimpleNotification, NotificationStats, PaginationParams } from '../../types/api';

export class NotificationsService {
  // Get my notifications
  async getMyNotifications(
    unreadOnly: boolean = false,
    params?: PaginationParams
  ): Promise<SimpleNotification[]> {
    const queryParams = new URLSearchParams();
    queryParams.set('unread_only', unreadOnly.toString());
    if (params?.skip) queryParams.set('skip', params.skip.toString());
    if (params?.limit) queryParams.set('limit', params.limit.toString());

    return apiClient.get<SimpleNotification[]>(
      `/notifications/my-notifications?${queryParams.toString()}`
    );
  }

  // Get notification statistics
  async getNotificationStatistics(daysBack: number = 30): Promise<NotificationStats> {
    return apiClient.get<NotificationStats>(
      `/notifications/statistics?days_back=${daysBack}`
    );
  }

  // Get notification digest
  async getNotificationDigest(
    digestType: 'daily' | 'weekly' = 'daily'
  ): Promise<{
    digest_type: string;
    period: { start: string; end: string };
    summary: {
      total_notifications: number;
      by_type: Record<string, number>;
      urgent_count: number;
    };
    highlights: Array<{
      notification_id: string;
      title: string;
      importance: 'high' | 'medium' | 'low';
    }>;
    recommendations: string[];
  }> {
    return apiClient.get(
      `/notifications/digest?digest_type=${digestType}`
    );
  }

  // Mark notification as read
  async markAsRead(notificationId: string): Promise<SimpleNotification> {
    return apiClient.put<SimpleNotification>(
      `/notifications/${notificationId}/read`
    );
  }

  // Mark all notifications as read
  async markAllAsRead(): Promise<{ marked_as_read_count: number }> {
    return apiClient.put('/notifications/read-all');
  }

  // Batch create notifications (admin only)
  async createBatchNotifications(request: {
    user_ids: string[];
    title: string;
    message: string;
    notification_type: string;
  }): Promise<{
    success_count: number;
    failure_count: number;
    created_notifications: string[];
  }> {
    return apiClient.post('/notifications/batch', request);
  }

  // Legacy endpoints for backward compatibility
  
  // Get user notifications (admin only - legacy)
  async getUserNotifications(userId: string): Promise<SimpleNotification[]> {
    return apiClient.get<SimpleNotification[]>(`/notifications/${userId}`);
  }

  // Create notification (admin only - legacy)
  async createNotification(notificationData: {
    user_id: string;
    title: string;
    message: string;
    notification_type: string;
  }): Promise<SimpleNotification> {
    return apiClient.post<SimpleNotification>('/notifications/', notificationData);
  }
}

export const notificationsService = new NotificationsService();