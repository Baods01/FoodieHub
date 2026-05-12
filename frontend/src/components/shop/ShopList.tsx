import type { ShopCardData } from '../../types/shop';
import { ShopCard } from './ShopCard';

interface ShopListProps {
  shops: ShopCardData[];
  onShopClick?: (id: number) => void;
}

export function ShopList({ shops, onShopClick }: ShopListProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {shops.map((shop) => (
        <ShopCard key={shop.id} shop={shop} onClick={onShopClick} />
      ))}
    </div>
  );
}
