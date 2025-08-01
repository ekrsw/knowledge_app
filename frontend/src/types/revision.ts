export interface Revision {
  id: number
  title: string
  description: string
  content: string
  status: RevisionStatus
  category_id: number
  article_id?: number
  author_id: number
  created_at: string
  updated_at: string
  author?: {
    id: number
    name: string
    username: string
  }
  category?: {
    id: number
    name: string
    code: string
  }
  article?: {
    id: number
    title: string
    content: string
  }
}

export type RevisionStatus = 'draft' | 'submitted' | 'approved' | 'rejected' | 'deleted'

export interface CreateRevisionRequest {
  title: string
  description: string
  content: string
  category_id: number
  article_id?: number
}

export interface UpdateRevisionRequest {
  title?: string
  description?: string
  content?: string
  category_id?: number
  status?: RevisionStatus
}

export interface RevisionListParams {
  page?: number
  limit?: number
  status?: RevisionStatus
  category_id?: number
  author_id?: number
  search?: string
}

export interface InfoCategory {
  id: number
  name: string
  code: string
  description?: string
}

export interface Article {
  id: number
  title: string
  content: string
  category_id: number
  created_at: string
  updated_at: string
  category?: InfoCategory
}