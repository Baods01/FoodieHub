interface Props {
  /** 卡片高度，默认 400px */
  height?: string;
}

export default function AnnouncementBanner({ height = 'h-[400px]' }: Props) {
  return (
    <div className={`w-full rounded-xl shadow-[0_2px_12px_rgba(0,0,0,0.08)] overflow-hidden relative ${height}`}>
      {/* 毛玻璃背景层：铺满卡片 */}
      <img
        src="/announcement-banner.png"
        alt=""
        aria-hidden="true"
        className="absolute inset-0 w-full h-full object-cover blur-sm scale-105"
      />
      {/* 主内容层：完整显示图片内容 */}
      <img
        src="/announcement-banner.png"
        alt="公告"
        className="relative w-full h-full object-contain"
      />
    </div>
  );
}
