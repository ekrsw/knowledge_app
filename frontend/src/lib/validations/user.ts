/**
 * ユーザー関連のバリデーションスキーマ
 */

import { z } from 'zod';

export const userRoleSchema = z.enum(['user', 'approver', 'admin']);

export const loginSchema = z.object({
  username: z
    .string()
    .min(1, 'ユーザー名を入力してください')
    .max(50, 'ユーザー名は50文字以内で入力してください'),
  password: z
    .string()
    .min(1, 'パスワードを入力してください')
    .min(8, 'パスワードは8文字以上で入力してください')
});

export const userCreateSchema = z.object({
  username: z
    .string()
    .min(1, 'ユーザー名を入力してください')
    .max(50, 'ユーザー名は50文字以内で入力してください')
    .regex(/^[a-zA-Z0-9_-]+$/, 'ユーザー名は英数字、アンダースコア、ハイフンのみ使用可能です'),
  email: z
    .string()
    .min(1, 'メールアドレスを入力してください')
    .email('有効なメールアドレスを入力してください')
    .max(255, 'メールアドレスは255文字以内で入力してください'),
  password: z
    .string()
    .min(8, 'パスワードは8文字以上で入力してください')
    .max(100, 'パスワードは100文字以内で入力してください')
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, 'パスワードは大文字、小文字、数字を含む必要があります'),
  full_name: z
    .string()
    .min(1, '氏名を入力してください')
    .max(100, '氏名は100文字以内で入力してください'),
  sweet_name: z
    .string()
    .max(50, 'スイート名は50文字以内で入力してください')
    .nullable()
    .optional(),
  ctstage_name: z
    .string()
    .max(50, 'CTステージ名は50文字以内で入力してください')
    .nullable()
    .optional(),
  role: userRoleSchema.default('user'),
  approval_group_id: z
    .string()
    .uuid('有効なUUIDを入力してください')
    .nullable()
    .optional()
});

export const userUpdateSchema = z.object({
  email: z
    .string()
    .email('有効なメールアドレスを入力してください')
    .max(255, 'メールアドレスは255文字以内で入力してください')
    .optional(),
  full_name: z
    .string()
    .min(1, '氏名を入力してください')
    .max(100, '氏名は100文字以内で入力してください')
    .optional(),
  sweet_name: z
    .string()
    .max(50, 'スイート名は50文字以内で入力してください')
    .nullable()
    .optional(),
  ctstage_name: z
    .string()
    .max(50, 'CTステージ名は50文字以内で入力してください')
    .nullable()
    .optional(),
  role: userRoleSchema.optional(),
  approval_group_id: z
    .string()
    .uuid('有効なUUIDを入力してください')
    .nullable()
    .optional(),
  is_active: z.boolean().optional()
});

export const passwordUpdateSchema = z.object({
  current_password: z
    .string()
    .min(1, '現在のパスワードを入力してください'),
  new_password: z
    .string()
    .min(8, '新しいパスワードは8文字以上で入力してください')
    .max(100, '新しいパスワードは100文字以内で入力してください')
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, '新しいパスワードは大文字、小文字、数字を含む必要があります'),
  confirm_password: z.string()
}).refine((data) => data.new_password === data.confirm_password, {
  message: 'パスワードが一致しません',
  path: ['confirm_password']
});

// Type inference
export type LoginInput = z.infer<typeof loginSchema>;
export type UserCreateInput = z.infer<typeof userCreateSchema>;
export type UserUpdateInput = z.infer<typeof userUpdateSchema>;
export type PasswordUpdateInput = z.infer<typeof passwordUpdateSchema>;