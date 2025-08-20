import apiClient from '../api';
import {
  Revision,
  ApprovalDecision,
  ApprovalQueue,
  ApprovalMetrics,
  PaginationParams,
} from '../../types/api';

export class ApprovalsService {
  // Process approval decision
  async processApproval(
    revisionId: string,
    decision: ApprovalDecision
  ): Promise<Revision> {
    return apiClient.post<Revision>(
      `/approvals/${revisionId}/decide`,
      decision
    );
  }

  // Check if user can approve a revision
  async canApprove(revisionId: string): Promise<{ can_approve: boolean }> {
    return apiClient.get<{ can_approve: boolean }>(
      `/approvals/${revisionId}/can-approve`
    );
  }

  // Get approval queue
  async getApprovalQueue(
    priority?: 'low' | 'medium' | 'high' | 'urgent',
    params?: PaginationParams
  ): Promise<ApprovalQueue[]> {
    const queryParams = new URLSearchParams();
    if (priority) queryParams.set('priority', priority);
    if (params?.limit) queryParams.set('limit', params.limit.toString());

    const query = queryParams.toString();
    return apiClient.get<ApprovalQueue[]>(
      `/approvals/queue${query ? `?${query}` : ''}`
    );
  }

  // Get approval metrics
  async getApprovalMetrics(daysBack: number = 30): Promise<ApprovalMetrics> {
    return apiClient.get<ApprovalMetrics>(
      `/approvals/metrics?days_back=${daysBack}`
    );
  }

  // Get workload for current approver
  async getWorkload(): Promise<{
    pending_count: number;
    overdue_count: number;
    average_processing_time: number;
    efficiency_score: number;
  }> {
    return apiClient.get(`/approvals/workload`);
  }

  // Get workload for specific approver (admin only)
  async getApproverWorkload(approverId: string): Promise<{
    pending_count: number;
    overdue_count: number;
    average_processing_time: number;
    efficiency_score: number;
  }> {
    return apiClient.get(`/approvals/workload/${approverId}`);
  }

  // Bulk approval/rejection
  async processBulkApproval(request: {
    revision_ids: string[];
    action: 'approve' | 'reject' | 'request_changes' | 'defer';
    comment: string;
  }): Promise<{
    success_count: number;
    failure_count: number;
    skipped_count: number;
    results: Array<{ revision_id: string; status: string; message: string }>;
  }> {
    return apiClient.post('/approvals/bulk', request);
  }

  // Get approval history
  async getApprovalHistory(
    revisionId?: string,
    approverId?: string,
    params?: PaginationParams
  ): Promise<Array<{
    revision_id: string;
    approver_id: string;
    action: string;
    comment: string;
    processed_at: string;
  }>> {
    const queryParams = new URLSearchParams();
    if (revisionId) queryParams.set('revision_id', revisionId);
    if (approverId) queryParams.set('approver_id', approverId);
    if (params?.limit) queryParams.set('limit', params.limit.toString());

    const query = queryParams.toString();
    return apiClient.get(`/approvals/history${query ? `?${query}` : ''}`);
  }

  // Get dashboard statistics for approvers
  async getDashboardStatistics(): Promise<{
    queue_summary: {
      total_pending: number;
      high_priority: number;
      overdue: number;
    };
    performance_metrics: ApprovalMetrics;
    recent_activity: {
      approved_today: number;
      rejected_today: number;
      processing_time_today: number;
    };
    urgent_items: ApprovalQueue[];
  }> {
    return apiClient.get('/approvals/statistics/dashboard');
  }

  // Get team overview (admin only)
  async getTeamOverview(): Promise<{
    team_metrics: {
      total_approvers: number;
      active_approvers: number;
      bottlenecks: Array<{ approver_id: string; pending_count: number }>;
    };
    workload_distribution: Array<{
      approver_id: string;
      name: string;
      pending_count: number;
      efficiency_score: number;
    }>;
    recommendations: Array<{ type: string; message: string; priority: string }>;
  }> {
    return apiClient.get('/approvals/team-overview');
  }

  // Quick approval action
  async quickAction(
    revisionId: string,
    action: 'approve' | 'reject' | 'request_changes' | 'defer',
    comment?: string
  ): Promise<Revision> {
    const params = comment ? `?comment=${encodeURIComponent(comment)}` : '';
    return apiClient.post<Revision>(
      `/approvals/${revisionId}/quick-actions/${action}${params}`
    );
  }

  // Get workflow recommendations
  async getWorkflowRecommendations(): Promise<Array<{
    type: 'efficiency' | 'priority' | 'process';
    title: string;
    description: string;
    impact: 'low' | 'medium' | 'high';
    action_items: string[];
  }>> {
    return apiClient.get('/approvals/workflow/recommendations');
  }

  // Get approval checklist for a revision
  async getApprovalChecklist(revisionId: string): Promise<{
    checklist_items: Array<{
      category: string;
      items: Array<{
        id: string;
        description: string;
        required: boolean;
        completed: boolean;
      }>;
    }>;
    overall_score: number;
    recommendations: string[];
  }> {
    return apiClient.get(`/approvals/workflow/checklist/${revisionId}`);
  }
}

export const approvalsService = new ApprovalsService();