import { useState, useRef } from 'react';
import { Image, Loader2 } from 'lucide-react';
import { AlbumLightbox } from './AlbumLightbox';
import { uploadImage } from '../../api/upload';

interface AlbumSectionProps {
  images: string[];
  shopId: number;
  isLoggedIn: boolean;
  onUpload?: () => void;
  maxCount?: number;
  onViewAll?: () => void;
}

export function AlbumSection({ images, shopId, isLoggedIn, onUpload, maxCount = 6, onViewAll }: AlbumSectionProps) {
  const [lightboxIndex, setLightboxIndex] = useState<number | null>(null);
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const previewImages = onViewAll ? images.slice(0, maxCount) : images;

  return (
    <section>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold pl-3 border-l-[3px] border-orange-400">店铺相册</h2>
        {isLoggedIn && (
          <>
            <input
              ref={fileRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              className="hidden"
              onChange={async (e) => {
                const file = e.target.files?.[0];
                if (!file) return;
                setUploading(true);
                try {
                  await uploadImage(file, 'shop', shopId);
                  onUpload?.();
                } finally {
                  setUploading(false);
                  if (fileRef.current) fileRef.current.value = '';
                }
              }}
            />
            <button
              type="button"
              onClick={() => fileRef.current?.click()}
              disabled={uploading}
              className="flex items-center gap-1 px-3 py-1.5 rounded-lg border border-orange-400 text-orange-500 text-sm hover:bg-orange-50 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {uploading ? <Loader2 size={14} className="animate-spin" /> : <Image size={14} />}
              <span>{uploading ? '上传中...' : '上传图片'}</span>
            </button>
          </>
        )}
      </div>

      {/* Empty state */}
      {images.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 bg-gray-50 rounded-lg">
          <Image size={36} className="text-gray-300" />
          <p className="text-gray-400 text-sm mt-3">暂无图片</p>
        </div>
      ) : (
        /* Grid */
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
      )}

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
