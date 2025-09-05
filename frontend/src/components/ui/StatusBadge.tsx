import React from 'react';
import { RevisionStatus } from '@/types';
import { getStatusConfig, getStatusDisplayName, getStatusClassName } from '@/lib/utils/status';

export interface StatusBadgeProps {
  status: RevisionStatus;
  className?: string;
}

export function StatusBadge({ status, className = '' }: StatusBadgeProps) {
  const config = getStatusConfig(status);
  
  if (!config) {
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-600 text-gray-200 ${className}`}>
        {status}
      </span>
    );
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusClassName(status)} ${className}`}>
      {getStatusDisplayName(status)}
    </span>
  );
}