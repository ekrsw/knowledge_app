import apiClient from '../api';
import {
  Revision,
  RevisionCreate,
  RevisionUpdate,
  PaginationParams,
  ProposalStatistics,
  RevisionStatus,
} from '../../types/api';

export class ProposalsService {
  // Create new proposal (with business logic validation)
  async createProposal(proposalData: RevisionCreate): Promise<Revision> {
    return apiClient.post<Revision>('/proposals/', proposalData);
  }

  // Update proposal (draft only, with validation)
  async updateProposal(
    proposalId: string,
    updateData: RevisionUpdate
  ): Promise<Revision> {
    return apiClient.put<Revision>(`/proposals/${proposalId}`, updateData);
  }

  // Submit proposal (draft -> submitted)
  async submitProposal(proposalId: string): Promise<Revision> {
    return apiClient.post<Revision>(`/proposals/${proposalId}/submit`);
  }

  // Withdraw proposal (submitted -> draft)
  async withdrawProposal(proposalId: string): Promise<Revision> {
    return apiClient.post<Revision>(`/proposals/${proposalId}/withdraw`);
  }

  // Delete proposal (draft only)
  async deleteProposal(proposalId: string): Promise<void> {
    return apiClient.delete(`/proposals/${proposalId}`);
  }

  // Get my proposals
  async getMyProposals(
    status?: RevisionStatus,
    params?: PaginationParams
  ): Promise<Revision[]> {
    const queryParams = new URLSearchParams();
    if (status) queryParams.set('status', status);
    if (params?.skip) queryParams.set('skip', params.skip.toString());
    if (params?.limit) queryParams.set('limit', params.limit.toString());

    const query = queryParams.toString();
    return apiClient.get<Revision[]>(
      `/proposals/my-proposals${query ? `?${query}` : ''}`
    );
  }

  // Get proposals for approval
  async getProposalsForApproval(params?: PaginationParams): Promise<Revision[]> {
    const queryParams = new URLSearchParams();
    if (params?.skip) queryParams.set('skip', params.skip.toString());
    if (params?.limit) queryParams.set('limit', params.limit.toString());

    const query = queryParams.toString();
    return apiClient.get<Revision[]>(
      `/proposals/for-approval${query ? `?${query}` : ''}`
    );
  }

  // Get proposal statistics
  async getProposalStatistics(userId?: string): Promise<ProposalStatistics> {
    const queryParams = new URLSearchParams();
    if (userId) queryParams.set('user_id', userId);

    const query = queryParams.toString();
    return apiClient.get<ProposalStatistics>(
      `/proposals/statistics${query ? `?${query}` : ''}`
    );
  }

  // Get proposal detail (with permission check)
  async getProposal(proposalId: string): Promise<Revision> {
    return apiClient.get<Revision>(`/proposals/${proposalId}`);
  }

  // Update approved proposal (approver only)
  async updateApprovedProposal(
    proposalId: string,
    updateData: RevisionUpdate
  ): Promise<Revision> {
    return apiClient.put<Revision>(
      `/proposals/${proposalId}/approved-update`,
      updateData
    );
  }
}

export const proposalsService = new ProposalsService();