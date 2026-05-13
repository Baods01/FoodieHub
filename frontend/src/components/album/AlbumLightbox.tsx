import { useState, useEffect, useCallback } from 'react';
import { Dialog, DialogPanel, DialogBackdrop } from '@headlessui/react';
import { X, ChevronLeft, ChevronRight } from 'lucide-react';

interface AlbumLightboxProps {
  images: string[];
  initialIndex: number;
  onClose: () => void;
}

export function AlbumLightbox({ images, initialIndex, onClose }: AlbumLightboxProps) {
  const [currentIndex, setCurrentIndex] = useState(initialIndex);

  const goPrev = useCallback(() => {
    setCurrentIndex((i) => (i > 0 ? i - 1 : images.length - 1));
  }, [images.length]);

  const goNext = useCallback(() => {
    setCurrentIndex((i) => (i < images.length - 1 ? i + 1 : 0));
  }, [images.length]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowLeft') goPrev();
      if (e.key === 'ArrowRight') goNext();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [goPrev, goNext]);

  const total = images.length;

  return (
    <Dialog open onClose={onClose} className="relative z-50">
      <DialogBackdrop className="fixed inset-0 bg-black/90" />

      <div className="fixed inset-0 flex items-center justify-center">
        <DialogPanel className="relative w-full h-full flex items-center justify-center">
          {/* Close button */}
          <button
            type="button"
            onClick={onClose}
            className="absolute top-4 right-4 z-10 p-2 rounded-full bg-black/30 text-white hover:bg-black/50 transition-colors"
          >
            <X size={24} />
          </button>

          {/* Previous button */}
          {total > 1 && (
            <button
              type="button"
              onClick={goPrev}
              className="absolute left-4 z-10 p-2 rounded-full bg-black/30 text-white/70 hover:bg-black/50 hover:text-white transition-colors"
            >
              <ChevronLeft size={32} />
            </button>
          )}

          {/* Image */}
          <div className="flex items-center justify-center w-full h-full px-16 py-12">
            <img
              src={images[currentIndex]}
              alt={`相册图片 ${currentIndex + 1}`}
              className="max-h-[90vh] max-w-[90vw] object-contain select-none"
            />
          </div>

          {/* Next button */}
          {total > 1 && (
            <button
              type="button"
              onClick={goNext}
              className="absolute right-4 z-10 p-2 rounded-full bg-black/30 text-white/70 hover:bg-black/50 hover:text-white transition-colors"
            >
              <ChevronRight size={32} />
            </button>
          )}

          {/* Counter */}
          {total > 1 && (
            <div className="absolute bottom-6 left-1/2 -translate-x-1/2 px-4 py-1.5 rounded-full bg-black/50 text-white text-sm">
              {currentIndex + 1} / {total}
            </div>
          )}
        </DialogPanel>
      </div>
    </Dialog>
  );
}
