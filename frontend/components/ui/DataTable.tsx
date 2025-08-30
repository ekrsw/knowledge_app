import React from 'react';

interface Column<T> {
  key: keyof T | string;
  title: string;
  render?: (value: unknown, record: T, index: number) => React.ReactNode;
  width?: string | number;
  sortable?: boolean;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;
  onRow?: (record: T, index: number) => {
    onClick?: () => void;
    className?: string;
  };
  className?: string;
  emptyText?: string;
}

export function DataTable<T extends Record<string, unknown>>({
  columns,
  data,
  loading = false,
  onRow,
  className = '',
  emptyText = 'データがありません'
}: DataTableProps<T>) {
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

  if (data.length === 0) {
    return (
      <div className={`bg-gray-800 rounded-lg ${className}`}>
        <div className="p-8 text-center text-gray-400">
          {emptyText}
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-gray-800 rounded-lg overflow-hidden ${className}`}>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-700 border-b border-gray-600">
              {columns.map((column, index) => (
                <th
                  key={String(column.key) || index}
                  className="px-6 py-4 text-left text-sm font-medium text-gray-300 uppercase tracking-wider"
                  style={{ width: column.width }}
                >
                  {column.title}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-600">
            {data.map((record, index) => {
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