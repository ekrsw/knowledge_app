import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <h2 className="text-6xl font-bold text-gray-400 mb-4">404</h2>
        <h3 className="text-2xl font-semibold text-gray-900 mb-4">ページが見つかりません</h3>
        <p className="text-gray-600 mb-6">
          お探しのページは存在しないか、移動した可能性があります。
        </p>
        <Link 
          href="/"
          className="bg-blue-600 text-white px-6 py-3 rounded hover:bg-blue-700 transition-colors"
        >
          ホームに戻る
        </Link>
      </div>
    </div>
  )
}