import { Heart } from 'lucide-react';

interface ShopInfoSectionProps {
  name: string;
  category: string;
  area: string;
  description?: string;
  diningMethods?: string[];
  isFavorited: boolean;
  favoriteCount: number;
  isLoggedIn: boolean;
  onToggleFavorite: () => void;
  onLoginPrompt: () => void;
}

export function ShopInfoSection({
  name,
  category,
  area,
  description,
  diningMethods,
  isFavorited,
  favoriteCount,
  isLoggedIn,
  onToggleFavorite,
  onLoginPrompt,
}: ShopInfoSectionProps) {
  const handleFavorite = () => {
    if (!isLoggedIn) {
      onLoginPrompt();
      return;
    }
    onToggleFavorite();
  };

  return (
    <div className="flex justify-between items-start">
      {/* Left: shop info */}
      <div className="flex-1 min-w-0">
        <h1 className="text-2xl font-bold truncate">{name}</h1>

        <div className="flex flex-wrap gap-2 mt-2">
          <span className="inline-block px-2 py-0.5 text-xs rounded border border-orange-300 text-orange-600">
            {category}
          </span>
          <span className="inline-block px-2 py-0.5 text-xs rounded border border-gray-300 text-gray-500">
            {area}
          </span>
          {diningMethods?.map((m) => (
            <span key={m} className="inline-block px-2 py-0.5 text-xs rounded border border-blue-200 text-blue-500">
              {m}
            </span>
          ))}
        </div>

        {description && (
          <p className="text-sm text-gray-500 mt-2 leading-relaxed">{description}</p>
        )}
      </div>

      {/* Right: actions */}
      <div className="flex-shrink-0 ml-4 flex items-start gap-3">
        {/* Favorite button */}
        <button
          type="button"
          onClick={handleFavorite}
          className={`flex items-center gap-1 text-sm transition-colors ${
            isFavorited
              ? 'text-red-500'
              : 'text-gray-400 hover:text-red-500'
          }`}
          title={isFavorited ? '取消收藏' : '收藏'}
        >
          <Heart
            size={18}
            fill={isFavorited ? 'currentColor' : 'none'}
            strokeWidth={isFavorited ? 0 : 2}
          />
          {favoriteCount > 0 && <span>{favoriteCount}</span>}
        </button>

        {/* Feedback button */}
        <button
          type="button"
          className="text-sm text-gray-400 hover:text-orange-500 transition-colors"
        >
          反馈
        </button>
      </div>
    </div>
  );
}
