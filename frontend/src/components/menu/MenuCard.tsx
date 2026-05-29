import type { MenuItem } from '../../types/shop';

interface MenuCardProps {
  item: MenuItem;
  onClick: (item: MenuItem) => void;
}

export function MenuCard({ item, onClick }: MenuCardProps) {
  return (
    <div
      className="w-36 flex-shrink-0 bg-white rounded-lg border border-gray-200 overflow-hidden cursor-pointer hover:shadow-md transition-shadow"
      onClick={() => onClick(item)}
    >
      <div className="px-3 py-2.5">
        <p className="text-sm font-medium text-gray-800 truncate">{item.name}</p>
        {item.price != null && (
          <p className="text-xs text-orange-500 mt-0.5">¥{item.price.toFixed(2)}</p>
        )}
      </div>
    </div>
  );
}
