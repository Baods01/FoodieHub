import { useState, useRef } from 'react';
import { Image, Loader2, X } from 'lucide-react';
import { uploadImage } from '../../api/upload';

interface CommentInputProps {
  onSubmit: (content: string, imageId?: number) => void;
  isSubmitting: boolean;
  isLoggedIn: boolean;
  onLoginPrompt: () => void;
  entityType?: string;
  entityId?: number;
}

const MAX_CHARS = 500;

export function CommentInput({
  onSubmit,
  isSubmitting,
  isLoggedIn,
  onLoginPrompt,
  entityType = 'shop_comment',
  entityId,
}: CommentInputProps) {
  const [content, setContent] = useState('');
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [uploadingImage, setUploadingImage] = useState(false);
  const [imageId, setImageId] = useState<number | undefined>(undefined);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);

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

  const handleImageSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !entityId) return;
    setUploadingImage(true);
    try {
      const result = await uploadImage(file, entityType, entityId);
      setImageId(result.id);
      // 本地预览
      setPreviewUrl(URL.createObjectURL(file));
    } catch (err) {
      console.error('图片上传失败', err);
    } finally {
      setUploadingImage(false);
      if (fileRef.current) fileRef.current.value = '';
    }
  };

  const removeImage = () => {
    setImageId(undefined);
    setPreviewUrl(null);
  };

  const handleSubmit = () => {
    const trimmed = content.trim();
    if (!trimmed || isSubmitting) return;
    onSubmit(trimmed, imageId);
    setContent('');
    setImageId(undefined);
    setPreviewUrl(null);
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

  const canSubmit = content.trim().length > 0 && !isSubmitting && !uploadingImage;

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
          className="w-full resize-none rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 pr-20 text-sm outline-none transition-colors duration-200 focus:border-orange-300 focus:bg-white focus:ring-1 focus:ring-orange-200"
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

      {/* Image preview + upload button */}
      <div className="flex items-center gap-2">
        {previewUrl ? (
          <div className="relative group">
            <img src={previewUrl} alt="预览" className="h-16 w-16 rounded-lg object-cover border border-gray-200" />
            <button
              type="button"
              onClick={removeImage}
              className="absolute -top-1.5 -right-1.5 rounded-full bg-black/60 p-0.5 text-white hover:bg-black/80"
            >
              <X size={12} />
            </button>
          </div>
        ) : (
          <>
            <input
              ref={fileRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              className="hidden"
              onChange={handleImageSelect}
            />
            <button
              type="button"
              onClick={() => fileRef.current?.click()}
              disabled={uploadingImage}
              className="inline-flex items-center gap-1 rounded-lg border border-gray-200 px-2.5 py-1.5 text-xs text-gray-500 transition-colors hover:border-orange-300 hover:text-orange-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {uploadingImage ? <Loader2 size={12} className="animate-spin" /> : <Image size={12} />}
              {uploadingImage ? '上传中' : '添加图片'}
            </button>
          </>
        )}
        <span className="text-xs text-gray-400">（可选，最多 1 张）</span>
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