'use client';

import { useState, ReactNode } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { Footer } from './Footer';

interface MainLayoutProps {
  children: ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const { isAuthenticated, isLoading } = useAuth();

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const closeSidebar = () => {
    setIsSidebarOpen(false);
  };

  // 認証されていない場合はレイアウトを適用しない
  if (!isAuthenticated) {
    return <>{children}</>;
  }

  // ローディング中の表示
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          <p className="mt-4 text-gray-400">読み込み中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 flex">
      {/* サイドバー */}
      <Sidebar isOpen={isSidebarOpen} onClose={closeSidebar} />
      
      {/* メインコンテンツエリア */}
      <div className="flex-1 flex flex-col lg:pl-0">
        {/* ヘッダー */}
        <Header />
        
        {/* モバイル用メニューボタン */}
        <div className="lg:hidden bg-gray-800 px-4 py-2 border-b border-gray-700">
          <button
            onClick={toggleSidebar}
            className="text-gray-400 hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 p-2 rounded"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
        
        {/* メインコンテンツ */}
        <main className="flex-1 bg-gray-900">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            {children}
          </div>
        </main>
        
        {/* フッター */}
        <Footer />
      </div>
    </div>
  );
}