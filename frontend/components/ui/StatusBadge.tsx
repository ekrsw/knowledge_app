import React from 'react';
import { RevisionStatus } from '@/types';

interface StatusBadgeProps {
  status: RevisionStatus;
  className?: string;
}

const statusConfig = {
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

export function StatusBadge({ status, className = '' }: StatusBadgeProps) {
  const config = statusConfig[status];
  
  if (!config) {
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-600 text-gray-200 ${className}`}>
        {status}
      </span>
    );
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.className} ${className}`}>
      {config.label}
    </span>
  );
}