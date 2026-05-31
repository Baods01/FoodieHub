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
  shops: 'admin/shops',
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

/** 获取各资源的 Mock 数据 */export const dataProvider: DataProvider = {
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

    // 客户端排序（后端不支持传 sort_by 时兜底）
    const sortField = params.sort?.field;
    const sortOrder = params.sort?.order;
    if (sortField && inner.length > 0 && sortField in inner[0]) {
      inner = [...inner].sort((a: any, b: any) => {
        const va = a[sortField] ?? '';
        const vb = b[sortField] ?? '';
        if (typeof va === 'number') {
          return sortOrder === 'ASC' ? va - vb : vb - va;
        }
        return sortOrder === 'ASC'
          ? String(va).localeCompare(String(vb))
          : String(vb).localeCompare(String(va));
      });
    }

    return { data: inner, total };
  },

  getOne: async (resource, params) => {
    const payload = await safeApiGet(`/${apiPath(resource)}/${params.id}`);

    if (payload && typeof payload === 'object' && !Array.isArray(payload)) {
      return { data: payload };
    }

    return { data: { id: params.id } as any };
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
      return { data: [] };
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
