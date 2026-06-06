import { useState, useEffect, useRef, useCallback } from 'react';
import { fetchBannerImages } from '../../api/upload';

const SWITCH_INTERVAL = 4000; // 每张图展示 4 秒

export default function AnnouncementBanner() {
  const [images, setImages] = useState<string[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const roundRef = useRef(0);       // 当前轮次，用于 key 防闪烁
  const indexRef = useRef(0);       // 实时索引，避免闭包陷阱
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  /** 清除定时器 */
  const clearTimer = useCallback(() => {
    if (timerRef.current !== null) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  /** 加载图片数据（重置轮播状态） */
  const loadImages = useCallback(async () => {
    try {
      const items = await fetchBannerImages();
      const urls = items.map((i) => i.url);
      setImages(urls);
      setCurrentIndex(0);
      indexRef.current = 0;
      roundRef.current += 1; // 递增轮次，让 key 变化
    } catch {
      setImages([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // 初始化加载
  useEffect(() => {
    loadImages();
  }, [loadImages]);

  // 轮播定时器：每张图切换，一轮结束后刷新数据
  useEffect(() => {
    if (images.length <= 1) return;

    clearTimer();
    timerRef.current = setInterval(() => {
      const nextIndex = indexRef.current + 1;

      if (nextIndex >= images.length) {
        // 所有图片都展示过一次 → 触发新一轮数据请求
        clearTimer();
        loadImages();
        return;
      }

      indexRef.current = nextIndex;
      setCurrentIndex(nextIndex);
    }, SWITCH_INTERVAL);

    return () => clearTimer();
  }, [images, clearTimer, loadImages]);

  // ====== 无数据状态：渐变色占位 ======
  if (!loading && images.length === 0) {
    return (
      <div className="h-[360px] bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl flex items-center justify-center select-none">
        <div className="text-center">
          <p className="text-orange-300 text-lg font-medium">分享你发现的宝藏店铺</p>
          <p className="text-orange-200 text-sm mt-1">上传店铺图片，让校园美食被更多人看到</p>
        </div>
      </div>
    );
  }

  // ====== 加载中 / 只有一张图 ======
  if (images.length <= 1) {
    return (
      <div className="relative h-[360px] overflow-hidden rounded-xl select-none">
        {loading ? (
          <div className="w-full h-full bg-gray-100 animate-pulse" />
        ) : (
          <img
            src={images[0]}
            alt="首页轮播"
            className="w-full h-full object-cover"
            style={{ pointerEvents: 'none' }}
          />
        )}
      </div>
    );
  }

  // ====== 多图轮播装饰 ======
  return (
    <div className="relative h-[360px] overflow-hidden rounded-xl group select-none">
      {/* 图片轨道 */}
      <div
        className="flex h-full transition-transform duration-500 ease-in-out"
        style={{ transform: `translateX(-${currentIndex * 100}%)` }}
      >
        {images.map((src, i) => (
          <div key={`r${roundRef.current}-${i}`} className="min-w-full h-full flex-shrink-0">
            <img
              src={src}
              alt={`首页轮播 ${i + 1}`}
              className="w-full h-full object-cover"
              style={{ pointerEvents: 'none' }}
              loading="lazy"
            />
          </div>
        ))}
      </div>

      {/* 底部渐变遮罩 */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/10 to-transparent pointer-events-none" />

      {/* 指示点 */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-2">
        {images.map((_, i) => (
          <div
            key={i}
            className={`rounded-full transition-all duration-300 ${
              i === currentIndex ? 'w-5 h-2 bg-white' : 'w-2 h-2 bg-white/50'
            }`}
          />
        ))}
      </div>
    </div>
  );
}