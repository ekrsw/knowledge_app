# KSAP キーボードショートカット仕様

## ⌨️ 承認作業効率化のためのショートカット設計

### 設計思想
- **左手操作中心**: 右手はマウス、左手はキーボードの自然な操作
- **覚えやすい配列**: A=Approve, R=Reject など直感的なキー配置
- **衝突回避**: ブラウザ標準・OS標準ショートカットとの重複回避
- **文脈考慮**: 入力フィールドフォーカス時は無効化

## 🎯 承認レビューページ ショートカット一覧

### 主要判定アクション
| キー | アクション | 説明 |
|------|-----------|------|
| `A` | **Approve** | 提案を承認する |
| `R` | **Reject** | 提案を却下する |
| `C` | **Request Changes** | 変更要求を送信する |
| `D` | **Defer** | 判定を保留する |

### ナビゲーション
| キー | アクション | 説明 |
|------|-----------|------|
| `→` | **Next** | 次の承認案件へ移動 |
| `←` | **Previous** | 前の承認案件へ移動 |
| `Shift + →` | **Skip & Next** | スキップして次へ |

### 入力・操作
| キー | アクション | 説明 |
|------|-----------|------|
| `T` | **Focus Comment** | コメント入力欄にフォーカス |
| `Ctrl/Cmd + Enter` | **Submit Decision** | コメント入力中に判定送信 |
| `Escape` | **Cancel/Clear Focus** | フォーカス解除・入力クリア |
| `?` | **Show Help** | ショートカットヘルプ表示 |

### 表示・UI制御
| キー | アクション | 説明 |
|------|-----------|------|
| `Space` | **Toggle Diff Expand** | 差分表示の展開/折りたたみ |
| `F` | **Toggle Full Screen** | 差分ビューアー全画面表示 |
| `Ctrl/Cmd + +` | **Zoom In** | 差分表示拡大 |
| `Ctrl/Cmd + -` | **Zoom Out** | 差分表示縮小 |

## 💻 実装仕様

### キーイベント処理
```typescript
// hooks/useKeyboardShortcuts.ts
interface KeyboardShortcutsConfig {
  onApprove: () => void;
  onReject: () => void;
  onRequestChanges: () => void;
  onDefer: () => void;
  onNext: () => void;
  onPrevious: () => void;
  onFocusComment: () => void;
  onToggleHelp: () => void;
}

export function useKeyboardShortcuts(config: KeyboardShortcutsConfig) {
  const [helpVisible, setHelpVisible] = useState(false);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // 入力フィールドフォーカス時はスキップ
      if (isInputFocused(event.target)) {
        handleInputModeShortcuts(event, config);
        return;
      }

      // モディファイヤーキーの組み合わせ
      if (event.ctrlKey || event.metaKey) {
        handleModifierShortcuts(event, config);
        return;
      }

      // 基本ショートカット
      switch (event.key.toLowerCase()) {
        case 'a':
          event.preventDefault();
          config.onApprove();
          break;
        case 'r':
          event.preventDefault();
          config.onReject();
          break;
        case 'c':
          event.preventDefault();
          config.onRequestChanges();
          break;
        case 'd':
          event.preventDefault();
          config.onDefer();
          break;
        case 'arrowright':
          event.preventDefault();
          config.onNext();
          break;
        case 'arrowleft':
          event.preventDefault();
          config.onPrevious();
          break;
        case 't':
          event.preventDefault();
          config.onFocusComment();
          break;
        case '?':
          event.preventDefault();
          setHelpVisible(!helpVisible);
          config.onToggleHelp();
          break;
        default:
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [config, helpVisible]);

  return { helpVisible, setHelpVisible };
}

// 入力フィールド判定
function isInputFocused(target: EventTarget | null): boolean {
  if (!target || !(target instanceof Element)) return false;

  const tagName = target.tagName.toLowerCase();
  const inputTypes = ['input', 'textarea', 'select'];

  return (
    inputTypes.includes(tagName) ||
    target.hasAttribute('contenteditable') ||
    target.closest('[role="textbox"]') !== null
  );
}

// 入力モード時のショートカット
function handleInputModeShortcuts(
  event: KeyboardEvent,
  config: KeyboardShortcutsConfig
) {
  // Ctrl/Cmd + Enter で判定送信
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
    event.preventDefault();
    // フォーカス中の判定ボタンに応じて適切なアクションを実行
    const lastAction = getLastFocusedAction();
    switch (lastAction) {
      case 'approve':
        config.onApprove();
        break;
      case 'reject':
        config.onReject();
        break;
      case 'request_changes':
        config.onRequestChanges();
        break;
      case 'defer':
        config.onDefer();
        break;
    }
  }

  // Escape でフォーカス解除
  if (event.key === 'Escape') {
    (event.target as HTMLElement).blur();
  }
}

// モディファイヤー付きショートカット
function handleModifierShortcuts(
  event: KeyboardEvent,
  config: KeyboardShortcutsConfig
) {
  if (event.key === 'Enter') {
    // Ctrl/Cmd + Enter で判定送信
    event.preventDefault();
    // 実装は上記と同様
  }
}
```

### ビジュアルフィードバック
```typescript
// components/approvals/KeyboardShortcutIndicator.tsx
export function KeyboardShortcutIndicator({
  shortcut,
  description,
  active = false
}: {
  shortcut: string;
  description: string;
  active?: boolean;
}) {
  return (
    <div className={clsx(
      'flex items-center justify-between p-2 rounded',
      active && 'bg-blue-100 ring-2 ring-blue-500'
    )}>
      <span className="text-sm text-gray-700">{description}</span>
      <kbd className={clsx(
        'px-2 py-1 text-xs font-mono rounded border',
        active
          ? 'bg-blue-200 border-blue-400 text-blue-900'
          : 'bg-gray-100 border-gray-300 text-gray-700'
      )}>
        {shortcut}
      </kbd>
    </div>
  );
}

// ショートカット案内パネル
export function ShortcutHelpPanel({ visible, onClose }: {
  visible: boolean;
  onClose: () => void;
}) {
  if (!visible) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">キーボードショートカット</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        <div className="space-y-1">
          <div className="font-medium text-sm text-gray-900 mb-2">判定アクション</div>
          <KeyboardShortcutIndicator shortcut="A" description="承認する" />
          <KeyboardShortcutIndicator shortcut="R" description="却下する" />
          <KeyboardShortcutIndicator shortcut="C" description="変更要求" />
          <KeyboardShortcutIndicator shortcut="D" description="保留する" />

          <div className="font-medium text-sm text-gray-900 mb-2 mt-4">ナビゲーション</div>
          <KeyboardShortcutIndicator shortcut="→" description="次の案件" />
          <KeyboardShortcutIndicator shortcut="←" description="前の案件" />

          <div className="font-medium text-sm text-gray-900 mb-2 mt-4">その他</div>
          <KeyboardShortcutIndicator shortcut="T" description="コメント入力" />
          <KeyboardShortcutIndicator shortcut="Ctrl+Enter" description="判定送信" />
          <KeyboardShortcutIndicator shortcut="?" description="このヘルプ" />
        </div>

        <div className="mt-6 text-xs text-gray-500">
          入力フィールドフォーカス中は一部のショートカットが無効になります
        </div>
      </div>
    </div>
  );
}
```

## 🎨 UI統合

### アクションボタンでの表示
```typescript
// components/approvals/ApprovalActionButton.tsx
export function ApprovalActionButton({
  action,
  label,
  shortcut,
  variant,
  onClick,
  disabled
}: ApprovalActionButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={clsx(
        'w-full py-3 px-4 rounded-lg font-medium transition-all duration-200',
        'focus:ring-4 focus:ring-offset-2 focus:outline-none',
        'relative group',
        getVariantStyles(variant),
        disabled && 'opacity-50 cursor-not-allowed'
      )}
      aria-label={`${label}する (ショートカット: ${shortcut})`}
    >
      <div className="flex items-center justify-between">
        <span>{label}</span>
        <div className="flex items-center gap-2">
          {/* ショートカットバッジ */}
          <kbd className="px-2 py-1 text-xs font-mono bg-white bg-opacity-20 rounded border border-white border-opacity-30">
            {shortcut}
          </kbd>
          {/* アイコン */}
          {getActionIcon(action)}
        </div>
      </div>

      {/* ホバー時のツールチップ */}
      <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 -translate-y-full opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none">
        <div className="bg-gray-900 text-white text-xs py-1 px-2 rounded whitespace-nowrap">
          {shortcut} キーでも実行可能
        </div>
      </div>
    </button>
  );
}

function getActionIcon(action: string) {
  switch (action) {
    case 'approve':
      return <CheckIcon className="w-5 h-5" />;
    case 'reject':
      return <XMarkIcon className="w-5 h-5" />;
    case 'request_changes':
      return <ExclamationTriangleIcon className="w-5 h-5" />;
    case 'defer':
      return <ClockIcon className="w-5 h-5" />;
    default:
      return null;
  }
}
```

## 🚨 注意事項とベストプラクティス

### 1. アクセシビリティ対応
```typescript
// WAI-ARIA属性の適切な設定
<div
  role="application"
  aria-label="承認レビューアプリケーション"
  aria-describedby="shortcuts-help"
>
  <div id="shortcuts-help" className="sr-only">
    A キーで承認、R キーで却下、矢印キーでナビゲーション
  </div>

  {/* ショートカット有効時の状態通知 */}
  <div aria-live="polite" aria-atomic="true" className="sr-only">
    {lastAction && `${lastAction}を実行しました`}
  </div>
</div>
```

### 2. 国際化対応
```typescript
// i18n対応のショートカットキー
const getShortcutKey = (action: string, locale: string) => {
  const shortcuts = {
    ja: { approve: 'A', reject: 'R', changes: 'C', defer: 'D' },
    en: { approve: 'A', reject: 'R', changes: 'C', defer: 'D' },
    // 他の言語でもローマ字ベースで統一
  };

  return shortcuts[locale]?.[action] || shortcuts.en[action];
};
```

### 3. パフォーマンス最適化
```typescript
// デバウンス処理で連続入力を防ぐ
export function useKeyboardShortcuts(config: KeyboardShortcutsConfig) {
  const debouncedConfig = useMemo(
    () => Object.fromEntries(
      Object.entries(config).map(([key, fn]) => [
        key,
        debounce(fn, 150) // 150ms のデバウンス
      ])
    ),
    [config]
  );

  // 既存の実装...
}

// メモ化でレンダリング最適化
const ShortcutHelpPanel = memo(({ visible, onClose }) => {
  // コンポーネント実装
});
```

### 4. テスト方針
```typescript
// __tests__/shortcuts.test.tsx
describe('Keyboard Shortcuts', () => {
  it('should trigger approve action on A key press', () => {
    const mockOnApprove = jest.fn();

    render(<ApprovalReviewPage />);

    fireEvent.keyDown(document, { key: 'a', code: 'KeyA' });

    expect(mockOnApprove).toHaveBeenCalledTimes(1);
  });

  it('should not trigger shortcuts when input is focused', () => {
    const mockOnApprove = jest.fn();

    render(<ApprovalReviewPage />);

    const commentInput = screen.getByRole('textbox');
    commentInput.focus();

    fireEvent.keyDown(document, { key: 'a', code: 'KeyA' });

    expect(mockOnApprove).not.toHaveBeenCalled();
  });

  it('should show help panel on ? key press', () => {
    render(<ApprovalReviewPage />);

    fireEvent.keyDown(document, { key: '?', code: 'Slash', shiftKey: true });

    expect(screen.getByText('キーボードショートカット')).toBeInTheDocument();
  });
});
```

## 📊 効果測定指標

### ショートカット使用率
```typescript
// analytics/shortcut-metrics.ts
export class ShortcutMetrics {
  private static metrics = {
    totalActions: 0,
    keyboardActions: 0,
    mouseActions: 0,
    shortcutUsage: {} as Record<string, number>
  };

  static trackShortcutUse(shortcut: string) {
    this.metrics.keyboardActions++;
    this.metrics.totalActions++;
    this.metrics.shortcutUsage[shortcut] = (this.metrics.shortcutUsage[shortcut] || 0) + 1;
  }

  static trackMouseAction() {
    this.metrics.mouseActions++;
    this.metrics.totalActions++;
  }

  static getUsageReport() {
    const keyboardRatio = this.metrics.keyboardActions / this.metrics.totalActions;
    return {
      keyboardRatio: keyboardRatio * 100, // パーセンテージ
      mostUsedShortcut: Object.entries(this.metrics.shortcutUsage)
        .sort(([,a], [,b]) => b - a)[0],
      totalActions: this.metrics.totalActions
    };
  }
}
```

この仕様により、承認者は年間10,000件の処理を効率的に行うことができ、キーボードショートカットによって判定速度の大幅な向上が期待できます。