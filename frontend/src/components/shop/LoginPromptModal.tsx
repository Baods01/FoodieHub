import { Dialog, DialogPanel, DialogTitle, DialogDescription } from '@headlessui/react';

interface LoginPromptModalProps {
  isOpen: boolean;
  message?: string;
  onClose: () => void;
  onGoLogin: () => void;
}

export function LoginPromptModal({
  isOpen,
  message = '登录后即可使用此功能',
  onClose,
  onGoLogin,
}: LoginPromptModalProps) {
  return (
    <Dialog open={isOpen} onClose={onClose} className="relative z-50">
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/30" aria-hidden="true" />

      {/* Panel container */}
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <DialogPanel className="w-full max-w-sm rounded-xl bg-white p-6 shadow-xl">
          <DialogTitle className="text-center text-base font-semibold text-gray-800">
            提示
          </DialogTitle>

          <DialogDescription className="mt-3 text-center text-sm text-gray-500">
            {message}
          </DialogDescription>

          <div className="mt-6 flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-600 transition-colors hover:bg-gray-50"
            >
              稍再说
            </button>
            <button
              type="button"
              onClick={onGoLogin}
              className="flex-1 rounded-lg bg-orange-500 px-4 py-2 text-sm text-white transition-colors hover:bg-orange-600"
            >
              去登录
            </button>
          </div>
        </DialogPanel>
      </div>
    </Dialog>
  );
}
