import { Fragment, useState } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { X, Trash2, Loader2 } from 'lucide-react';
import { AlbumLightbox } from './AlbumLightbox';
import { deleteImage } from '../../api/images';
import type { ImageItem } from '../../types/shop';

interface AllAlbumModalProps {
  images: ImageItem[];
  isOpen: boolean;
  onClose: () => void;
  currentUserId?: number;
  isAdmin?: boolean;
  onDelete?: () => void;
}

export default function AllAlbumModal({
  images,
  isOpen,
  onClose,
  currentUserId,
  isAdmin,
  onDelete,
}: AllAlbumModalProps) {
  const [lightboxIndex, setLightboxIndex] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const canDelete = (img: ImageItem) => {
    return img.uploader_id === currentUserId || isAdmin;
  };

  const handleDelete = async (imageId: number) => {
    if (!window.confirm('确定要删除这张图片吗？')) return;
    setDeletingId(imageId);
    try {
      await deleteImage(imageId);
      onDelete?.();
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <>
      <Transition show={isOpen} as={Fragment}>
        <Dialog as="div" className="relative z-50" onClose={onClose}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-200"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-150"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black/40" />
          </Transition.Child>

          <div className="fixed inset-0 overflow-hidden">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-200"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-150"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="h-full w-full bg-white flex flex-col">
                {/* Header */}
                <div className="flex items-center justify-between px-4 h-14 border-b border-gray-200 flex-shrink-0">
                  <button
                    type="button"
                    onClick={onClose}
                    className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 transition-colors"
                  >
                    &larr; 返回
                  </button>
                  <Dialog.Title className="text-base font-semibold">
                    全部相册 ({images.length})
                  </Dialog.Title>
                  <button
                    type="button"
                    onClick={onClose}
                    className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <X size={20} />
                  </button>
                </div>

                {/* Content — grid layout */}
                <div className="flex-1 overflow-y-auto p-4">
                  {images.length === 0 ? (
                    <div className="flex items-center justify-center py-20 text-sm text-gray-400">
                      暂无图片
                    </div>
                  ) : (
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                      {images.map((img, i) => (
                        <div key={img.id} className="relative aspect-square rounded-lg overflow-hidden bg-gray-100 group">
                          <button
                            type="button"
                            onClick={() => setLightboxIndex(i)}
                            className="w-full h-full focus:outline-none focus:ring-2 focus:ring-orange-400"
                          >
                            <img
                              src={img.url}
                              alt={`相册图片 ${i + 1}`}
                              className="w-full h-full object-cover hover:scale-105 transition-transform duration-200"
                            />
                          </button>
                          {/* Delete button */}
                          {canDelete(img) && (
                            <button
                              type="button"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDelete(img.id);
                              }}
                              disabled={deletingId === img.id}
                              className="absolute top-1 right-1 p-1.5 rounded-md bg-black/50 text-white hover:bg-red-500 transition-colors opacity-0 group-hover:opacity-100 disabled:opacity-50"
                              title="删除图片"
                            >
                              {deletingId === img.id ? (
                                <Loader2 size={14} className="animate-spin" />
                              ) : (
                                <Trash2 size={14} />
                              )}
                            </button>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </Dialog>
      </Transition>

      {/* Lightbox */}
      {lightboxIndex !== null && (
        <AlbumLightbox
          images={images.map((img) => img.url)}
          initialIndex={lightboxIndex}
          onClose={() => setLightboxIndex(null)}
          deletable={canDelete(images[lightboxIndex])}
          onDelete={() => {
            const img = images[lightboxIndex];
            if (img) handleDelete(img.id);
            setLightboxIndex(null);
          }}
          isDeleting={deletingId === images[lightboxIndex]?.id}
        />
      )}
    </>
  );
}