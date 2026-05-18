import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Edit3, Star, MessageSquare, Heart, MapPin, HelpCircle } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { fetchActivities } from '../api/activities';
import type { Activity, ActivityType } from '../types/activity';
import SectionCard from '../components/ui/SectionCard';

/** 格式化相对时间 */
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

/** 活动图标映射 */
const activityIcon: Record<ActivityType, typeof Star> = {
  rating: Star,
  comment: MessageSquare,
  favorite: Heart,
  add_shop: MapPin,
  question: HelpCircle,
};

const activityColors: Record<ActivityType, string> = {
  rating: 'text-yellow-500',
  comment: 'text-blue-500',
  favorite: 'text-red-500',
  add_shop: 'text-orange-500',
  question: 'text-purple-500',
};

/** 手机号脱敏 */
function maskPhone(phone: string): string {
  if (!phone || phone.length < 7) return phone;
  return phone.slice(0, 3) + '****' + phone.slice(-4);
}

export default function ProfilePage() {
  const navigate = useNavigate();
  const { userName, userAvatar, userEmail, userPhone, userId } = useAuthStore();
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!userId) return;
    fetchActivities(userId)
      .then(setActivities)
      .finally(() => setLoading(false));
  }, [userId]);

  return (
    <div className="max-w-2xl mx-auto py-8 space-y-5">
      {/* Card 1: 个人信息 */}
      <SectionCard>
        <div className="flex flex-col items-center text-center">
          {/* Avatar */}
          <div className="w-24 h-24 rounded-full bg-gradient-to-br from-[#FF7E3A] to-[#FF9A5C] flex items-center justify-center shadow-lg shadow-orange-200 mb-4">
            {userAvatar ? (
              <img src={userAvatar} alt={userName} className="w-full h-full rounded-full object-cover" />
            ) : (
              <span className="text-3xl font-bold text-white">{userName.charAt(0)}</span>
            )}
          </div>

          {/* Name */}
          <h1 className="text-xl font-bold text-gray-800">{userName}</h1>

          {/* Contact */}
          <div className="flex items-center gap-2 mt-1 text-sm text-gray-400">
            <span>{userEmail}</span>
            {userPhone && (
              <>
                <span>·</span>
                <span>{maskPhone(userPhone)}</span>
              </>
            )}
          </div>

          {/* Bio */}
          <p className="text-sm text-gray-500 mt-3 max-w-xs">
            分享让美食更有温度
          </p>

          {/* Edit button */}
          <button
            type="button"
            onClick={() => {}}
            className="mt-5 inline-flex items-center gap-1.5 px-4 py-2 rounded-xl border border-orange-200 text-orange-500 text-sm hover:bg-orange-50 transition-colors"
          >
            <Edit3 size={14} />
            编辑资料
          </button>
        </div>
      </SectionCard>

      {/* Card 2: 个人动态 */}
      <SectionCard>
        <h2 className="text-base font-bold text-gray-800 mb-4 pl-3 border-l-[3px] border-orange-400">
          个人动态
        </h2>

        {loading ? (
          <div className="space-y-4 animate-pulse">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-gray-200" />
                <div className="flex-1 space-y-1.5">
                  <div className="h-3 w-3/4 bg-gray-200 rounded" />
                  <div className="h-2.5 w-1/4 bg-gray-100 rounded" />
                </div>
              </div>
            ))}
          </div>
        ) : activities.length === 0 ? (
          <div className="py-12 text-center text-sm text-gray-400">
            还没有动态，开始探索校园美食吧
          </div>
        ) : (
          <div className="space-y-0 divide-y divide-gray-100">
            {activities.map((activity) => {
              const Icon = activityIcon[activity.type];
              const color = activityColors[activity.type];

              return (
                <button
                  key={activity.id}
                  type="button"
                  onClick={() => navigate(`/shop/${activity.shopId}`)}
                  className="w-full flex items-center gap-3 py-3.5 px-2 text-left hover:bg-orange-50/50 transition-colors rounded-lg"
                >
                  {/* Icon */}
                  <div className={`w-8 h-8 rounded-full bg-gray-50 flex items-center justify-center flex-shrink-0 ${color}`}>
                    <Icon size={16} />
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-700 truncate">
                      <span className="font-medium text-gray-900">{userName}</span>
                      {' '}{activity.content}
                    </p>
                    {activity.type === 'rating' && activity.extra?.score && (
                      <div className="flex items-center gap-0.5 mt-0.5">
                        {Array.from({ length: activity.extra.score }).map((_, i) => (
                          <Star key={i} size={12} className="fill-yellow-400 text-yellow-400" />
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Time */}
                  <span className="text-xs text-gray-400 flex-shrink-0">
                    {relativeTime(activity.createdAt)}
                  </span>
                </button>
              );
            })}
          </div>
        )}
      </SectionCard>
    </div>
  );
}
