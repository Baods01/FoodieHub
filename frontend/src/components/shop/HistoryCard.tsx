import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Trash2 } from 'lucide-react';
import type { HistoryItem } from '../../types/history';

interface HistoryCardProps {
  item: HistoryItem;
  onRemove: (id: number) => void;
}

/** 相对时间 */
function relativeTime(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const min = Math.floor(diffMs / 60000);
  if (min < 1) return '刚刚';
  if (min < 60) return `${min}分钟前`;
  const hour = Math.floor(min / 60);
  if (hour < 24) return `${hour}小时前`;
  const day = Math.floor(hour / 24);
  if (day < 30) return `${day}天前`;
  return `${Math.floor(day / 30)}个月前`;
}

export default function HistoryCard({ item, onRemove }: HistoryCardProps) {
  const navigate = useNavigate();
  const [imgError, setImgError] = useState(false);

  const handleRemove = (e: React.MouseEvent) => {
    e.stopPropagation();
    onRemove(item.id);
  };

  return (
    <div
      className="bg-white rounded-xl shadow-[0_2px_8px_rgba(0,0,0,0.04)] border border-gray-100 flex flex-row overflow-hidden cursor-pointer transition-all duration-200 hover:shadow-[0_4px_16px_rgba(0,0,0,0.08)] hover:-translate-y-0.5"
      onClick={() => navigate(`/shop/${item.shop_id}`)}
    >
      {/* Left: cover image */}
      <div className="w-40 h-28 flex-shrink-0 bg-gray-100 overflow-hidden">
        {item.shop_cover && !imgError ? (
          <img
            src={item.shop_cover}
            alt={item.shop_name}
            className="w-full h-full object-cover"
            onError={() => setImgError(true)}
          />
        ) : (
          <img src="/nocover.png" alt="暂无封面" className="w-full h-full object-cover" />
        )}
      </div>

      {/* Right: info */}
      <div className="flex-1 min-w-0 px-4 py-3 flex flex-col justify-between">
        {/* Shop name */}
        <h3 className="text-base font-bold text-gray-800 truncate">{item.shop_name}</h3>

        {/* Bottom row: remove + time */}
        <div className="flex justify-between items-center mt-2">
          <button
            type="button"
            onClick={handleRemove}
            className="flex items-center gap-1 text-xs text-gray-400 hover:text-red-500 transition-colors"
          >
            <Trash2 size={12} />
            移除
          </button>
          <span className="text-xs text-gray-400">
            浏览于 {relativeTime(item.viewed_at)}
          </span>
        </div>
      </div>
    </div>
  );
}
