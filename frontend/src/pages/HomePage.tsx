import { useReducer, useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDebounce } from '../hooks/useDebounce';
import { useInfiniteScroll } from '../hooks/useInfiniteScroll';
import { fetchShops, fetchAnnouncement } from '../api/shops';
import { fetchDictData } from '../api/dictionary';
import type { ShopCardData, ShopFilter, SortOption } from '../types/shop';
import { AnnouncementBanner } from '../components/shop/AnnouncementBanner';
import SearchBar from '../components/shop/SearchBar';
import SortFilterBar from '../components/shop/SortFilterBar';
import { ShopList } from '../components/shop/ShopList';
import { ShopCardGridSkeleton } from '../components/shop/ShopCardSkeleton';
import { EmptyState } from '../components/ui/EmptyState';
import { ErrorState } from '../components/ui/ErrorState';

interface FilterState extends ShopFilter {}

type FilterAction =
  | { type: 'SET_KEYWORD'; payload: string }
  | { type: 'SET_SORT'; payload: SortOption }
  | { type: 'SET_CATEGORY'; payload: string }
  | { type: 'SET_AREA'; payload: string }
  | { type: 'NEXT_PAGE' }
  | { type: 'RESET_PAGE' }
  | { type: 'RESET_ALL' };

const initialFilter: FilterState = {
  keyword: '', sort: 'favorites', category: '', area: '', page: 1,
};

function filterReducer(state: FilterState, action: FilterAction): FilterState {
  switch (action.type) {
    case 'SET_KEYWORD':  return { ...state, keyword: action.payload, page: 1 };
    case 'SET_SORT':     return { ...state, sort: action.payload, page: 1 };
    case 'SET_CATEGORY': return { ...state, category: action.payload, page: 1 };
    case 'SET_AREA':     return { ...state, area: action.payload, page: 1 };
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
  const [categories, setCategories] = useState<string[]>([]);
  const [areas, setAreas] = useState<string[]>([]);
  const [announcement, setAnnouncement] = useState<{ title: string; content: string } | null>(null);

  useEffect(() => {
    fetchDictData('category').then((items) => setCategories(items.map((i) => i.name)));
    fetchDictData('location_type').then((items) => setAreas(items.map((i) => i.name)));
    fetchAnnouncement().then(setAnnouncement);
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

    const currentFilter = { ...filter, keyword: debouncedKeyword };

    fetchShops(currentFilter)
      .then((result) => {
        if (isLoadMore) {
          setShops((prev) => [...prev, ...result.data]);
        } else {
          setShops(result.data);
        }
        setHasMore(result.hasMore);
      })
      .catch(() => {
        setIsError(true);
      })
      .finally(() => {
        setIsLoading(false);
        setIsLoadingMore(false);
      });
  }, [debouncedKeyword, filter.sort, filter.category, filter.area, filter.page]);

  const handleLoadMore = useCallback(() => {
    if (!isLoadingMore && hasMore) {
      dispatch({ type: 'NEXT_PAGE' });
    }
  }, [isLoadingMore, hasMore]);

  const sentinelRef = useInfiniteScroll(handleLoadMore, hasMore && !isLoading && !isLoadingMore);

  const handleRetry = useCallback(() => {
    setIsLoading(true);
    setIsError(false);
    const currentFilter = { ...filter, keyword: debouncedKeyword };
    fetchShops(currentFilter)
      .then((result) => {
        setShops(result.data);
        setHasMore(result.hasMore);
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
      <AnnouncementBanner announcement={announcement} />

      <div className="rounded-xl shadow-[0_2px_12px_rgba(0,0,0,0.04)] border border-gray-100/80">
        {/* Upper layer: white bg, search fills width */}
        <div className="bg-white px-5 py-4 rounded-t-xl">
          <SearchBar
            value={filter.keyword}
            onChange={(v) => dispatch({ type: 'SET_KEYWORD', payload: v })}
            onSearch={() => {}}
          />
        </div>
        {/* Lower layer: warm light-orange bg, left-aligned filters */}
        <div className="bg-[#FFF7F0] px-5 py-3 rounded-b-xl">
          <SortFilterBar
            sort={filter.sort}
            category={filter.category}
            area={filter.area}
            categories={categories}
            areas={areas}
            onSortChange={(s) => dispatch({ type: 'SET_SORT', payload: s })}
            onCategoryChange={(c) => dispatch({ type: 'SET_CATEGORY', payload: c })}
            onAreaChange={(a) => dispatch({ type: 'SET_AREA', payload: a })}
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
