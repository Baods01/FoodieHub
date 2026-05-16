import type { SortOption } from '../../types/shop';
import FilterDropdown from './FilterDropdown';
import SortDropdown from './SortDropdown';

interface SortFilterBarProps {
  sort: SortOption;
  category: string;
  area: string;
  categories: string[];
  areas: string[];
  onSortChange: (sort: SortOption) => void;
  onCategoryChange: (cat: string) => void;
  onAreaChange: (area: string) => void;
  onClear: () => void;
}

const sortOptions: { value: SortOption; label: string }[] = [
  { value: 'favorites', label: '收藏最多' },
  { value: 'views', label: '浏览量最高' },
  { value: 'rating', label: '最高评分' },
  { value: 'reviews', label: '最多评论' },
];

export default function SortFilterBar({
  sort,
  category,
  area,
  categories,
  areas,
  onSortChange,
  onCategoryChange,
  onAreaChange,
  onClear,
}: SortFilterBarProps) {
  const hasActiveFilter = category !== '' || area !== '';

  return (
    <div className="flex justify-between items-center">
      <div className="flex items-center gap-2">
        <SortDropdown
          value={sort}
          options={sortOptions}
          onChange={(v) => onSortChange(v as SortOption)}
        />
      </div>

      <div className="flex items-center gap-2">
        <FilterDropdown
          label="品类"
          options={categories}
          value={category}
          onChange={onCategoryChange}
        />
        <FilterDropdown
          label="区域"
          options={areas}
          value={area}
          onChange={onAreaChange}
        />
        {hasActiveFilter && (
          <button
            type="button"
            onClick={onClear}
            className="text-sm text-gray-500 hover:text-gray-700 px-2"
          >
            清除
          </button>
        )}
      </div>
    </div>
  );
}
