import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Star, Eye, MessageSquare, Trash2 } from 'lucide-react';
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
      onClick={() => navigate(`/shop/${item.id}`)}
    >
      {/* Left: cover image */}
      <div className="w-40 h-28 flex-shrink-0 bg-gray-100 overflow-hidden">
        {item.coverImage && !imgError ? (
          <img
            src={item.coverImage}
            alt={item.name}
            className="w-full h-full object-cover"
            onError={() => setImgError(true)}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <span className="text-gray-400 text-xs">暂无图片</span>
          </div>
        )}
      </div>

      {/* Right: info */}
      <div className="flex-1 min-w-0 px-4 py-3 flex flex-col justify-between">
        {/* Top row: name + rating */}
        <div className="flex justify-between items-start">
          <h3 className="text-base font-bold text-gray-800 truncate">{item.name}</h3>
          <span className="flex items-center gap-1 text-sm text-gray-400 flex-shrink-0 ml-2">
            <Star size={14} className="text-yellow-400 fill-yellow-400" />
            {item.rating}
          </span>
        </div>

        {/* Tags row */}
        <div className="flex items-center gap-2 mt-1">
          <span className="px-2 py-0.5 text-xs rounded border border-orange-300 text-orange-600">
            {item.category}
          </span>
          <span className="px-2 py-0.5 text-xs rounded border border-gray-300 text-gray-500">
            {item.area}
          </span>
        </div>

        {/* Stats row */}
        <div className="flex items-center gap-3 text-xs text-gray-400 mt-1.5">
          <span className="flex items-center gap-1">
            <MessageSquare size={12} /> {item.reviewCount}
          </span>
          <span>·</span>
          <span className="flex items-center gap-1">
            <Eye size={12} /> {item.viewCount}
          </span>
        </div>

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
            浏览于 {relativeTime(item.viewedAt)}
          </span>
        </div>
      </div>
    </div>
  );
}
