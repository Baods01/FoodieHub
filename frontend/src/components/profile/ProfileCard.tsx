import { Edit3, Mail, Phone, User, Calendar, Quote } from 'lucide-react';

interface ProfileCardProps {
  username: string;
  avatar: string | null;
  email?: string;
  phone?: string;
  bio: string | null;
  gender: string | null;
  createdAt: string;
  onEdit?: () => void;
}

function maskPhone(phone: string): string {
  if (!phone || phone.length < 7) return phone;
  return phone.slice(0, 3) + '****' + phone.slice(-4);
}

function formatDate(iso: string): string {
  if (!iso) return '-';
  const d = new Date(iso);
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`;
}

function genderLabel(gender: string | null): string {
  if (gender === 'male') return '男';
  if (gender === 'female') return '女';
  return '未设置';
}

export default function ProfileCard({ username, avatar, email, phone, bio, gender, createdAt, onEdit }: ProfileCardProps) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      {/* 顶部头像区 */}
      <div className="bg-gradient-to-r from-orange-400 to-orange-300 px-6 pt-8 pb-16 text-center">
        <div className="w-20 h-20 rounded-full mx-auto border-4 border-white/60 shadow-lg overflow-hidden bg-white">
          {avatar ? (
            <img src={avatar} alt={username} className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-2xl font-bold text-orange-500">
              {username.charAt(0)}
            </div>
          )}
        </div>
        <h1 className="text-xl font-bold text-white mt-3">{username}</h1>
      </div>

      {/* 信息区 */}
      <div className="px-6 -mt-10">
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm divide-y divide-gray-50">
          {/* Bio */}
          {bio && (
            <div className="flex items-start gap-3 px-4 py-3.5">
              <Quote size={16} className="text-orange-400 mt-0.5 flex-shrink-0" />
              <p className="text-sm text-gray-600 leading-relaxed">{bio}</p>
            </div>
          )}

          {/* Email */}
          {email && (
            <div className="flex items-center gap-3 px-4 py-3.5">
              <Mail size={16} className="text-gray-400 flex-shrink-0" />
              <span className="text-sm text-gray-700">{email}</span>
            </div>
          )}

          {/* Phone */}
          {phone && (
            <div className="flex items-center gap-3 px-4 py-3.5">
              <Phone size={16} className="text-gray-400 flex-shrink-0" />
              <span className="text-sm text-gray-700">{maskPhone(phone)}</span>
            </div>
          )}

          {/* Gender */}
          <div className="flex items-center gap-3 px-4 py-3.5">
            <User size={16} className="text-gray-400 flex-shrink-0" />
            <span className="text-sm text-gray-700">{genderLabel(gender)}</span>
          </div>

          {/* Register time */}
          <div className="flex items-center gap-3 px-4 py-3.5">
            <Calendar size={16} className="text-gray-400 flex-shrink-0" />
            <span className="text-sm text-gray-700">{formatDate(createdAt)} 加入</span>
          </div>
        </div>

        {/* Edit button */}
        {onEdit && (
          <button
            type="button"
            onClick={onEdit}
            className="w-full mt-4 mb-6 inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-orange-500 text-sm text-white font-medium hover:bg-orange-600 transition-colors"
          >
            <Edit3 size={15} />
            编辑资料
          </button>
        )}
      </div>
    </div>
  );
}
