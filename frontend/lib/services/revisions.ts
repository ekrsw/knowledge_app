import apiClient from '../api';
import {
  Revision,
  RevisionCreate,
  RevisionUpdate,
  PaginationParams,
  RevisionStatus,
} from '../../types/api';

export class RevisionsService {
  // Get all revisions (with permissions)
  async getRevisions(params?: PaginationParams): Promise<Revision[]> {
    const queryParams = new URLSearchParams();
    if (params?.skip) queryParams.set('skip', params.skip.toString());
    if (params?.limit) queryParams.set('limit', params.limit.toString());

    const query = queryParams.toString();
    return apiClient.get<Revision[]>(`/revisions/${query ? `?${query}` : ''}`);
  }

  // Get revision by ID
  async getRevision(revisionId: string): Promise<Revision> {
    return apiClient.get<Revision>(`/revisions/${revisionId}`);
  }

  // Create new revision
  async createRevision(revisionData: RevisionCreate): Promise<Revision> {
    return apiClient.post<Revision>('/revisions/', revisionData);
  }

  // Update revision (draft only)
  async updateRevision(
    revisionId: string,
    updateData: RevisionUpdate
  ): Promise<Revision> {
    return apiClient.put<Revision>(`/revisions/${revisionId}`, updateData);
  }

  // Delete revision (draft only)
  async deleteRevision(revisionId: string): Promise<void> {
    return apiClient.delete(`/revisions/${revisionId}`);
  }

  // Get revisions by proposer
  async getRevisionsByProposer(
    proposerId: string,
    params?: PaginationParams
  ): Promise<Revision[]> {
    const queryParams = new URLSearchParams();
    if (params?.skip) queryParams.set('skip', params.skip.toString());
    if (params?.limit) queryParams.set('limit', params.limit.toString());

    const query = queryParams.toString();
    return apiClient.get<Revision[]>(
      `/revisions/by-proposer/${proposerId}${query ? `?${query}` : ''}`
    );
  }

  // Get revisions by status
  async getRevisionsByStatus(
    status: RevisionStatus,
    params?: PaginationParams
  ): Promise<Revision[]> {
    const queryParams = new URLSearchParams();
    if (params?.skip) queryParams.set('skip', params.skip.toString());
    if (params?.limit) queryParams.set('limit', params.limit.toString());

    const query = queryParams.toString();
    return apiClient.get<Revision[]>(
      `/revisions/by-status/${status}${query ? `?${query}` : ''}`
    );
  }

  // Get revisions by article (public only)
  async getRevisionsByArticle(
    articleId: string,
    params?: PaginationParams
  ): Promise<Revision[]> {
    const queryParams = new URLSearchParams();
    if (params?.skip) queryParams.set('skip', params.skip.toString());
    if (params?.limit) queryParams.set('limit', params.limit.toString());

    const query = queryParams.toString();
    return apiClient.get<Revision[]>(
      `/revisions/by-article/${articleId}${query ? `?${query}` : ''}`
    );
  }

  // Update revision status (admin only)
  async updateRevisionStatus(
    revisionId: string,
    status: RevisionStatus
  ): Promise<Revision> {
    return apiClient.patch<Revision>(`/revisions/${revisionId}/status`, {
      status,
    });
  }
}

export const revisionsService = new RevisionsService();