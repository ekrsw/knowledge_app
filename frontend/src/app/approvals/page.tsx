'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useRequireAuth } from '@/hooks/useRequireAuth';
import { MainLayout } from '@/components/layout';
import { DataTable, Button, Select, StatusBadge, Modal } from '@/components/ui';
import { useToast } from '@/components/ui';
import {
  getApprovalQueue,
  approveRevision,
  rejectRevision,
  type ApprovalQueueItem,
} from '@/lib/api/approvals';

const DEFAULT_PAGE_SIZE = 10;

const priorityOptions = [
  { value: '', label: '全ての優先度' },
  { value: 'critical', label: '重大' },
  { value: 'high', label: '高' },
  { value: 'medium', label: '中' },
  { value: 'low', label: '低' }
];

export default function ApprovalsPage() {
  const router = useRouter();
  const { toast } = useToast();
  const { user, isLoading: authLoading, hasPermission } = useRequireAuth({ 
    requiredRole: ['approver', 'admin'] 
  });
  
  // 全てのstate hooksを最初に宣言
  const [queue, setQueue] = useState<ApprovalQueueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [priority, setPriority] = useState<string>('');
  const [selectedRevision, setSelectedRevision] = useState<ApprovalQueueItem | null>(null);
  const [actionType, setActionType] = useState<'approve' | 'reject' | null>(null);
  const [processing, setProcessing] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // useCallback hookも宣言
  const fetchQueue = useCallback(async () => {
    try {
      setLoading(true);
      
      // キューデータを取得
      const queueData = await getApprovalQueue(priority || undefined);
      setQueue(queueData);
      
    } catch (error) {
      console.error('Failed to fetch approval queue:', error);
      setQueue([]);
      toast.error('承認キューの取得に失敗しました');
    } finally {
      setLoading(false);
    }
  }, [priority]); // toastを依存配列から除去

  useEffect(() => {
    fetchQueue();
  }, [fetchQueue]);

  const handleApprove = async (item: ApprovalQueueItem) => {
    setSelectedRevision(item);
    setActionType('approve');
    setIsModalOpen(true);
  };

  const handleReject = async (item: ApprovalQueueItem) => {
    setSelectedRevision(item);
    setActionType('reject');
    setIsModalOpen(true);
  };

  const handleRowClick = (item: ApprovalQueueItem) => {
    router.push(`/revisions/${item.revision_id}`);
  };

  const handlePriorityFilterChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const newPriority = event.target.value;
    setPriority(newPriority);
  };

  const confirmAction = async () => {
    if (!selectedRevision || !actionType) return;

    try {
      setProcessing(true);
      if (actionType === 'approve') {
        await approveRevision(selectedRevision.revision_id, { comment: 'Approved via approval queue' });
        toast.success('修正案を承認しました');
      } else {
        await rejectRevision(selectedRevision.revision_id, { comment: 'Rejected via approval queue' });
        toast.success('修正案を却下しました');
      }
      // データを再取得
      fetchQueue();
    } catch (error) {
      console.error(`Failed to ${actionType} revision:`, error);
      toast.error(`修正案の${actionType === 'approve' ? '承認' : '却下'}に失敗しました`);
    } finally {
      setProcessing(false);
      setSelectedRevision(null);
      setActionType(null);
      setIsModalOpen(false);
    }
  };

  const closeModal = () => {
    if (!processing) {
      setSelectedRevision(null);
      setActionType(null);
      setIsModalOpen(false);
    }
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

  const getPriorityBadgeColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-100 text-red-800';
      case 'high':
        return 'bg-orange-100 text-orange-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // 認証チェック（全てのHooks宣言後に配置）
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          <p className="mt-4 text-gray-400">読み込み中...</p>
        </div>
      </div>
    );
  }

  if (!hasPermission) {
    return null; // リダイレクト処理中
  }

  const columns = [
    {
      key: 'article_number' as keyof ApprovalQueueItem,
      title: '記事番号',
      width: '120px',
      render: (value: unknown) => (
        <span className="font-mono text-sm">
          {(value as string) || '-'}
        </span>
      )
    },
    {
      key: 'proposer_name' as keyof ApprovalQueueItem,
      title: '提案者',
      width: '120px'
    },
    {
      key: 'reason' as keyof ApprovalQueueItem,
      title: '修正理由',
      render: (value: unknown) => (
        <div className="max-w-xs truncate" title={(value as string)}>
          {(value as string)}
        </div>
      )
    },
    {
      key: 'priority' as keyof ApprovalQueueItem,
      title: '優先度',
      width: '100px',
      render: (value: unknown) => (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPriorityBadgeColor(value as string)}`}>
          {value as string}
        </span>
      )
    },
    {
      key: 'impact_level' as keyof ApprovalQueueItem,
      title: '影響度',
      width: '100px',
      render: (value: unknown) => (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPriorityBadgeColor(value as string)}`}>
          {value as string}
        </span>
      )
    },
    {
      key: 'days_pending' as keyof ApprovalQueueItem,
      title: '経過日数',
      width: '100px',
      render: (value: unknown, record: ApprovalQueueItem) => (
        <div className="flex items-center space-x-1">
          {record.is_overdue && (
            <span className="text-orange-500 text-xs">⚠</span>
          )}
          <span className={record.is_overdue ? 'text-orange-500 font-medium' : ''}>
            {value as number}日
          </span>
        </div>
      )
    },
    {
      key: 'submitted_at' as keyof ApprovalQueueItem,
      title: '提出日時',
      width: '150px',
      render: (value: unknown) => formatDate(value as string)
    },
    {
      key: 'actions' as keyof ApprovalQueueItem,
      title: '操作',
      width: '200px',
      render: (value: unknown, record: ApprovalQueueItem) => (
        <div className="flex space-x-2">
          <Button
            size="sm"
            variant="outline"
            onClick={(e) => {
              e.stopPropagation();
              router.push(`/revisions/${record.revision_id}`);
            }}
          >
            詳細
          </Button>
          <Button
            size="sm"
            className="bg-green-600 hover:bg-green-700"
            onClick={(e) => {
              e.stopPropagation();
              handleApprove(record);
            }}
          >
            承認
          </Button>
          <Button
            size="sm"
            className="bg-red-600 hover:bg-red-700"
            onClick={(e) => {
              e.stopPropagation();
              handleReject(record);
            }}
          >
            却下
          </Button>
        </div>
      )
    }
  ];

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* ページヘッダー */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-semibold text-white">承認キュー</h1>
            <p className="text-gray-400 mt-1">承認待ちの修正案を確認し、承認または却下を行います</p>
          </div>
          <Button onClick={fetchQueue} className="bg-gray-700 hover:bg-gray-600">
            更新
          </Button>
        </div>

        {/* フィルター */}
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-gray-300">
                優先度:
              </label>
              <Select
                value={priority}
                onChange={handlePriorityFilterChange}
                options={priorityOptions}
                className="w-48"
              />
            </div>
            <div className="text-sm text-gray-400">
              {queue.length}件の承認待ち修正案
            </div>
          </div>
        </div>

        {/* 承認キューテーブル */}
        <DataTable<ApprovalQueueItem>
          columns={columns}
          data={queue}
          loading={loading}
          onRow={(record) => ({
            onClick: () => handleRowClick(record),
            className: 'cursor-pointer hover:bg-gray-700'
          })}
          emptyText="承認待ちの修正案がありません"
        />

        {/* 確認モーダル */}
        <Modal
          isOpen={isModalOpen}
          onClose={closeModal}
          title={actionType === 'approve' ? '修正案の承認' : '修正案の却下'}
        >
          {selectedRevision && (
            <div className="space-y-4">
              <div className="bg-gray-100 p-4 rounded">
                <div className="space-y-2 text-sm">
                  <p><strong>記事番号:</strong> {selectedRevision.article_number || '-'}</p>
                  <p><strong>提案者:</strong> {selectedRevision.proposer_name}</p>
                  <p><strong>修正理由:</strong> {selectedRevision.reason}</p>
                  <p><strong>優先度:</strong> {selectedRevision.priority}</p>
                  <p><strong>影響度:</strong> {selectedRevision.impact_level}</p>
                </div>
              </div>
              
              <p className="text-gray-700 font-medium">
                {actionType === 'approve'
                  ? 'この修正案を承認してもよろしいですか？'
                  : 'この修正案を却下してもよろしいですか？'}
              </p>
              
              <div className="flex justify-end space-x-3 pt-4">
                <Button
                  variant="outline"
                  onClick={closeModal}
                  disabled={processing}
                >
                  キャンセル
                </Button>
                <Button
                  className={actionType === 'reject' ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'}
                  onClick={confirmAction}
                  disabled={processing}
                >
                  {processing && (
                    <svg className="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  )}
                  {actionType === 'approve' ? '承認する' : '却下する'}
                </Button>
              </div>
            </div>
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}