'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { MainLayout } from '@/components/layout';
import { DataTable, Pagination, StatusBadge, Button, Select } from '../../components/ui';
import { useToast } from '../../components/ui';
import { getMyRevisions, RevisionsListParams } from '@/lib/api/revisions';
import { Revision, RevisionStatus } from '@/types';
import { PaginatedResponse } from '@/types/api';

const DEFAULT_PAGE_SIZE = 10;

const statusOptions = [
  { value: '', label: '全てのステータス' },
  { value: 'draft', label: '下書き' },
  { value: 'submitted', label: '提出済み' },
  { value: 'approved', label: '承認済み' },
  { value: 'rejected', label: '却下' },
  { value: 'deleted', label: '削除済み' }
];

export default function MyRevisionsPage() {
  const router = useRouter();
  const { user } = useAuth();
  const { toast } = useToast();
  
  const [revisions, setRevisions] = useState<Revision[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [totalItems, setTotalItems] = useState(0);
  const [statusFilter, setStatusFilter] = useState<RevisionStatus | ''>('');

  const fetchMyRevisions = useCallback(async () => {
    try {
      setLoading(true);
      const response: PaginatedResponse<Revision> = await getMyRevisions({
        skip: (currentPage - 1) * DEFAULT_PAGE_SIZE,
        limit: DEFAULT_PAGE_SIZE,
        status: statusFilter || undefined,
      });
      
      // APIレスポンスがPaginatedResponse形式であることを確認
      const items = Array.isArray(response.items) ? response.items : [];
      setRevisions(items);
      setTotalItems(response.total || 0);
      setTotalPages(Math.ceil((response.total || 0) / DEFAULT_PAGE_SIZE));
    } catch (error) {
      console.error('自分の修正案の取得に失敗しました:', error);
      toast.error('自分の修正案の取得に失敗しました');
      setRevisions([]);
      setTotalItems(0);
      setTotalPages(0);
    } finally {
      setLoading(false);
    }
  }, [currentPage, statusFilter, toast]);

  useEffect(() => {
    fetchMyRevisions();
  }, [currentPage, statusFilter]); // fetchMyRevisionsを依存配列から削除し、直接currentPageとstatusFilterを監視

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const handleStatusFilterChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const status = event.target.value as RevisionStatus | '';
    setStatusFilter(status);
    setCurrentPage(1); // フィルター変更時は1ページ目に戻る
  };

  const handleRowClick = (revision: Revision) => {
    router.push(`/revisions/${revision.revision_id}`);
  };

  const handleCreateRevision = () => {
    router.push('/revisions/new');
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleString('ja-JP', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateString;
    }
  };

  const columns = [
    {
      key: 'article_number' as keyof Revision,
      title: '記事番号',
      width: '150px'
    },
    {
      key: 'after_title' as keyof Revision,
      title: 'タイトル',
      render: (value: unknown, record: Revision) => (
        <div className="max-w-xs truncate" title={(value as string) || record.article_number || record.target_article_id}>
          {(value as string) || record.article_number || record.target_article_id}
        </div>
      )
    },
    {
      key: 'status' as keyof Revision,
      title: 'ステータス',
      width: '120px',
      render: (status: unknown) => <StatusBadge status={status as RevisionStatus} />
    },
    {
      key: 'approver_name' as keyof Revision,
      title: '承認者',
      width: '120px',
      render: (value: unknown) => (
        <span className="text-gray-300">
          {(value as string) || '未指定'}
        </span>
      )
    },
    {
      key: 'created_at' as keyof Revision,
      title: '作成日時',
      width: '150px',
      render: (value: unknown) => formatDate(value as string)
    },
    {
      key: 'updated_at' as keyof Revision,
      title: '更新日時',
      width: '150px',
      render: (value: unknown) => formatDate(value as string)
    }
  ];

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* ページヘッダー */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-semibold text-white">自分の修正案</h1>
            <p className="text-gray-400 mt-1">
              {user?.full_name || user?.username}さんが作成した修正案一覧
            </p>
          </div>
          <Button onClick={handleCreateRevision} className="bg-blue-600 hover:bg-blue-700">
            新しい修正案を作成
          </Button>
        </div>

        {/* フィルター */}
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-gray-300">
                ステータス:
              </label>
              <Select
                value={statusFilter}
                onChange={handleStatusFilterChange}
                options={statusOptions}
                className="w-48"
              />
            </div>
            <div className="text-sm text-gray-400">
              {totalItems}件の修正案
            </div>
          </div>
        </div>

        {/* 修正案一覧テーブル */}
        <DataTable<Revision>
          columns={columns}
          data={revisions}
          loading={loading}
          onRow={(record) => ({
            onClick: () => handleRowClick(record),
            className: 'cursor-pointer hover:bg-gray-700'
          })}
          emptyText="作成された修正案がありません"
        />

        {/* ページネーション */}
        {totalPages > 1 && (
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            totalItems={totalItems}
            itemsPerPage={DEFAULT_PAGE_SIZE}
            onPageChange={handlePageChange}
            className="mt-6"
          />
        )}
      </div>
    </MainLayout>
  );
}