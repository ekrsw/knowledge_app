/**
 * ステータス表示関連のユーティリティ関数
 */

import { RevisionStatus } from '@/types';

/**
 * ステータス設定の型定義
 */
export interface StatusConfig {
  label: string;
  className: string;
}

/**
 * ステータス設定マップ
 */
export const statusConfig: Record<RevisionStatus, StatusConfig> = {
  draft: {
    label: '下書き',
    className: 'bg-gray-600 text-gray-200'
  },
  submitted: {
    label: '提出済み',
    className: 'bg-blue-600 text-blue-100'
  },
  approved: {
    label: '承認済み',
    className: 'bg-green-600 text-green-100'
  },
  rejected: {
    label: '却下',
    className: 'bg-red-600 text-red-100'
  },
  deleted: {
    label: '削除済み',
    className: 'bg-gray-500 text-gray-200'
  }
};

/**
 * ステータスの日本語表示名を取得
 */
export function getStatusDisplayName(status: RevisionStatus): string {
  return statusConfig[status]?.label || status;
}

/**
 * ステータスのCSSクラス名を取得
 */
export function getStatusClassName(status: RevisionStatus): string {
  return statusConfig[status]?.className || 'bg-gray-600 text-gray-200';
}

/**
 * ステータス設定を取得
 */
export function getStatusConfig(status: RevisionStatus): StatusConfig | null {
  return statusConfig[status] || null;
}

/**
 * フィルター用のステータスオプションを取得
 */
export function getStatusOptions() {
  return [
    { value: '', label: '全てのステータス' },
    { value: 'draft', label: getStatusDisplayName('draft') },
    { value: 'submitted', label: getStatusDisplayName('submitted') },
    { value: 'approved', label: getStatusDisplayName('approved') },
    { value: 'rejected', label: getStatusDisplayName('rejected') },
    { value: 'deleted', label: getStatusDisplayName('deleted') }
  ];
}

/**
 * 全ステータス設定の一覧を取得
 */
export function getAllStatusConfigs(): Record<RevisionStatus, StatusConfig> {
  return statusConfig;
}