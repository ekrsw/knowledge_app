/**
 * コンテキストの統一エクスポート
 */

export { AuthProvider, useAuth, useRequireAuth, useRequireRole } from './AuthContext';
export type { AuthContextType } from './AuthContext';

// 将来的に追加されるコンテキスト用の準備
// export { ThemeProvider, useTheme } from './ThemeContext';
// export { NotificationProvider, useNotification } from './NotificationContext';