# KSAP フロントエンド UI/UX仕様

## 🎨 デザインシステム基盤

### デザイントークン (TailwindCSS v4)
```css
/* 色彩システム */
:root {
  /* Primary Colors (承認・成功) */
  --color-green-50: #f0fdf4;
  --color-green-500: #22c55e;
  --color-green-600: #16a34a;
  --color-green-700: #15803d;

  /* Danger Colors (却下・削除) */
  --color-red-50: #fef2f2;
  --color-red-500: #ef4444;
  --color-red-600: #dc2626;
  --color-red-700: #b91c1c;

  /* Warning Colors (変更要求・注意) */
  --color-yellow-50: #fefce8;
  --color-yellow-500: #eab308;
  --color-yellow-600: #ca8a04;
  --color-yellow-700: #a16207;

  /* Gray Scale (UI基調色) */
  --color-gray-50: #f9fafb;
  --color-gray-100: #f3f4f6;
  --color-gray-600: #4b5563;
  --color-gray-700: #374151;
  --color-gray-800: #1f2937;
  --color-gray-900: #111827;

  /* Critical (重要変更強調) */
  --color-orange-100: #fed7aa;
  --color-orange-500: #f97316;
  --color-orange-600: #ea580c;

  /* Typography */
  --font-family-sans: 'Geist', system-ui, sans-serif;
  --font-family-mono: 'Geist Mono', 'Courier New', monospace;
}
```

### タイポグラフィ階層
```css
/* 見出しシステム */
.heading-xl { @apply text-2xl font-bold leading-tight; }    /* ページタイトル */
.heading-lg { @apply text-xl font-semibold leading-tight; } /* セクションタイトル */
.heading-md { @apply text-lg font-medium leading-snug; }    /* サブセクション */
.heading-sm { @apply text-base font-medium leading-normal; } /* カード見出し */

/* 本文システム */
.body-lg { @apply text-base leading-relaxed; }    /* メイン本文 */
.body-md { @apply text-sm leading-relaxed; }      /* 補足テキスト */
.body-sm { @apply text-xs leading-normal; }       /* キャプション・ラベル */

/* モノスペース */
.mono-md { @apply font-mono text-sm; }            /* コード・差分表示 */
```

## 📱 レスポンシブデザイン戦略

### ブレークポイント定義
```typescript
const breakpoints = {
  sm: '640px',   // タブレット縦
  md: '768px',   // タブレット横
  lg: '1024px',  // デスクトップ (承認作業最適化)
  xl: '1280px',  // 大画面デスクトップ
  '2xl': '1536px' // 超大画面
} as const;

// 用途別画面サイズ
interface ScreenSizes {
  mobile: '~767px';     // ハンバーガーメニュー + 単一カラム
  tablet: '768px~1023px'; // サイドバー180px + メインコンテンツ
  desktop: '1024px+';    // サイドバー220px + 左60%右40%レイアウト
}
```

### サイドバーナビゲーション + 承認レビューのレスポンシブ
```css
/* アプリケーション全体レイアウト */
.app-layout {
  @apply flex h-screen bg-gray-50;
}

/* サイドバーナビゲーション */
.sidebar {
  @apply bg-white border-r border-gray-200 flex-shrink-0;
  transition: width 0.2s ease-in-out;
}

/* モバイル (ハンバーガーメニュー) */
@media (max-width: 767px) {
  .sidebar {
    @apply fixed inset-y-0 left-0 z-50 w-64 transform;
    /* JavaScript で -translate-x-full / translate-x-0 切り替え */
  }

  .main-content {
    @apply flex-1 flex flex-col;
  }

  .approval-review-layout {
    @apply flex flex-col gap-4 p-4 h-full;
  }

  .proposal-summary { @apply flex-shrink-0; }
  .diff-viewer { @apply flex-1 overflow-hidden; }
  .approval-actions { @apply flex-shrink-0; }
}

/* タブレット (サイドバー180px) */
@media (min-width: 768px) and (max-width: 1023px) {
  .sidebar {
    width: 180px;
  }

  .main-content {
    @apply flex-1 flex flex-col;
  }

  .approval-review-layout {
    @apply flex flex-col gap-4 p-4 h-full;
  }

  .proposal-summary { @apply flex-shrink-0; }
  .diff-viewer { @apply flex-1 overflow-hidden; }
  .approval-actions { @apply flex-shrink-0; }
}

/* デスクトップ (サイドバー220px + 左60%右40%) */
@media (min-width: 1024px) {
  .sidebar {
    width: 220px;
  }

  .main-content {
    @apply flex-1 flex flex-col;
  }

  .approval-review-layout {
    @apply flex gap-6 p-6 h-full;
  }

  .left-column {
    @apply flex-[3] flex flex-col gap-4 overflow-hidden;
  }

  .right-column {
    @apply flex-[2] flex flex-col gap-4;
  }

  .proposal-summary { @apply flex-shrink-0; }
  .diff-viewer { @apply flex-1 overflow-hidden; }
  .approval-actions { @apply flex-shrink-0; }
}
```

### サイドバーナビゲーション仕様
```css
/* サイドバー基本スタイル */
.sidebar-navigation {
  @apply flex-1 px-2 py-4 space-y-1 overflow-y-auto;
}

.nav-item {
  @apply flex items-center px-2 py-2 text-sm font-medium rounded-md;
  @apply hover:bg-gray-100 hover:text-gray-900;
  @apply focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500;
}

.nav-item.active {
  @apply bg-blue-100 text-blue-900;
}

.nav-item-icon {
  @apply mr-3 h-5 w-5 flex-shrink-0;
}

/* 折りたたみ対応 */
.sidebar.collapsed .nav-item-text {
  @apply hidden;
}

.sidebar.collapsed .nav-item-icon {
  @apply mr-0;
}

/* ユーザープロファイル */
.user-profile {
  @apply p-4 border-b border-gray-200;
}

.user-avatar {
  @apply h-8 w-8 rounded-full;
}

.sidebar.collapsed .user-profile {
  @apply px-2;
}

.sidebar.collapsed .user-info {
  @apply hidden;
}
```

## ⚡ 高速判定に特化したUI設計

### アクションボタンのサイズ・配置
```css
/* 承認アクションボタン (大型・明確) */
.action-button {
  @apply w-full py-4 px-6 text-lg font-semibold rounded-lg;
  @apply transition-all duration-200 ease-in-out;
  @apply focus:ring-4 focus:ring-offset-2 focus:outline-none;
  min-height: 56px; /* タッチターゲット最小サイズ */
}

.action-button-approve {
  @apply bg-green-600 hover:bg-green-700 text-white;
  @apply focus:ring-green-500;
}

.action-button-reject {
  @apply bg-red-600 hover:bg-red-700 text-white;
  @apply focus:ring-red-500;
}

.action-button-request-changes {
  @apply bg-yellow-600 hover:bg-yellow-700 text-white;
  @apply focus:ring-yellow-500;
}

.action-button-defer {
  @apply bg-gray-600 hover:bg-gray-700 text-white;
  @apply focus:ring-gray-500;
}

/* ホバー時の視覚フィードバック強化 */
.action-button:hover {
  @apply scale-105 shadow-lg;
}

/* 押下時のフィードバック */
.action-button:active {
  @apply scale-95;
}
```

### キーボードショートカット表示
```tsx
// components/ui/KeyboardShortcutsPanel.tsx
export function KeyboardShortcutsPanel() {
  return (
    <div className="bg-gray-50 rounded-lg p-4 space-y-2">
      <h4 className="font-medium text-sm text-gray-700 mb-3">
        ⌨️ キーボードショートカット
      </h4>

      <div className="space-y-2 text-sm">
        <ShortcutItem hotkey="A" action="承認" />
        <ShortcutItem hotkey="R" action="却下" />
        <ShortcutItem hotkey="C" action="変更要求" />
        <ShortcutItem hotkey="D" action="保留" />
        <ShortcutItem hotkey="→" action="次の案件" />
        <ShortcutItem hotkey="←" action="前の案件" />
        <ShortcutItem hotkey="T" action="コメント入力" />
      </div>
    </div>
  );
}

function ShortcutItem({ hotkey, action }: { hotkey: string; action: string }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-gray-600">{action}</span>
      <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-white border border-gray-200 rounded">
        {hotkey}
      </kbd>
    </div>
  );
}
```

## 🔍 差分理解に特化したUI設計

### 差分表示の視覚階層
```css
/* 差分アイテムの基本スタイル */
.diff-item {
  @apply border-l-4 rounded-r-lg p-4 mb-3;
  @apply transition-all duration-200;
}

/* 変更タイプ別スタイリング */
.diff-item-added {
  @apply border-l-green-500 bg-green-50;
}

.diff-item-modified {
  @apply border-l-yellow-500 bg-yellow-50;
}

.diff-item-removed {
  @apply border-l-red-500 bg-red-50;
}

/* 重要変更の強調表示 */
.diff-item-critical {
  @apply ring-2 ring-orange-400 bg-orange-50;
  @apply relative;
}

.diff-item-critical::before {
  content: "重要";
  @apply absolute -top-2 -right-2 bg-orange-500 text-white text-xs px-2 py-1 rounded;
}

/* インタラクティブ要素 */
.diff-item:hover {
  @apply shadow-md;
}

.diff-item-expandable {
  @apply cursor-pointer;
}

/* 長文テキストの制御 */
.diff-content-collapsed {
  @apply max-h-20 overflow-hidden relative;
}

.diff-content-collapsed::after {
  content: "";
  @apply absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-white to-transparent;
}
```

### Before/After 比較UI
```tsx
// components/approvals/BeforeAfterComparison.tsx
export function BeforeAfterComparison({ fieldDiff }: { fieldDiff: FieldDiff }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3">
      {/* Before (変更前) */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <ArrowLeftIcon className="w-4 h-4 text-red-500" />
          <label className="text-sm font-medium text-red-700">変更前</label>
        </div>
        <div className="p-3 bg-red-50 border border-red-200 rounded-md">
          <pre className="whitespace-pre-wrap text-sm font-mono text-red-800">
            {fieldDiff.old_value || '(なし)'}
          </pre>
        </div>
      </div>

      {/* After (変更後) */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <ArrowRightIcon className="w-4 h-4 text-green-500" />
          <label className="text-sm font-medium text-green-700">変更後</label>
        </div>
        <div className="p-3 bg-green-50 border border-green-200 rounded-md">
          <pre className="whitespace-pre-wrap text-sm font-mono text-green-800">
            {fieldDiff.new_value || '(なし)'}
          </pre>
        </div>
      </div>
    </div>
  );
}
```

### 変更サマリーインジケーター
```tsx
// components/approvals/ChangeSummaryIndicator.tsx
export function ChangeSummaryIndicator({ diff }: { diff: RevisionDiff }) {
  return (
    <div className="flex items-center gap-6 text-sm">
      {/* 総変更数 */}
      <div className="flex items-center gap-1">
        <PencilIcon className="w-4 h-4 text-gray-500" />
        <span className="font-medium">{diff.total_changes}件の変更</span>
      </div>

      {/* 重要変更数 */}
      {diff.critical_changes > 0 && (
        <div className="flex items-center gap-1 text-orange-600">
          <ExclamationTriangleIcon className="w-4 h-4" />
          <span className="font-medium">{diff.critical_changes}件が重要</span>
        </div>
      )}

      {/* 影響レベル */}
      <ImpactLevelBadge level={diff.impact_level} />

      {/* 変更カテゴリ */}
      <div className="flex gap-1">
        {diff.change_categories.map(category => (
          <CategoryBadge key={category} category={category} />
        ))}
      </div>
    </div>
  );
}

function ImpactLevelBadge({ level }: { level: 'low' | 'medium' | 'high' }) {
  const styles = {
    low: 'bg-blue-100 text-blue-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-red-100 text-red-800'
  };

  const labels = {
    low: '影響小',
    medium: '影響中',
    high: '影響大'
  };

  return (
    <span className={`px-2 py-1 text-xs font-medium rounded-full ${styles[level]}`}>
      {labels[level]}
    </span>
  );
}
```

## ♿ アクセシビリティ対応

### WCAG 2.1 AA準拠
```css
/* フォーカスインジケーター */
.focus-ring {
  @apply focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:outline-none;
}

/* 高コントラスト対応 */
@media (prefers-contrast: high) {
  .text-gray-600 { @apply text-gray-800; }
  .bg-gray-50 { @apply bg-gray-100; }
  .border-gray-200 { @apply border-gray-400; }
}

/* 動作縮減対応 */
@media (prefers-reduced-motion: reduce) {
  .transition-all { @apply transition-none; }
  .hover\\:scale-105:hover { @apply scale-100; }
}

/* 大きなテキスト対応 */
@media (min-resolution: 2dppx) {
  .text-sm { @apply text-base; }
  .text-xs { @apply text-sm; }
}
```

### スクリーンリーダー対応
```tsx
// アクセシブルな承認ボタン
<button
  className="action-button action-button-approve"
  onClick={handleApprove}
  aria-label="このメンテナンス提案を承認します。ショートカット: A キー"
  aria-describedby="approval-help-text"
>
  <CheckIcon className="w-5 h-5" aria-hidden="true" />
  承認する [A]
</button>

<div id="approval-help-text" className="sr-only">
  承認するとメンテナンス提案が承認済み状態になり、提案者に通知が送信されます
</div>

// 差分表示のアクセシビリティ
<div
  role="region"
  aria-label="変更内容の差分表示"
  aria-describedby="diff-summary"
>
  <div id="diff-summary" className="sr-only">
    {diff.total_changes}件の変更があります。うち{diff.critical_changes}件が重要な変更です。
  </div>

  {diff.field_diffs.map((fieldDiff, index) => (
    <div
      key={index}
      role="article"
      aria-label={`${fieldDiff.field_label}の${fieldDiff.change_type}変更`}
    >
      {/* 差分内容 */}
    </div>
  ))}
</div>
```

### キーボードナビゲーション
```tsx
// Tabインデックスの適切な管理
const TAB_ORDER = {
  SUMMARY: 1,
  DIFF_VIEWER: 2,
  COMMENT_INPUT: 3,
  APPROVE_BUTTON: 4,
  REJECT_BUTTON: 5,
  REQUEST_CHANGES_BUTTON: 6,
  DEFER_BUTTON: 7,
  NAVIGATION_BUTTONS: 8,
} as const;

// フォーカス管理
export function useAccessibleFocus() {
  const focusNextElement = () => {
    const focusableElements = document.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const currentIndex = Array.from(focusableElements).indexOf(document.activeElement as Element);
    const nextElement = focusableElements[currentIndex + 1];
    if (nextElement) {
      (nextElement as HTMLElement).focus();
    }
  };

  return { focusNextElement };
}
```

## 📊 ユーザビリティ最適化

### ローディング状態の段階表示
```tsx
// components/ui/ProgressiveLoading.tsx
export function ProgressiveLoadingIndicator({
  revision,
  diff,
  revisionLoading,
  diffLoading
}: {
  revision: RevisionWithNames | null;
  diff: RevisionDiff | null;
  revisionLoading: boolean;
  diffLoading: boolean;
}) {
  return (
    <div className="space-y-4">
      {/* プログレスバー */}
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-blue-500 h-2 rounded-full transition-all duration-500"
          style={{
            width: `${(!revisionLoading ? 50 : 0) + (!diffLoading ? 50 : 0)}%`
          }}
        />
      </div>

      {/* 段階的メッセージ */}
      <div className="text-sm text-gray-600">
        {revisionLoading && diffLoading && "データを読み込み中..."}
        {!revisionLoading && diffLoading && "差分を解析中..."}
        {!revisionLoading && !diffLoading && "読み込み完了"}
      </div>

      {/* Skeleton UI */}
      {(revisionLoading || diffLoading) && <LoadingSkeleton />}
    </div>
  );
}
```

### エラー状態のユーザーフレンドリー表示
```tsx
// components/ui/ErrorDisplay.tsx
export function ErrorDisplay({ error, onRetry }: {
  error: string;
  onRetry?: () => void;
}) {
  return (
    <div className="text-center py-12">
      <ExclamationCircleIcon className="w-16 h-16 text-red-400 mx-auto mb-4" />

      <h3 className="text-lg font-medium text-gray-900 mb-2">
        データの読み込みに失敗しました
      </h3>

      <p className="text-gray-600 mb-6 max-w-md mx-auto">
        {error}
      </p>

      {onRetry && (
        <div className="space-x-4">
          <Button onClick={onRetry} variant="primary">
            再試行
          </Button>
          <Button onClick={() => window.location.reload()} variant="secondary">
            ページを更新
          </Button>
        </div>
      )}
    </div>
  );
}
```

## 🎯 判定効率化のマイクロインタラクション

### ボタンホバー・押下フィードバック
```css
/* スムーズなトランジション */
.action-button {
  @apply transition-all duration-150 ease-out;
  transform-origin: center;
}

/* ホバー状態での予備フィードバック */
.action-button:hover {
  @apply shadow-lg;
  transform: translateY(-1px) scale(1.02);
}

/* アクティブ状態での即座フィードバック */
.action-button:active {
  @apply shadow-inner;
  transform: translateY(0) scale(0.98);
}

/* フォーカス時の明確な表示 */
.action-button:focus {
  @apply ring-4 ring-offset-2;
  outline: 2px solid transparent;
}
```

### 成功フィードバックアニメーション
```tsx
// components/ui/SuccessAnimation.tsx
export function SuccessAnimation({ show }: { show: boolean }) {
  return (
    <AnimatePresence>
      {show && (
        <motion.div
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.5 }}
          className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50"
        >
          <div className="bg-white rounded-lg p-8 flex flex-col items-center">
            <CheckCircleIcon className="w-16 h-16 text-green-500 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              判定完了！
            </h3>
            <p className="text-gray-600">
              次の案件に進みます...
            </p>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
```

## 📐 サイドバーナビゲーション + フレックスレイアウトシステム

### サイドバー + メインコンテンツレイアウト
```css
/* アプリケーション全体レイアウト */
.app-layout {
  @apply flex h-screen bg-gray-50;
}

/* サイドバーの基本構造 */
.sidebar {
  @apply bg-white border-r border-gray-200 flex-shrink-0 flex flex-col;
  transition: width 0.2s ease-in-out;
}

.main-content {
  @apply flex-1 flex flex-col overflow-hidden;
}

/* ページヘッダー */
.page-header {
  @apply flex-shrink-0 bg-white border-b border-gray-200 px-6 py-4;
}

/* コンテンツエリア */
.content-area {
  @apply flex-1 overflow-hidden;
}

/* 承認レビューページの2カラムレイアウト (デスクトップ) */
@media (min-width: 1024px) {
  .approval-review-content {
    @apply flex gap-6 p-6 h-full;
  }

  .left-column {
    @apply flex-[3] flex flex-col gap-4 overflow-hidden;
    min-width: 600px;
  }

  .right-column {
    @apply flex-[2] flex flex-col gap-4;
    min-width: 300px;
    max-width: 400px;
  }
}

/* タブレット・モバイルでは縦積み */
@media (max-width: 1023px) {
  .approval-review-content {
    @apply flex flex-col gap-4 p-4 h-full;
  }

  .left-column, .right-column {
    @apply flex-none;
  }

  .diff-viewer {
    @apply flex-1 overflow-hidden;
  }
}
```

### サイドバーナビゲーション詳細仕様
```css
/* サイドバー内部構造 */
.sidebar-header {
  @apply p-4 border-b border-gray-200;
}

.sidebar-navigation {
  @apply flex-1 px-2 py-4 space-y-1 overflow-y-auto;
}

.sidebar-footer {
  @apply p-4 border-t border-gray-200;
}

/* ナビゲーションアイテム */
.nav-group {
  @apply mb-6;
}

.nav-group-title {
  @apply px-2 mb-2 text-xs font-semibold text-gray-500 uppercase tracking-wide;
}

.nav-item {
  @apply flex items-center px-2 py-2 text-sm font-medium rounded-md;
  @apply hover:bg-gray-100 hover:text-gray-900;
  @apply focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500;
  @apply transition-colors duration-150;
}

.nav-item.active {
  @apply bg-blue-100 text-blue-900;
}

.nav-item-icon {
  @apply mr-3 h-5 w-5 flex-shrink-0;
}

.nav-item-badge {
  @apply ml-auto inline-flex items-center px-2 py-1 rounded-full text-xs font-medium;
  @apply bg-gray-100 text-gray-600;
}

.nav-item.active .nav-item-badge {
  @apply bg-blue-200 text-blue-800;
}

/* レスポンシブ幅制御 */
@media (max-width: 767px) {
  .sidebar {
    @apply fixed inset-y-0 left-0 z-50 w-64;
    transform: translateX(-100%);
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .sidebar-overlay {
    @apply fixed inset-0 bg-black bg-opacity-50 z-40;
  }
}

@media (min-width: 768px) and (max-width: 1023px) {
  .sidebar {
    width: 180px;
  }
}

@media (min-width: 1024px) {
  .sidebar {
    width: 220px;
  }
}
```

### 承認レビューページレイアウト詳細
```css
/* ページ全体構造 */
.approval-review-page {
  @apply flex flex-col h-full;
}

/* ヘッダー部分 */
.page-header {
  @apply flex-shrink-0 bg-white border-b border-gray-200 px-6 py-4;
}

.breadcrumb-nav {
  @apply flex items-center space-x-2 text-sm text-gray-500 mb-2;
}

.page-title {
  @apply text-2xl font-bold text-gray-900;
}

/* メインコンテンツエリア */
.approval-content {
  @apply flex-1 overflow-hidden;
}

/* 左カラム（メンテナンス提案サマリー + 差分ビューア） */
.left-column {
  .proposal-summary {
    @apply flex-shrink-0;
  }

  .diff-viewer {
    @apply flex-1 overflow-hidden;
  }
}

/* 右カラム（アクション + 履歴） */
.right-column {
  .approval-actions {
    @apply flex-shrink-0;
  }

  .approval-history {
    @apply flex-1 overflow-y-auto;
  }

  .navigation-controls {
    @apply flex-shrink-0 border-t border-gray-200 pt-4;
  }
}
```