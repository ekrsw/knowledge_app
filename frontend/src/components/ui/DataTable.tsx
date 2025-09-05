'use client';

import React, { useState, useMemo } from 'react';
import { Button } from './Button';
import { Input } from './Input';
import { Select } from './Select';

export type SortDirection = 'asc' | 'desc';

export interface SortConfig {
  key: string;
  direction: SortDirection;
}

export interface FilterConfig {
  key: string;
  value: string;
  type: 'text' | 'select' | 'date';
}

export interface Column<T> {
  key: keyof T | string;
  title: string;
  render?: (value: unknown, record: T, index: number) => React.ReactNode;
  width?: string | number;
  sortable?: boolean;
  filterable?: boolean;
  filterType?: 'text' | 'select' | 'date';
  filterOptions?: Array<{ label: string; value: string }>;
}

export interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;
  onRow?: (record: T, index: number) => {
    onClick?: () => void;
    className?: string;
  };
  className?: string;
  emptyText?: string;
  showSearch?: boolean;
  searchPlaceholder?: string;
  sortable?: boolean;
  filterable?: boolean;
  onSort?: (sortConfig: SortConfig | null) => void;
  onFilter?: (filters: FilterConfig[]) => void;
  defaultSortConfig?: SortConfig;
  defaultFilters?: FilterConfig[];
}

export function DataTable<T extends Record<string, unknown>>({
  columns,
  data,
  loading = false,
  onRow,
  className = '',
  emptyText = 'データがありません',
  showSearch = false,
  searchPlaceholder = '検索...',
  sortable = true,
  filterable = false,
  onSort,
  onFilter,
  defaultSortConfig,
  defaultFilters = []
}: DataTableProps<T>) {
  const [sortConfig, setSortConfig] = useState<SortConfig | null>(defaultSortConfig || null);
  const [filters, setFilters] = useState<FilterConfig[]>(defaultFilters);
  const [searchTerm, setSearchTerm] = useState('');

  // ソート関数
  const handleSort = (key: string) => {
    if (!sortable) return;
    
    const newSortConfig: SortConfig = 
      sortConfig?.key === key && sortConfig.direction === 'asc'
        ? { key, direction: 'desc' }
        : { key, direction: 'asc' };
    
    setSortConfig(newSortConfig);
    onSort?.(newSortConfig);
  };

  // フィルター関数
  const handleFilter = (key: string, value: string, type: 'text' | 'select' | 'date') => {
    const newFilters = filters.filter(f => f.key !== key);
    if (value) {
      newFilters.push({ key, value, type });
    }
    setFilters(newFilters);
    onFilter?.(newFilters);
  };

  // データの処理（ソート・フィルター・検索）
  const processedData = useMemo(() => {
    let result = [...data];

    // 検索フィルタリング
    if (searchTerm) {
      result = result.filter(record =>
        columns.some(column => {
          const keyStr = String(column.key);
          const value = keyStr.includes('.') 
            ? keyStr.split('.').reduce((obj: unknown, key: string) => 
                (obj as Record<string, unknown>)?.[key], record)
            : record[column.key as keyof T];
          return String(value || '').toLowerCase().includes(searchTerm.toLowerCase());
        })
      );
    }

    // カラムフィルタリング
    filters.forEach(filter => {
      result = result.filter(record => {
        const keyStr = String(filter.key);
        const value = keyStr.includes('.') 
          ? keyStr.split('.').reduce((obj: unknown, key: string) => 
              (obj as Record<string, unknown>)?.[key], record)
          : record[filter.key as keyof T];
        
        if (filter.type === 'text') {
          return String(value || '').toLowerCase().includes(filter.value.toLowerCase());
        } else if (filter.type === 'select') {
          return String(value) === filter.value;
        } else if (filter.type === 'date') {
          return String(value).includes(filter.value);
        }
        return true;
      });
    });

    // ソート
    if (sortConfig && !onSort) { // onSortが提供されていない場合のみローカルソートを実行
      result.sort((a, b) => {
        const keyStr = String(sortConfig.key);
        const aVal = keyStr.includes('.') 
          ? keyStr.split('.').reduce((obj: unknown, key: string) => 
              (obj as Record<string, unknown>)?.[key], a)
          : a[sortConfig.key as keyof T];
        const bVal = keyStr.includes('.') 
          ? keyStr.split('.').reduce((obj: unknown, key: string) => 
              (obj as Record<string, unknown>)?.[key], b)
          : b[sortConfig.key as keyof T];

        if (aVal == null && bVal == null) return 0;
        if (aVal == null) return 1;
        if (bVal == null) return -1;

        const comparison = String(aVal).localeCompare(String(bVal), 'ja', { numeric: true });
        return sortConfig.direction === 'asc' ? comparison : -comparison;
      });
    }

    return result;
  }, [data, sortConfig, filters, searchTerm, columns, onSort]);

  if (loading) {
    return (
      <div className={`bg-gray-800 rounded-lg ${className}`}>
        <div className="p-8 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <div className="mt-2 text-gray-400">読み込み中...</div>
        </div>
      </div>
    );
  }

  // 検索とフィルターのUIを描画する関数
  const renderSearchAndFilters = () => {
    const hasSearchOrFilters = showSearch || (filterable && columns.some(col => col.filterable));
    
    if (!hasSearchOrFilters) return null;

    return (
      <div className="p-4 border-b border-gray-600 space-y-4">
        {showSearch && (
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <Input
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder={searchPlaceholder}
                className="w-full"
              />
            </div>
            {searchTerm && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSearchTerm('')}
              >
                クリア
              </Button>
            )}
          </div>
        )}

        {filterable && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {columns
              .filter(column => column.filterable)
              .map(column => {
                const keyStr = String(column.key);
                const currentFilter = filters.find(f => f.key === keyStr);
                
                if (column.filterType === 'select' && column.filterOptions) {
                  return (
                    <div key={keyStr}>
                      <label className="block text-sm font-medium text-gray-400 mb-1">
                        {column.title}
                      </label>
                      <Select
                        value={currentFilter?.value || ''}
                        onChange={(e) => handleFilter(keyStr, e.target.value, 'select')}
                        options={[
                          { label: 'すべて', value: '' },
                          ...column.filterOptions!
                        ]}
                        className="w-full"
                      />
                    </div>
                  );
                } else {
                  return (
                    <div key={keyStr}>
                      <label className="block text-sm font-medium text-gray-400 mb-1">
                        {column.title}
                      </label>
                      <Input
                        value={currentFilter?.value || ''}
                        onChange={(e) => handleFilter(keyStr, e.target.value, column.filterType || 'text')}
                        placeholder={`${column.title}で絞り込み...`}
                        type={column.filterType === 'date' ? 'date' : 'text'}
                        className="w-full"
                      />
                    </div>
                  );
                }
              })}
            
            {filters.length > 0 && (
              <div className="flex items-end">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setFilters([]);
                    onFilter?.([]);
                  }}
                  className="w-full"
                >
                  フィルターをクリア
                </Button>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  if (processedData.length === 0 && !loading) {
    return (
      <div className={`bg-gray-800 rounded-lg ${className}`}>
        {renderSearchAndFilters()}
        <div className="p-8 text-center text-gray-400">
          {searchTerm || filters.length > 0 ? '条件に一致するデータがありません' : emptyText}
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-gray-800 rounded-lg overflow-hidden ${className}`}>
      {renderSearchAndFilters()}
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-700 border-b border-gray-600">
              {columns.map((column, index) => (
                <th
                  key={String(column.key) || index}
                  className={`px-6 py-4 text-left text-sm font-medium text-gray-300 uppercase tracking-wider ${
                    column.sortable && sortable ? 'cursor-pointer hover:bg-gray-600 transition-colors' : ''
                  }`}
                  style={{ width: column.width }}
                  onClick={() => column.sortable && handleSort(String(column.key))}
                >
                  <div className="flex items-center space-x-2">
                    <span>{column.title}</span>
                    {column.sortable && sortable && (
                      <span className="text-xs">
                        {sortConfig?.key === String(column.key) ? (
                          sortConfig.direction === 'asc' ? '↑' : '↓'
                        ) : '↕'}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-600">
            {processedData.map((record, index) => {
              const rowProps = onRow?.(record, index);
              return (
                <tr
                  key={index}
                  className={`hover:bg-gray-700 transition-colors ${rowProps?.className || ''} ${
                    rowProps?.onClick ? 'cursor-pointer' : ''
                  }`}
                  onClick={rowProps?.onClick}
                >
                  {columns.map((column, colIndex) => {
                    const keyStr = String(column.key);
                    const value = keyStr.includes('.') 
                      ? keyStr.split('.').reduce((obj: unknown, key: string) => 
                          (obj as Record<string, unknown>)?.[key], record)
                      : record[column.key as keyof T];
                    
                    return (
                      <td
                        key={String(column.key) || colIndex}
                        className="px-6 py-4 whitespace-nowrap text-sm text-gray-300"
                      >
                        {column.render ? column.render(value, record, index) : String(value || '')}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}