import { Fragment, useState, useEffect, useCallback } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { X } from 'lucide-react';
import type { Comment } from '../../types/comment';
import { fetchComments, postComment, toggleCommentLike, replyComment } from '../../api/comments';
import { CommentInput } from './CommentInput';
import { CommentCard } from './CommentCard';

interface AllCommentsModalProps {
  shopId: number;
  isOpen: boolean;
  onClose: () => void;
  isLoggedIn: boolean;
  onLoginPrompt: () => void;
}

export default function AllCommentsModal({
  shopId,
  isOpen,
  onClose,
  isLoggedIn,
  onLoginPrompt,
}: AllCommentsModalProps) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const loadComments = useCallback(
    (pageNum: number, append: boolean) => {
      if (append) setIsLoadingMore(true);
      else setIsLoading(true);

      return fetchComments(shopId, pageNum)
        .then((result) => {
          if (append) {
            setComments((prev) => [...prev, ...result.data]);
          } else {
            setComments(result.data);
          }
          setHasMore(result.hasMore);
        })
        .finally(() => {
          setIsLoading(false);
          setIsLoadingMore(false);
        });
    },
    [shopId],
  );

  useEffect(() => {
    if (isOpen) {
      setPage(1);
      loadComments(1, false);
    }
  }, [isOpen, loadComments]);

  const handleSubmit = async (content: string) => {
    if (!isLoggedIn) {
      onLoginPrompt();
      return;
    }
    setIsSubmitting(true);
    try {
      const newComment = await postComment(shopId, content);
      setComments((prev) => [newComment, ...prev]);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleLike = async (commentId: number) => {
    if (!isLoggedIn) {
      onLoginPrompt();
      return;
    }
    // Optimistic update
    setComments((prev) =>
      prev.map((c) =>
        c.id === commentId
          ? { ...c, isLiked: !c.isLiked, likeCount: c.isLiked ? c.likeCount - 1 : c.likeCount + 1 }
          : c,
      ),
    );
    try {
      await toggleCommentLike(commentId);
    } catch {
      // Rollback
      setComments((prev) =>
        prev.map((c) =>
          c.id === commentId
            ? { ...c, isLiked: !c.isLiked, likeCount: c.isLiked ? c.likeCount - 1 : c.likeCount + 1 }
            : c,
        ),
      );
    }
  };

  const handleReply = async (parentId: number, content: string) => {
    if (!isLoggedIn) {
      onLoginPrompt();
      return;
    }
    try {
      const newReply = await replyComment(parentId, content);
      setComments((prev) =>
        prev.map((c) =>
          c.id === parentId
            ? { ...c, replies: [...(c.replies || []), newReply], replyCount: c.replyCount + 1 }
            : c,
        ),
      );
    } catch {
      // silently fail
    }
  };

  const handleLoadMore = () => {
    if (!hasMore || isLoadingMore) return;
    const next = page + 1;
    setPage(next);
    loadComments(next, true);
  };

  return (
    <Transition show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        {/* Backdrop */}
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-200"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-150"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/40" />
        </Transition.Child>

        {/* Full-screen panel */}
        <div className="fixed inset-0 overflow-hidden">
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-200"
            enterFrom="opacity-0 scale-95"
            enterTo="opacity-100 scale-100"
            leave="ease-in duration-150"
            leaveFrom="opacity-100 scale-100"
            leaveTo="opacity-0 scale-95"
          >
            <Dialog.Panel className="h-full w-full bg-white flex flex-col">
              {/* Header */}
              <div className="flex items-center justify-between px-4 h-14 border-b border-gray-200 flex-shrink-0">
                <button
                  type="button"
                  onClick={onClose}
                  className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 transition-colors"
                >
                  &larr; 返回
                </button>
                <Dialog.Title className="text-base font-semibold">
                  全部评论
                </Dialog.Title>
                <button
                  type="button"
                  onClick={onClose}
                  className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <X size={20} />
                </button>
              </div>

              {/* Content */}
              <div className="flex-1 overflow-y-auto">
                {/* Comment input */}
                <div className="px-4 py-3 border-b border-gray-100">
                  <CommentInput
                    onSubmit={handleSubmit}
                    isSubmitting={isSubmitting}
                    isLoggedIn={isLoggedIn}
                    onLoginPrompt={onLoginPrompt}
                  />
                </div>

                {/* Loading */}
                {isLoading && (
                  <div className="px-4 py-8 space-y-4">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="animate-pulse space-y-2">
                        <div className="h-4 w-24 bg-gray-200 rounded" />
                        <div className="h-3 w-full bg-gray-100 rounded" />
                        <div className="h-3 w-3/4 bg-gray-100 rounded" />
                      </div>
                    ))}
                  </div>
                )}

                {/* Empty */}
                {!isLoading && comments.length === 0 && (
                  <div className="flex items-center justify-center py-20 text-sm text-gray-400">
                    还没有评论
                  </div>
                )}

                {/* Comments */}
                {!isLoading && comments.length > 0 && (
                  <div className="divide-y divide-gray-100">
                    {[...comments]
                      .sort((a, b) => b.likeCount - a.likeCount)
                      .map((comment) => (
                        <div key={comment.id} className="px-4">
                          <CommentCard
                            comment={comment}
                            onLike={handleLike}
                            onReply={handleReply}
                          />
                        </div>
                      ))}
                  </div>
                )}

                {/* Load more */}
                {!isLoading && hasMore && comments.length > 0 && (
                  <div className="text-center py-4">
                    <button
                      type="button"
                      onClick={handleLoadMore}
                      disabled={isLoadingMore}
                      className="rounded-lg border border-gray-200 px-6 py-2 text-sm text-gray-500 hover:border-orange-200 hover:text-orange-500 disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
                    >
                      {isLoadingMore ? '加载中...' : '加载更多'}
                    </button>
                  </div>
                )}
              </div>
            </Dialog.Panel>
          </Transition.Child>
        </div>
      </Dialog>
    </Transition>
  );
}
