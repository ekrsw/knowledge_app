/**
 * 記事関連のバリデーションスキーマ
 */

import { z } from 'zod';

export const articleCreateSchema = z.object({
  article_id: z
    .string()
    .min(1, '記事IDを入力してください')
    .max(100, '記事IDは100文字以内で入力してください')
    .regex(/^[a-zA-Z0-9_-]+$/, '記事IDは英数字、アンダースコア、ハイフンのみ使用可能です'),
  title: z
    .string()
    .min(1, 'タイトルを入力してください')
    .max(255, 'タイトルは255文字以内で入力してください'),
  info_category: z
    .string()
    .uuid('有効な情報カテゴリを選択してください')
    .nullable()
    .optional(),
  keywords: z
    .string()
    .max(500, 'キーワードは500文字以内で入力してください')
    .nullable()
    .optional(),
  importance: z
    .boolean()
    .default(false),
  publish_start: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, '有効な日付形式(YYYY-MM-DD)で入力してください')
    .nullable()
    .optional(),
  publish_end: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, '有効な日付形式(YYYY-MM-DD)で入力してください')
    .nullable()
    .optional(),
  target: z
    .string()
    .max(100, '対象は100文字以内で入力してください')
    .nullable()
    .optional(),
  question: z
    .string()
    .nullable()
    .optional(),
  answer: z
    .string()
    .nullable()
    .optional(),
  additional_comment: z
    .string()
    .nullable()
    .optional(),
  approval_group: z
    .string()
    .uuid('有効な承認グループを選択してください')
    .nullable()
    .optional()
}).refine((data) => {
  // If both dates are provided, start should be before or equal to end
  if (data.publish_start && data.publish_end) {
    return data.publish_start <= data.publish_end;
  }
  return true;
}, {
  message: '公開開始日は公開終了日以前の日付を設定してください',
  path: ['publish_end']
});

export const articleUpdateSchema = z.object({
  title: z
    .string()
    .min(1, 'タイトルを入力してください')
    .max(255, 'タイトルは255文字以内で入力してください')
    .optional(),
  info_category: z
    .string()
    .uuid('有効な情報カテゴリを選択してください')
    .nullable()
    .optional(),
  keywords: z
    .string()
    .max(500, 'キーワードは500文字以内で入力してください')
    .nullable()
    .optional(),
  importance: z
    .boolean()
    .optional(),
  publish_start: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, '有効な日付形式(YYYY-MM-DD)で入力してください')
    .nullable()
    .optional(),
  publish_end: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, '有効な日付形式(YYYY-MM-DD)で入力してください')
    .nullable()
    .optional(),
  target: z
    .string()
    .max(100, '対象は100文字以内で入力してください')
    .nullable()
    .optional(),
  question: z
    .string()
    .nullable()
    .optional(),
  answer: z
    .string()
    .nullable()
    .optional(),
  additional_comment: z
    .string()
    .nullable()
    .optional(),
  approval_group: z
    .string()
    .uuid('有効な承認グループを選択してください')
    .nullable()
    .optional(),
  is_active: z
    .boolean()
    .optional()
}).refine((data) => {
  // If both dates are provided, start should be before or equal to end
  if (data.publish_start && data.publish_end) {
    return data.publish_start <= data.publish_end;
  }
  return true;
}, {
  message: '公開開始日は公開終了日以前の日付を設定してください',
  path: ['publish_end']
});

export const infoCategoryCreateSchema = z.object({
  category_name: z
    .string()
    .min(1, 'カテゴリ名を入力してください')
    .max(100, 'カテゴリ名は100文字以内で入力してください'),
  description: z
    .string()
    .max(500, '説明は500文字以内で入力してください')
    .nullable()
    .optional(),
  display_order: z
    .number()
    .int('表示順序は整数で入力してください')
    .min(0, '表示順序は0以上で入力してください')
    .default(0)
});

export const infoCategoryUpdateSchema = z.object({
  category_name: z
    .string()
    .min(1, 'カテゴリ名を入力してください')
    .max(100, 'カテゴリ名は100文字以内で入力してください')
    .optional(),
  description: z
    .string()
    .max(500, '説明は500文字以内で入力してください')
    .nullable()
    .optional(),
  display_order: z
    .number()
    .int('表示順序は整数で入力してください')
    .min(0, '表示順序は0以上で入力してください')
    .optional(),
  is_active: z
    .boolean()
    .optional()
});

export const approvalGroupCreateSchema = z.object({
  group_name: z
    .string()
    .min(1, 'グループ名を入力してください')
    .max(100, 'グループ名は100文字以内で入力してください'),
  description: z
    .string()
    .max(500, '説明は500文字以内で入力してください')
    .nullable()
    .optional()
});

export const approvalGroupUpdateSchema = z.object({
  group_name: z
    .string()
    .min(1, 'グループ名を入力してください')
    .max(100, 'グループ名は100文字以内で入力してください')
    .optional(),
  description: z
    .string()
    .max(500, '説明は500文字以内で入力してください')
    .nullable()
    .optional(),
  is_active: z
    .boolean()
    .optional()
});

// Type inference
export type ArticleCreateInput = z.infer<typeof articleCreateSchema>;
export type ArticleUpdateInput = z.infer<typeof articleUpdateSchema>;
export type InfoCategoryCreateInput = z.infer<typeof infoCategoryCreateSchema>;
export type InfoCategoryUpdateInput = z.infer<typeof infoCategoryUpdateSchema>;
export type ApprovalGroupCreateInput = z.infer<typeof approvalGroupCreateSchema>;
export type ApprovalGroupUpdateInput = z.infer<typeof approvalGroupUpdateSchema>;