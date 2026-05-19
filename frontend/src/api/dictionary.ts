/** 字典数据类型 */
export interface DictItem {
  code: string;
  name: string;
}

/** 已知字典类型 */
export type DictType = 'category' | 'location_type' | 'dining_method';

// 对接后端时取消注释:
// import apiClient from './client';
// import type { ApiResponse } from '../types/common';

/**
 * 按类型获取字典数据
 * @param type 字典类型编码
 * @returns DictItem[] 包含 code + name
 */
export async function fetchDictData(type: DictType): Promise<DictItem[]> {
  // const { data } = await apiClient.get<ApiResponse<DictItem[]>>(`/dictionaries/${type}`);
  // return data.data;
  return mockDictData(type);
}

// ============ Mock ============

const mockDict: Record<DictType, DictItem[]> = {
  category: [
    { code: 'local_cuisine', name: '地方菜' },
    { code: 'hotpot',        name: '火锅' },
    { code: 'barbecue',      name: '烧烤/烤肉' },
    { code: 'western_food',  name: '异域料理' },
    { code: 'snacks',        name: '小吃快餐' },
    { code: 'specialty',     name: '特色菜' },
    { code: 'drinks',        name: '饮品' },
    { code: 'desserts',      name: '甜点/面包' },
  ],
  location_type: [
    { code: 'nei_taisan',  name: '泰山区' },
    { code: 'nei_huashan', name: '华山区' },
    { code: 'nei_qilin',   name: '启林区' },
    { code: 'nei_liuyi',   name: '六一区' },
    { code: 'zhuxiaoqu',   name: '主校区' },
    { code: 'wai_outside', name: '校外' },
  ],
  dining_method: [
    { code: 'dine_in',   name: '堂食' },
    { code: 'pickup',    name: '自取' },
    { code: 'delivery',  name: '外卖' },
  ],
};

const delay = () => new Promise((r) => setTimeout(r, 200 + Math.random() * 200));

async function mockDictData(type: DictType): Promise<DictItem[]> {
  await delay();
  return [...mockDict[type]];
}
