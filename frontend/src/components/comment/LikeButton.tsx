interface LikeButtonProps {
  count: number;
  isLiked: boolean;
  onClick: () => void;
}

export function LikeButton({ count, isLiked, onClick }: LikeButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`inline-flex items-center gap-1 text-sm transition-colors duration-200 ${
        isLiked
          ? 'text-red-500 hover:text-red-600'
          : 'text-gray-400 hover:text-red-400'
      }`}
    >
      <span className="text-base leading-none">{isLiked ? '♥' : '♡'}</span>
      <span>{count}</span>
    </button>
  );
}
