import { useState } from 'react';
import { Star } from 'lucide-react';
import { Dialog, DialogPanel, DialogTitle } from '@headlessui/react';

export interface RatingSectionProps {
  rating: number;
  totalRatings: number;
  distribution: Record<1 | 2 | 3 | 4 | 5, number>;
  userRating: number | null;
  onRate: (rating: number) => void;
  isLoggedIn: boolean;
  onLoginPrompt: () => void;
}

const STAR_LABELS = [5, 4, 3, 2, 1] as const;

export function RatingSection({
  rating,
  totalRatings,
  distribution,
  userRating,
  onRate,
  isLoggedIn,
  onLoginPrompt,
}: RatingSectionProps) {
  const [hoveredRating, setHoveredRating] = useState(0);
  const [selectedRating, setSelectedRating] = useState(0);
  const [showConfirm, setShowConfirm] = useState(false);

  const isRated = userRating !== null;
  const maxCount = Math.max(...Object.values(distribution), 1);
  const hasRatings = totalRatings > 0;

  /* ---- Star fill helpers ---- */

  /** Whether a specific star (1-5) should appear filled right now. */
  const isStarFilled = (star: number): boolean => {
    if (showConfirm || selectedRating > 0) {
      return star <= selectedRating;
    }
    if (isRated) {
      return star <= userRating;
    }
    if (hoveredRating > 0) {
      return star <= hoveredRating;
    }
    return false;
  };

  /** Whether the star row is interactive (not yet rated, and user is logged in). */
  const canRate = !isRated && isLoggedIn;

  /* ---- Handlers ---- */

  const handleStarClick = (star: number) => {
    if (!isLoggedIn) {
      onLoginPrompt();
      return;
    }
    if (isRated) return;

    setSelectedRating(star);
    setShowConfirm(true);
  };

  const handleConfirm = () => {
    onRate(selectedRating);
    setShowConfirm(false);
    setSelectedRating(0);
    setHoveredRating(0);
  };

  const handleCancel = () => {
    setShowConfirm(false);
    setSelectedRating(0);
    setHoveredRating(0);
  };

  /* ---- Render helpers ---- */

  const renderStarButton = (star: number) => {
    const filled = isStarFilled(star);

    return (
      <button
        key={star}
        type="button"
        disabled={!canRate}
        onClick={() => handleStarClick(star)}
        onMouseEnter={() => canRate && setHoveredRating(star)}
        onMouseLeave={() => canRate && setHoveredRating(0)}
        className={canRate ? 'cursor-pointer' : 'cursor-default'}
        aria-label={`${star} 星`}
      >
        <Star
          size={20}
          className={
            filled
              ? 'fill-orange-400 text-orange-400'
              : isRated
                ? 'text-gray-300'
                : 'text-gray-300'
          }
        />
      </button>
    );
  };

  const renderDistributionBar = (star: 1 | 2 | 3 | 4 | 5) => {
    const pct = hasRatings ? (distribution[star] / maxCount) * 100 : 0;

    return (
      <div key={star} className="flex items-center gap-2">
        <span className="text-xs text-gray-500 w-6 flex-shrink-0">{star}星</span>
        <div className="flex-1 h-2 rounded-full bg-gray-200 overflow-hidden">
          {hasRatings && (
            <div
              className="h-full rounded-full bg-orange-400 transition-all duration-300"
              style={{ width: `${pct}%` }}
            />
          )}
        </div>
      </div>
    );
  };

  return (
    <div>
      {/* ---- Row 1: your rating ---- */}
      <div className="flex items-center justify-center gap-2 mb-5">
        <span className="text-sm text-gray-500">你的评分:</span>
        <div className="flex gap-1">
          {[1, 2, 3, 4, 5].map(renderStarButton)}
        </div>
      </div>

      {/* ---- Row 2: score + distribution bars + count ---- */}
      <div className="flex items-center gap-5">
        {/* Left: overall score */}
        <div className="flex flex-col items-center gap-0.5 flex-shrink-0">
          <Star size={28} className="fill-yellow-400 text-yellow-400" />
          <span className="text-2xl font-bold leading-none">
            {hasRatings ? rating.toFixed(1) : '--'}
          </span>
        </div>

        {/* Right: distribution bars + count */}
        <div className="flex-1 min-w-0">
          <div className="flex flex-col gap-1.5">
            {STAR_LABELS.map((star) => renderDistributionBar(star))}
          </div>

          <p className="text-sm text-gray-400 mt-2">
            {hasRatings ? `共 ${totalRatings} 人评分` : '暂无评分'}
          </p>
        </div>
      </div>

      {/* ---- Confirm dialog ---- */}
      <Dialog open={showConfirm} onClose={handleCancel} className="relative z-50">
        {/* Backdrop */}
        <div className="fixed inset-0 bg-black/30" aria-hidden="true" />

        {/* Panel container */}
        <div className="fixed inset-0 flex items-center justify-center p-4">
          <DialogPanel className="w-full max-w-xs rounded-xl bg-white p-6 shadow-xl">
            <DialogTitle className="text-center text-base font-semibold">
              确认评为 {selectedRating} 星？
            </DialogTitle>

            <div className="mt-5 flex gap-3">
              <button
                type="button"
                onClick={handleCancel}
                className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-600 transition-colors hover:bg-gray-50"
              >
                取消
              </button>
              <button
                type="button"
                onClick={handleConfirm}
                className="flex-1 rounded-lg bg-orange-500 px-4 py-2 text-sm text-white transition-colors hover:bg-orange-600"
              >
                确认
              </button>
            </div>
          </DialogPanel>
        </div>
      </Dialog>
    </div>
  );
}
