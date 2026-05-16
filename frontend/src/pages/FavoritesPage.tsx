import { Link } from 'react-router-dom';
import { Heart } from 'lucide-react';

export default function FavoritesPage() {
  return (
    <div className="max-w-4xl mx-auto py-8">
      <div className="flex items-center gap-3 mb-6">
        <Heart size={24} className="text-red-500" />
        <h1 className="text-xl font-bold">收藏夹</h1>
      </div>
      <div className="bg-white rounded-xl shadow-sm p-12 text-center">
        <Heart size={48} className="text-gray-200 mx-auto" />
        <p className="text-gray-500 mt-3">还没有收藏任何店铺</p>
        <Link to="/" className="inline-block mt-3 text-sm text-orange-500 hover:text-orange-600">
          去发现美食 →
        </Link>
      </div>
    </div>
  );
}
