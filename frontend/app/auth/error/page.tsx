'use client'

import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

const errorMessages: Record<string, string> = {
  Configuration: 'サーバー設定に問題があります。管理者にお問い合わせください。',
  AccessDenied: 'アクセスが拒否されました。適切な権限がありません。',
  Verification: '認証トークンが無効または期限切れです。',
  Default: '認証中にエラーが発生しました。もう一度お試しください。',
}

export default function AuthErrorPage() {
  const searchParams = useSearchParams()
  const error = searchParams.get('error') || 'Default'
  const message = errorMessages[error] || errorMessages.Default

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl text-red-600">認証エラー</CardTitle>
          <CardDescription>
            ログイン処理中に問題が発生しました
          </CardDescription>
        </CardHeader>
        <CardContent className="text-center space-y-4">
          <p className="text-gray-700">{message}</p>
          <div className="space-y-2">
            <Button asChild className="w-full">
              <Link href="/auth/signin">
                ログイン画面に戻る
              </Link>
            </Button>
            <Button variant="outline" asChild className="w-full">
              <Link href="/">
                ホームに戻る
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}