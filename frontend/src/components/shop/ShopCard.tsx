import { useState } from 'react';
import { Star, Eye } from 'lucide-react';
import type { ShopCardData } from '../../types/shop';

interface ShopCardProps {
  shop: ShopCardData;
  onClick?: (id: number) => void;
}

export function ShopCard({ shop, onClick }: ShopCardProps) {
  const [imgError, setImgError] = useState(false);

  return (
    <div
      className="bg-white rounded-lg border border-gray-100 shadow-[0_2px_8px_rgba(0,0,0,0.04)] cursor-pointer transition-all duration-200 hover:shadow-[0_8px_24px_rgba(255,126,58,0.12)] hover:-translate-y-0.5 hover:border-orange-200"
      onClick={() => onClick?.(shop.id)}
    >
      {/* Cover image */}
      <div className="aspect-[16/9] rounded-t-lg overflow-hidden">
        {shop.coverImage && !imgError ? (
          <img
            src={shop.coverImage}
            alt={shop.name}
            className="w-full h-full object-cover"
            onError={() => setImgError(true)}
          />
        ) : (
          <div className="w-full h-full bg-gray-200 flex items-center justify-center">
            <span className="text-gray-400 text-sm">暂无图片</span>
          </div>
        )}
      </div>

      {/* Info area */}
      <div className="p-3">
        {/* Name */}
        <div className="text-base font-bold truncate">{shop.name}</div>

        {/* Tags */}
        <div className="flex gap-2 mt-1">
          <span className="px-2 py-0.5 text-xs rounded border border-orange-300 text-orange-600">
            {shop.category}
          </span>
          <span className="px-2 py-0.5 text-xs rounded border border-gray-300 text-gray-500">
            {shop.area}
          </span>
        </div>

        {/* Rating & views */}
        <div className="flex justify-between mt-2 text-sm text-gray-400">
          <span className="flex items-center gap-1">
            <Star size={14} />
            {shop.rating}
          </span>
          <span className="flex items-center gap-1">
            <Eye size={14} />
            {shop.viewCount}
          </span>
        </div>
      </div>
    </div>
  );
}
