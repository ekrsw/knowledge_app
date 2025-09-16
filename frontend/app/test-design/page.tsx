'use client';

import { useState, useEffect } from 'react';

// サイドバーナビゲーションコンポーネント
const SidebarNavigation = ({
  isCollapsed,
  onToggle,
  isMobileOpen,
  onMobileClose
}: {
  isCollapsed: boolean;
  onToggle: () => void;
  isMobileOpen: boolean;
  onMobileClose: () => void;
}) => {
  const navigationItems = [
    {
      label: 'ダッシュボード',
      href: '/dashboard',
      icon: '📊',
      isActive: false,
    },
    {
      label: '新規メンテナンス',
      href: '/maintenance/new',
      icon: '➕',
      isActive: false,
    },
    {
      label: 'メンテナンス一覧',
      href: '/maintenance',
      icon: '📋',
      isActive: true,
      children: [
        {
          label: '検索・フィルター',
          href: '/maintenance/search',
          icon: '🔍',
        },
        {
          label: '集計機能',
          href: '/maintenance/analytics',
          icon: '📊',
        },
      ],
    },
    {
      label: '承認待ち',
      href: '/approvals/pending',
      icon: '⏳',
      badge: 5,
      isActive: false,
    },
    {
      label: '管理機能',
      href: '/admin',
      icon: '⚙️',
      isActive: false,
      children: [
        {
          label: 'ユーザー管理',
          href: '/admin/users',
          icon: '👥',
        },
        {
          label: 'システム統計',
          href: '/admin/stats',
          icon: '📊',
        },
      ],
    },
  ];

  return (
    <>
      {/* モバイル用オーバーレイ */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={onMobileClose}
        />
      )}

      {/* サイドバー */}
      <div
        className={`
          ${isCollapsed ? 'w-16' : 'w-64'}
          bg-white border-r border-gray-200 flex-shrink-0 transition-all duration-200 ease-in-out
          lg:static lg:translate-x-0
          ${isMobileOpen ? 'translate-x-0' : '-translate-x-full'}
          fixed inset-y-0 left-0 z-50 lg:z-auto
        `}
      >
      {/* サイドバーヘッダー */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">
            K
          </div>
          {!isCollapsed && (
            <div>
              <h1 className="text-lg font-semibold text-gray-900">KSAP</h1>
              <p className="text-xs text-gray-500">Knowledge System</p>
            </div>
          )}
        </div>
      </div>

      {/* ユーザー情報 */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
            👤
          </div>
          {!isCollapsed && (
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                田中 太郎
              </p>
              <p className="text-xs text-gray-500 truncate">
                承認者
              </p>
            </div>
          )}
        </div>
      </div>

      {/* ナビゲーションメニュー */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navigationItems.map((item, index) => (
          <div key={index}>
            <div
              className={`flex items-center px-3 py-2 text-sm font-medium rounded-md cursor-pointer transition-colors ${
                item.isActive
                  ? 'bg-blue-100 text-blue-900'
                  : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
              }`}
            >
              <span className="mr-3 text-lg">{item.icon}</span>
              {!isCollapsed && (
                <>
                  <span className="flex-1">{item.label}</span>
                  {item.badge && (
                    <span className="ml-2 bg-red-500 text-white text-xs rounded-full px-2 py-1">
                      {item.badge}
                    </span>
                  )}
                </>
              )}
            </div>

            {/* サブメニュー */}
            {!isCollapsed && item.children && item.isActive && (
              <div className="ml-6 mt-1 space-y-1">
                {item.children.map((child, childIndex) => (
                  <div
                    key={childIndex}
                    className="flex items-center px-3 py-2 text-sm text-gray-600 rounded-md cursor-pointer hover:bg-gray-50 hover:text-gray-900"
                  >
                    <span className="mr-3 text-base">{child.icon}</span>
                    <span>{child.label}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </nav>

      {/* 折りたたみボタン */}
      <div className="p-4 border-t border-gray-200">
        <button
          onClick={onToggle}
          className="w-full flex items-center justify-center px-3 py-2 text-sm font-medium text-gray-700 rounded-md hover:bg-gray-100 transition-colors"
        >
          <span className="text-lg">{isCollapsed ? '→' : '←'}</span>
          {!isCollapsed && <span className="ml-2">折りたたみ</span>}
        </button>
        </div>
      </div>
    </>
  );
};

// メインコンテンツエリア
const MainContent = ({ onMobileMenuOpen }: { onMobileMenuOpen: () => void }) => {
  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* ページヘッダー */}
      <header className="bg-white border-b border-gray-200 px-4 lg:px-6 py-4">
        <div className="flex items-center justify-between">
          {/* モバイルメニューボタン */}
          <button
            onClick={onMobileMenuOpen}
            className="lg:hidden p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <div className="flex-1 lg:flex-none lg:block">
            <nav className="flex text-sm text-gray-500">
              <a href="#" className="hover:text-gray-700">ダッシュボード</a>
              <span className="mx-2">/</span>
              <a href="#" className="hover:text-gray-700">メンテナンス一覧</a>
              <span className="mx-2">/</span>
              <span className="text-gray-900">検索・フィルター</span>
            </nav>
            <h1 className="mt-1 text-2xl font-semibold text-gray-900">
              メンテナンス一覧
            </h1>
          </div>
          <button className="bg-blue-600 text-white px-3 lg:px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors text-sm lg:text-base">
            <span className="hidden sm:inline">新規作成</span>
            <span className="sm:hidden">➕</span>
          </button>
        </div>
      </header>

      {/* メインコンテンツ */}
      <main className="flex-1 overflow-auto p-4 lg:p-6">
        <div className="max-w-7xl mx-auto">
          {/* 検索・フィルターセクション */}
          <div className="bg-white rounded-lg border border-gray-200 p-4 lg:p-6 mb-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">検索・フィルター</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  キーワード検索
                </label>
                <input
                  type="text"
                  placeholder="タイトル、内容で検索..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  ステータス
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                  <option value="">すべて</option>
                  <option value="draft">ドラフト</option>
                  <option value="submitted">承認待ち</option>
                  <option value="approved">承認済み</option>
                  <option value="rejected">却下</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  カテゴリ
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                  <option value="">すべて</option>
                  <option value="system">システム</option>
                  <option value="process">プロセス</option>
                  <option value="document">ドキュメント</option>
                </select>
              </div>
            </div>
          </div>


          {/* メンテナンス一覧テーブル */}
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div className="px-4 lg:px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">メンテナンス提案一覧</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      案件番号
                    </th>
                    <th className="px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      タイトル
                    </th>
                    <th className="px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider hidden sm:table-cell">
                      ステータス
                    </th>
                    <th className="px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider hidden md:table-cell">
                      提案者
                    </th>
                    <th className="px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider hidden lg:table-cell">
                      更新日
                    </th>
                    <th className="px-4 lg:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      アクション
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {[
                    {
                      id: 'MAINT-001',
                      title: 'システム監視手順の更新',
                      status: 'submitted',
                      author: '佐藤 花子',
                      date: '2025-01-15',
                    },
                    {
                      id: 'MAINT-002',
                      title: 'データベースバックアップ手順改善',
                      status: 'approved',
                      author: '田中 太郎',
                      date: '2025-01-14',
                    },
                    {
                      id: 'MAINT-003',
                      title: 'セキュリティ設定ガイドライン',
                      status: 'draft',
                      author: '山田 次郎',
                      date: '2025-01-13',
                    },
                  ].map((item, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-4 lg:px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {item.id}
                      </td>
                      <td className="px-4 lg:px-6 py-4 text-sm text-gray-900">
                        <div className="lg:whitespace-nowrap">
                          {item.title}
                        </div>
                        <div className="sm:hidden mt-1">
                          <span
                            className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              item.status === 'submitted' ? 'bg-yellow-100 text-yellow-800' :
                              item.status === 'approved' ? 'bg-green-100 text-green-800' :
                              'bg-gray-100 text-gray-800'
                            }`}
                          >
                            {item.status === 'submitted' ? '承認待ち' :
                             item.status === 'approved' ? '承認済み' :
                             'ドラフト'}
                          </span>
                        </div>
                      </td>
                      <td className="px-4 lg:px-6 py-4 whitespace-nowrap hidden sm:table-cell">
                        <span
                          className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            item.status === 'submitted' ? 'bg-yellow-100 text-yellow-800' :
                            item.status === 'approved' ? 'bg-green-100 text-green-800' :
                            'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {item.status === 'submitted' ? '承認待ち' :
                           item.status === 'approved' ? '承認済み' :
                           'ドラフト'}
                        </span>
                      </td>
                      <td className="px-4 lg:px-6 py-4 whitespace-nowrap text-sm text-gray-900 hidden md:table-cell">
                        {item.author}
                      </td>
                      <td className="px-4 lg:px-6 py-4 whitespace-nowrap text-sm text-gray-900 hidden lg:table-cell">
                        {item.date}
                      </td>
                      <td className="px-4 lg:px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button className="text-blue-600 hover:text-blue-900 mr-3">
                          詳細
                        </button>
                        <button className="text-gray-600 hover:text-gray-900 hidden sm:inline">
                          編集
                        </button>
                        <button className="text-gray-600 hover:text-gray-900 sm:hidden">
                          ⋯
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

// メインのテストデザインページ
export default function TestDesignPage() {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // モバイルでサイドバーを自動的に折りたたむ
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 1024) {
        setIsSidebarCollapsed(true);
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div className="h-screen flex bg-gray-50">
      <SidebarNavigation
        isCollapsed={isSidebarCollapsed}
        onToggle={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        isMobileOpen={isMobileMenuOpen}
        onMobileClose={() => setIsMobileMenuOpen(false)}
      />
      <MainContent onMobileMenuOpen={() => setIsMobileMenuOpen(true)} />
    </div>
  );
}