/**
 * Zodバリデーションスキーマ
 * フォーム入力とAPI通信の検証用
 */

import { z } from 'zod';

// 共通のバリデーション関数
const createOptionalStringSchema = (maxLength?: number) => {
  let schema = z.string().nullable().optional();
  if (maxLength) {
    return schema.refine(
      (val) => !val || val.length <= maxLength,
      { message: `${maxLength}文字以下で入力してください` }
    );
  }
  return schema;
};

const createRequiredStringSchema = (minLength: number, maxLength?: number) => {
  let schema = z.string().min(minLength, `${minLength}文字以上で入力してください`);
  if (maxLength) {
    schema = schema.max(maxLength, `${maxLength}文字以下で入力してください`);
  }
  return schema;
};

// ユーザー関連のスキーマ
export const userRoleSchema = z.enum(['user', 'approver', 'admin'], {
  errorMap: () => ({ message: '有効なロールを選択してください' })
});

export const userCreateSchema = z.object({
  username: createRequiredStringSchema(1, 50),
  email: z.string().email('有効なメールアドレスを入力してください'),
  full_name: createRequiredStringSchema(1, 100),
  sweet_name: createOptionalStringSchema(50),
  ctstage_name: createOptionalStringSchema(50),
  role: userRoleSchema,
  approval_group_id: z.string().uuid('有効なUUIDを入力してください').nullable().optional(),
  is_active: z.boolean(),
  password: createRequiredStringSchema(8)
});

export const userUpdateSchema = userCreateSchema.partial().omit({ password: true }).extend({
  password: z.string().min(8, '8文字以上で入力してください').optional()
});

export const loginSchema = z.object({
  username: createRequiredStringSchema(1),
  password: createRequiredStringSchema(1)
});

// 修正案関連のスキーマ
export const revisionStatusSchema = z.enum(['draft', 'submitted', 'approved', 'rejected', 'deleted'], {
  errorMap: () => ({ message: '有効なステータスを選択してください' })
});

export const revisionCreateSchema = z.object({
  target_article_id: createRequiredStringSchema(1, 100),
  approver_id: z.string().uuid('承認者を選択してください'),
  reason: createRequiredStringSchema(1),
  // after_* フィールド
  after_title: createOptionalStringSchema(),
  after_info_category: z.string().uuid('有効なカテゴリを選択してください').nullable().optional(),
  after_keywords: createOptionalStringSchema(),
  after_importance: z.boolean().nullable().optional(),
  after_publish_start: z.string().date('有効な日付を入力してください').nullable().optional(),
  after_publish_end: z.string().date('有効な日付を入力してください').nullable().optional(),
  after_target: createOptionalStringSchema(100),
  after_question: createOptionalStringSchema(),
  after_answer: createOptionalStringSchema(),
  after_additional_comment: createOptionalStringSchema()
}).refine(
  (data) => {
    // 開始日と終了日のバリデーション
    if (data.after_publish_start && data.after_publish_end) {
      return new Date(data.after_publish_start) <= new Date(data.after_publish_end);
    }
    return true;
  },
  {
    message: '公開終了日は開始日以降で設定してください',
    path: ['after_publish_end']
  }
);

export const revisionUpdateSchema = z.object({
  reason: z.string().min(1).optional(),
  status: revisionStatusSchema.optional(),
  processed_at: z.string().datetime().nullable().optional(),
  approver_id: z.string().uuid().optional(),
  
  // after_* フィールド
  after_title: createOptionalStringSchema(),
  after_info_category: z.string().uuid('有効なカテゴリを選択してください').nullable().optional(),
  after_keywords: createOptionalStringSchema(),
  after_importance: z.boolean().nullable().optional(),
  after_publish_start: z.string().date('有効な日付を入力してください').nullable().optional(),
  after_publish_end: z.string().date('有効な日付を入力してください').nullable().optional(),
  after_target: createOptionalStringSchema(100),
  after_question: createOptionalStringSchema(),
  after_answer: createOptionalStringSchema(),
  after_additional_comment: createOptionalStringSchema()
});

export const revisionStatusUpdateSchema = z.object({
  status: z.enum(['submitted', 'approved', 'rejected', 'deleted'])
});

// 記事関連のスキーマ
export const articleCreateSchema = z.object({
  article_id: createRequiredStringSchema(1, 100),
  article_number: createRequiredStringSchema(1, 100),
  article_url: z.string().url('有効なURLを入力してください').nullable().optional(),
  approval_group: z.string().uuid('有効な承認グループを選択してください').nullable().optional(),
  title: createOptionalStringSchema(),
  info_category: z.string().uuid('有効なカテゴリを選択してください').nullable().optional(),
  keywords: createOptionalStringSchema(),
  importance: z.boolean().nullable().optional(),
  publish_start: z.string().date('有効な日付を入力してください').nullable().optional(),
  publish_end: z.string().date('有効な日付を入力してください').nullable().optional(),
  target: createOptionalStringSchema(100),
  question: createOptionalStringSchema(),
  answer: createOptionalStringSchema(),
  additional_comment: createOptionalStringSchema()
});

export const articleUpdateSchema = articleCreateSchema.partial().omit({ article_id: true });

// 承認グループ関連のスキーマ
export const approvalGroupCreateSchema = z.object({
  group_name: createRequiredStringSchema(1, 100),
  description: createOptionalStringSchema(),
  is_active: z.boolean()
});

export const approvalGroupUpdateSchema = approvalGroupCreateSchema.partial();

// 情報カテゴリ関連のスキーマ
export const infoCategoryCreateSchema = z.object({
  category_name: createRequiredStringSchema(1, 100),
  description: createOptionalStringSchema(),
  is_active: z.boolean()
});

export const infoCategoryUpdateSchema = infoCategoryCreateSchema.partial();

// 通知関連のスキーマ
export const notificationCreateSchema = z.object({
  user_id: z.string().uuid('有効なユーザーIDが必要です'),
  message: createRequiredStringSchema(1),
  is_read: z.boolean(),
  notification_type: createRequiredStringSchema(1),
  revision_id: z.string().uuid().nullable().optional()
});

// クエリパラメータのスキーマ
export const queryParamsSchema = z.object({
  skip: z.number().int().min(0).optional(),
  limit: z.number().int().min(1).max(1000).optional(),
  sort_by: z.string().optional(),
  sort_order: z.enum(['asc', 'desc']).optional()
});

export const revisionQueryParamsSchema = queryParamsSchema.extend({
  status: revisionStatusSchema.optional(),
  proposer_id: z.string().uuid().optional(),
  approver_id: z.string().uuid().optional(),
  target_article_id: z.string().optional()
});

// 型エクスポート
export type UserCreateInput = z.infer<typeof userCreateSchema>;
export type UserUpdateInput = z.infer<typeof userUpdateSchema>;
export type LoginInput = z.infer<typeof loginSchema>;
export type RevisionCreateInput = z.infer<typeof revisionCreateSchema>;
export type RevisionUpdateInput = z.infer<typeof revisionUpdateSchema>;
export type RevisionStatusUpdateInput = z.infer<typeof revisionStatusUpdateSchema>;
export type ArticleCreateInput = z.infer<typeof articleCreateSchema>;
export type ArticleUpdateInput = z.infer<typeof articleUpdateSchema>;
export type ApprovalGroupCreateInput = z.infer<typeof approvalGroupCreateSchema>;
export type ApprovalGroupUpdateInput = z.infer<typeof approvalGroupUpdateSchema>;
export type InfoCategoryCreateInput = z.infer<typeof infoCategoryCreateSchema>;
export type InfoCategoryUpdateInput = z.infer<typeof infoCategoryUpdateSchema>;
export type NotificationCreateInput = z.infer<typeof notificationCreateSchema>;
export type QueryParamsInput = z.infer<typeof queryParamsSchema>;
export type RevisionQueryParamsInput = z.infer<typeof revisionQueryParamsSchema>;