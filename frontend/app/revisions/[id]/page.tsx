'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { ArrowLeft, Edit, Trash2, Send, FileText } from 'lucide-react'
import { ProtectedRoute } from '@/components/auth/protected-route'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { RevisionService } from '@/services/revision-service'
import { Revision, RevisionStatus } from '@/types/revision'
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

interface RevisionDetailPageProps {
  params: { id: string }
}

export default function RevisionDetailPage({ params }: RevisionDetailPageProps) {
  return (
    <ProtectedRoute>
      <RevisionDetailContent revisionId={parseInt(params.id)} />
    </ProtectedRoute>
  )
}

function RevisionDetailContent({ revisionId }: { revisionId: number }) {
  const router = useRouter()
  const { user } = useAuth()
  const [revision, setRevision] = useState<Revision | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [actionLoading, setActionLoading] = useState(false)

  useEffect(() => {
    fetchRevision()
  }, [revisionId])

  const fetchRevision = async () => {
    try {
      setLoading(true)
      const data = await RevisionService.getRevision(revisionId)
      setRevision(data)
    } catch (err: any) {
      setError(err.message || '修正案の取得に失敗しました')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async () => {
    if (!revision || revision.status !== 'draft') return

    try {
      setActionLoading(true)
      await RevisionService.submitRevision(revision.id)
      await fetchRevision() // 最新状態を取得
    } catch (err: any) {
      setError(err.message || '修正案の提出に失敗しました')
    } finally {
      setActionLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!revision) return

    if (!confirm('この修正案を削除してもよろしいですか？')) return

    try {
      setActionLoading(true)
      await RevisionService.deleteRevision(revision.id)
      router.push('/revisions')
    } catch (err: any) {
      setError(err.message || '修正案の削除に失敗しました')
    } finally {
      setActionLoading(false)
    }
  }

  const isOwner = revision && user && revision.author_id === parseInt(user.id)
  const canEdit = isOwner && (revision?.status === 'draft' || revision?.status === 'rejected')
  const canSubmit = isOwner && revision?.status === 'draft'
  const canDelete = isOwner && (revision?.status === 'draft' || revision?.status === 'rejected')

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md">
          {error}
        </div>
      </div>
    )
  }

  if (!revision) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <p className="text-gray-500">修正案が見つかりません</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.back()}
              className="mr-4"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              戻る
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{revision.title}</h1>
              <p className="text-gray-600 mt-2">{revision.description}</p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <span className={`px-3 py-1 text-sm font-medium rounded-full ${statusColors[revision.status]}`}>
              {statusLabels[revision.status]}
            </span>
          </div>
        </div>

        {/* アクションボタン */}
        {(canEdit || canSubmit || canDelete) && (
          <div className="flex items-center justify-end space-x-2 mb-6">
            {canEdit && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => router.push(`/revisions/${revision.id}/edit`)}
              >
                <Edit className="mr-2 h-4 w-4" />
                編集
              </Button>
            )}
            {canSubmit && (
              <Button
                size="sm"
                onClick={handleSubmit}
                disabled={actionLoading}
              >
                <Send className="mr-2 h-4 w-4" />
                提出する
              </Button>
            )}
            {canDelete && (
              <Button
                variant="destructive"
                size="sm"
                onClick={handleDelete}
                disabled={actionLoading}
              >
                <Trash2 className="mr-2 h-4 w-4" />
                削除
              </Button>
            )}
          </div>
        )}

        <div className="space-y-6">
          {/* 修正案情報 */}
          <Card>
            <CardHeader>
              <CardTitle>修正案情報</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">作成者</label>
                  <p className="text-gray-900">{revision.author?.name} (@{revision.author?.username})</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">カテゴリ</label>
                  <p className="text-gray-900">{revision.category?.name} ({revision.category?.code})</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">作成日時</label>
                  <p className="text-gray-900">{new Date(revision.created_at).toLocaleString('ja-JP')}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">更新日時</label>
                  <p className="text-gray-900">{new Date(revision.updated_at).toLocaleString('ja-JP')}</p>
                </div>
              </div>

              {revision.article && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">関連記事</label>
                  <div className="flex items-center space-x-2">
                    <FileText className="h-4 w-4 text-gray-500" />
                    <span className="text-gray-900">{revision.article.title}</span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* 修正内容 */}
          <Card>
            <CardHeader>
              <CardTitle>修正内容</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="prose max-w-none">
                <pre className="whitespace-pre-wrap bg-gray-50 p-4 rounded-md text-sm">
                  {revision.content}
                </pre>
              </div>
            </CardContent>
          </Card>

          {/* 関連記事の内容（参考用） */}
          {revision.article && (
            <Card>
              <CardHeader>
                <CardTitle>関連記事の内容（参考）</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="prose max-w-none">
                  <pre className="whitespace-pre-wrap bg-blue-50 p-4 rounded-md text-sm">
                    {revision.article.content}
                  </pre>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}