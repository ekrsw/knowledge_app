import React from 'react';
import { Button } from './Button';

export interface PaginationProps {
  currentPage: number;
  totalPages: number;
  totalItems: number;
  itemsPerPage: number;
  onPageChange: (page: number) => void;
  className?: string;
}

export function Pagination({
  currentPage,
  totalPages,
  totalItems,
  itemsPerPage,
  onPageChange,
  className = ''
}: PaginationProps) {
  const startItem = (currentPage - 1) * itemsPerPage + 1;
  const endItem = Math.min(currentPage * itemsPerPage, totalItems);

  const renderPageNumbers = () => {
    const pages = [];
    const maxVisiblePages = 5;
    
    if (totalPages <= maxVisiblePages) {
      // すべてのページを表示
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // ページ数が多い場合の省略表示
      const startPage = Math.max(1, currentPage - 2);
      const endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
      
      if (startPage > 1) {
        pages.push(1);
        if (startPage > 2) pages.push('...');
      }
      
      for (let i = startPage; i <= endPage; i++) {
        pages.push(i);
      }
      
      if (endPage < totalPages) {
        if (endPage < totalPages - 1) pages.push('...');
        pages.push(totalPages);
      }
    }

    return pages.map((page, index) => {
      if (page === '...') {
        return (
          <span key={index} className="px-3 py-2 text-gray-400">
            ...
          </span>
        );
      }

      return (
        <Button
          key={page}
          variant={page === currentPage ? 'primary' : 'ghost'}
          size="sm"
          onClick={() => onPageChange(page as number)}
          className="min-w-[40px]"
        >
          {page}
        </Button>
      );
    });
  };

  if (totalPages <= 1) return null;

  return (
    <div className={`flex items-center justify-between ${className}`}>
      <div className="text-sm text-gray-400">
        {totalItems > 0 ? (
          <>
            {startItem}-{endItem}件 / 全{totalItems}件
          </>
        ) : (
          '0件'
        )}
      </div>
      
      <div className="flex items-center space-x-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage <= 1}
        >
          前へ
        </Button>
        
        {renderPageNumbers()}
        
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage >= totalPages}
        >
          次へ
        </Button>
      </div>
    </div>
  );
}