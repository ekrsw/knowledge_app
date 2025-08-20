/**
 * バリデーションスキーマのエクスポート
 */

// User validations
export * from './user';

// Revision validations
export * from './revision';

// Article validations
export * from './article';

// Common validation utilities
export { z } from 'zod';

// Common validation helpers
import { z } from 'zod';

export const uuidSchema = z.string().uuid('有効なUUIDを入力してください');

export const dateSchema = z
  .string()
  .regex(/^\d{4}-\d{2}-\d{2}$/, '有効な日付形式(YYYY-MM-DD)で入力してください');

export const datetimeSchema = z
  .string()
  .datetime('有効な日時形式を入力してください');

export const paginationSchema = z.object({
  skip: z
    .number()
    .int('整数を入力してください')
    .min(0, '0以上の値を入力してください')
    .default(0),
  limit: z
    .number()
    .int('整数を入力してください')
    .min(1, '1以上の値を入力してください')
    .max(100, '100以下の値を入力してください')
    .default(20)
});

export const searchSchema = z.object({
  q: z
    .string()
    .min(1, '検索キーワードを入力してください')
    .max(100, '検索キーワードは100文字以内で入力してください')
    .optional(),
  fields: z
    .array(z.string())
    .optional()
});

// Validation helper functions
export function validateForm<T>(schema: z.ZodSchema<T>, data: unknown): {
  success: boolean;
  data?: T;
  errors?: Record<string, string>;
} {
  try {
    const result = schema.parse(data);
    return { success: true, data: result };
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errors: Record<string, string> = {};
      error.issues.forEach((err: z.ZodIssue) => {
        const path = err.path.join('.');
        errors[path] = err.message;
      });
      return { success: false, errors };
    }
    return { success: false, errors: { _form: 'バリデーションエラーが発生しました' } };
  }
}

export function getFieldError(errors: Record<string, string> | undefined, field: string): string | undefined {
  return errors?.[field];
}

// Type inference for common schemas
export type PaginationInput = z.infer<typeof paginationSchema>;
export type SearchInput = z.infer<typeof searchSchema>;