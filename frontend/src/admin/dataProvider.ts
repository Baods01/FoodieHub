/**
 * FastAPI → react-admin 数据适配层
 *
 * 后端返回 ResponseModel 格式：{ code: 200, message: "success", data: ... }
 * react-admin 期望：{ data: [...], total: N }
 *
 * Resource 命名到 API 路径的映射：
 *   "users" → "/admin/users"
 *   "logs"  → "/admin/logs"
 *
 * 开发阶段提供 Mock 数据回退，后端未运行时仍可查看页面 UI。
 */
import type { DataProvider } from 'react-admin';
import apiClient from '../api/client';

/**
 * 统一提取：从 Axios response 中取出 ResponseModel 内的 data
 * 后端返回格式：{ code: 200, message: "xxx", data: ... }
 */
function extractApiData(response: any): any {
  if (response?.data && typeof response.data === 'object' && 'code' in response.data) {
    return response.data.data;
  }
  return response?.data;
}

/** Resource 名称到 API 路径的映射表 */
const resourceApiPath: Record<string, string> = {
  users: 'admin/users',
  logs: 'admin/logs',
  feedbacks: 'admin/feedbacks',
};

function apiPath(resource: string): string {
  return resourceApiPath[resource] ?? resource;
}

/** 从后端列表响应中提取 items 数组 */
function extractItems(payload: any): any[] {
  if (!payload) return [];
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.items)) return payload.items;
  if (Array.isArray(payload?.data)) return payload.data;
  if (Array.isArray(payload?.results)) return payload.results;
  return [];
}

/** 从后端列表响应中提取 total */
function extractTotal(payload: any): number {
  if (typeof payload?.total === 'number') return payload.total;
  if (Array.isArray(payload)) return payload.length;
  return 0;
}

/**
 * 安全 GET — 失败时返回 null
 */
async function safeApiGet(url: string, params?: Record<string, any>) {
  try {
    const response = await apiClient.get(url, { params });
    return extractApiData(response);
  } catch {
    return null;
  }
}

async function safeApiDelete(url: string) {
  try {
    await apiClient.delete(url);
  } catch {
    // 静默
  }
}

/** 获取各资源的 Mock 数据 */
function getMockData(resource: string) {
  if (resource === 'users') {
    return [
      { id: 1, username: 'admin', email: 'admin@foodiehub.cn', phone: '13800138001', role: 1, is_active: true, created_at: '2026-03-01T00:00:00Z', avatar: null, bio: '系统管理员' },
      { id: 2, username: '张三', email: 'zhangsan@scau.edu.cn', phone: '13800138002', role: 0, is_active: true, created_at: '2026-03-15T00:00:00Z' },
      { id: 3, username: '李四', email: 'lisi@scau.edu.cn', phone: '13800138003', role: 0, is_active: false, created_at: '2026-04-01T00:00:00Z' },
      { id: 4, username: '王五', email: 'wangwu@scau.edu.cn', phone: '13800138004', role: 0, is_active: true, created_at: '2026-04-10T00:00:00Z' },
      { id: 5, username: '赵六', email: 'zhaoliu@scau.edu.cn', phone: '13800138005', role: 0, is_active: true, created_at: '2026-04-20T00:00:00Z' },
    ];
  }
  if (resource === 'logs') {
    return [
      { id: 1, operator_name: 'admin', operation_module: '举报处理', operation_type: 'delete_comment', target_object_type: 'comment', target_object_id: 42, created_at: new Date().toISOString(), detail: '删除违规评论' },
      { id: 2, operator_name: 'admin', operation_module: '用户管理', operation_type: 'ban', target_object_type: 'user', target_object_id: 3, created_at: new Date(Date.now() - 86400000).toISOString(), detail: '封禁用户' },
      { id: 3, operator_name: 'admin', operation_module: '店铺管理', operation_type: 'approve', target_object_type: 'edit_request', target_object_id: 5, created_at: new Date(Date.now() - 172800000).toISOString(), detail: '通过店铺勘误' },
      { id: 4, operator_name: 'admin', operation_module: '举报处理', operation_type: 'reject', target_object_type: 'complaint', target_object_id: 12, created_at: new Date(Date.now() - 259200000).toISOString(), detail: '驳回举报' },
    ];
  }
  return [];
}

export const dataProvider: DataProvider = {
  getList: async (resource, params) => {
    const path = apiPath(resource);
    const page = params.pagination?.page ?? 1;
    const perPage = params.pagination?.perPage ?? 20;
    const queryParams: Record<string, any> = {
      page,
      page_size: perPage,
      ...params.filter,
    };

    const payload = await safeApiGet(`/${path}`, queryParams);

    let inner = extractItems(payload);
    let total = extractTotal(payload);

    if (inner.length === 0 && total === 0) {
      const mockData = getMockData(resource);
      inner = mockData.slice(0, perPage);
      total = mockData.length;
    }

    return { data: inner, total };
  },

  getOne: async (resource, params) => {
    const payload = await safeApiGet(`/${apiPath(resource)}/${params.id}`);

    if (payload && typeof payload === 'object' && !Array.isArray(payload)) {
      return { data: payload };
    }

    const mockData = getMockData(resource).find((d: any) => d.id === params.id);
    return { data: mockData ?? { id: params.id } };
  },

  create: async (resource, params) => {
    const path = apiPath(resource);
    try {
      const response = await apiClient.post(`/${path}`, params.data);
      const payload = extractApiData(response);
      return { data: (payload ?? { id: Date.now(), ...params.data }) as any };
    } catch {
      return { data: { id: Date.now(), ...params.data } as any };
    }
  },

  update: async (resource, params) => {
    const path = apiPath(resource);
    try {
      const response = await apiClient.put(`/${path}/${params.id}`, params.data);
      const payload = extractApiData(response);
      return { data: (payload ?? { id: params.id, ...params.data }) as any };
    } catch {
      return { data: { id: params.id, ...params.data } as any };
    }
  },

  delete: async (resource, params) => {
    const path = apiPath(resource);
    await safeApiDelete(`/${path}/${params.id}`);
    return { data: params.meta?.previousData ?? ({ id: params.id } as any) };
  },

  getMany: async (resource, params) => {
    const path = apiPath(resource);
    const promises = params.ids.map((id) => safeApiGet(`/${path}/${id}`));
    const results = await Promise.all(promises);
    const resolved = results.filter(Boolean).filter((r) => typeof r === 'object');
    if (resolved.length === 0) {
      const allMock = getMockData(resource);
      return { data: allMock.filter((d: any) => params.ids.includes(d.id)) };
    }
    return { data: resolved };
  },

  getManyReference: async (resource, params) => {
    return dataProvider.getList(resource, {
      ...params,
      filter: { ...params.filter, [params.target]: params.id },
    });
  },

  updateMany: async (resource, params) => {
    const path = apiPath(resource);
    try {
      const promises = params.ids.map((id) =>
        apiClient.put(`/${path}/${id}`, params.data)
      );
      await Promise.all(promises);
    } catch {
      // 忽略失败
    }
    return { data: params.ids };
  },

  deleteMany: async (resource, params) => {
    const path = apiPath(resource);
    await Promise.all(params.ids.map((id) => safeApiDelete(`/${path}/${id}`)));
    return { data: params.ids };
  },
};
