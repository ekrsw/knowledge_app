import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: false, // 開発時の二重実行を一時的に無効化
  
  // APIリライト設定（プロキシ回避）
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: 'http://localhost:8000/api/v1/:path*',
      },
    ];
  },
  
  // 環境変数の設定
  env: {
    NO_PROXY: 'localhost,127.0.0.1',
    no_proxy: 'localhost,127.0.0.1',
  },
};

export default nextConfig;
