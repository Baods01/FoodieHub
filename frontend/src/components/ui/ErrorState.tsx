import { AlertCircle } from 'lucide-react';

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export function ErrorState({
  message = '加载失败',
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      <AlertCircle size={48} className="text-red-400" />
      <p className="text-gray-500 text-base mt-4">{message}</p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="px-6 py-2 mt-4 rounded-lg border border-orange-400 text-orange-500 hover:bg-orange-50 transition-colors duration-200"
        >
          点击重试
        </button>
      )}
    </div>
  );
}
