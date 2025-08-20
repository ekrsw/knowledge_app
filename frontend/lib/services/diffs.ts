import apiClient from '../api';
import { RevisionDiff, Article } from '../../types/api';

export class DiffsService {
  // Get revision diff
  async getRevisionDiff(revisionId: string): Promise<RevisionDiff> {
    return apiClient.get<RevisionDiff>(`/diffs/${revisionId}`);
  }

  // Get article snapshot
  async getArticleSnapshot(articleId: string): Promise<Article> {
    return apiClient.get<Article>(`/diffs/article/${articleId}/snapshot`);
  }

  // Get article history
  async getArticleHistory(
    articleId: string,
    params?: { limit?: number }
  ): Promise<RevisionDiff[]> {
    const queryParams = new URLSearchParams();
    if (params?.limit) queryParams.set('limit', params.limit.toString());

    const query = queryParams.toString();
    return apiClient.get<RevisionDiff[]>(
      `/diffs/article/${articleId}/history${query ? `?${query}` : ''}`
    );
  }

  // Compare two revisions
  async compareRevisions(
    revisionId1: string,
    revisionId2: string
  ): Promise<{
    revision_1: RevisionDiff;
    revision_2: RevisionDiff;
    comparison: {
      common_changes: string[];
      unique_to_1: string[];
      unique_to_2: string[];
      conflict_fields: string[];
    };
  }> {
    return apiClient.post('/diffs/compare', {
      revision_id_1: revisionId1,
      revision_id_2: revisionId2,
    });
  }

  // Get formatted diff
  async getFormattedDiff(
    revisionId: string,
    includeFormatting: boolean = true
  ): Promise<{
    revision_id: string;
    formatted_diffs: Record<string, {
      current: string;
      proposed: string;
      diff_html: string;
      change_type: string;
    }>;
    summary: {
      total_changes: number;
      significant_changes: number;
      formatting_changes: number;
    };
  }> {
    return apiClient.get(
      `/diffs/${revisionId}/formatted?include_formatting=${includeFormatting}`
    );
  }

  // Get diff summary
  async getDiffSummary(revisionId: string): Promise<{
    revision_id: string;
    summary: {
      total_changes: number;
      fields_changed: string[];
      impact_level: 'low' | 'medium' | 'high';
      estimated_review_time: number;
      change_categories: Record<string, number>;
    };
    recommendations: string[];
  }> {
    return apiClient.get(`/diffs/${revisionId}/summary`);
  }

  // Get bulk summaries
  async getBulkSummaries(
    revisionIds: string[]
  ): Promise<Array<{
    revision_id: string;
    summary: {
      total_changes: number;
      impact_level: 'low' | 'medium' | 'high';
      estimated_review_time: number;
    };
    error?: string;
  }>> {
    return apiClient.post('/diffs/bulk-summaries', {
      revision_ids: revisionIds,
    });
  }

  // Get change statistics
  async getChangeStatistics(
    days: number = 30
  ): Promise<{
    time_range: {
      start_date: string;
      end_date: string;
      days: number;
    };
    statistics: {
      total_changes: number;
      by_status: Record<string, number>;
      by_impact: Record<string, number>;
      by_field: Record<string, number>;
      by_day: Array<{ date: string; count: number }>;
    };
    trends: {
      change_volume_trend: 'increasing' | 'decreasing' | 'stable';
      complexity_trend: 'increasing' | 'decreasing' | 'stable';
      popular_fields: string[];
    };
  }> {
    return apiClient.get(`/diffs/statistics/changes?days=${days}`);
  }
}

export const diffsService = new DiffsService();