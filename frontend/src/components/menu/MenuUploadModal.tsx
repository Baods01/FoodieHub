import { useState, useRef } from 'react';
import { Dialog, DialogPanel } from '@headlessui/react';
import { X, Loader2, Camera } from 'lucide-react';
import { addMenuItem } from '../../api/shops';
import { uploadImage } from '../../api/upload';

interface MenuUploadModalProps {
  shopId: number;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function MenuUploadModal({ shopId, isOpen, onClose, onSuccess }: MenuUploadModalProps) {
  const [name, setName] = useState('');
  const [price, setPrice] = useState('');
  const [description, setDescription] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const fileRef = useRef<HTMLInputElement>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!name.trim()) {
      setError('请输入菜品名称');
      return;
    }
    setError('');
    setSubmitting(true);
    try {
      const item = await addMenuItem(shopId, name.trim(), price ? parseFloat(price) : undefined, description.trim() || undefined);
      // 上传菜品图片（如果有）
      if (imageFile) {
        await uploadImage(imageFile, 'menu_item', item.id);
      }
      setName('');
      setPrice('');
      setDescription('');
      setImageFile(null);
      setImagePreview(null);
      onSuccess();
      onClose();
    } catch {
      setError('添加失败，请重试');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onClose={onClose} className="relative z-50">
      <div className="fixed inset-0 bg-black/40" />
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <DialogPanel className="w-full max-w-sm bg-white rounded-2xl p-6 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-bold">添加菜品</h3>
            <button type="button" onClick={onClose} className="p-1 text-gray-400 hover:text-gray-600">
              <X size={18} />
            </button>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">菜品名称 <span className="text-red-500">*</span></label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="例如：招牌牛肉面"
                className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-orange-300"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">价格（选填）</label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                placeholder="例如：28.00"
                className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-orange-300"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">描述（选填）</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="菜品简介..."
                rows={2}
                className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-orange-300 resize-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">菜品图片（选填）</label>
              <input
                ref={fileRef}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) {
                    setImageFile(file);
                    const reader = new FileReader();
                    reader.onload = () => setImagePreview(reader.result as string);
                    reader.readAsDataURL(file);
                  }
                }}
              />
              {imagePreview ? (
                <div className="relative h-24 rounded-lg overflow-hidden bg-gray-100">
                  <img src={imagePreview} alt="菜品预览" className="w-full h-full object-cover" />
                  <button
                    type="button"
                    onClick={() => { setImageFile(null); setImagePreview(null); if (fileRef.current) fileRef.current.value = ''; }}
                    className="absolute top-1 right-1 w-6 h-6 rounded-full bg-black/40 text-white flex items-center justify-center hover:bg-black/60"
                  >
                    <X size={12} />
                  </button>
                </div>
              ) : (
                <button
                  type="button"
                  onClick={() => fileRef.current?.click()}
                  className="w-full h-24 rounded-lg border-2 border-dashed border-gray-200 flex flex-col items-center justify-center gap-1 text-gray-400 hover:border-orange-300 hover:text-orange-500 transition-all"
                >
                  <Camera size={20} />
                  <span className="text-xs">点击上传图片</span>
                </button>
              )}
            </div>

            {error && <p className="text-red-500 text-sm">{error}</p>}

            <button
              type="button"
              disabled={submitting}
              onClick={handleSubmit}
              className="w-full py-2 rounded-xl bg-gradient-to-r from-[#FF7E3A] to-[#FF9A5C] text-white text-sm font-medium hover:shadow-lg disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {submitting ? <><Loader2 size={14} className="animate-spin" /> 添加中...</> : '确认添加'}
            </button>
          </div>
        </DialogPanel>
      </div>
    </Dialog>
  );
}
