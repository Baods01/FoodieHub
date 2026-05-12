interface EmptyStateProps {
  message?: string;
  actionText?: string;
  onAction?: () => void;
}

export function EmptyState({
  message = '还没有店铺',
  actionText = '成为第一个分享的人',
  onAction,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      {/* Empty box icon */}
      <svg
        width="64"
        height="64"
        viewBox="0 0 64 64"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <rect
          x="8"
          y="16"
          width="48"
          height="36"
          rx="4"
          stroke="#9CA3AF"
          strokeWidth="2"
          fill="none"
        />
        <path
          d="M8 28h48"
          stroke="#9CA3AF"
          strokeWidth="2"
        />
        <path
          d="M24 28v-8a8 8 0 0 1 16 0v8"
          stroke="#9CA3AF"
          strokeWidth="2"
          fill="none"
        />
      </svg>

      <p className="text-gray-500 text-base mt-4">{message}</p>

      {onAction && (
        <button
          type="button"
          onClick={onAction}
          className="px-6 py-2 mt-4 rounded-lg border border-orange-400 text-orange-500 hover:bg-orange-50 transition-colors duration-200"
        >
          {actionText}
        </button>
      )}
    </div>
  );
}
