import apiClient from './client';
import type { ApiResponse } from '../types/common';

export interface DictItem {
  id: number;
  name: string;
}

export interface DictType {
  id: number;
  name: string;
  target_table: string;
}

/**
 * 获取所有字典类型
 */
export async function fetchDictTypes(): Promise<DictType[]> {
  const res = await apiClient.get<ApiResponse<DictType[]>>('/dict/types');
  return res.data.data ?? [];
}

/**
 * 按类型名称查询字典数据
 * @param typeName 类型名称，如 "品类"、"区域"、"就餐方式"
 */
export async function fetchDictData(typeName: string): Promise<DictItem[]> {
  const res = await apiClient.get<ApiResponse<DictItem[]>>('/dict/data', {
    params: { type_name: typeName },
  });
  return res.data.data ?? [];
}

/**
 * 按类型名称查询字典数据（包含完整信息，含 id）
 * 用于将字典名称转换为 ID
 */
export async function fetchDictDataWithId(typeName: string): Promise<{ id: number; name: string }[]> {
  const res = await apiClient.get<ApiResponse<{ id: number; name: string }[]>>('/dict/data', {
    params: { type_name: typeName },
  });
  return res.data.data ?? [];
}
