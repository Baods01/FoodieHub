import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { fetchShopDetail, submitRating, toggleFavorite } from '../api/shops';
import type { ShopDetail } from '../types/shop';
import { ShopCarousel } from '../components/shop/ShopCarousel';
import { ShopInfoSection } from '../components/shop/ShopInfoSection';
import { RatingSection } from '../components/shop/RatingSection';
import { CommentSection } from '../components/comment/CommentSection';
import { QASection } from '../components/question/QASection';
import { MenuSection } from '../components/menu/MenuSection';
import { AlbumSection } from '../components/album/AlbumSection';
import { ShopDetailSkeleton } from '../components/shop/ShopDetailSkeleton';
import { LoginPromptModal } from '../components/shop/LoginPromptModal';
import { ErrorState } from '../components/ui/ErrorState';

export function ShopDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [shop, setShop] = useState<ShopDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [loginModalOpen, setLoginModalOpen] = useState(false);
  const [loginModalMsg, setLoginModalMsg] = useState('');
  const isLoggedIn = useAuthStore((s) => s.isLoggedIn);
  const shopId = Number(id);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    setError(false);
    fetchShopDetail(shopId)
      .then(setShop)
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const promptLogin = (msg: string) => {
    setLoginModalMsg(msg);
    setLoginModalOpen(true);
  };

  const handleRetry = () => {
    setError(false);
    setLoading(true);
    fetchShopDetail(shopId)
      .then(setShop)
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  };

  // Loading state
  if (loading) {
    return <ShopDetailSkeleton />;
  }

  // Error state
  if (error) {
    return <ErrorState onRetry={handleRetry} />;
  }

  // Not found state
  if (!shop) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <p className="text-gray-500 text-base">店铺不存在或已被封禁</p>
        <Link
          to="/"
          className="mt-4 rounded-lg bg-orange-500 px-6 py-2 text-sm text-white transition-colors hover:bg-orange-600"
        >
          返回首页
        </Link>
      </div>
    );
  }

  // Main render
  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-12">
      <ShopCarousel images={shop.albumImages} />

      <ShopInfoSection
        name={shop.name}
        category={shop.category}
        area={shop.area}
        description={shop.description}
      />

      <RatingSection
        rating={shop.rating}
        totalRatings={shop.totalRatings}
        distribution={shop.ratingDistribution}
        userRating={shop.userRating}
        onRate={(r) =>
          submitRating(shop.id, r).then(() => {
            setShop((prev) => (prev ? { ...prev, userRating: r } : prev));
          })
        }
        isLoggedIn={isLoggedIn}
        onLoginPrompt={() => promptLogin('登录后即可评分')}
      />

      <hr className="border-gray-100" />

      <CommentSection
        shopId={shop.id}
        isLoggedIn={isLoggedIn}
        onLoginPrompt={() => promptLogin('登录后即可评论')}
      />

      <hr className="border-gray-100" />

      <QASection
        shopId={shop.id}
        isLoggedIn={isLoggedIn}
        onLoginPrompt={() => promptLogin('登录后即可提问')}
      />

      <hr className="border-gray-100" />

      <MenuSection
        items={shop.menu}
        isLoggedIn={isLoggedIn}
        onUpload={() => {}}
      />

      <hr className="border-gray-100" />

      <AlbumSection
        images={shop.albumImages}
        isLoggedIn={isLoggedIn}
        onUpload={() => {}}
      />

      <LoginPromptModal
        isOpen={loginModalOpen}
        message={loginModalMsg}
        onClose={() => setLoginModalOpen(false)}
        onGoLogin={() => {
          setLoginModalOpen(false);
          navigate('/login');
        }}
      />
    </div>
  );
}
