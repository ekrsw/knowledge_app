'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Plus, Search, Filter } from 'lucide-react'
import { ProtectedRoute } from '@/components/auth/protected-route'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { RevisionService } from '@/services/revision-service'
import { Revision, RevisionStatus, InfoCategory } from '@/types/revision'
import { useAuth } from '@/hooks/use-auth'

const statusLabels: Record<RevisionStatus, string> = {
  draft: '下書き',
  submitted: '提出済み',
  approved: '承認済み',
  rejected: '却下',
  deleted: '削除済み'
}

const statusColors: Record<RevisionStatus, string> = {
  draft: 'bg-gray-100 text-gray-800',
  submitted: 'bg-blue-100 text-blue-800',
  approved: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
  deleted: 'bg-gray-100 text-gray-500'
}

export default function RevisionsPage() {
  return (
    <ProtectedRoute>
      <RevisionsContent />
    </ProtectedRoute>
  )
}

function RevisionsContent() {
  const { user } = useAuth()
  const [revisions, setRevisions] = useState<Revision[]>([])
  const [categories, setCategories] = useState<InfoCategory[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  
  // フィルタ状態
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedStatus, setSelectedStatus] = useState<RevisionStatus | ''>('')
  const [selectedCategory, setSelectedCategory] = useState<number | ''>('')
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)

  // データ取得
  const fetchRevisions = async () => {
    try {
      setLoading(true)
      const params = {
        page: currentPage,
        limit: 10,
        ...(searchTerm && { search: searchTerm }),
        ...(selectedStatus && { status: selectedStatus }),
        ...(selectedCategory && { category_id: selectedCategory }),
      }
      
      const response = await RevisionService.getRevisions(params)
      setRevisions(response.revisions)
      setTotalPages(response.total_pages)
    } catch (err) {
      setError('修正案の取得に失敗しました')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const fetchCategories = async () => {
    try {
      const data = await RevisionService.getCategories()
      setCategories(data)
    } catch (err) {
      console.error('カテゴリ取得エラー:', err)
    }
  }

  useEffect(() => {
    fetchCategories()
  }, [])

  useEffect(() => {
    fetchRevisions()
  }, [currentPage, selectedStatus, selectedCategory])

  const handleSearch = () => {
    setCurrentPage(1)
    fetchRevisions()
  }

  const handleReset = () => {
    setSearchTerm('')
    setSelectedStatus('')
    setSelectedCategory('')
    setCurrentPage(1)
  }

  if (loading && currentPage === 1) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">修正案管理</h1>
          <p className="text-gray-600 mt-2">ナレッジの修正案を管理します</p>
        </div>
        <Button asChild>
          <Link href="/revisions/new">
            <Plus className="mr-2 h-4 w-4" />
            新規作成
          </Link>
        </Button>
      </div>

      {/* フィルタ・検索 */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-lg">検索・フィルタ</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="flex space-x-2">
              <Input
                placeholder="修正案を検索..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="flex-1"
              />
              <Button onClick={handleSearch} size="sm">
                <Search className="h-4 w-4" />
              </Button>
            </div>
            
            <Select value={selectedStatus} onValueChange={(value: string) => setSelectedStatus(value as RevisionStatus | '')}>
              <SelectTrigger>
                <SelectValue placeholder="ステータス" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">すべてのステータス</SelectItem>
                {Object.entries(statusLabels).map(([value, label]) => (
                  <SelectItem key={value} value={value}>
                    {label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={selectedCategory.toString()} onValueChange={(value: string) => setSelectedCategory(value ? Number(value) : '')}>
              <SelectTrigger>
                <SelectValue placeholder="カテゴリ" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">すべてのカテゴリ</SelectItem>
                {categories.map((category) => (
                  <SelectItem key={category.id} value={category.id.toString()}>
                    {category.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Button variant="outline" onClick={handleReset}>
              <Filter className="mr-2 h-4 w-4" />
              リセット
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* エラー表示 */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md mb-6">
          {error}
        </div>
      )}

      {/* 修正案一覧 */}
      <div className="space-y-4">
        {revisions.length === 0 ? (
          <Card>
            <CardContent className="text-center py-8">
              <p className="text-gray-500">修正案が見つかりませんでした</p>
            </CardContent>
          </Card>
        ) : (
          revisions.map((revision) => (
            <Card key={revision.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg">
                      <Link 
                        href={`/revisions/${revision.id}`}
                        className="hover:text-blue-600 transition-colors"
                      >
                        {revision.title}
                      </Link>
                    </CardTitle>
                    <CardDescription className="mt-1">
                      {revision.description}
                    </CardDescription>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusColors[revision.status]}`}>
                      {statusLabels[revision.status]}
                    </span>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <div className="flex items-center space-x-4">
                    <span>作成者: {revision.author?.name}</span>
                    <span>カテゴリ: {revision.category?.name}</span>
                  </div>
                  <span>{new Date(revision.created_at).toLocaleDateString('ja-JP')}</span>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* ページネーション */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center space-x-2 mt-8">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
            disabled={currentPage === 1}
          >
            前へ
          </Button>
          <span className="px-4 py-2 text-sm">
            {currentPage} / {totalPages}
          </span>
          <Button
            variant="outline" 
            size="sm"
            onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
            disabled={currentPage === totalPages}
          >
            次へ
          </Button>
        </div>
      )}
    </div>
  )
}