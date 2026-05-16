import { Fragment, useState } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { X } from 'lucide-react';
import type { MenuItem } from '../../types/shop';
import { MenuCard } from './MenuCard';
import { MenuDetailModal } from './MenuDetailModal';

interface AllMenuModalProps {
  items: MenuItem[];
  isOpen: boolean;
  onClose: () => void;
}

export default function AllMenuModal({ items, isOpen, onClose }: AllMenuModalProps) {
  const [selectedItem, setSelectedItem] = useState<MenuItem | null>(null);

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
                    全部菜单 ({items.length})
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
                  {items.length === 0 ? (
                    <div className="flex items-center justify-center py-20 text-sm text-gray-400">
                      暂无菜单
                    </div>
                  ) : (
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                      {items.map((item) => (
                        <MenuCard key={item.id} item={item} onClick={setSelectedItem} />
                      ))}
                    </div>
                  )}
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </Dialog>
      </Transition>

      {/* Detail modal (reuse existing) */}
      <MenuDetailModal item={selectedItem} onClose={() => setSelectedItem(null)} />
    </>
  );
}
