import { Link } from 'react-router-dom';
import { Bell } from 'lucide-react';

export default function NotificationsPage() {
  return (
    <div className="max-w-4xl mx-auto py-8">
      <div className="flex items-center gap-3 mb-6">
        <Bell size={24} className="text-yellow-500" />
        <h1 className="text-xl font-bold">消息通知</h1>
      </div>
      <div className="bg-white rounded-xl shadow-sm p-12 text-center">
        <Bell size={48} className="text-gray-200 mx-auto" />
        <p className="text-gray-500 mt-3">暂无新消息</p>
        <Link to="/" className="inline-block mt-3 text-sm text-orange-500 hover:text-orange-600">
          返回首页
        </Link>
      </div>
    </div>
  );
}
