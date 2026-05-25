/** 一个筛选控件的定义 */
export interface FilterConfig {
  dictType: string;      // 字典类型编码，如 'category', 'dining_method'
  label: string;         // 显示名称，如 '品类', '就餐方式'
  component: 'single-select' | 'multi-select';
}

/** 首页筛选栏配置 — 新增字典类型只需在此加一行 */
export const filterConfigs: FilterConfig[] = [
  { dictType: 'category',      label: '品类',   component: 'single-select' },
  { dictType: 'location_type', label: '区域',   component: 'single-select' },
  { dictType: 'dining_method', label: '就餐方式', component: 'multi-select'  },
];
