import { useState, useEffect, useCallback } from 'react';

interface ShopCarouselProps {
  images: string[];
  interval?: number;
}

export function ShopCarousel({ images, interval = 3000 }: ShopCarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0);

  const goTo = useCallback((index: number) => {
    setCurrentIndex(index);
  }, []);

  // Reset index when the images array changes (e.g. navigating to a different shop)
  useEffect(() => {
    setCurrentIndex(0);
  }, [images]);

  // Auto-rotate when there are multiple images
  useEffect(() => {
    if (images.length <= 1) return;

    const timer = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % images.length);
    }, interval);

    return () => clearInterval(timer);
  }, [images.length, interval]);

  /* ---- No images ---- */
  if (images.length === 0) {
    return (
      <div className="h-80 max-md:h-52 bg-gray-100 flex items-center justify-center overflow-hidden rounded-lg">
        <span className="text-gray-400 text-sm">暂无店铺照片</span>
      </div>
    );
  }

  /* ---- Single image ---- */
  if (images.length === 1) {
    return (
      <div className="h-80 max-md:h-52 overflow-hidden rounded-lg">
        <img
          src={images[0]}
          alt="店铺照片"
          className="w-full h-full object-cover"
        />
      </div>
    );
  }

  /* ---- Multiple images (carousel) ---- */
  return (
    <div className="relative h-80 max-md:h-52 overflow-hidden rounded-lg">
      {/* Track */}
      <div
        className="flex h-full transition-transform duration-500 ease-in-out"
        style={{ transform: `translateX(-${currentIndex * 100}%)` }}
      >
        {images.map((src, i) => (
          <div key={i} className="min-w-full h-full flex-shrink-0">
            <img
              src={src}
              alt={`店铺照片 ${i + 1}`}
              className="w-full h-full object-cover"
            />
          </div>
        ))}
      </div>

      {/* Dot indicators */}
      <div className="absolute bottom-3 left-1/2 -translate-x-1/2 flex items-center gap-2">
        {images.map((_, i) => (
          <button
            key={i}
            type="button"
            onClick={() => goTo(i)}
            aria-label={`第 ${i + 1} 张照片`}
            className={`w-2 h-2 rounded-full transition-all duration-200 ${
              i === currentIndex ? 'bg-white' : 'bg-white/50'
            }`}
          />
        ))}
      </div>
    </div>
  );
}
