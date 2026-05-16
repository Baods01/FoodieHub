import { Link } from 'react-router-dom';
import { User } from 'lucide-react';

export default function ProfilePage() {
  return (
    <div className="max-w-2xl mx-auto py-8">
      <div className="bg-white rounded-xl shadow-sm p-8 text-center">
        <div className="w-20 h-20 rounded-full bg-orange-100 flex items-center justify-center mx-auto">
          <User size={36} className="text-orange-500" />
        </div>
        <h1 className="text-xl font-bold mt-4">个人中心</h1>
        <p className="text-gray-500 mt-1 text-sm">个人信息、统计数据和设置</p>
        <p className="text-gray-400 text-xs mt-8">页面内容开发中，敬请期待</p>
        <Link to="/" className="inline-block mt-4 text-sm text-orange-500 hover:text-orange-600">
          ← 返回首页
        </Link>
      </div>
    </div>
  );
}
