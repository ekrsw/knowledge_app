'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { 
  PencilIcon, 
  TrashIcon, 
  EyeIcon,
  PlusIcon,
  FunnelIcon,
  ChevronLeftIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline'
import { Article, ArticleListResponse, articleAdminService } from '@/services/article-admin-service'

interface ArticleListProps {
  initialData?: ArticleListResponse
}

interface Filters {
  category: string
  source: string
  is_draft: string
  search: string
}

export function ArticleList({ initialData }: ArticleListProps) {
  const [data, setData] = useState<ArticleListResponse | null>(initialData || null)
  const [loading, setLoading] = useState(!initialData)
  const [error, setError] = useState<string | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [showFilters, setShowFilters] = useState(false)
  const [filters, setFilters] = useState<Filters>({
    category: '',
    source: '',
    is_draft: '',
    search: ''
  })

  const loadArticles = async (page: number = 1) => {
    setLoading(true)
    setError(null)
    
    try {
      const params: any = { page, limit: 20 }
      
      if (filters.category) params.category = filters.category
      if (filters.source) params.source = filters.source
      if (filters.is_draft) params.is_draft = filters.is_draft === 'true'
      
      const response = await articleAdminService.getArticles(params)
      setData(response)
      setCurrentPage(page)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load articles')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!initialData) {
      loadArticles()
    }
  }, [initialData])

  const handleFilterChange = (key: keyof Filters, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  const applyFilters = () => {
    loadArticles(1)
  }

  const clearFilters = () => {
    setFilters({
      category: '',
      source: '',
      is_draft: '',
      search: ''
    })
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const getCategoryName = (category: string) => {
    return `Category ${category}`
  }

  if (loading && !data) {
    return (
      <div className="animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
        {[...Array(5)].map((_, i) => (
          <div key={i} className="border-b border-gray-200 py-4">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error loading articles</h3>
            <div className="mt-2 text-sm text-red-700">
              <p>{error}</p>
            </div>
            <div className="mt-4">
              <button
                onClick={() => loadArticles(currentPage)}
                className="bg-red-100 text-red-800 px-3 py-1 rounded text-sm hover:bg-red-200"
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Article Management</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage articles in the knowledge base
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            <FunnelIcon className="h-4 w-4 mr-2" />
            Filters
          </button>
          <Link
            href="/admin/articles/new"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            New Article
          </Link>
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="bg-gray-50 p-4 rounded-lg border">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Category
              </label>
              <select
                value={filters.category}
                onChange={(e) => handleFilterChange('category', e.target.value)}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              >
                <option value="">All Categories</option>
                {[...Array(26)].map((_, i) => {
                  const num = (i + 1).toString().padStart(2, '0')
                  return (
                    <option key={num} value={num}>
                      Category {num}
                    </option>
                  )
                })}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Source
              </label>
              <select
                value={filters.source}
                onChange={(e) => handleFilterChange('source', e.target.value)}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              >
                <option value="">All Sources</option>
                <option value="manual">Manual</option>
                <option value="external">External</option>
                <option value="sync">Sync</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                value={filters.is_draft}
                onChange={(e) => handleFilterChange('is_draft', e.target.value)}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              >
                <option value="">All Status</option>
                <option value="false">Published</option>
                <option value="true">Draft</option>
              </select>
            </div>
            
            <div className="flex items-end space-x-2">
              <button
                onClick={applyFilters}
                className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700"
              >
                Apply
              </button>
              <button
                onClick={clearFilters}
                className="px-4 py-2 bg-gray-300 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-400"
              >
                Clear
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Stats */}
      {data && (
        <div className="bg-white px-4 py-3 border rounded-lg">
          <p className="text-sm text-gray-600">
            Showing {data.articles.length} of {data.total_count} articles
            {data.page > 1 && ` (Page ${data.page})`}
          </p>
        </div>
      )}

      {/* Article List */}
      {data && data.articles.length > 0 ? (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {data.articles.map((article) => (
              <li key={article.article_id}>
                <div className="px-4 py-4 sm:px-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center">
                        <h3 className="text-lg font-medium text-gray-900 truncate">
                          {article.title}
                        </h3>
                        <div className="ml-2 flex-shrink-0 flex">
                          {article.is_draft && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                              Draft
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="mt-1 flex items-center text-sm text-gray-500">
                        <span>ID: {article.article_id}</span>
                        <span className="mx-2">•</span>
                        <span>{getCategoryName(article.info_category)}</span>
                        <span className="mx-2">•</span>
                        <span>Updated {formatDate(article.updated_at)}</span>
                      </div>
                      {article.tags.length > 0 && (
                        <div className="mt-2 flex flex-wrap gap-1">
                          {article.tags.map((tag) => (
                            <span
                              key={tag}
                              className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    <div className="ml-4 flex-shrink-0 flex items-center space-x-2">
                      <Link
                        href={`/admin/articles/${article.article_id}`}
                        className="text-blue-600 hover:text-blue-900"
                        title="View details"
                      >
                        <EyeIcon className="h-5 w-5" />
                      </Link>
                      <Link
                        href={`/admin/articles/${article.article_id}/edit`}
                        className="text-gray-600 hover:text-gray-900"
                        title="Edit article"
                      >
                        <PencilIcon className="h-5 w-5" />
                      </Link>
                      <button
                        className="text-red-600 hover:text-red-900"
                        title="Delete article"
                        onClick={() => {
                          // TODO: Implement delete confirmation dialog
                          console.log('Delete article:', article.article_id)
                        }}
                      >
                        <TrashIcon className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <div className="text-center py-12">
          <BookOpenIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No articles found</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by creating a new article.
          </p>
          <div className="mt-6">
            <Link
              href="/admin/articles/new"
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              New Article
            </Link>
          </div>
        </div>
      )}

      {/* Pagination */}
      {data && data.total_count > 20 && (
        <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
          <div className="flex-1 flex justify-between sm:hidden">
            <button
              onClick={() => loadArticles(currentPage - 1)}
              disabled={!data.has_prev || loading}
              className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => loadArticles(currentPage + 1)}
              disabled={!data.has_next || loading}
              className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              Next
            </button>
          </div>
          <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-gray-700">
                Showing page <span className="font-medium">{data.page}</span> of{' '}
                <span className="font-medium">{Math.ceil(data.total_count / 20)}</span>
              </p>
            </div>
            <div>
              <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                <button
                  onClick={() => loadArticles(currentPage - 1)}
                  disabled={!data.has_prev || loading}
                  className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                >
                  <ChevronLeftIcon className="h-5 w-5" />
                </button>
                <button
                  onClick={() => loadArticles(currentPage + 1)}
                  disabled={!data.has_next || loading}
                  className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                >
                  <ChevronRightIcon className="h-5 w-5" />
                </button>
              </nav>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}