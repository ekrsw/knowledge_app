import { apiClient } from '@/lib/api-client'
import {
  Revision,
  CreateRevisionRequest,
  UpdateRevisionRequest,
  RevisionListParams,
  InfoCategory,
  Article
} from '@/types/revision'

export class RevisionService {
  // 修正案一覧取得
  static async getRevisions(params: RevisionListParams = {}) {
    const queryParams = new URLSearchParams()
    
    if (params.page) queryParams.append('page', params.page.toString())
    if (params.limit) queryParams.append('limit', params.limit.toString())
    if (params.status) queryParams.append('status', params.status)
    if (params.category_id) queryParams.append('category_id', params.category_id.toString())
    if (params.author_id) queryParams.append('author_id', params.author_id.toString())
    if (params.search) queryParams.append('search', params.search)

    const query = queryParams.toString()
    const endpoint = `/api/v1/revisions${query ? `?${query}` : ''}`
    
    return apiClient.get<{
      revisions: Revision[]
      total: number
      page: number
      limit: number
      total_pages: number
    }>(endpoint)
  }

  // 修正案詳細取得
  static async getRevision(id: number): Promise<Revision> {
    return apiClient.get<Revision>(`/api/v1/revisions/${id}`)
  }

  // 修正案作成
  static async createRevision(data: CreateRevisionRequest): Promise<Revision> {
    return apiClient.post<Revision>('/api/v1/revisions', data)
  }

  // 修正案更新
  static async updateRevision(id: number, data: UpdateRevisionRequest): Promise<Revision> {
    return apiClient.put<Revision>(`/api/v1/revisions/${id}`, data)
  }

  // 修正案削除
  static async deleteRevision(id: number): Promise<void> {
    return apiClient.delete<void>(`/api/v1/revisions/${id}`)
  }

  // 修正案提出
  static async submitRevision(id: number): Promise<Revision> {
    return apiClient.put<Revision>(`/api/v1/revisions/${id}/submit`, {})
  }

  // カテゴリ一覧取得
  static async getCategories(): Promise<InfoCategory[]> {
    return apiClient.get<InfoCategory[]>('/api/v1/info-categories')
  }

  // 記事一覧取得
  static async getArticles(categoryId?: number): Promise<Article[]> {
    const endpoint = categoryId 
      ? `/api/v1/articles?category_id=${categoryId}`
      : '/api/v1/articles'
    return apiClient.get<Article[]>(endpoint)
  }
}