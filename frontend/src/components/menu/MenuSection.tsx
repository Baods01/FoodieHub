import { useState } from 'react';
import { Camera } from 'lucide-react';
import type { MenuItem } from '../../types/shop';
import { MenuCard } from './MenuCard';
import { MenuDetailModal } from './MenuDetailModal';

interface MenuSectionProps {
  items: MenuItem[];
  isLoggedIn: boolean;
  onUpload: () => void;
  maxCount?: number;
  onViewAll?: () => void;
}

export function MenuSection({ items, isLoggedIn, onUpload, maxCount = 6, onViewAll }: MenuSectionProps) {
  const [selectedItem, setSelectedItem] = useState<MenuItem | null>(null);

  return (
    <section>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold">菜单</h2>
        {isLoggedIn && (
          <button
            type="button"
            onClick={onUpload}
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg border border-orange-400 text-orange-500 text-sm hover:bg-orange-50 transition-colors"
          >
            <Camera size={14} />
            <span>上传菜单</span>
          </button>
        )}
      </div>

      {/* Items */}
      {items.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 bg-gray-50 rounded-lg">
          <Camera size={36} className="text-gray-300" />
          <p className="text-gray-400 text-sm mt-3">还没有菜单，快来上传吧</p>
        </div>
      ) : (
        <>
          <div className="overflow-x-auto">
            <div className="flex gap-3 pb-2">
              {items.slice(0, onViewAll ? maxCount : undefined).map((item) => (
                <MenuCard key={item.id} item={item} onClick={setSelectedItem} />
              ))}
            </div>
          </div>

          {/* View all (preview mode) */}
          {onViewAll && items.length > maxCount && (
            <div className="text-center mt-3">
              <button
                type="button"
                onClick={onViewAll}
                className="rounded-lg border border-orange-200 px-5 py-1.5 text-sm text-orange-500 hover:bg-orange-50 transition-colors"
              >
                查看全部菜单 ({items.length}) &gt;
              </button>
            </div>
          )}
        </>
      )}

      {/* Detail modal */}
      <MenuDetailModal item={selectedItem} onClose={() => setSelectedItem(null)} />
    </section>
  );
}
