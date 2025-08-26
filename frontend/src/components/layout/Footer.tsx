'use client';

export function Footer() {
  return (
    <footer className="bg-gray-800 border-t border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <p className="text-gray-400 text-sm">
              © 2025 Knowledge System Approval Platform (KSAP)
            </p>
          </div>
          
          <div className="flex items-center space-x-6">
            <a 
              href="/help" 
              className="text-gray-400 hover:text-white text-sm transition-colors"
            >
              ヘルプ
            </a>
            <a 
              href="/privacy" 
              className="text-gray-400 hover:text-white text-sm transition-colors"
            >
              プライバシーポリシー
            </a>
            <a 
              href="/terms" 
              className="text-gray-400 hover:text-white text-sm transition-colors"
            >
              利用規約
            </a>
          </div>
        </div>
        
        <div className="mt-2 pt-2 border-t border-gray-700">
          <p className="text-gray-500 text-xs text-center">
            ナレッジ改訂提案・承認システム - 組織の知識を正確で最新の状態に保つ
          </p>
        </div>
      </div>
    </footer>
  );
}