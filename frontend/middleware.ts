import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// 公開パス（認証不要）
const publicPaths = [
  '/login',
  '/api-test',
];

// 管理者専用パス
const adminPaths = [
  '/admin',
  '/users',
];

// 承認者専用パス（承認者と管理者がアクセス可能）
const approverPaths = [
  '/approvals',
  '/approval-queue',
];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // 公開パスへのアクセスは許可
  if (publicPaths.some(path => pathname === path || pathname.startsWith(`${path}/`))) {
    return NextResponse.next();
  }

  // APIルートは別途処理
  if (pathname.startsWith('/api/')) {
    return NextResponse.next();
  }

  // 静的ファイルは許可
  if (pathname.startsWith('/_next/') || pathname.startsWith('/static/')) {
    return NextResponse.next();
  }

  // ホームページの特別処理
  if (pathname === '/') {
    // トークンがない場合は許可（ランディングページとして表示）
    const token = request.cookies.get('auth-token')?.value;
    if (!token) {
      return NextResponse.next();
    }
    // トークンがある場合はダッシュボードへリダイレクト
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  // トークンの確認（cookieまたはheaderから）
  const token = request.cookies.get('auth-token')?.value || 
                request.headers.get('authorization')?.replace('Bearer ', '');

  // 認証チェック
  if (!token) {
    // 認証されていない場合はログインページへリダイレクト
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('returnUrl', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // JWTトークンのデコード（簡易版）
  try {
    // トークンのペイロード部分を取得
    const payload = JSON.parse(
      Buffer.from(token.split('.')[1], 'base64').toString()
    );
    
    // トークンの有効期限チェック
    if (payload.exp && payload.exp * 1000 < Date.now()) {
      const loginUrl = new URL('/login', request.url);
      loginUrl.searchParams.set('returnUrl', pathname);
      return NextResponse.redirect(loginUrl);
    }

    // ロールベースのアクセス制御
    const userRole = payload.role || 'user';

    // 管理者専用パスへのアクセスチェック
    if (adminPaths.some(path => pathname.startsWith(path))) {
      if (userRole !== 'admin') {
        return NextResponse.redirect(new URL('/unauthorized', request.url));
      }
    }

    // 承認者専用パスへのアクセスチェック
    if (approverPaths.some(path => pathname.startsWith(path))) {
      if (userRole !== 'approver' && userRole !== 'admin') {
        return NextResponse.redirect(new URL('/unauthorized', request.url));
      }
    }

    // アクセス許可
    return NextResponse.next();
  } catch (error) {
    // トークンのデコードに失敗した場合
    console.error('Token decode error:', error);
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('returnUrl', pathname);
    return NextResponse.redirect(loginUrl);
  }
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico, sitemap.xml, robots.txt (metadata files)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt|public/).*)',
  ],
};