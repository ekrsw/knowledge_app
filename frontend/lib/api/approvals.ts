import { apiClient } from '../../src/lib/api/client';

// Types
export interface ApprovalQueueItem {
  revision_id: string;
  target_article_id: string;
  article_number?: string;
  proposer_name: string;
  reason: string;
  priority: string;
  impact_level: string;
  total_changes: number;
  critical_changes: number;
  estimated_review_time: number;
  submitted_at: string;
  days_pending: number;
  is_overdue: boolean;
}

export interface ApprovalRequest {
  comment?: string;
}

export interface ApprovalDecision {
  action: 'approve' | 'reject';
  comment?: string;
  priority?: string;
}

export interface ApprovalResponse {
  revision_id: string;
  status: string;
  approver_id?: string;
  processed_at?: string;
  message: string;
}

export interface ApprovalStats {
  pending: number;
  approved_today: number;
  rejected_today: number;
  average_time: number;
}

// API Functions

/**
 * Get approval queue
 */
export async function getApprovalQueue(
  priority?: string,
  limit: number = 50
): Promise<ApprovalQueueItem[]> {
  const params = new URLSearchParams();
  if (priority) params.append('priority', priority);
  params.append('limit', limit.toString());
  
  const response = await apiClient.get(`/approvals/queue?${params.toString()}`);
  return response.data;
}

/**
 * Approve a revision
 */
export async function approveRevision(
  revisionId: string,
  request?: ApprovalRequest
): Promise<any> {
  const decision: ApprovalDecision = {
    action: 'approve',
    comment: request?.comment
  };
  const response = await apiClient.post(`/approvals/${revisionId}/decide`, decision);
  return response.data;
}

/**
 * Reject a revision
 */
export async function rejectRevision(
  revisionId: string,
  request?: ApprovalRequest
): Promise<any> {
  const decision: ApprovalDecision = {
    action: 'reject',
    comment: request?.comment
  };
  const response = await apiClient.post(`/approvals/${revisionId}/decide`, decision);
  return response.data;
}

/**
 * Get approval statistics for current user
 */
export async function getApprovalStats(): Promise<ApprovalStats> {
  try {
    // ダッシュボードAPIを使用して統計情報を取得
    const response = await apiClient.get('/approvals/statistics/dashboard');
    const dashboard = response.data;
    
    // ワークロードデータから統計を抽出
    return {
      pending: dashboard.summary?.pending_count || dashboard.workload?.pending_count || 0,
      approved_today: 0, // ダッシュボードからは取得できないためデフォルト値
      rejected_today: 0,
      average_time: dashboard.metrics?.average_processing_time || 0
    };
  } catch (error) {
    // フォールバック: メトリクスAPIを使用
    try {
      const response = await apiClient.get('/approvals/metrics');
      const metrics = response.data;
      return {
        pending: 0, // メトリクスからは現在の保留件数が取得できない
        approved_today: metrics.daily_approved || 0,
        rejected_today: metrics.daily_rejected || 0,
        average_time: metrics.average_processing_time || 0
      };
    } catch (fallbackError) {
      // 最終的なフォールバック: デフォルト値を返す
      return {
        pending: 0,
        approved_today: 0,
        rejected_today: 0,
        average_time: 0
      };
    }
  }
}