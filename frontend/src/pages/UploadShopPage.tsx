import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapPin, Camera, Check, X, Loader2 } from 'lucide-react';
import { fetchDictData } from '../api/dictionary';
import { createShop } from '../api/uploadShop';
import { uploadImage } from '../api/upload';
import type { DictItem } from '../api/dictionary';
import { Header } from '../components/layout/Header';
import { useAuthStore } from '../store/authStore';

// 将前端的显示名称映射回字典 code
const nameToId = (items: DictItem[], name: string): number =>
  (items.find((i) => i.name === name)?.id ?? 0) as number

export default function UploadShopPage() {
  const navigate = useNavigate();
  const isLoggedIn = useAuthStore((s) => s.isLoggedIn);
  const fileRef = useRef<HTMLInputElement>(null);

  // 字典数据
  const [categories, setCategories] = useState<DictItem[]>([]);
  const [areas, setAreas] = useState<DictItem[]>([]);
  const [diningMethods, setDiningMethods] = useState<DictItem[]>([]);

  // 表单值
  const [name, setName] = useState('');
  const [category, setCategory] = useState('');
  const [area, setArea] = useState('');
  const [dining, setDining] = useState<string[]>([]);
  const [cover, setCover] = useState<string | null>(null);
  const [coverFile, setCoverFile] = useState<File | null>(null);  // 保留 File 对象用于上传

  // 状态
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    Promise.all([
      fetchDictData('品类'),
      fetchDictData('区域'),
      fetchDictData('就餐方式'),
    ]).then(([c, a, d]) => {
      setCategories(c);
      setAreas(a);
      setDiningMethods(d);
      setLoading(false);
    });
  }, []);

  // 图片上传
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setCoverFile(file);  // 保存 File 对象用于后续上传
    const reader = new FileReader();
    reader.onload = () => setCover(reader.result as string);
    reader.readAsDataURL(file);
  };

  // 移除封面图片
  const handleRemoveCover = () => {
    setCover(null);
    setCoverFile(null);
    if (fileRef.current) fileRef.current.value = '';
  };

  // 切换就餐方式
  const toggleDining = (item: string) => {
    setDining((prev) =>
      prev.includes(item) ? prev.filter((v) => v !== item) : [...prev, item]
    );
  };

  // 提交
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const errs: Record<string, string> = {};

    if (!name.trim()) errs.name = '请输入店铺名称';
    if (!category) errs.category = '请选择品类';
    if (!area) errs.area = '请选择区域';
    if (dining.length === 0) errs.dining = '请至少选择一种就餐方式';

    if (Object.keys(errs).length > 0) {
      setErrors(errs);
      return;
    }
    setErrors({});
    setSubmitting(true);

    try {
      const catCode = nameToId(categories, category);
      const areaCode = nameToId(areas, area);
      const diningCodes: number[] = dining.map((d) => nameToId(diningMethods, d)).filter(Boolean) as unknown as number[];

      // Step 1: 先创建店铺（获得 shop.id）
      const result = await createShop({
        name: name.trim(),
        dict_data_ids: [...[catCode, areaCode].filter(Boolean), ...diningCodes] as number[],
      });

      // Step 2: 如果有封面图片，上传并绑定到店铺
      if (coverFile) {
        await uploadImage(coverFile, 'shop', result.id);
      }

      navigate(`/shop/${result.id}`);
    } catch {
      setErrors({ submit: '分享失败，请重试' });
    } finally {
      setSubmitting(false);
    }
  };

  if (!isLoggedIn) {
    navigate('/login');
    return null;
  }

  return (
    <div className="min-h-screen flex flex-col bg-white">
      <Header />
      <div className="flex-1 flex items-start justify-center px-4 py-10">
        <div className="w-full max-w-2xl bg-white rounded-2xl shadow-[0_2px_8px_rgba(0,0,0,0.04),0_8px_32px_rgba(0,0,0,0.10)] border border-gray-100/80 animate-fade-slide-up">
          <div className="p-8">
            {/* Title */}
            <div className="flex items-center gap-2 mb-1">
              <MapPin size={22} className="text-orange-500" />
              <h1 className="text-xl font-bold">分享店铺</h1>
            </div>
            <p className="text-sm text-gray-400 mb-8">分享你发现的宝藏美食店铺</p>

            {loading ? (
              <div className="space-y-4 animate-pulse">
                <div className="h-10 bg-gray-200 rounded-xl" />
                <div className="grid grid-cols-2 gap-4">
                  <div className="h-10 bg-gray-200 rounded-xl" />
                  <div className="h-10 bg-gray-200 rounded-xl" />
                </div>
                <div className="h-10 bg-gray-200 rounded-xl" />
                <div className="h-36 bg-gray-200 rounded-xl" />
                <div className="h-10 bg-gray-200 rounded-xl" />
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* 店铺名称 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    店铺名称 <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="例如：陈记糖水铺"
                    className={`w-full px-4 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 focus:ring-orange-400 transition-all duration-200 ${
                      errors.name ? 'border-red-400 bg-red-50' : 'border-gray-200 bg-gray-50/50 hover:border-gray-300'
                    }`}
                  />
                  {errors.name && <p className="text-red-500 text-xs mt-1 animate-fade-in">{errors.name}</p>}
                </div>

                {/* 品类 + 区域（同行） */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">
                      品类 <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={category}
                      onChange={(e) => setCategory(e.target.value)}
                      className={`w-full px-4 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 focus:ring-orange-400 transition-all duration-200 appearance-none bg-no-repeat bg-[length:14px] bg-[right_14px_center] ${
                        errors.category ? 'border-red-400 bg-red-50' : 'border-gray-200 bg-gray-50/50 hover:border-gray-300'
                      }`}
                      style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='%239CA3AF' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E")` }}
                    >
                      <option value="">选择品类</option>
                      {categories.map((item) => (
                        <option key={item.id} value={item.name}>{item.name}</option>
                      ))}
                    </select>
                    {errors.category && <p className="text-red-500 text-xs mt-1 animate-fade-in">{errors.category}</p>}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">
                      区域 <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={area}
                      onChange={(e) => setArea(e.target.value)}
                      className={`w-full px-4 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 focus:ring-orange-400 transition-all duration-200 appearance-none bg-no-repeat bg-[length:14px] bg-[right_14px_center] ${
                        errors.area ? 'border-red-400 bg-red-50' : 'border-gray-200 bg-gray-50/50 hover:border-gray-300'
                      }`}
                      style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='%239CA3AF' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E")` }}
                    >
                      <option value="">选择区域</option>
                      {areas.map((item) => (
                        <option key={item.id} value={item.name}>{item.name}</option>
                      ))}
                    </select>
                    {errors.area && <p className="text-red-500 text-xs mt-1 animate-fade-in">{errors.area}</p>}
                  </div>
                </div>

                {/* 就餐方式 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    就餐方式 <span className="text-red-500">*</span>
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {diningMethods.map((item) => {
                      const selected = dining.includes(item.name);
                      return (
                        <button
                          key={item.id}
                          type="button"
                          onClick={() => toggleDining(item.name)}
                          className={`flex items-center gap-1.5 px-4 py-2 rounded-xl border text-sm transition-all duration-200 ${
                            selected
                              ? 'bg-orange-500 text-white border-orange-500 shadow-sm'
                              : 'bg-white text-gray-600 border-gray-200 hover:border-gray-300'
                          }`}
                        >
                          {selected ? <Check size={14} /> : null}
                          {item.name}
                        </button>
                      );
                    })}
                  </div>
                  {errors.dining && <p className="text-red-500 text-xs mt-1 animate-fade-in">{errors.dining}</p>}
                </div>

                {/* 封面图片 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    封面图片 <span className="text-gray-400 font-normal">（选填）</span>
                  </label>
                  <input
                    ref={fileRef}
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                  {cover ? (
                    <div className="relative h-36 rounded-xl overflow-hidden bg-gray-100">
                      <img src={cover} alt="封面预览" className="w-full h-full object-cover" />
                      <button
                        type="button"
                        onClick={handleRemoveCover}
                        className="absolute top-2 right-2 w-7 h-7 rounded-full bg-black/40 text-white flex items-center justify-center hover:bg-black/60 transition-colors"
                      >
                        <X size={14} />
                      </button>
                      <button
                        type="button"
                        onClick={() => fileRef.current?.click()}
                        className="absolute bottom-2 right-2 px-3 py-1 rounded-lg bg-black/40 text-white text-xs hover:bg-black/60 transition-colors"
                      >
                        重新选择
                      </button>
                    </div>
                  ) : (
                    <button
                      type="button"
                      onClick={() => fileRef.current?.click()}
                      className="w-full h-36 rounded-xl border-2 border-dashed border-gray-200 flex flex-col items-center justify-center gap-2 text-gray-400 hover:border-orange-300 hover:text-orange-500 transition-all duration-200"
                    >
                      <Camera size={28} />
                      <span className="text-sm">点击上传封面图片</span>
                      <span className="text-xs">建议尺寸 16:9</span>
                    </button>
                  )}
                </div>

                {/* 提交错误 */}
                {errors.submit && (
                  <p className="text-red-500 text-sm text-center">{errors.submit}</p>
                )}

                {/* 提交按钮 */}
                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full py-2.5 rounded-xl bg-gradient-to-r from-[#FF7E3A] to-[#FF9A5C] text-white text-sm font-medium hover:shadow-lg hover:shadow-orange-200 hover:scale-[1.01] active:scale-[0.99] transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center gap-2"
                >
                  {submitting ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      分享中...
                    </>
                  ) : (
                    <>
                      <MapPin size={16} />
                      立即分享
                    </>
                  )}
                </button>
              </form>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
