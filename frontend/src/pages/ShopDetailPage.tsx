import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { toggleFavorite } from '../api/favorites';
import { fetchShopDetail, submitRating } from '../api/shops';
import type { ShopDetail } from '../types/shop';
import { getCategoryName, getAreaName, getDiningMethods } from '../types/shop';
import { ShopCarousel } from '../components/shop/ShopCarousel';
import { ShopInfoSection } from '../components/shop/ShopInfoSection';
import { RatingSection } from '../components/shop/RatingSection';
import { CommentSection } from '../components/comment/CommentSection';
import { QASection } from '../components/question/QASection';
import { MenuSection } from '../components/menu/MenuSection';
import MenuUploadModal from '../components/menu/MenuUploadModal';
import FeedbackModal from '../components/shop/FeedbackModal';
import { AlbumSection } from '../components/album/AlbumSection';
import { AlertCircle } from 'lucide-react';
import { ShopDetailSkeleton } from '../components/shop/ShopDetailSkeleton';
import { LoginPromptModal } from '../components/shop/LoginPromptModal';
import AllCommentsModal from '../components/comment/AllCommentsModal';
import AllQAModal from '../components/question/AllQAModal';
import AllMenuModal from '../components/menu/AllMenuModal';
import AllAlbumModal from '../components/album/AllAlbumModal';
import SectionCard from '../components/ui/SectionCard';

export function ShopDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [shop, setShop] = useState<ShopDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | false>(false);
  const [loginModalOpen, setLoginModalOpen] = useState(false);
  const [loginModalMsg, setLoginModalMsg] = useState('');
  const [commentsModalOpen, setCommentsModalOpen] = useState(false);
  const [qaModalOpen, setQaModalOpen] = useState(false);
  const [menuModalOpen, setMenuModalOpen] = useState(false);
  const [albumModalOpen, setAlbumModalOpen] = useState(false);
  const [menuUploadOpen, setMenuUploadOpen] = useState(false);
  const [feedbackOpen, setFeedbackOpen] = useState(false);
  const isLoggedIn = useAuthStore((s) => s.isLoggedIn);
  const shopId = Number(id);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    setError(false);
    fetchShopDetail(shopId)
      .then((data: any) => { setShop(data); })
      .catch((e: any) => setError(e?.response?.data?.detail || true))
      .finally(() => setLoading(false));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const promptLogin = (msg: string) => {
    setLoginModalMsg(msg);
    setLoginModalOpen(true);
  };

  const handleToggleFavorite = () => {
    const prev = shop!;
    const nextFav = !prev.is_favorited;
    setShop({ ...prev, is_favorited: nextFav, favorite_count: prev.favorite_count + (nextFav ? 1 : -1) });
    toggleFavorite(shopId).catch(() => {
      setShop(prev);
    });
  };

  const handleRefresh = () => {
    fetchShopDetail(shopId)
      .then((data: any) => { setShop(data); })
      .catch(() => {});
  };

  const handleRetry = () => {
    setError(false);
    setLoading(true);
    fetchShopDetail(shopId)
      .then((data: any) => { setShop(data); })
      .catch((e: any) => setError(e?.response?.data?.detail || true))
      .finally(() => setLoading(false));
  };

  if (loading) {
    return <ShopDetailSkeleton />;
  }

  if (error) {
    const errMsg = typeof error === 'string' ? error : undefined;
    const isBanned = errMsg === '该店铺已被封禁';
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <AlertCircle size={48} className="text-red-400" />
        <p className="text-gray-500 text-base mt-4">{errMsg || '加载失败'}</p>
        {!isBanned && (
          <button
            type="button"
            onClick={handleRetry}
            className="px-6 py-2 mt-4 rounded-lg border border-orange-400 text-orange-500 hover:bg-orange-50 transition-colors duration-200"
          >
            点击重试
          </button>
        )}
        <Link
          to="/"
          className="mt-4 rounded-lg bg-orange-500 px-6 py-2 text-sm text-white transition-colors hover:bg-orange-600"
        >
          返回首页
        </Link>
      </div>
    );
  }

  if (!shop) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <p className="text-gray-500 text-base">店铺不存在或已被封禁</p>
        <Link to="/" className="mt-4 rounded-lg bg-orange-500 px-6 py-2 text-sm text-white transition-colors hover:bg-orange-600">
          返回首页
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-5 pb-12">
      <ShopCarousel images={shop.images.map(i => i.url)} />

      <SectionCard>
        <ShopInfoSection
          name={shop.name}
          category={getCategoryName(shop.dict_data)}
          area={getAreaName(shop.dict_data)}
          description={shop.description}
          diningMethods={getDiningMethods(shop.dict_data)}
          isFavorited={shop.is_favorited}
          favoriteCount={shop.favorite_count}
          isLoggedIn={isLoggedIn}
          onToggleFavorite={handleToggleFavorite}
          onLoginPrompt={() => promptLogin('登录后即可收藏')}
          onFeedback={() => setFeedbackOpen(true)}
        />
      </SectionCard>

      <SectionCard>
        <RatingSection
          rating={shop.average_rating}
          totalRatings={shop.rating_distribution.total}
          distribution={{
            1: shop.rating_distribution.star_1,
            2: shop.rating_distribution.star_2,
            3: shop.rating_distribution.star_3,
            4: shop.rating_distribution.star_4,
            5: shop.rating_distribution.star_5,
          }}
          userRating={shop.user_rating?.score ?? null}
          onRate={(r) =>
            submitRating(shop.id, r).then(() => {
              setShop((prev) => (prev ? { ...prev, user_rating: { score: r } } : prev));
            })
          }
          isLoggedIn={isLoggedIn}
          onLoginPrompt={() => promptLogin('登录后即可评分')}
        />
      </SectionCard>

      <SectionCard>
        <CommentSection
          shopId={shop.id}
          isLoggedIn={isLoggedIn}
          onLoginPrompt={() => promptLogin('登录后即可评论')}
          maxCount={5}
          onViewAll={() => setCommentsModalOpen(true)}
        />
      </SectionCard>

      <SectionCard>
        <QASection
          shopId={shop.id}
          isLoggedIn={isLoggedIn}
          onLoginPrompt={() => promptLogin('登录后即可提问')}
          maxCount={3}
          onViewAll={() => setQaModalOpen(true)}
        />
      </SectionCard>

      <SectionCard>
        <MenuSection
          items={shop.menu_items}
          isLoggedIn={isLoggedIn}
          onUpload={() => setMenuUploadOpen(true)}
          maxCount={6}
          onViewAll={() => setMenuModalOpen(true)}
        />
      </SectionCard>

      <SectionCard>
        <AlbumSection
          images={shop.images.map(i => i.url)}
          shopId={shop.id}
          isLoggedIn={isLoggedIn}
          onUpload={handleRefresh}
          maxCount={6}
          onViewAll={() => setAlbumModalOpen(true)}
        />
      </SectionCard>

      <AllCommentsModal
        shopId={shop.id}
        isOpen={commentsModalOpen}
        onClose={() => setCommentsModalOpen(false)}
        isLoggedIn={isLoggedIn}
        onLoginPrompt={() => promptLogin('登录后即可互动')}
      />

      <AllQAModal
        shopId={shop.id}
        isOpen={qaModalOpen}
        onClose={() => setQaModalOpen(false)}
        isLoggedIn={isLoggedIn}
        onLoginPrompt={() => promptLogin('登录后即可提问')}
      />

      <AllMenuModal
        items={shop.menu_items}
        isOpen={menuModalOpen}
        onClose={() => setMenuModalOpen(false)}
      />

      <AllAlbumModal
        images={shop.images.map(i => i.url)}
        isOpen={albumModalOpen}
        onClose={() => setAlbumModalOpen(false)}
      />

      <MenuUploadModal
        shopId={shop.id}
        isOpen={menuUploadOpen}
        onClose={() => setMenuUploadOpen(false)}
        onSuccess={handleRefresh}
      />

      <FeedbackModal
        shopId={shop.id}
        isOpen={feedbackOpen}
        onClose={() => setFeedbackOpen(false)}
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
