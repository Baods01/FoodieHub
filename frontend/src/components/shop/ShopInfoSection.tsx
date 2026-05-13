interface ShopInfoSectionProps {
  name: string;
  category: string;
  area: string;
  description?: string;
}

export function ShopInfoSection({ name, category, area, description }: ShopInfoSectionProps) {
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
        </div>

        {description && (
          <p className="text-sm text-gray-500 mt-2 leading-relaxed">{description}</p>
        )}
      </div>

      {/* Right: feedback button */}
      <button
        type="button"
        className="flex-shrink-0 ml-4 text-sm text-gray-400 hover:text-orange-500 transition-colors"
      >
        反馈
      </button>
    </div>
  );
}
