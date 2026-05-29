import type { SortOption } from '../../types/shop';
import type { FilterConfig } from '../../config/filters';
import FilterDropdown from './FilterDropdown';
import MultiFilterDropdown from './MultiFilterDropdown';
import SortDropdown from './SortDropdown';

interface SortFilterBarProps {
  sort: SortOption;
  /** 筛选配置列表 */
  filterConfigs: FilterConfig[];
  /** 各字典的选项 { dictType: displayName[] } */
  filterOptions: Record<string, string[]>;
  /** 当前筛选值 { dictType: string | string[] } */
  filterValues: Record<string, string | string[]>;
  onSortChange: (sort: SortOption) => void;
  /** 通用筛选变更回调 */
  onFilterChange: (dictType: string, value: string | string[]) => void;
  onClear: () => void;
}

const sortOptions: { value: SortOption; label: string }[] = [
  { value: 'favorite_count', label: '收藏最多' },
  { value: 'view_count', label: '浏览量最高' },
  { value: 'average_rating', label: '最高评分' },
  { value: 'created_at', label: '最新发布' },
];

export default function SortFilterBar({
  sort,
  filterConfigs,
  filterOptions,
  filterValues,
  onSortChange,
  onFilterChange,
  onClear,
}: SortFilterBarProps) {
  // 是否有活动的筛选
  const hasActive = Object.values(filterValues).some((v) => {
    if (Array.isArray(v)) return v.length > 0;
    return v !== '';
  });

  return (
    <div className="flex items-center gap-2 flex-wrap">
      <SortDropdown
        value={sort}
        options={sortOptions}
        onChange={(v) => onSortChange(v as SortOption)}
      />

      {/* 动态渲染筛选控件 — 根据配置自动生成 */}
      {filterConfigs.map((cfg) => {
        const options = filterOptions[cfg.dictType] ?? [];
        const value = filterValues[cfg.dictType];

        if (cfg.component === 'multi-select') {
          return (
            <MultiFilterDropdown
              key={cfg.dictType}
              label={cfg.label}
              options={options}
              values={(value as string[]) ?? []}
              onChange={(vals) => onFilterChange(cfg.dictType, vals)}
            />
          );
        }

        return (
          <FilterDropdown
            key={cfg.dictType}
            label={cfg.label}
            options={options}
            value={(value as string) ?? ''}
            onChange={(v) => onFilterChange(cfg.dictType, v)}
          />
        );
      })}

      {hasActive && (
        <button
          type="button"
          onClick={onClear}
          className="text-sm text-gray-500 hover:text-gray-700 px-2"
        >
          清除
        </button>
      )}
    </div>
  );
}
