import { Dialog, DialogPanel, DialogBackdrop } from '@headlessui/react';
import { X } from 'lucide-react';
import type { MenuItem } from '../../types/shop';

interface MenuDetailModalProps {
  item: MenuItem | null;
  onClose: () => void;
}

export function MenuDetailModal({ item, onClose }: MenuDetailModalProps) {
  if (!item) return null;

  return (
    <Dialog open={!!item} onClose={onClose} className="relative z-50">
      <DialogBackdrop className="fixed inset-0 bg-black/50" />

      <div className="fixed inset-0 flex items-center justify-center p-4">
        <DialogPanel className="bg-white rounded-xl max-w-md w-full max-h-[90vh] overflow-y-auto shadow-xl">
          {/* Close button */}
          <div className="flex justify-end p-2">
            <button
              type="button"
              onClick={onClose}
              className="p-1 rounded-full hover:bg-gray-100 transition-colors"
            >
              <X size={20} className="text-gray-500" />
            </button>
          </div>

          {/* Image */}
          <div className="px-4">
            <div className="w-full aspect-video rounded-lg overflow-hidden bg-gray-100">
              {item.image ? (
                <img
                  src={item.image}
                  alt={item.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <span className="text-gray-400 text-sm">暂无图片</span>
                </div>
              )}
            </div>
          </div>

          {/* Info */}
          <div className="p-4 space-y-3">
            <h3 className="text-xl font-bold text-gray-900">{item.name}</h3>
            <p className="text-lg font-semibold text-orange-500">
              ¥{item.price.toFixed(2)}
            </p>
            {item.description && (
              <p className="text-sm text-gray-600 leading-relaxed">{item.description}</p>
            )}
          </div>
        </DialogPanel>
      </div>
    </Dialog>
  );
}
