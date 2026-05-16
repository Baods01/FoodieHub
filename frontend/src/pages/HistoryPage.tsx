import { Link } from 'react-router-dom';
import { Clock } from 'lucide-react';

export default function HistoryPage() {
  return (
    <div className="max-w-4xl mx-auto py-8">
      <div className="flex items-center gap-3 mb-6">
        <Clock size={24} className="text-blue-500" />
        <h1 className="text-xl font-bold">浏览历史</h1>
      </div>
      <div className="bg-white rounded-xl shadow-sm p-12 text-center">
        <Clock size={48} className="text-gray-200 mx-auto" />
        <p className="text-gray-500 mt-3">暂无浏览记录</p>
        <Link to="/" className="inline-block mt-3 text-sm text-orange-500 hover:text-orange-600">
          去看看 →
        </Link>
      </div>
    </div>
  );
}
