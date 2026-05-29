import { useState, useEffect, useCallback, Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { Heart } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { fetchFavorites, toggleFavorite } from '../api/favorites';
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
  const navigate = useNavigate();
  const isLoggedIn = useAuthStore((s) => s.isLoggedIn);
  const [items, setItems] = useState<FavoriteItem[]>([]);
  const [sort, setSort] = useState('time');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [confirmTarget, setConfirmTarget] = useState<{ id: number; shopId: number } | null>(null);

  // 登录守卫
  useEffect(() => {
    if (!isLoggedIn) {
      navigate('/login', { replace: true });
    }
  }, [isLoggedIn, navigate]);

  const load = useCallback(() => {
    setLoading(true);
    setError(false);
    fetchFavorites()
      .then((result: any) => setItems(result.items ?? []))
      .catch((err: any) => {
        console.error('加载收藏失败:', err?.response?.data || err);
        setError(true);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { load(); }, [load]);

  // 点击取消收藏 → 弹确认框
  const handleRemoveClick = (id: number, shopId: number) => {
    setConfirmTarget({ id, shopId });
  };

  // 确认取消收藏
  const handleConfirmRemove = () => {
    if (!confirmTarget) return;
    const { id, shopId } = confirmTarget;
    setConfirmTarget(null);
    setItems((cur) => cur.filter((i) => i.id !== id));
    toggleFavorite(shopId).catch(() => load());
  };

  // 排序
  const sorted = [...items].sort((a, b) => {
    if (sort === 'name') {
      return (a.shop_name ?? '').localeCompare(b.shop_name ?? '');
    }
    // 'time' 和 'rating' 都按时间倒序（rating 无数据字段）
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });

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
                <div className="flex justify-between">
                  <div className="h-3 w-12 bg-gray-100 rounded" />
                  <div className="h-3 w-24 bg-gray-100 rounded" />
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
            <FavoriteCard key={item.id} item={item} onRemove={handleRemoveClick} />
          ))}
        </div>
      )}

      {/* 取消收藏确认弹窗 */}
      <Transition show={confirmTarget !== null} as={Fragment}>
        <Dialog as="div" className="relative z-50" onClose={() => setConfirmTarget(null)}>
          <Transition.Child as={Fragment} enter="ease-out duration-200" enterFrom="opacity-0" enterTo="opacity-100" leave="ease-in duration-150" leaveFrom="opacity-100" leaveTo="opacity-0">
            <div className="fixed inset-0 bg-black/30" />
          </Transition.Child>
          <div className="fixed inset-0 flex items-center justify-center p-4">
            <Transition.Child as={Fragment} enter="ease-out duration-200" enterFrom="opacity-0 scale-95" enterTo="opacity-100 scale-100" leave="ease-in duration-150" leaveFrom="opacity-100 scale-100" leaveTo="opacity-0 scale-95">
              <Dialog.Panel className="w-full max-w-sm bg-white rounded-2xl p-6 shadow-xl">
                <Dialog.Title className="text-base font-bold text-gray-800">取消收藏</Dialog.Title>
                <p className="text-sm text-gray-500 mt-2">确定取消收藏该店铺？</p>
                <div className="flex justify-end gap-3 mt-6">
                  <button
                    type="button"
                    onClick={() => setConfirmTarget(null)}
                    className="px-4 py-2 rounded-xl border border-gray-200 text-sm text-gray-600 hover:bg-gray-50 transition-colors"
                  >
                    取消
                  </button>
                  <button
                    type="button"
                    onClick={handleConfirmRemove}
                    className="px-4 py-2 rounded-xl bg-red-500 text-sm text-white hover:bg-red-600 transition-colors"
                  >
                    确定取消
                  </button>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </Dialog>
      </Transition>
    </div>
  );
}
