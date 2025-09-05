'use client';

import React, { useState, useCallback, useEffect } from 'react';
import { DataTable, DataTableProps, SortConfig, FilterConfig } from './DataTable';
import { Pagination } from './Pagination';

export interface PaginatedDataTableProps<T> extends Omit<DataTableProps<T>, 'data'> {
  data: T[];
  totalItems: number;
  currentPage: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  onPageSizeChange?: (pageSize: number) => void;
  pageSizeOptions?: number[];
  showPageSizeSelector?: boolean;
}

export function PaginatedDataTable<T extends Record<string, unknown>>({
  data,
  totalItems,
  currentPage,
  pageSize,
  onPageChange,
  onPageSizeChange,
  pageSizeOptions = [10, 20, 50, 100],
  showPageSizeSelector = true,
  columns,
  ...tableProps
}: PaginatedDataTableProps<T>) {
  const totalPages = Math.ceil(totalItems / pageSize);

  const renderPageSizeSelector = () => {
    if (!showPageSizeSelector || !onPageSizeChange) return null;

    return (
      <div className="flex items-center space-x-2">
        <span className="text-sm text-gray-400">表示件数:</span>
        <select
          value={pageSize}
          onChange={(e) => onPageSizeChange(Number(e.target.value))}
          className="bg-gray-700 border border-gray-600 text-gray-300 text-sm rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {pageSizeOptions.map(size => (
            <option key={size} value={size}>
              {size}件
            </option>
          ))}
        </select>
      </div>
    );
  };

  return (
    <div className="space-y-4">
      <DataTable
        columns={columns}
        data={data}
        {...tableProps}
      />
      
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        {renderPageSizeSelector()}
        
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          totalItems={totalItems}
          itemsPerPage={pageSize}
          onPageChange={onPageChange}
        />
      </div>
    </div>
  );
}

// useLocalPagination フック - ローカルデータの場合に使用
export function useLocalPagination<T>(
  data: T[],
  initialPageSize = 10,
  initialPage = 1
) {
  const [currentPage, setCurrentPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [sortConfig, setSortConfig] = useState<SortConfig | null>(null);
  const [filters, setFilters] = useState<FilterConfig[]>([]);

  // データの処理
  const processedData = React.useMemo(() => {
    let result = [...data];

    // フィルタリング
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
    if (sortConfig) {
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
  }, [data, sortConfig, filters]);

  // ページネーション
  const paginatedData = React.useMemo(() => {
    const startIndex = (currentPage - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    return processedData.slice(startIndex, endIndex);
  }, [processedData, currentPage, pageSize]);

  const totalItems = processedData.length;
  const totalPages = Math.ceil(totalItems / pageSize);

  // ハンドラー
  const handlePageChange = useCallback((page: number) => {
    setCurrentPage(page);
  }, []);

  const handlePageSizeChange = useCallback((newPageSize: number) => {
    setPageSize(newPageSize);
    setCurrentPage(1); // ページサイズ変更時は1ページ目に戻る
  }, []);

  const handleSort = useCallback((newSortConfig: SortConfig | null) => {
    setSortConfig(newSortConfig);
    setCurrentPage(1); // ソート時は1ページ目に戻る
  }, []);

  const handleFilter = useCallback((newFilters: FilterConfig[]) => {
    setFilters(newFilters);
    setCurrentPage(1); // フィルター時は1ページ目に戻る
  }, []);

  // フィルター/ソートが変わった時にページ数を超えている場合は1ページ目に戻る
  useEffect(() => {
    if (currentPage > totalPages && totalPages > 0) {
      setCurrentPage(1);
    }
  }, [currentPage, totalPages]);

  return {
    // データ
    data: paginatedData,
    totalItems,
    totalPages,
    currentPage,
    pageSize,

    // ハンドラー
    onPageChange: handlePageChange,
    onPageSizeChange: handlePageSizeChange,
    onSort: handleSort,
    onFilter: handleFilter,

    // 設定
    sortConfig,
    filters,

    // リセット用
    reset: () => {
      setCurrentPage(1);
      setSortConfig(null);
      setFilters([]);
    }
  };
}