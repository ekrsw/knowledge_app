'use client'

import { ProtectedRoute } from '@/components/auth/protected-route'
import { useAuth } from '@/hooks/use-auth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  )
}

function DashboardContent() {
  const { user } = useAuth()

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">ダッシュボード</h1>
        <p className="text-gray-600">ようこそ、{user?.name}さん</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>ユーザー情報</CardTitle>
            <CardDescription>あなたのアカウント情報</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <div>
              <span className="font-medium">名前: </span>
              <span>{user?.name}</span>
            </div>
            <div>
              <span className="font-medium">ユーザー名: </span>
              <span>@{user?.username}</span>
            </div>
            <div>
              <span className="font-medium">役割: </span>
              <span>{user?.role}</span>
            </div>
            <div>
              <span className="font-medium">承認グループID: </span>
              <span>{user?.approval_group_id}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>修正案</CardTitle>
            <CardDescription>あなたの修正案統計</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">0</div>
              <div className="text-sm text-gray-600">提出した修正案</div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>承認待ち</CardTitle>
            <CardDescription>あなたの承認が必要な案件</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">0</div>
              <div className="text-sm text-gray-600">承認待ちの案件</div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}