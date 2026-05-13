import { useState, useRef } from 'react';

interface CommentInputProps {
  onSubmit: (content: string) => void;
  isSubmitting: boolean;
  isLoggedIn: boolean;
  onLoginPrompt: () => void;
}

const MAX_CHARS = 500;

export function CommentInput({
  onSubmit,
  isSubmitting,
  isLoggedIn,
  onLoginPrompt,
}: CommentInputProps) {
  const [content, setContent] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  if (!isLoggedIn) {
    return (
      <div
        onClick={onLoginPrompt}
        className="cursor-pointer rounded-xl border-2 border-dashed border-gray-200 px-4 py-6 text-center text-sm text-gray-400 transition-colors duration-200 hover:border-orange-200 hover:text-orange-400"
      >
        登录后即可评论
      </div>
    );
  }

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value;
    if (val.length > MAX_CHARS) return;
    setContent(val);
    // Auto-resize
    const el = e.target;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
  };

  const handleSubmit = () => {
    const trimmed = content.trim();
    if (!trimmed || isSubmitting) return;
    onSubmit(trimmed);
    setContent('');
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const canSubmit = content.trim().length > 0 && !isSubmitting;

  return (
    <div className="space-y-2">
      <div className="relative">
        <textarea
          ref={textareaRef}
          value={content}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder="分享你的体验..."
          rows={3}
          className="w-full resize-none rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm outline-none transition-colors duration-200 focus:border-orange-300 focus:bg-white focus:ring-1 focus:ring-orange-200"
        />
        <span
          className={`absolute bottom-2 right-3 text-xs ${
            content.length >= MAX_CHARS
              ? 'text-red-400'
              : 'text-gray-400'
          }`}
        >
          {content.length}/{MAX_CHARS}
        </span>
      </div>
      <div className="flex justify-end">
        <button
          type="button"
          onClick={handleSubmit}
          disabled={!canSubmit}
          className={`rounded-lg px-5 py-2 text-sm text-white transition-colors duration-200 ${
            canSubmit
              ? 'bg-orange-400 hover:bg-orange-500'
              : 'cursor-not-allowed bg-gray-300'
          }`}
        >
          {isSubmitting ? '发布中...' : '发布'}
        </button>
      </div>
    </div>
  );
}
