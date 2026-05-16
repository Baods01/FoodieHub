import { useState, useEffect, useCallback } from 'react';
import type { Comment } from '../../types/comment';
import {
  fetchComments,
  postComment,
  toggleCommentLike,
  replyComment,
} from '../../api/comments';
import { CommentInput } from './CommentInput';
import { CommentCard } from './CommentCard';

interface CommentSectionProps {
  shopId: number;
  isLoggedIn: boolean;
  onLoginPrompt: () => void;
  maxCount?: number;
  onViewAll?: () => void;
}

/** A single skeleton comment block used during first load */
function CommentSkeleton() {
  return (
    <div className="animate-pulse py-4">
      <div className="flex items-center gap-2">
        <div className="h-8 w-8 rounded-full bg-gray-200" />
        <div className="h-4 w-24 rounded bg-gray-200" />
        <div className="h-3 w-12 rounded bg-gray-100" />
      </div>
      <div className="mt-3 space-y-2">
        <div className="h-3 w-full rounded bg-gray-200" />
        <div className="h-3 w-3/4 rounded bg-gray-200" />
      </div>
      <div className="mt-3 flex items-center gap-4">
        <div className="h-4 w-12 rounded bg-gray-200" />
        <div className="h-4 w-12 rounded bg-gray-200" />
      </div>
    </div>
  );
}

export function CommentSection({
  shopId,
  isLoggedIn,
  onLoginPrompt,
  maxCount = 5,
  onViewAll,
}: CommentSectionProps) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [isError, setIsError] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  /** Fetch a page and merge into state */
  const loadComments = useCallback(
    (pageNum: number, append: boolean) => {
      if (append) {
        setIsLoadingMore(true);
      } else {
        setIsLoading(true);
      }
      setIsError(false);

      return fetchComments(shopId, pageNum)
        .then((result) => {
          if (append) {
            setComments((prev) => [...prev, ...result.data]);
          } else {
            setComments(result.data);
          }
          setHasMore(result.hasMore);
        })
        .catch(() => {
          setIsError(true);
        })
        .finally(() => {
          setIsLoading(false);
          setIsLoadingMore(false);
        });
    },
    [shopId],
  );

  // First load
  useEffect(() => {
    loadComments(1, false);
  }, [loadComments]);

  /** Load more (pagination) */
  const handleLoadMore = () => {
    if (isLoadingMore || !hasMore) return;
    const nextPage = page + 1;
    setPage(nextPage);
    loadComments(nextPage, true);
  };

  /** Post a new top-level comment */
  const handleSubmitComment = (content: string) => {
    setIsSubmitting(true);
    postComment(shopId, content)
      .then((newComment) => {
        setComments((prev) => [newComment, ...prev]);
      })
      .catch(() => {
        // Silently fail — could add a toast in the future
      })
      .finally(() => {
        setIsSubmitting(false);
      });
  };

  /** Toggle like with optimistic update */
  const handleLike = (commentId: number) => {
    setComments((prev) =>
      prev.map((c) =>
        c.id === commentId
          ? {
              ...c,
              isLiked: !c.isLiked,
              likeCount: c.isLiked ? c.likeCount - 1 : c.likeCount + 1,
            }
          : c,
      ),
    );
    toggleCommentLike(commentId).catch(() => {
      // Revert on failure
      setComments((prev) =>
        prev.map((c) =>
          c.id === commentId
            ? {
                ...c,
                isLiked: !c.isLiked,
                likeCount: c.isLiked ? c.likeCount - 1 : c.likeCount + 1,
              }
            : c,
        ),
      );
    });
  };

  /** Reply to a comment */
  const handleReply = (
    commentId: number,
    content: string,
    targetUserName?: string,
  ) => {
    replyComment(commentId, content, targetUserName)
      .then((newReply) => {
        setComments((prev) =>
          prev.map((c) =>
            c.id === commentId
              ? {
                  ...c,
                  replies: [...c.replies, newReply],
                }
              : c,
          ),
        );
      })
      .catch(() => {
        // Silently fail
      });
  };

  /** Retry after error */
  const handleRetry = () => {
    setPage(1);
    loadComments(1, false);
  };

  // --- Render ---

  return (
    <div className="space-y-4">
      {/* Title */}
      <h3 className="text-base font-bold text-gray-800 pl-3 border-l-[3px] border-orange-400">评论</h3>

      {/* Comment input */}
      <CommentInput
        onSubmit={handleSubmitComment}
        isSubmitting={isSubmitting}
        isLoggedIn={isLoggedIn}
        onLoginPrompt={onLoginPrompt}
      />

      {/* First load skeleton */}
      {isLoading && (
        <div className="divide-y divide-gray-100">
          <CommentSkeleton />
          <CommentSkeleton />
          <CommentSkeleton />
        </div>
      )}

      {/* Error state */}
      {isError && !isLoading && (
        <div className="flex flex-col items-center justify-center py-8">
          <p className="text-gray-400 text-sm">加载失败</p>
          <button
            type="button"
            onClick={handleRetry}
            className="mt-3 rounded-lg border border-orange-400 px-4 py-1.5 text-sm text-orange-500 transition-colors duration-200 hover:bg-orange-50"
          >
            点击重试
          </button>
        </div>
      )}

      {/* Empty state */}
      {!isLoading && !isError && comments.length === 0 && (
        <p className="py-8 text-center text-sm text-gray-400">
          还没有评论，来写第一条吧
        </p>
      )}

      {/* Comment list */}
      {!isLoading && !isError && comments.length > 0 && (
        <div className="divide-y divide-gray-100">
          {/* Sort by likeCount desc, slice for preview if onViewAll */}
          {[...comments]
            .sort((a, b) => b.likeCount - a.likeCount)
            .slice(0, onViewAll ? maxCount : undefined)
            .map((comment) => (
              <CommentCard
                key={comment.id}
                comment={comment}
                onLike={handleLike}
                onReply={handleReply}
              />
            ))}
        </div>
      )}

      {/* View all button (preview mode) */}
      {!isLoading && !isError && onViewAll && comments.length > maxCount && (
        <div className="text-center mt-4">
          <button
            type="button"
            onClick={onViewAll}
            className="rounded-lg border border-orange-200 px-6 py-2 text-sm text-orange-500 hover:bg-orange-50 transition-colors"
          >
            查看全部 {comments.length} 条评论 &gt;
          </button>
        </div>
      )}

      {/* Load more (full mode - no onViewAll) */}
      {!isLoading && !isError && !onViewAll && hasMore && comments.length > 0 && (
        <div className="text-center">
          <button
            type="button"
            onClick={handleLoadMore}
            disabled={isLoadingMore}
            className="rounded-lg border border-gray-200 px-6 py-2 text-sm text-gray-500 transition-colors duration-200 hover:border-orange-200 hover:text-orange-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isLoadingMore ? '加载中...' : '加载更多'}
          </button>
        </div>
      )}
    </div>
  );
}
