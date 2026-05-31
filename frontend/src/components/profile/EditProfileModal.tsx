import { useState, useRef } from 'react';
import { X, Camera, Loader2 } from 'lucide-react';
import apiClient from '../../api/client';

interface EditProfileModalProps {
  open: boolean;
  onClose: () => void;
  onSaved: () => void;
  initial: {
    username: string;
    avatar: string | null;
    bio: string | null;
    gender: string | null;
  };
}

export default function EditProfileModal({ open, onClose, onSaved, initial }: EditProfileModalProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [avatarUrl, setAvatarUrl] = useState(initial.avatar ?? '');
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState(initial.avatar ?? '');
  const [bio, setBio] = useState(initial.bio ?? '');
  const [gender, setGender] = useState(initial.gender ?? '');
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);

  if (!open) return null;

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setAvatarFile(file);
    setAvatarPreview(URL.createObjectURL(file));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      let finalAvatar = avatarUrl;

      // 有上传新头像文件 → 先上传图片
      if (avatarFile) {
        setUploading(true);
        const formData = new FormData();
        formData.append('file', avatarFile);
        formData.append('entity_type', 'avatar');
        formData.append('entity_id', '0');
        const uploadRes = await apiClient.post('/images/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        finalAvatar = (uploadRes.data as any)?.data?.url ?? avatarUrl;
        setUploading(false);
      }

      // 更新用户资料
      await apiClient.put('/users/me', {
        avatar: finalAvatar || null,
        bio: bio || null,
        gender: gender || null,
      });

      onSaved();
      onClose();
    } catch {
      alert('保存失败');
    } finally {
      setSaving(false);
      setUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40" onClick={onClose}>
      <div
        className="bg-white rounded-2xl w-full max-w-md mx-4 shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h2 className="text-lg font-bold text-gray-800">编辑资料</h2>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-gray-100 transition-colors">
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-5 space-y-6">

          {/* 用户名（只读） */}
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">用户名</label>
            <div className="px-3 py-2.5 bg-gray-50 rounded-xl text-sm text-gray-800 border border-gray-200">
              {initial.username}
            </div>
            <p className="text-xs text-gray-400 mt-1">用户名不可修改</p>
          </div>

          {/* 头像上传 */}
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-2">头像</label>
            <div className="flex items-center gap-4">
              {/* 当前头像预览 */}
              <div className="relative w-16 h-16 rounded-full overflow-hidden border-2 border-gray-200 bg-gray-100 flex-shrink-0">
                {avatarPreview ? (
                  <img src={avatarPreview} alt="头像预览" className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-400 text-xl font-bold">
                    {initial.username.charAt(0)}
                  </div>
                )}
                {uploading && (
                  <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
                    <Loader2 size={20} className="text-white animate-spin" />
                  </div>
                )}
              </div>

              {/* 上传按钮 */}
              <div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/jpeg,image/png,image/webp,image/gif"
                  className="hidden"
                  onChange={handleFileSelect}
                />
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploading}
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl border border-orange-200 text-orange-500 text-sm hover:bg-orange-50 disabled:opacity-50 transition-colors"
                >
                  <Camera size={15} />
                  上传新头像
                </button>
                {avatarFile && (
                  <p className="text-xs text-gray-400 mt-1">{avatarFile.name}</p>
                )}
              </div>
            </div>
            <p className="text-xs text-gray-400 mt-2">支持 JPG / PNG / WebP / GIF，最大 10MB</p>
          </div>

          {/* 性别 */}
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-2">性别</label>
            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => setGender(gender === 'male' ? '' : 'male')}
                className={`flex-1 py-2.5 rounded-xl text-sm font-medium border transition-colors ${
                  gender === 'male'
                    ? 'border-orange-400 bg-orange-50 text-orange-600'
                    : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
                }`}
              >
                男
              </button>
              <button
                type="button"
                onClick={() => setGender(gender === 'female' ? '' : 'female')}
                className={`flex-1 py-2.5 rounded-xl text-sm font-medium border transition-colors ${
                  gender === 'female'
                    ? 'border-orange-400 bg-orange-50 text-orange-600'
                    : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
                }`}
              >
                女
              </button>
            </div>
          </div>

          {/* 个人简介 */}
          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="text-sm font-medium text-gray-500">个人简介</label>
              <span className={`text-xs ${bio.length > 500 ? 'text-red-500' : 'text-gray-400'}`}>
                {bio.length} / 500
              </span>
            </div>
            <textarea
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              placeholder="介绍一下自己..."
              rows={4}
              maxLength={500}
              className="w-full px-3 py-2.5 rounded-xl border border-gray-200 text-sm outline-none resize-none focus:border-orange-400 focus:ring-1 focus:ring-orange-200 transition-colors"
            />
          </div>
        </div>

        {/* Footer */}
        <div className="flex gap-3 px-6 py-4 border-t border-gray-100">
          <button
            onClick={onClose}
            className="flex-1 py-2.5 rounded-xl border border-gray-200 text-sm text-gray-600 hover:bg-gray-50 transition-colors"
          >
            取消
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex-1 py-2.5 rounded-xl bg-orange-500 text-sm text-white font-medium hover:bg-orange-600 disabled:bg-gray-300 transition-colors"
          >
            {saving ? '保存中...' : '保存'}
          </button>
        </div>
      </div>
    </div>
  );
}
