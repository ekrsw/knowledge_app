/**
 * 型定義の統一エクスポート
 * すべての型定義をここからインポートできます
 */

// ユーザー関連
export * from './user';

// 修正案関連
export * from './revision';

// 記事関連
export * from './article';

// 共通の型（承認グループ、情報カテゴリ、通知など）
export * from './common';

// API関連
export * from './api';

// バリデーション関連
export * from './validation';

// 型の再エクスポート（頻繁に使用される型の便利なエイリアス）
import type { User, UserRole, CurrentUser } from './user';
import type { Revision, RevisionStatus, RevisionCreate, RevisionUpdate } from './revision';
import type { Article, ArticleCreate, ArticleUpdate } from './article';
import type { ApprovalGroup, InfoCategory, Notification } from './common';
import type { ApiResponse, PaginatedResponse, ApiError, LoginRequest, LoginResponse } from './api';
import type {
  UserCreateInput,
  UserUpdateInput,
  LoginInput,
  RevisionCreateInput,
  RevisionUpdateInput,
  QueryParamsInput,
} from './validation';

// よく使用される型の便利なエクスポート
export type {
  // Core entities
  User,
  UserRole,
  CurrentUser,
  Revision,
  RevisionStatus,
  Article,
  ApprovalGroup,
  InfoCategory,
  Notification,
  
  // API types
  ApiResponse,
  PaginatedResponse,
  ApiError,
  LoginRequest,
  LoginResponse,
  
  // Create/Update types
  RevisionCreate,
  RevisionUpdate,
  ArticleCreate,
  ArticleUpdate,
  
  // Validation input types
  UserCreateInput,
  UserUpdateInput,
  LoginInput,
  RevisionCreateInput,
  RevisionUpdateInput,
  QueryParamsInput,
};