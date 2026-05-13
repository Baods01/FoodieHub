export function ShopDetailSkeleton() {
  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-12 animate-pulse">
      {/* Carousel skeleton */}
      <div className="h-80 max-md:h-52 bg-gray-200 rounded-lg" />

      {/* Info + tags skeleton */}
      <div className="flex justify-between items-start">
        <div className="flex-1 min-w-0 space-y-3">
          <div className="h-7 w-48 bg-gray-200 rounded" />
          <div className="flex gap-2">
            <div className="h-5 w-12 bg-gray-200 rounded" />
            <div className="h-5 w-16 bg-gray-200 rounded" />
          </div>
          <div className="h-4 w-full bg-gray-200 rounded" />
          <div className="h-4 w-3/4 bg-gray-200 rounded" />
        </div>
        <div className="h-5 w-10 bg-gray-200 rounded flex-shrink-0 ml-4" />
      </div>

      {/* Rating section skeleton */}
      <div className="flex items-center justify-center gap-2 py-4">
        <div className="h-4 w-16 bg-gray-200 rounded" />
        <div className="flex gap-1">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-5 w-5 bg-gray-200 rounded" />
          ))}
        </div>
      </div>
      <div className="flex items-center gap-5">
        <div className="flex flex-col items-center gap-1">
          <div className="h-7 w-7 bg-gray-200 rounded" />
          <div className="h-8 w-10 bg-gray-200 rounded" />
        </div>
        <div className="flex-1 space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="flex items-center gap-2">
              <div className="h-3 w-6 bg-gray-200 rounded" />
              <div className="flex-1 h-2 bg-gray-200 rounded-full" />
            </div>
          ))}
          <div className="h-4 w-24 bg-gray-200 rounded mt-2" />
        </div>
      </div>

      {/* Comment skeletons (3 items) */}
      <div className="space-y-4 pt-2">
        <div className="h-5 w-12 bg-gray-200 rounded" />
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="py-4 border-t border-gray-100">
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 bg-gray-200 rounded-full" />
              <div className="h-4 w-24 bg-gray-200 rounded" />
              <div className="h-3 w-12 bg-gray-100 rounded" />
            </div>
            <div className="mt-3 space-y-2">
              <div className="h-3 w-full bg-gray-200 rounded" />
              <div className="h-3 w-3/4 bg-gray-200 rounded" />
            </div>
            <div className="mt-3 flex items-center gap-4">
              <div className="h-4 w-12 bg-gray-200 rounded" />
              <div className="h-4 w-12 bg-gray-200 rounded" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
