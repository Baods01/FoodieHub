import { useState, useEffect, useCallback, Fragment } from 'react';
import { Clock, Trash2 } from 'lucide-react';
import { Dialog, Transition } from '@headlessui/react';
import { fetchHistory, removeHistory, clearHistory } from '../api/history';
import type { HistoryItem } from '../types/history';
import HistoryCard from '../components/shop/HistoryCard';
import { ErrorState } from '../components/ui/ErrorState';
import SectionCard from '../components/ui/SectionCard';

export default function HistoryPage() {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [clearOpen, setClearOpen] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    setError(false);
    fetchHistory()
      .then(setItems)
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { load(); }, [load]);

  // 移除单条（乐观更新）
  const handleRemove = (id: number) => {
    const prev = items;
    setItems((cur) => cur.filter((i) => i.id !== id));
    removeHistory(id).catch(() => {
      setItems(prev);
    });
  };

  // 清空全部（乐观更新）
  const handleClear = () => {
    setClearOpen(false);
    const prev = items;
    setItems([]);
    clearHistory().catch(() => {
      setItems(prev);
    });
  };

  return (
    <div className="max-w-4xl mx-auto py-8 space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Clock size={24} className="text-blue-500" />
          <h1 className="text-xl font-bold">浏览历史</h1>
        </div>
        <div className="flex items-center gap-3">
          {!loading && items.length > 0 && (
            <button
              type="button"
              onClick={() => setClearOpen(true)}
              className="flex items-center gap-1 text-sm text-gray-400 hover:text-red-500 transition-colors"
            >
              <Trash2 size={14} />
              清空记录
            </button>
          )}
          {!loading && (
            <span className="text-sm text-gray-400">共 {items.length} 条</span>
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
                  <div className="h-3 w-10 bg-gray-100 rounded" />
                  <div className="h-3 w-24 bg-gray-100 rounded" />
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : items.length === 0 ? (
        <SectionCard>
          <div className="py-12 text-center">
            <Clock size={48} className="text-gray-200 mx-auto" />
            <p className="text-gray-500 mt-3">暂无浏览记录</p>
            <a
              href="/"
              className="inline-block mt-3 text-sm text-orange-500 hover:text-orange-600"
            >
              去看看 &rarr;
            </a>
          </div>
        </SectionCard>
      ) : (
        <div className="space-y-4">
          {items.map((item) => (
            <HistoryCard key={item.id} item={item} onRemove={handleRemove} />
          ))}
        </div>
      )}

      {/* Clear confirmation dialog */}
      <Transition show={clearOpen} as={Fragment}>
        <Dialog as="div" className="relative z-50" onClose={() => setClearOpen(false)}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-200"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-150"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black/30" />
          </Transition.Child>

          <div className="fixed inset-0 flex items-center justify-center p-4">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-200"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-150"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-sm bg-white rounded-2xl p-6 shadow-xl">
                <Dialog.Title className="text-base font-bold text-gray-800">
                  清空浏览记录
                </Dialog.Title>
                <p className="text-sm text-gray-500 mt-2">
                  确定清空所有浏览记录？此操作不可撤销。
                </p>
                <div className="flex justify-end gap-3 mt-6">
                  <button
                    type="button"
                    onClick={() => setClearOpen(false)}
                    className="px-4 py-2 rounded-xl border border-gray-200 text-sm text-gray-600 hover:bg-gray-50 transition-colors"
                  >
                    取消
                  </button>
                  <button
                    type="button"
                    onClick={handleClear}
                    className="px-4 py-2 rounded-xl bg-red-500 text-sm text-white hover:bg-red-600 transition-colors"
                  >
                    确定清空
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
