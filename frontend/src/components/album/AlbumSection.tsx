import { useState } from 'react';
import { Image } from 'lucide-react';
import { AlbumLightbox } from './AlbumLightbox';

interface AlbumSectionProps {
  images: string[];
  isLoggedIn: boolean;
  onUpload: () => void;
  maxCount?: number;
  onViewAll?: () => void;
}

export function AlbumSection({ images, isLoggedIn, onUpload, maxCount = 6, onViewAll }: AlbumSectionProps) {
  const [lightboxIndex, setLightboxIndex] = useState<number | null>(null);

  if (images.length === 0) return null;

  const previewImages = onViewAll ? images.slice(0, maxCount) : images;

  return (
    <section>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold">店铺相册</h2>
        {isLoggedIn && (
          <button
            type="button"
            onClick={onUpload}
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg border border-orange-400 text-orange-500 text-sm hover:bg-orange-50 transition-colors"
          >
            <Image size={14} />
            <span>上传图片</span>
          </button>
        )}
      </div>

      {/* Grid */}
      <div className="grid grid-cols-3 gap-2">
        {previewImages.map((src, i) => (
          <button
            key={i}
            type="button"
            onClick={() => setLightboxIndex(i)}
            className="aspect-square rounded-lg overflow-hidden bg-gray-100 focus:outline-none focus:ring-2 focus:ring-orange-400"
          >
            <img
              src={src}
              alt={`相册图片 ${i + 1}`}
              className="w-full h-full object-cover hover:scale-105 transition-transform duration-200"
            />
          </button>
        ))}
      </div>

      {/* View all (preview mode) */}
      {onViewAll && images.length > maxCount && (
        <div className="text-center mt-3">
          <button
            type="button"
            onClick={onViewAll}
            className="rounded-lg border border-orange-200 px-5 py-1.5 text-sm text-orange-500 hover:bg-orange-50 transition-colors"
          >
            查看全部 ({images.length}) &gt;
          </button>
        </div>
      )}

      {/* Lightbox */}
      {lightboxIndex !== null && (
        <AlbumLightbox
          images={images}
          initialIndex={lightboxIndex}
          onClose={() => setLightboxIndex(null)}
        />
      )}
    </section>
  );
}
