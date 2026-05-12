/** 分页响应包装 */
export interface PaginatedResult<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

/** API 统一响应格式 */
export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}
