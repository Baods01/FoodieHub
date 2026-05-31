import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Star, MessageSquare, Heart, MapPin, HelpCircle, Reply, MessageCircle, ArrowLeft } from 'lucide-react';
import { fetchActivities } from '../api/activities';
import ProfileCard from '../components/profile/ProfileCard';
import SectionCard from '../components/ui/SectionCard';
import type { Activity, ActivityType } from '../types/activity';
import { getActivityText } from '../types/activity';
import apiClient from '../api/client';

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

const activityIcon: Record<ActivityType, typeof Star> = {
  rating: Star,
  comment: MessageSquare,
  answer: MessageCircle,
  reply: Reply,
  favorite: Heart,
  add_shop: MapPin,
  question: HelpCircle,
};

const activityColors: Record<ActivityType, string> = {
  rating: 'text-yellow-500',
  comment: 'text-blue-500',
  answer: 'text-indigo-500',
  reply: 'text-green-500',
  favorite: 'text-red-500',
  add_shop: 'text-orange-500',
  question: 'text-purple-500',
};

interface UserProfile {
  id: number;
  username: string;
  avatar: string | null;
  bio: string | null;
  gender: string | null;
  created_at: string;
}

export default function UserProfilePage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    Promise.all([
      apiClient.get(`/users/${id}/profile`).then(r => (r.data as any)?.data ?? null),
      fetchActivities(Number(id)).then((result: any) => result.items ?? []),
    ])
      .then(([profileData, activityItems]) => {
        if (!profileData) { setNotFound(true); return; }
        setProfile(profileData);
        setActivities(activityItems);
      })
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto py-8 space-y-5 animate-pulse">
        <div className="bg-white rounded-2xl h-64" />
        <div className="bg-white rounded-2xl h-48" />
      </div>
    );
  }

  if (notFound || !profile) {
    return (
      <div className="max-w-2xl mx-auto py-20 text-center">
        <p className="text-gray-500 text-base">用户不存在</p>
        <button
          onClick={() => navigate('/')}
          className="mt-4 rounded-lg bg-orange-500 px-6 py-2 text-sm text-white hover:bg-orange-600 transition-colors"
        >
          返回首页
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto py-8 space-y-5">
      {/* 返回按钮 */}
      <button
        onClick={() => navigate(-1)}
        className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 transition-colors"
      >
        <ArrowLeft size={16} />
        返回
      </button>

      {/* 用户资料卡片 */}
      <ProfileCard
        username={profile.username}
        avatar={profile.avatar}
        bio={profile.bio}
        gender={profile.gender}
        createdAt={profile.created_at}
      />

      {/* 用户动态 */}
      <SectionCard>
        <h2 className="text-base font-bold text-gray-800 mb-4 pl-3 border-l-[3px] border-orange-400">
          动态
        </h2>

        {activities.length === 0 ? (
          <div className="py-12 text-center text-sm text-gray-400">
            还没有动态
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
                  onClick={() => navigate(`/shop/${activity.shop_id}`)}
                  className="w-full flex items-center gap-3 py-3.5 px-2 text-left hover:bg-orange-50/50 transition-colors rounded-lg"
                >
                  <div className={`w-8 h-8 rounded-full bg-gray-50 flex items-center justify-center flex-shrink-0 ${color}`}>
                    <Icon size={16} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-700 truncate">
                      <span className="font-medium text-gray-900">{profile.username}</span>
                      {' '}{getActivityText(activity.type)}
                    </p>
                  </div>
                  <span className="text-xs text-gray-400 flex-shrink-0">
                    {relativeTime(activity.created_at)}
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
