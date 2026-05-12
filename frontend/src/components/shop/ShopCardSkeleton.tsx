import { Skeleton } from '../ui/Skeleton';

export function ShopCardSkeleton() {
  return (
    <div className="bg-white rounded-lg shadow-[0_2px_8px_rgba(0,0,0,0.06)]">
      <Skeleton className="aspect-[16/9] rounded-t-lg" />
      <div className="p-3">
        <Skeleton className="h-4 w-3/4 mt-3" />
        <Skeleton className="h-5 w-24 mt-2" />
        <Skeleton className="h-4 w-32 mt-2 mb-3" />
      </div>
    </div>
  );
}

export function ShopCardGridSkeleton({ count = 8 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <ShopCardSkeleton key={i} />
      ))}
    </div>
  );
}
