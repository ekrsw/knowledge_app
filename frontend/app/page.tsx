export default function HomePage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Knowledge Revision System
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          ナレッジの修正案を提出・承認する機能
        </p>
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold mb-4">システム概要</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-3">
                <span className="text-blue-600 text-2xl">📝</span>
              </div>
              <h3 className="font-semibold mb-2">修正案作成</h3>
              <p className="text-sm text-gray-600">
                既存ナレッジの修正案を作成・提出
              </p>
            </div>
            <div className="text-center">
              <div className="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-3">
                <span className="text-green-600 text-2xl">✅</span>
              </div>
              <h3 className="font-semibold mb-2">承認ワークフロー</h3>
              <p className="text-sm text-gray-600">
                承認グループによる効率的な承認プロセス
              </p>
            </div>
            <div className="text-center">
              <div className="bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-3">
                <span className="text-purple-600 text-2xl">🔍</span>
              </div>
              <h3 className="font-semibold mb-2">差分表示</h3>
              <p className="text-sm text-gray-600">
                修正前後の差分を視覚的に表示
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}