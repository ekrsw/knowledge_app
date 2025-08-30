import { ApiResponse, PaginatedResponse } from '@/types/api';
import { Revision, RevisionStatus } from '@/types';
import { apiClient } from './client';

export interface RevisionsListParams {
  skip?: number;
  limit?: number;
  status?: RevisionStatus;
  target_article_id?: string;
}

export interface RevisionCreateData {
  target_article_id: string;
  approver_id: string;
  revision_reason: string;
  after_title?: string;
  after_content?: string;
  after_summary?: string;
  after_tags?: string[];
  after_category_id?: string;
  after_publish_start?: string;
  after_publish_end?: string;
}

export interface RevisionUpdateData {
  revision_reason?: string;
  after_title?: string;
  after_content?: string;
  after_summary?: string;
  after_tags?: string[];
  after_category_id?: string;
  after_publish_start?: string;
  after_publish_end?: string;
}

/**
 * 修正案一覧を取得
 */
export async function getRevisions(params: RevisionsListParams = {}): Promise<PaginatedResponse<Revision>> {
  const searchParams = new URLSearchParams();
  
  if (params.skip !== undefined) searchParams.set('skip', params.skip.toString());
  if (params.limit !== undefined) searchParams.set('limit', params.limit.toString());
  if (params.status) searchParams.set('status', params.status);
  if (params.target_article_id) searchParams.set('target_article_id', params.target_article_id);

  const url = `/revisions/${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
  const response = await apiClient.get<Revision[]>(url);
  
  // バックエンドはList[Revision]を返すので、PaginatedResponseに変換
  const items = response.data;
  return {
    items,
    total: items.length, // 実際のtotalCountが必要な場合は別途APIで取得
    skip: params.skip || 0,
    limit: params.limit || 100,
    has_more: items.length === (params.limit || 100)
  };
}

/**
 * 修正案詳細を取得
 */
export async function getRevision(id: string): Promise<Revision> {
  const response = await apiClient.get<Revision>(`/revisions/${id}`);
  return response.data;
}

/**
 * 修正案を作成
 */
export async function createRevision(data: RevisionCreateData): Promise<Revision> {
  const response = await apiClient.post<Revision>('/revisions/', data);
  return response.data;
}

/**
 * 修正案を更新
 */
export async function updateRevision(id: string, data: RevisionUpdateData): Promise<Revision> {
  const response = await apiClient.put<Revision>(`/revisions/${id}`, data);
  return response.data;
}

/**
 * 修正案を削除
 */
export async function deleteRevision(id: string): Promise<void> {
  await apiClient.delete(`/revisions/${id}`);
}

/**
 * 自分の修正案一覧を取得
 */
export async function getMyRevisions(params: Omit<RevisionsListParams, 'target_article_id'> = {}): Promise<PaginatedResponse<Revision>> {
  const searchParams = new URLSearchParams();
  
  if (params.skip !== undefined) searchParams.set('skip', params.skip.toString());
  if (params.limit !== undefined) searchParams.set('limit', params.limit.toString());
  if (params.status) searchParams.set('status', params.status);

  const url = `/proposals/my-proposals${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
  const response = await apiClient.get<Revision[]>(url);
  
  // バックエンドはList[Revision]を返すので、PaginatedResponseに変換
  const items = response.data;
  return {
    items,
    total: items.length,
    skip: params.skip || 0,
    limit: params.limit || 100,
    has_more: items.length === (params.limit || 100)
  };
}

/**
 * 記事別修正案一覧を取得
 */
export async function getRevisionsByArticle(articleId: string, params: Omit<RevisionsListParams, 'target_article_id'> = {}): Promise<PaginatedResponse<Revision>> {
  const searchParams = new URLSearchParams();
  
  if (params.skip !== undefined) searchParams.set('skip', params.skip.toString());
  if (params.limit !== undefined) searchParams.set('limit', params.limit.toString());
  if (params.status) searchParams.set('status', params.status);

  const url = `/revisions/by-article/${articleId}${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
  const response = await apiClient.get<Revision[]>(url);
  
  // バックエンドはList[Revision]を返すので、PaginatedResponseに変換
  const items = response.data;
  return {
    items,
    total: items.length,
    skip: params.skip || 0,
    limit: params.limit || 100,
    has_more: items.length === (params.limit || 100)
  };
}