'use client';

import { useState } from 'react';
import { 
  Button, 
  Input, 
  Textarea, 
  Select, 
  Alert, 
  Modal, 
  ModalBody, 
  ModalFooter, 
  useToast 
} from '@/components/ui';

export default function UITestPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [showAlert, setShowAlert] = useState(true);
  const { toast } = useToast();

  const selectOptions = [
    { value: 'option1', label: 'オプション 1' },
    { value: 'option2', label: 'オプション 2' },
    { value: 'option3', label: 'オプション 3' },
  ];

  return (
    <div className="min-h-screen bg-gray-900 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-white mb-4">UI Components Test</h1>
          <p className="text-gray-400">共通UIコンポーネントの動作確認ページ</p>
        </div>

        {/* Button Components */}
        <section className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Buttons</h2>
          <div className="space-y-4">
            <div className="flex flex-wrap gap-4">
              <Button variant="primary">Primary</Button>
              <Button variant="secondary">Secondary</Button>
              <Button variant="success">Success</Button>
              <Button variant="warning">Warning</Button>
              <Button variant="danger">Danger</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="outline">Outline</Button>
            </div>
            
            <div className="flex flex-wrap gap-4">
              <Button size="sm">Small</Button>
              <Button size="md">Medium</Button>
              <Button size="lg">Large</Button>
              <Button size="xl">Extra Large</Button>
            </div>
            
            <div className="flex flex-wrap gap-4">
              <Button loading>Loading</Button>
              <Button disabled>Disabled</Button>
              <Button leftIcon={
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              }>
                With Icon
              </Button>
            </div>
          </div>
        </section>

        {/* Form Components */}
        <section className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Form Components</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <Input 
                label="基本入力"
                placeholder="プレースホルダー"
                helperText="ヘルプテキスト"
              />
              
              <Input 
                label="エラー状態"
                placeholder="エラーの入力"
                error="エラーメッセージ"
              />
              
              <Input 
                label="アイコン付き"
                placeholder="検索..."
                leftIcon={
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                }
              />
              
              <Select 
                label="選択肢"
                placeholder="選択してください"
                options={selectOptions}
              />
            </div>
            
            <div className="space-y-4">
              <Textarea 
                label="テキストエリア"
                placeholder="複数行のテキスト..."
                helperText="最大500文字まで入力できます"
                rows={4}
              />
              
              <Textarea 
                label="エラー状態"
                placeholder="エラーのテキストエリア"
                error="入力内容に問題があります"
                rows={3}
              />
            </div>
          </div>
        </section>

        {/* Alert Components */}
        <section className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Alerts</h2>
          <div className="space-y-4">
            {showAlert && (
              <Alert 
                variant="info" 
                title="情報"
                dismissible
                onDismiss={() => setShowAlert(false)}
              >
                これは情報アラートです。重要な情報をユーザーに伝えます。
              </Alert>
            )}
            
            <Alert variant="success" title="成功">
              操作が正常に完了しました。
            </Alert>
            
            <Alert variant="warning" title="警告">
              注意が必要な状況です。確認してください。
            </Alert>
            
            <Alert variant="error" title="エラー">
              エラーが発生しました。再度お試しください。
            </Alert>
          </div>
        </section>

        {/* Modal and Toast */}
        <section className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Modal & Toast</h2>
          <div className="flex flex-wrap gap-4">
            <Button onClick={() => setIsModalOpen(true)}>
              モーダルを開く
            </Button>
            
            <Button onClick={() => toast.info('情報トースト')}>
              Info Toast
            </Button>
            
            <Button onClick={() => toast.success('成功トースト')}>
              Success Toast
            </Button>
            
            <Button onClick={() => toast.warning('警告トースト')}>
              Warning Toast
            </Button>
            
            <Button onClick={() => toast.error('エラートースト')}>
              Error Toast
            </Button>
          </div>
        </section>

        {/* Modal */}
        <Modal 
          isOpen={isModalOpen} 
          onClose={() => setIsModalOpen(false)}
          title="モーダルテスト"
          size="md"
        >
          <ModalBody>
            <div className="space-y-4">
              <p className="text-gray-300">
                これはモーダルのテストです。様々な機能を試すことができます。
              </p>
              
              <Input 
                label="モーダル内の入力"
                placeholder="何かを入力..."
              />
              
              <Textarea 
                label="メモ"
                placeholder="メモを入力..."
                rows={3}
              />
            </div>
          </ModalBody>
          
          <ModalFooter>
            <Button variant="outline" onClick={() => setIsModalOpen(false)}>
              キャンセル
            </Button>
            <Button onClick={() => {
              toast.success('モーダルで操作完了');
              setIsModalOpen(false);
            }}>
              保存
            </Button>
          </ModalFooter>
        </Modal>
      </div>
    </div>
  );
}