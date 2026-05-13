import { useState } from 'react';
import { Image } from 'lucide-react';
import { AlbumLightbox } from './AlbumLightbox';

interface AlbumSectionProps {
  images: string[];
  isLoggedIn: boolean;
  onUpload: () => void;
}

const PER_PAGE = 9;

export function AlbumSection({ images, isLoggedIn, onUpload }: AlbumSectionProps) {
  const [page, setPage] = useState(0);
  const [lightboxIndex, setLightboxIndex] = useState<number | null>(null);

  if (images.length === 0) return null;

  const totalPages = Math.ceil(images.length / PER_PAGE);
  const start = page * PER_PAGE;
  const pageImages = images.slice(start, start + PER_PAGE);
  const hasPrev = page > 0;
  const hasNext = page < totalPages - 1;

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
      <div className="relative">
        <div className="grid grid-cols-3 gap-2">
          {pageImages.map((src, i) => (
            <button
              key={start + i}
              type="button"
              onClick={() => setLightboxIndex(start + i)}
              className="aspect-square rounded-lg overflow-hidden bg-gray-100 focus:outline-none focus:ring-2 focus:ring-orange-400"
            >
              <img
                src={src}
                alt={`相册图片 ${start + i + 1}`}
                className="w-full h-full object-cover hover:scale-105 transition-transform duration-200"
              />
            </button>
          ))}
        </div>

        {/* Pagination arrows */}
        {totalPages > 1 && (
          <>
            {hasPrev && (
              <button
                type="button"
                onClick={() => setPage((p) => p - 1)}
                className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-3 w-8 h-8 rounded-full bg-white shadow-md flex items-center justify-center hover:bg-gray-50 transition-colors"
              >
                <svg className="w-4 h-4 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
                </svg>
              </button>
            )}
            {hasNext && (
              <button
                type="button"
                onClick={() => setPage((p) => p + 1)}
                className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-3 w-8 h-8 rounded-full bg-white shadow-md flex items-center justify-center hover:bg-gray-50 transition-colors"
              >
                <svg className="w-4 h-4 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            )}
          </>
        )}
      </div>

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
