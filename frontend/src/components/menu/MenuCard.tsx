import type { MenuItem } from '../../types/shop';

interface MenuCardProps {
  item: MenuItem;
  onClick: (item: MenuItem) => void;
}

export function MenuCard({ item, onClick }: MenuCardProps) {
  return (
    <div
      className="w-32 flex-shrink-0 bg-white rounded-lg border border-gray-200 overflow-hidden cursor-pointer hover:shadow-md transition-shadow"
      onClick={() => onClick(item)}
    >
      {/* Image */}
      <div className="w-full h-24 overflow-hidden">
        {item.image ? (
          <img
            src={item.image}
            alt={item.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full bg-gray-100 flex items-center justify-center">
            <span className="text-gray-400 text-xs">暂无图片</span>
          </div>
        )}
      </div>

      {/* Name */}
      <div className="px-2 py-1.5">
        <p className="text-sm truncate text-gray-800">{item.name}</p>
      </div>
    </div>
  );
}
