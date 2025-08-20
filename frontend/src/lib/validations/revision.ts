/**
 * 修正案関連のバリデーションスキーマ
 */

import { z } from 'zod';

export const revisionStatusSchema = z.enum(['draft', 'submitted', 'approved', 'rejected', 'deleted']);

export const revisionCreateSchema = z.object({
  target_article_id: z
    .string()
    .min(1, '対象記事IDを入力してください'),
  approver_id: z
    .string()
    .uuid('有効な承認者IDを選択してください')
    .min(1, '承認者を選択してください'),
  reason: z
    .string()
    .min(1, '修正理由を入力してください')
    .max(1000, '修正理由は1000文字以内で入力してください'),
  
  // After fields - at least one must be provided
  after_title: z
    .string()
    .max(255, 'タイトルは255文字以内で入力してください')
    .nullable()
    .optional(),
  after_info_category: z
    .string()
    .uuid('有効な情報カテゴリを選択してください')
    .nullable()
    .optional(),
  after_keywords: z
    .string()
    .max(500, 'キーワードは500文字以内で入力してください')
    .nullable()
    .optional(),
  after_importance: z
    .boolean()
    .nullable()
    .optional(),
  after_publish_start: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, '有効な日付形式(YYYY-MM-DD)で入力してください')
    .nullable()
    .optional(),
  after_publish_end: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, '有効な日付形式(YYYY-MM-DD)で入力してください')
    .nullable()
    .optional(),
  after_target: z
    .string()
    .max(100, '対象は100文字以内で入力してください')
    .nullable()
    .optional(),
  after_question: z
    .string()
    .nullable()
    .optional(),
  after_answer: z
    .string()
    .nullable()
    .optional(),
  after_additional_comment: z
    .string()
    .nullable()
    .optional()
}).refine((data) => {
  // At least one after_* field must have a value
  const afterFields = [
    data.after_title,
    data.after_info_category,
    data.after_keywords,
    data.after_importance,
    data.after_publish_start,
    data.after_publish_end,
    data.after_target,
    data.after_question,
    data.after_answer,
    data.after_additional_comment
  ];
  
  return afterFields.some(field => field !== null && field !== undefined && field !== '');
}, {
  message: '少なくとも1つのフィールドを変更してください',
  path: ['after_title'] // Show error on first field
}).refine((data) => {
  // If both dates are provided, start should be before or equal to end
  if (data.after_publish_start && data.after_publish_end) {
    return data.after_publish_start <= data.after_publish_end;
  }
  return true;
}, {
  message: '公開開始日は公開終了日以前の日付を設定してください',
  path: ['after_publish_end']
});

export const revisionUpdateSchema = z.object({
  approver_id: z
    .string()
    .uuid('有効な承認者IDを選択してください')
    .optional(),
  reason: z
    .string()
    .min(1, '修正理由を入力してください')
    .max(1000, '修正理由は1000文字以内で入力してください')
    .optional(),
  
  after_title: z
    .string()
    .max(255, 'タイトルは255文字以内で入力してください')
    .nullable()
    .optional(),
  after_info_category: z
    .string()
    .uuid('有効な情報カテゴリを選択してください')
    .nullable()
    .optional(),
  after_keywords: z
    .string()
    .max(500, 'キーワードは500文字以内で入力してください')
    .nullable()
    .optional(),
  after_importance: z
    .boolean()
    .nullable()
    .optional(),
  after_publish_start: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, '有効な日付形式(YYYY-MM-DD)で入力してください')
    .nullable()
    .optional(),
  after_publish_end: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, '有効な日付形式(YYYY-MM-DD)で入力してください')
    .nullable()
    .optional(),
  after_target: z
    .string()
    .max(100, '対象は100文字以内で入力してください')
    .nullable()
    .optional(),
  after_question: z
    .string()
    .nullable()
    .optional(),
  after_answer: z
    .string()
    .nullable()
    .optional(),
  after_additional_comment: z
    .string()
    .nullable()
    .optional()
}).refine((data) => {
  // If both dates are provided, start should be before or equal to end
  if (data.after_publish_start && data.after_publish_end) {
    return data.after_publish_start <= data.after_publish_end;
  }
  return true;
}, {
  message: '公開開始日は公開終了日以前の日付を設定してください',
  path: ['after_publish_end']
});

export const approvalDecisionSchema = z.object({
  action: z.enum(['approve', 'reject', 'request_changes', 'defer']),
  comment: z
    .string()
    .min(1, 'コメントを入力してください')
    .max(1000, 'コメントは1000文字以内で入力してください'),
  priority: z
    .enum(['low', 'medium', 'high', 'urgent'])
    .default('medium')
    .optional()
});

// Search and filter schemas
export const revisionFilterSchema = z.object({
  status: z
    .array(revisionStatusSchema)
    .or(revisionStatusSchema)
    .optional(),
  proposer_id: z
    .string()
    .uuid()
    .optional(),
  approver_id: z
    .string()
    .uuid()
    .optional(),
  target_article_id: z
    .string()
    .optional(),
  date_from: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, '有効な日付形式(YYYY-MM-DD)で入力してください')
    .optional(),
  date_to: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, '有効な日付形式(YYYY-MM-DD)で入力してください')
    .optional()
}).refine((data) => {
  if (data.date_from && data.date_to) {
    return data.date_from <= data.date_to;
  }
  return true;
}, {
  message: '開始日は終了日以前の日付を設定してください',
  path: ['date_to']
});

// Type inference
export type RevisionCreateInput = z.infer<typeof revisionCreateSchema>;
export type RevisionUpdateInput = z.infer<typeof revisionUpdateSchema>;
export type ApprovalDecisionInput = z.infer<typeof approvalDecisionSchema>;
export type RevisionFilterInput = z.infer<typeof revisionFilterSchema>;