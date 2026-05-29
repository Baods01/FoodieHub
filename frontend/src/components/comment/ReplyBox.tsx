import { useState, useRef, useEffect } from 'react';

interface ReplyBoxProps {
  parentId: number;
  targetUserName?: string;
  onSubmit: (content: string) => void;
  onCancel: () => void;
}

export function ReplyBox({ targetUserName, onSubmit, onCancel }: ReplyBoxProps) {
  const [content, setContent] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  }, []);

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setContent(e.target.value);
    // Auto-resize
    const el = e.target;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  };

  const handleSubmit = () => {
    const trimmed = content.trim();
    if (!trimmed) return;
    onSubmit(trimmed);
    setContent('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const canSubmit = content.trim().length > 0;

  return (
    <div className="mt-2 space-y-2">
      <div className="flex items-start gap-0 rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 transition-colors duration-200 focus-within:border-orange-300 focus-within:bg-white focus-within:ring-1 focus-within:ring-orange-200">
        {targetUserName && (
          <span className="text-sm text-gray-400 flex-shrink-0 mt-0.5">@{targetUserName} </span>
        )}
        <textarea
          ref={textareaRef}
          value={content}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder="回复..."
          rows={2}
          className="w-full resize-none bg-transparent px-0 py-0 text-sm outline-none"
        />
      </div>
      <div className="flex justify-end gap-2">
        <button
          type="button"
          onClick={onCancel}
          className="rounded-lg px-3 py-1.5 text-sm text-gray-500 transition-colors duration-200 hover:bg-gray-100"
        >
          取消
        </button>
        <button
          type="button"
          onClick={handleSubmit}
          disabled={!canSubmit}
          className={`rounded-lg px-4 py-1.5 text-sm text-white transition-colors duration-200 ${
            canSubmit
              ? 'bg-orange-400 hover:bg-orange-500'
              : 'cursor-not-allowed bg-gray-300'
          }`}
        >
          发送
        </button>
      </div>
    </div>
  );
}
