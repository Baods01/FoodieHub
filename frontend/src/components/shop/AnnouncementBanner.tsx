interface BannerProps {
  announcement: { title: string; content: string } | null;
}

export function AnnouncementBanner({ announcement }: BannerProps) {
  if (!announcement) {
    return (
      <div className="h-[120px] bg-gray-100 rounded-lg flex items-center justify-center text-gray-400">
        发现华农周边美食
      </div>
    );
  }

  return (
    <div className="h-[120px] bg-[#FFF7F0] border-l-4 border-orange-400 rounded-lg flex flex-col justify-center px-6">
      <h3 className="font-bold text-gray-800">{announcement.title}</h3>
      <p className="text-sm text-gray-600 mt-1 line-clamp-2">{announcement.content}</p>
    </div>
  );
}
