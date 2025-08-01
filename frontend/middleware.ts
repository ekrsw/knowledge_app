import { withAuth } from 'next-auth/middleware'

export default withAuth(
  function middleware(req) {
    // 認証が必要なルートでの追加ロジックをここに追加可能
  },
  {
    callbacks: {
      authorized: ({ token, req }) => {
        // 保護されたルートの認証チェック
        const { pathname } = req.nextUrl
        
        // 認証が必要なパス
        const protectedPaths = [
          '/revisions',
          '/approvals', 
          '/notifications',
          '/dashboard',
          '/profile'
        ]

        // 保護されたパスの場合はトークンが必要
        if (protectedPaths.some(path => pathname.startsWith(path))) {
          return !!token
        }

        return true
      },
    },
  }
)

export const config = {
  matcher: [
    '/revisions/:path*',
    '/approvals/:path*',
    '/notifications/:path*',
    '/dashboard/:path*',
    '/profile/:path*'
  ]
}