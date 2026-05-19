import { useState, useEffect, useCallback, Fragment } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, MessageSquare, ThumbsUp, Megaphone } from 'lucide-react';
import { Dialog, Transition } from '@headlessui/react';
import { fetchNotifications, markAsRead } from '../api/notifications';
import type { NotificationItem, NotifType } from '../types/notification';
import { ErrorState } from '../components/ui/ErrorState';

// ====== 类型配置 ======

interface TabDef {
  key: NotifType;
  label: string;
  icon: typeof MessageSquare;
  color: string;
  bgColor: string;
}

const tabs: TabDef[] = [
  { key: 'reply',        label: '回复我的', icon: MessageSquare, color: 'text-blue-500',  bgColor: 'bg-blue-50' },
  { key: 'like',         label: '收到的赞', icon: ThumbsUp,      color: 'text-red-500',   bgColor: 'bg-red-50' },
  { key: 'announcement', label: '系统通知', icon: Megaphone,     color: 'text-orange-500', bgColor: 'bg-orange-50' },
];

// ====== 相对时间 ======

function relativeTime(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const min = Math.floor(diffMs / 60000);
  if (min < 1) return '刚刚';
  if (min < 60) return `${min}分钟前`;
  const hour = Math.floor(min / 60);
  if (hour < 24) return `${hour}小时前`;
  const day = Math.floor(hour / 24);
  if (day < 30) return `${day}天前`;
  return `${Math.floor(day / 30)}个月前`;
}

// ====== 骨架屏 ======

function ListSkeleton() {
  return (
    <div className="space-y-0 divide-y divide-gray-100 animate-pulse">
      {[1, 2, 3].map((i) => (
        <div key={i} className="flex items-start gap-3 px-4 py-3.5">
          <div className="w-8 h-8 rounded-full bg-gray-200 flex-shrink-0" />
          <div className="flex-1 space-y-2">
            <div className="h-3 w-2/3 bg-gray-200 rounded" />
            <div className="h-2.5 w-1/4 bg-gray-100 rounded" />
          </div>
        </div>
      ))}
    </div>
  );
}

// ====== 主页面 ======

export default function NotificationsPage() {
  const navigate = useNavigate();
  const [all, setAll] = useState<NotificationItem[]>([]);
  const [activeTab, setActiveTab] = useState<NotifType>('reply');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [announcement, setAnnouncement] = useState<NotificationItem | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    setError(false);
    fetchNotifications()
      .then(setAll)
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { load(); }, [load]);

  // 各分类计数
  const counts: Record<NotifType, number> = {
    reply: all.filter((n) => n.type === 'reply').length,
    like: all.filter((n) => n.type === 'like').length,
    announcement: all.filter((n) => n.type === 'announcement').length,
  };
  const unreadCounts: Record<NotifType, number> = {
    reply: all.filter((n) => n.type === 'reply' && !n.isRead).length,
    like: all.filter((n) => n.type === 'like' && !n.isRead).length,
    announcement: all.filter((n) => n.type === 'announcement' && !n.isRead).length,
  };

  const currentList = all
    .filter((n) => n.type === activeTab)
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());

  // 点击消息
  const handleClick = (item: NotificationItem) => {
    // 标记已读
    if (!item.isRead) {
      markAsRead(item.id);
      setAll((prev) => prev.map((n) => (n.id === item.id ? { ...n, isRead: true } : n)));
    }

    if (item.type === 'announcement') {
      setAnnouncement(item);
    } else if (item.shopId > 0) {
      navigate(`/shop/${item.shopId}`);
    }
  };

  const activeDef = tabs.find((t) => t.key === activeTab)!;

  return (
    <div className="max-w-4xl mx-auto py-8">
      {/* Outer card */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 flex flex-row overflow-hidden min-h-[520px]">
        {/* ===== Left sidebar ===== */}
        <div className="w-56 flex-shrink-0 border-r border-gray-100 flex flex-col">
          {/* Title */}
          <div className="flex items-center gap-2 px-4 pt-5 pb-3">
            <Bell size={18} className="text-yellow-500" />
            <span className="text-base font-bold">消息通知</span>
          </div>

          {/* Tabs */}
          <nav className="flex-1 space-y-0.5 px-2">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const unread = unreadCounts[tab.key];
              const isActive = activeTab === tab.key;
              return (
                <button
                  key={tab.key}
                  type="button"
                  onClick={() => setActiveTab(tab.key)}
                  className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                    isActive
                      ? 'bg-orange-50 text-orange-600 font-medium'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <Icon size={16} className={tab.color} />
                  <span className="flex-1 text-left">{tab.label}</span>
                  {unread > 0 && (
                    <span className="w-2 h-2 rounded-full bg-orange-400 flex-shrink-0" />
                  )}
                </button>
              );
            })}
          </nav>

          {/* Bottom counts */}
          <div className="px-4 py-3 border-t border-gray-100 space-y-1">
            {tabs.map((tab) => (
              <div key={tab.key} className="flex justify-between text-xs text-gray-400">
                <span>{tab.label}</span>
                <span>{counts[tab.key]}</span>
              </div>
            ))}
          </div>
        </div>

        {/* ===== Right content ===== */}
        <div className="flex-1 flex flex-col">
          {/* Tab header */}
          <div className="flex items-center justify-between px-5 pt-5 pb-3 border-b border-gray-100">
            <div className="flex items-center gap-2">
              <activeDef.icon size={18} className={activeDef.color} />
              <h2 className="text-base font-bold">{activeDef.label}</h2>
            </div>
            <span className="text-sm text-gray-400">
              {currentList.length} 条
            </span>
          </div>

          {/* List */}
          <div className="flex-1 overflow-y-auto">
            {error && !loading ? (
              <div className="p-4"><ErrorState onRetry={load} /></div>
            ) : loading ? (
              <ListSkeleton />
            ) : currentList.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 text-sm text-gray-400">
                <activeDef.icon size={36} className="text-gray-200" />
                <p className="mt-3">暂无{activeDef.label}消息</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {currentList.map((item) => {
                  const tabCfg = tabs.find((t) => t.key === item.type)!;
                  const Icon = tabCfg.icon;
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => handleClick(item)}
                      className="w-full flex items-start gap-3 px-5 py-3.5 text-left hover:bg-gray-50/50 transition-colors"
                    >
                      {/* Unread dot */}
                      {!item.isRead && (
                        <span className="w-2 h-2 rounded-full bg-orange-400 flex-shrink-0 mt-1.5" />
                      )}
                      {item.isRead && <span className="w-2 flex-shrink-0" />}

                      {/* Icon */}
                      <div className={`w-8 h-8 rounded-full ${tabCfg.bgColor} flex items-center justify-center flex-shrink-0 ${tabCfg.color}`}>
                        <Icon size={16} />
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm ${item.isRead ? 'text-gray-500' : 'text-gray-800 font-medium'}`}>
                          {item.description}
                        </p>
                        {item.type === 'announcement' && item.title && (
                          <p className="text-xs text-gray-400 mt-0.5 line-clamp-1">{item.fullContent}</p>
                        )}
                      </div>

                      {/* Time */}
                      <span className="text-xs text-gray-400 flex-shrink-0 mt-0.5">
                        {relativeTime(item.createdAt)}
                      </span>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ===== Announcement dialog ===== */}
      <Transition show={announcement !== null} as={Fragment}>
        <Dialog as="div" className="relative z-50" onClose={() => setAnnouncement(null)}>
          <Transition.Child as={Fragment} enter="ease-out duration-200" enterFrom="opacity-0" enterTo="opacity-100" leave="ease-in duration-150" leaveFrom="opacity-100" leaveTo="opacity-0">
            <div className="fixed inset-0 bg-black/30" />
          </Transition.Child>
          <div className="fixed inset-0 flex items-center justify-center p-4">
            <Transition.Child as={Fragment} enter="ease-out duration-200" enterFrom="opacity-0 scale-95" enterTo="opacity-100 scale-100" leave="ease-in duration-150" leaveFrom="opacity-100 scale-100" leaveTo="opacity-0 scale-95">
              <Dialog.Panel className="w-full max-w-lg bg-white rounded-2xl p-6 shadow-xl">
                {announcement && (
                  <>
                    <div className="flex items-center gap-2 mb-4">
                      <Megaphone size={18} className="text-orange-500" />
                      <Dialog.Title className="text-base font-bold">{announcement.title}</Dialog.Title>
                    </div>
                    <p className="text-sm text-gray-600 whitespace-pre-wrap leading-relaxed">
                      {announcement.fullContent}
                    </p>
                    <div className="flex justify-between items-center mt-6 pt-4 border-t border-gray-100">
                      <span className="text-xs text-gray-400">{relativeTime(announcement.createdAt)}</span>
                      <button
                        type="button"
                        onClick={() => setAnnouncement(null)}
                        className="px-4 py-2 rounded-xl bg-orange-50 text-orange-500 text-sm hover:bg-orange-100 transition-colors"
                      >
                        我知道了
                      </button>
                    </div>
                  </>
                )}
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </Dialog>
      </Transition>
    </div>
  );
}
