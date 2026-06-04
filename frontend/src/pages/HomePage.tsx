import { useReducer, useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDebounce } from '../hooks/useDebounce';
import { useInfiniteScroll } from '../hooks/useInfiniteScroll';
import { fetchShops } from '../api/shops';
import { fetchDictDataWithId } from '../api/dictionary';
import type { ShopCardData, SortOption } from '../types/shop';
import { filterConfigs } from '../config/filters';
import AnnouncementBanner from '../components/shop/AnnouncementBanner';
import SearchBar from '../components/shop/SearchBar';
import SortFilterBar from '../components/shop/SortFilterBar';
import { ShopList } from '../components/shop/ShopList';
import { ShopCardGridSkeleton } from '../components/shop/ShopCardSkeleton';
import { EmptyState } from '../components/ui/EmptyState';
import { ErrorState } from '../components/ui/ErrorState';

interface FilterState {
  keyword: string;
  sort: string;
  category: string;       // 存储品类 DictData ID
  area: string;           // 存储区域 DictData ID
  diningMethods: string[]; // 存储就餐方式 DictData ID 列表
  page: number;
}

type FilterAction =
  | { type: 'SET_KEYWORD'; payload: string }
  | { type: 'SET_SORT'; payload: SortOption }
  | { type: 'SET_CATEGORY'; payload: string }
  | { type: 'SET_AREA'; payload: string }
  | { type: 'SET_DINING'; payload: string[] }
  | { type: 'NEXT_PAGE' }
  | { type: 'RESET_PAGE' }
  | { type: 'RESET_ALL' };

const initialFilter: FilterState = {
  keyword: '', sort: 'favorite_count', category: '', area: '', diningMethods: [], page: 1,
};

function filterReducer(state: FilterState, action: FilterAction): FilterState {
  switch (action.type) {
    case 'SET_KEYWORD':  return { ...state, keyword: action.payload, page: 1 };
    case 'SET_SORT':     return { ...state, sort: action.payload, page: 1 };
    case 'SET_CATEGORY': return { ...state, category: action.payload, page: 1 };
    case 'SET_AREA':     return { ...state, area: action.payload, page: 1 };
    case 'SET_DINING':   return { ...state, diningMethods: action.payload, page: 1 };
    case 'NEXT_PAGE':    return { ...state, page: state.page + 1 };
    case 'RESET_PAGE':   return { ...state, page: 1 };
    case 'RESET_ALL':    return { ...initialFilter };
  }
}

export function HomePage() {
  const navigate = useNavigate();
  const [filter, dispatch] = useReducer(filterReducer, initialFilter);
  const [shops, setShops] = useState<ShopCardData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [isError, setIsError] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  // filterOptions: 下拉选项的显示名列表
  const [filterOptions, setFilterOptions] = useState<Record<string, string[]>>({});
  // optionsMap: 名称→ID 映射，用于将选中名称转为 ID
  const [optionsMap, setOptionsMap] = useState<Record<string, Record<string, number>>>({});

  useEffect(() => {
    // 从配置动态获取所有字典选项（同时获取 ID 和名称）
    filterConfigs.forEach(async (cfg) => {
      const items = await fetchDictDataWithId(cfg.dictType);
      setFilterOptions((prev) => ({ ...prev, [cfg.dictType]: (items ?? []).map((i) => i.name) }));
      setOptionsMap((prev) => {
        const map: Record<string, number> = {};
        (items ?? []).forEach((i) => { map[i.name] = i.id; });
        return { ...prev, [cfg.dictType]: map };
      });
    });
  }, []);

  const debouncedKeyword = useDebounce(filter.keyword, 300);

  useEffect(() => {
    const isLoadMore = filter.page > 1;
    if (isLoadMore) {
      setIsLoadingMore(true);
    } else {
      setIsLoading(true);
    }
    setIsError(false);

    // 将筛选名称转换为 ID（category_ids / district_ids 期望的是 ID 列表）
    const categoryIds = filter.category ? [parseInt(filter.category, 10)] : undefined;
    const districtIds = filter.area ? [parseInt(filter.area, 10)] : undefined;
    // diningMethods 存储的是 ID 字符串列表
    const diningMethodIds = filter.diningMethods.length > 0
      ? filter.diningMethods.map((id) => parseInt(id, 10))
      : undefined;

    const requestFilter = {
      keyword: debouncedKeyword || undefined,
      category_ids: categoryIds,
      district_ids: districtIds,
      dining_method_ids: diningMethodIds,
      sort_by: filter.sort,
      sort_order: 'desc',
      page: filter.page,
      page_size: 20,
    };

    fetchShops(requestFilter)
      .then((result: any) => {
        const items: ShopCardData[] = result.items || [];
        if (isLoadMore) {
          setShops((prev) => [...prev, ...items]);
        } else {
          setShops(items);
        }
        // 当返回的条目数小于 page_size 时，说明已无更多数据
        setHasMore(items.length >= 20);
      })
      .catch(() => {
        setIsError(true);
      })
      .finally(() => {
        setIsLoading(false);
        setIsLoadingMore(false);
      });
  }, [debouncedKeyword, filter.sort, filter.category, filter.area, filter.diningMethods, filter.page]);

  const handleLoadMore = useCallback(() => {
    if (!isLoadingMore && hasMore) {
      dispatch({ type: 'NEXT_PAGE' });
    }
  }, [isLoadingMore, hasMore]);

  const sentinelRef = useInfiniteScroll(handleLoadMore, hasMore && !isLoading && !isLoadingMore);

  const handleRetry = useCallback(() => {
    setIsLoading(true);
    setIsError(false);
    const categoryIds = filter.category ? [parseInt(filter.category, 10)] : undefined;
    const districtIds = filter.area ? [parseInt(filter.area, 10)] : undefined;
    const diningMethodIds = filter.diningMethods.length > 0
      ? filter.diningMethods.map((id) => parseInt(id, 10))
      : undefined;

    const requestFilter = {
      keyword: debouncedKeyword || undefined,
      category_ids: categoryIds,
      district_ids: districtIds,
      dining_method_ids: diningMethodIds,
      sort_by: filter.sort,
      sort_order: 'desc',
      page: 1,
      page_size: 20,
    };
    fetchShops(requestFilter)
      .then((result: any) => {
        const items: ShopCardData[] = result.items || [];
        setShops(items);
        setHasMore(items.length >= 20);
      })
      .catch(() => {
        setIsError(true);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [filter, debouncedKeyword]);

  return (
    <div className="space-y-6">
      <AnnouncementBanner />

      <div className="rounded-xl shadow-[0_2px_12px_rgba(0,0,0,0.04)] border border-gray-100/80">
        {/* Upper layer: white bg, search fills width */}
        <div className="bg-white px-5 py-4 rounded-t-xl">
          <SearchBar
            value={filter.keyword}
            onChange={(v) => dispatch({ type: 'SET_KEYWORD', payload: v })}
            onSearch={() => {}}
          />
        </div>
        {/* Lower layer: white bg with top separator */}
        <div className="bg-white px-5 py-3 rounded-b-xl border-t border-gray-100">
          <SortFilterBar
            sort={filter.sort as SortOption}
            filterConfigs={filterConfigs}
            filterOptions={filterOptions}
            filterValues={{
              '品类': filter.category,
              '区域': filter.area,
              '就餐方式': filter.diningMethods,
            }}
            onSortChange={(s: any) => dispatch({ type: 'SET_SORT' as any, payload: s })}
            onFilterChange={(dictType, value) => {
              const map: Record<string, string> = {
                '品类': 'SET_CATEGORY',
                '区域': 'SET_AREA',
                '就餐方式': 'SET_DINING',
              };
              const actionType = map[dictType];
              if (actionType === 'SET_DINING') {
                dispatch({ type: 'SET_DINING', payload: value as string[] });
              } else if (actionType) {
                dispatch({ type: actionType as any, payload: value as string });
              }
            }}
            onClear={() => dispatch({ type: 'RESET_ALL' })}
          />
        </div>
      </div>

      {isLoading && <ShopCardGridSkeleton count={8} />}

      {isError && !isLoading && <ErrorState onRetry={handleRetry} />}

      {!isLoading && !isError && shops.length === 0 && (
        <EmptyState onAction={() => window.location.href = '/upload-shop'} />
      )}

      {!isLoading && !isError && shops.length > 0 && (
        <>
          <ShopList shops={shops} onShopClick={(id) => navigate(`/shop/${id}`)} />
          {isLoadingMore && (
            <div className="text-center py-4 text-gray-400 text-sm">加载中...</div>
          )}
          <div ref={sentinelRef} className="h-4" />
          {!hasMore && shops.length > 0 && (
            <div className="text-center py-4 text-gray-400 text-sm">— 已加载全部店铺 —</div>
          )}
        </>
      )}
    </div>
  );
}