/**
 * 優先度・影響度表示関連のユーティリティ関数
 */

/**
 * 優先度・影響度レベルの型定義
 */
export type PriorityLevel = 'urgent' | 'high' | 'medium' | 'low';

/**
 * 優先度・影響度設定の型定義
 */
export interface PriorityConfig {
  label: string;
  className: string;
}

/**
 * 優先度設定マップ
 */
export const priorityConfig: Record<PriorityLevel, PriorityConfig> = {
  urgent: {
    label: '緊急',
    className: 'bg-red-100 text-red-800'
  },
  high: {
    label: '高',
    className: 'bg-orange-100 text-orange-800'
  },
  medium: {
    label: '中',
    className: 'bg-yellow-100 text-yellow-800'
  },
  low: {
    label: '低',
    className: 'bg-green-100 text-green-800'
  }
};

/**
 * 影響度設定マップ（優先度と同じレベル体系）
 */
export const impactConfig: Record<PriorityLevel, PriorityConfig> = {
  urgent: {
    label: '緊急',
    className: 'bg-red-100 text-red-800'
  },
  high: {
    label: '高',
    className: 'bg-orange-100 text-orange-800'
  },
  medium: {
    label: '中',
    className: 'bg-yellow-100 text-yellow-800'
  },
  low: {
    label: '低',
    className: 'bg-green-100 text-green-800'
  }
};

/**
 * 優先度の日本語表示名を取得
 */
export function getPriorityDisplayName(priority: string): string {
  return priorityConfig[priority as PriorityLevel]?.label || priority;
}

/**
 * 影響度の日本語表示名を取得
 */
export function getImpactDisplayName(impact: string): string {
  return impactConfig[impact as PriorityLevel]?.label || impact;
}

/**
 * 優先度のCSSクラス名を取得
 */
export function getPriorityClassName(priority: string): string {
  return priorityConfig[priority as PriorityLevel]?.className || 'bg-gray-100 text-gray-800';
}

/**
 * 影響度のCSSクラス名を取得
 */
export function getImpactClassName(impact: string): string {
  return impactConfig[impact as PriorityLevel]?.className || 'bg-gray-100 text-gray-800';
}

/**
 * 優先度設定を取得
 */
export function getPriorityConfig(priority: string): PriorityConfig | null {
  return priorityConfig[priority as PriorityLevel] || null;
}

/**
 * 影響度設定を取得
 */
export function getImpactConfig(impact: string): PriorityConfig | null {
  return impactConfig[impact as PriorityLevel] || null;
}

/**
 * フィルター用の優先度オプションを取得
 */
export function getPriorityOptions() {
  return [
    { value: '', label: '全ての優先度' },
    { value: 'urgent', label: getPriorityDisplayName('urgent') },
    { value: 'high', label: getPriorityDisplayName('high') },
    { value: 'medium', label: getPriorityDisplayName('medium') },
    { value: 'low', label: getPriorityDisplayName('low') }
  ];
}

/**
 * フィルター用の影響度オプションを取得
 */
export function getImpactOptions() {
  return [
    { value: '', label: '全ての影響度' },
    { value: 'urgent', label: getImpactDisplayName('urgent') },
    { value: 'high', label: getImpactDisplayName('high') },
    { value: 'medium', label: getImpactDisplayName('medium') },
    { value: 'low', label: getImpactDisplayName('low') }
  ];
}

/**
 * 全優先度設定の一覧を取得
 */
export function getAllPriorityConfigs(): Record<PriorityLevel, PriorityConfig> {
  return priorityConfig;
}

/**
 * 全影響度設定の一覧を取得
 */
export function getAllImpactConfigs(): Record<PriorityLevel, PriorityConfig> {
  return impactConfig;
}