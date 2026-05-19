import { useState, useEffect, useCallback } from 'react';
import { Heart } from 'lucide-react';
import { fetchFavorites, removeFavorite, sortFavorites } from '../api/favorites';
import type { FavoriteItem } from '../types/favorite';
import FavoriteCard from '../components/shop/FavoriteCard';
import SortDropdown from '../components/shop/SortDropdown';
import { ErrorState } from '../components/ui/ErrorState';
import SectionCard from '../components/ui/SectionCard';

const sortOptions = [
  { value: 'time', label: '收藏时间' },
  { value: 'rating', label: '评分最高' },
  { value: 'name', label: '名称 A-Z' },
];

export default function FavoritesPage() {
  const [items, setItems] = useState<FavoriteItem[]>([]);
  const [sort, setSort] = useState('time');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    setError(false);
    fetchFavorites()
      .then(setItems)
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { load(); }, [load]);

  // 移除收藏（乐观更新）
  const handleRemove = (id: number) => {
    const prev = items;
    setItems((cur) => cur.filter((i) => i.id !== id));
    removeFavorite(id).catch(() => {
      setItems(prev);
    });
  };

  const sorted = sortFavorites(items, sort);

  return (
    <div className="max-w-4xl mx-auto py-8 space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Heart size={24} className="text-red-500" />
          <h1 className="text-xl font-bold">收藏夹</h1>
        </div>
        <div className="flex items-center gap-3">
          <SortDropdown value={sort} options={sortOptions} onChange={setSort} />
          {!loading && (
            <span className="text-sm text-gray-400">共 {items.length} 家</span>
          )}
        </div>
      </div>

      {/* Content */}
      {error && !loading ? (
        <ErrorState onRetry={load} />
      ) : loading ? (
        <div className="space-y-4 animate-pulse">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white rounded-xl border border-gray-100 flex flex-row overflow-hidden">
              <div className="w-40 h-28 bg-gray-200 flex-shrink-0" />
              <div className="flex-1 p-4 space-y-3">
                <div className="h-4 w-1/3 bg-gray-200 rounded" />
                <div className="flex gap-2">
                  <div className="h-5 w-12 bg-gray-200 rounded" />
                  <div className="h-5 w-16 bg-gray-200 rounded" />
                </div>
                <div className="h-3 w-1/2 bg-gray-100 rounded" />
                <div className="flex justify-between">
                  <div className="h-3 w-16 bg-gray-100 rounded" />
                  <div className="h-3 w-20 bg-gray-100 rounded" />
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : sorted.length === 0 ? (
        <SectionCard>
          <div className="py-12 text-center">
            <Heart size={48} className="text-gray-200 mx-auto" />
            <p className="text-gray-500 mt-3">还没有收藏任何店铺</p>
            <a
              href="/"
              className="inline-block mt-3 text-sm text-orange-500 hover:text-orange-600"
            >
              去发现美食 &rarr;
            </a>
          </div>
        </SectionCard>
      ) : (
        <div className="space-y-4">
          {sorted.map((item) => (
            <FavoriteCard key={item.id} item={item} onRemove={handleRemove} />
          ))}
        </div>
      )}
    </div>
  );
}
