'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { ArrowLeft, Save, Send } from 'lucide-react'
import { ProtectedRoute } from '@/components/auth/protected-route'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { RevisionService } from '@/services/revision-service'
import { InfoCategory, Article, Revision, UpdateRevisionRequest } from '@/types/revision'
import { useAuth } from '@/hooks/use-auth'

interface EditRevisionPageProps {
  params: { id: string }
}

export default function EditRevisionPage({ params }: EditRevisionPageProps) {
  return (
    <ProtectedRoute>
      <EditRevisionContent revisionId={parseInt(params.id)} />
    </ProtectedRoute>
  )
}

function EditRevisionContent({ revisionId }: { revisionId: number }) {
  const router = useRouter()
  const { user } = useAuth()
  const [revision, setRevision] = useState<Revision | null>(null)
  const [categories, setCategories] = useState<InfoCategory[]>([])
  const [articles, setArticles] = useState<Article[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  // フォーム状態
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    content: '',
    category_id: '',
    article_id: ''
  })

  // バリデーションエラー
  const [errors, setErrors] = useState<Record<string, string>>({})

  useEffect(() => {
    fetchRevision()
    fetchCategories()
  }, [revisionId])

  useEffect(() => {
    if (formData.category_id) {
      fetchArticles(Number(formData.category_id))
    } else {
      setArticles([])
      setFormData(prev => ({ ...prev, article_id: '' }))
    }
  }, [formData.category_id])

  const fetchRevision = async () => {
    try {
      const data = await RevisionService.getRevision(revisionId)
      setRevision(data)
      
      // フォームデータを設定
      setFormData({
        title: data.title,
        description: data.description,
        content: data.content,
        category_id: data.category_id.toString(),
        article_id: data.article_id?.toString() || ''
      })
    } catch (err: any) {
      setError(err.message || '修正案の取得に失敗しました')
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

  const fetchArticles = async (categoryId: number) => {
    try {
      const data = await RevisionService.getArticles(categoryId)
      setArticles(data)
    } catch (err) {
      console.error('記事取得エラー:', err)
    }
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData.title.trim()) {
      newErrors.title = 'タイトルは必須です'
    }
    if (!formData.description.trim()) {
      newErrors.description = '概要は必須です'
    }
    if (!formData.content.trim()) {
      newErrors.content = '修正内容は必須です'
    }
    if (!formData.category_id) {
      newErrors.category_id = 'カテゴリは必須です'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (shouldSubmit: boolean = false) => {
    if (!validateForm() || !revision) return

    // 権限チェック
    const isOwner = user && revision.author_id === parseInt(user.id)
    const canEdit = isOwner && (revision.status === 'draft' || revision.status === 'rejected')
    
    if (!canEdit) {
      setError('この修正案を編集する権限がありません')
      return
    }

    setSaving(true)
    setError('')

    try {
      const updateData: UpdateRevisionRequest = {
        title: formData.title.trim(),
        description: formData.description.trim(),
        content: formData.content.trim(),
        category_id: Number(formData.category_id),
      }

      // article_idが変更された場合のみ送信
      if (formData.article_id !== (revision.article_id?.toString() || '')) {
        updateData.category_id = Number(formData.category_id)
      }

      await RevisionService.updateRevision(revision.id, updateData)

      // 提出する場合
      if (shouldSubmit && revision.status === 'draft') {
        await RevisionService.submitRevision(revision.id)
      }

      router.push(`/revisions/${revision.id}`)
    } catch (err: any) {
      setError(err.message || '修正案の更新に失敗しました')
    } finally {
      setSaving(false)
    }
  }

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // エラーをクリア
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
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

  // 権限チェック
  const isOwner = user && revision.author_id === parseInt(user.id)
  const canEdit = isOwner && (revision.status === 'draft' || revision.status === 'rejected')

  if (!canEdit) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md">
          この修正案を編集する権限がありません
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center mb-8">
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
            <h1 className="text-3xl font-bold text-gray-900">修正案編集</h1>
            <p className="text-gray-600 mt-2">修正案の内容を編集します</p>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md mb-6">
            {error}
          </div>
        )}

        <div className="space-y-6">
          {/* 基本情報 */}
          <Card>
            <CardHeader>
              <CardTitle>基本情報</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  タイトル <span className="text-red-500">*</span>
                </label>
                <Input
                  value={formData.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  placeholder="修正案のタイトルを入力"
                  className={errors.title ? 'border-red-500' : ''}
                />
                {errors.title && (
                  <p className="text-red-500 text-sm mt-1">{errors.title}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  概要 <span className="text-red-500">*</span>
                </label>
                <Textarea
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  placeholder="修正案の概要を入力"
                  rows={3}
                  className={errors.description ? 'border-red-500' : ''}
                />
                {errors.description && (
                  <p className="text-red-500 text-sm mt-1">{errors.description}</p>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    カテゴリ <span className="text-red-500">*</span>
                  </label>
                  <Select
                    value={formData.category_id}
                    onValueChange={(value: string) => handleInputChange('category_id', value)}
                  >
                    <SelectTrigger className={errors.category_id ? 'border-red-500' : ''}>
                      <SelectValue placeholder="カテゴリを選択" />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map((category) => (
                        <SelectItem key={category.id} value={category.id.toString()}>
                          {category.name} ({category.code})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {errors.category_id && (
                    <p className="text-red-500 text-sm mt-1">{errors.category_id}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    関連記事（任意）
                  </label>
                  <Select
                    value={formData.article_id}
                    onValueChange={(value: string) => handleInputChange('article_id', value)}
                    disabled={!formData.category_id}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="関連記事を選択" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">なし</SelectItem>
                      {articles.map((article) => (
                        <SelectItem key={article.id} value={article.id.toString()}>
                          {article.title}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 修正内容 */}
          <Card>
            <CardHeader>
              <CardTitle>修正内容</CardTitle>
            </CardHeader>
            <CardContent>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  修正内容 <span className="text-red-500">*</span>
                </label>
                <Textarea
                  value={formData.content}
                  onChange={(e) => handleInputChange('content', e.target.value)}
                  placeholder="修正する内容を詳しく入力してください"
                  rows={10}
                  className={errors.content ? 'border-red-500' : ''}
                />
                {errors.content && (
                  <p className="text-red-500 text-sm mt-1">{errors.content}</p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* アクションボタン */}
          <div className="flex items-center justify-end space-x-4">
            <Button
              variant="outline"
              onClick={() => handleSubmit(false)}
              disabled={saving}
            >
              <Save className="mr-2 h-4 w-4" />
              保存
            </Button>
            {revision.status === 'draft' && (
              <Button
                onClick={() => handleSubmit(true)}
                disabled={saving}
              >
                <Send className="mr-2 h-4 w-4" />
                保存して提出
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}