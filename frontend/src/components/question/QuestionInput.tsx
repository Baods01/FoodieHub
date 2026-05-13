import { useState } from 'react';

interface QuestionInputProps {
  onSubmit: (title: string, content: string) => void;
  isSubmitting: boolean;
  isLoggedIn: boolean;
  onLoginPrompt: () => void;
}

const TITLE_MIN = 2;
const TITLE_MAX = 50;
const CONTENT_MIN = 5;
const CONTENT_MAX = 200;

export function QuestionInput({
  onSubmit,
  isSubmitting,
  isLoggedIn,
  onLoginPrompt,
}: QuestionInputProps) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  const titleValid = title.length >= TITLE_MIN && title.length <= TITLE_MAX;
  const contentValid = content.length >= CONTENT_MIN && content.length <= CONTENT_MAX;
  const canSubmit = titleValid && contentValid && !isSubmitting;

  const handleSubmit = () => {
    if (!canSubmit) return;
    onSubmit(title.trim(), content.trim());
    setTitle('');
    setContent('');
  };

  if (!isLoggedIn) {
    return (
      <div
        className="bg-gray-50 rounded-lg p-4 text-center text-gray-400 text-sm cursor-pointer hover:bg-gray-100 transition-colors"
        onClick={onLoginPrompt}
      >
        登录后即可提问
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 space-y-3">
      {/* Title */}
      <div>
        <div className="flex items-center justify-between mb-1">
          <label className="text-sm text-gray-600">标题</label>
          <span className={`text-xs ${title.length > TITLE_MAX ? 'text-red-500' : 'text-gray-400'}`}>
            {title.length}/{TITLE_MAX}
          </span>
        </div>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="输入问题标题"
          maxLength={TITLE_MAX + 10}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-300 focus:border-orange-400"
        />
        {title.length > 0 && title.length < TITLE_MIN && (
          <p className="text-xs text-red-500 mt-1">至少输入 {TITLE_MIN} 个字符</p>
        )}
      </div>

      {/* Content */}
      <div>
        <div className="flex items-center justify-between mb-1">
          <label className="text-sm text-gray-600">问题描述</label>
          <span className={`text-xs ${content.length > CONTENT_MAX ? 'text-red-500' : 'text-gray-400'}`}>
            {content.length}/{CONTENT_MAX}
          </span>
        </div>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="详细描述你的问题（5-200字）"
          maxLength={CONTENT_MAX + 10}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-300 focus:border-orange-400 resize-none"
        />
        {content.length > 0 && content.length < CONTENT_MIN && (
          <p className="text-xs text-red-500 mt-1">至少输入 {CONTENT_MIN} 个字符</p>
        )}
      </div>

      {/* Submit */}
      <div className="flex justify-end">
        <button
          type="button"
          disabled={!canSubmit}
          onClick={handleSubmit}
          className={`px-5 py-1.5 rounded-lg text-sm font-medium transition-colors ${
            canSubmit
              ? 'bg-orange-500 text-white hover:bg-orange-600'
              : 'bg-gray-200 text-gray-400 cursor-not-allowed'
          }`}
        >
          {isSubmitting ? '提交中...' : '提问'}
        </button>
      </div>
    </div>
  );
}
