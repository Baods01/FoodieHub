import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Trash2 } from 'lucide-react';
import type { Comment, CommentReply } from '../../types/comment';
import { fetchReplies, toggleLike, deleteComment, deleteReply } from '../../api/comments';
import { LikeButton } from './LikeButton';
import { ReplyBox } from './ReplyBox';

interface CommentCardProps {
  comment: Comment;
  onLike: (id: number) => void;
  onReply: (commentId: number, content: string, replyToUserId?: number) => void;
  currentUserId: number | null;
  isAdmin: boolean;
  onDelete: (commentId: number) => void;
  onDeleteReply: (replyId: number) => void;
}

export function CommentCard({ comment, onLike, onReply, currentUserId, isAdmin, onDelete, onDeleteReply }: CommentCardProps) {
  const [replyBoxVisible, setReplyBoxVisible] = useState(false);
  const [replyTargetId, setReplyTargetId] = useState<number | undefined>(undefined);
  const [replyTargetName, setReplyTargetName] = useState<string | undefined>(undefined);
  const [replies, setReplies] = useState<CommentReply[] | undefined>(undefined);
  const [showReplies, setShowReplies] = useState(false);
  const [deleteConfirmId, setDeleteConfirmId] = useState<number | null>(null);
  const [deleteType, setDeleteType] = useState<'comment' | 'reply' | null>(null);

  // 从后端加载回复
  useEffect(() => {
    if (comment.reply_count > 0) {
      fetchReplies(comment.id).then(setReplies).catch(() => {});
    }
  }, []);

  // 合并父组件乐观更新到本地状态，避免覆盖已有回复
  useEffect(() => {
    if (comment.replies && comment.replies.length > 0) {
      setReplies((prev) => {
        const existingIds = new Set((prev ?? []).map((r) => r.id));
        const newOnes = comment.replies!.filter((r) => !existingIds.has(r.id));
        return newOnes.length > 0 ? [...(prev ?? []), ...newOnes] : prev;
      });
    }
  }, [comment.replies]);

  const displayReplies = replies;

  const canDeleteComment = currentUserId !== null && (
    comment.user?.id === currentUserId || isAdmin
  );

  const handleReplyLike = (replyId: number) => {
    setReplies((prev) =>
      (prev ?? []).map((r) =>
        r.id === replyId
          ? { ...r, has_liked: !r.has_liked, like_count: r.has_liked ? r.like_count - 1 : r.like_count + 1 }
          : r,
      ),
    );
    toggleLike('comment_reply', replyId).catch(() => {
      // revert on failure
      setReplies((prev) =>
        (prev ?? []).map((r) =>
          r.id === replyId
            ? { ...r, has_liked: !r.has_liked, like_count: r.has_liked ? r.like_count - 1 : r.like_count + 1 }
            : r,
        ),
      );
    });
  };

  const handleDeleteComment = () => {
    setDeleteType('comment');
    setDeleteConfirmId(comment.id);
  };

  const handleDeleteReply = (replyId: number) => {
    setDeleteType('reply');
    setDeleteConfirmId(replyId);
  };

  const confirmDelete = () => {
    if (deleteConfirmId === null || deleteType === null) return;
    if (deleteType === 'comment') {
      deleteComment(deleteConfirmId).then(() => {
        onDelete(deleteConfirmId);
      }).catch((err: any) => {
        console.error('删除评论失败:', err?.response?.data || err);
      });
    } else if (deleteType === 'reply') {
      deleteReply(deleteConfirmId).then(() => {
        onDeleteReply(deleteConfirmId);
      }).catch((err: any) => {
        console.error('删除回复失败:', err?.response?.data || err);
      });
    }
    setDeleteConfirmId(null);
    setDeleteType(null);
  };

  const cancelDelete = () => {
    setDeleteConfirmId(null);
    setDeleteType(null);
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMin = Math.floor(diffMs / 60000);
    const diffHour = Math.floor(diffMs / 3600000);
    const diffDay = Math.floor(diffMs / 86400000);

    if (diffMin < 1) return '刚刚';
    if (diffMin < 60) return `${diffMin}分钟前`;
    if (diffHour < 24) return `${diffHour}小时前`;
    if (diffDay < 7) return `${diffDay}天前`;

    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    if (date.getFullYear() === now.getFullYear()) {
      return `${month}-${day}`;
    }
    return `${date.getFullYear()}-${month}-${day}`;
  };

  const handleReply = (content: string) => {
    onReply(comment.id, content, replyTargetId);
    setReplyBoxVisible(false);
    setReplyTargetId(undefined);
    setReplyTargetName(undefined);
  };

  return (
    <div className="py-4">
      {/* Header: avatar + name + time + delete button */}
      <div className="flex items-center gap-2">
        {/* Avatar */}
        <Link to={`/user/${comment.user?.id}`} className="flex-shrink-0">
          <div className="h-8 w-8 overflow-hidden rounded-full bg-gray-200">
            {(comment.user?.avatar ?? undefined) ? (
              <img
                src={(comment.user?.avatar ?? undefined)}
                alt={(comment.user?.username ?? '')}
                className="h-full w-full object-cover"
              />
            ) : (
              <div className="flex h-full w-full items-center justify-center bg-gray-300 text-sm font-medium text-gray-600">
                {(comment.user?.username ?? '').charAt(0)}
              </div>
            )}
          </div>
        </Link>

        <div className="flex items-baseline gap-2 flex-1">
          <Link to={`/user/${comment.user?.id}`} className="text-sm font-medium text-gray-800 hover:text-orange-500 transition-colors">
            {(comment.user?.username ?? '')}
          </Link>
          <span className="text-xs text-gray-400">
            {formatTime(comment.created_at)}
          </span>
        </div>

        {/* Delete button for comment */}
        {canDeleteComment && (
          <button
            type="button"
            onClick={handleDeleteComment}
            className="p-1 text-gray-400 hover:text-red-500 transition-colors"
            title="删除评论"
          >
            <Trash2 size={16} />
          </button>
        )}
      </div>

      {/* Content text */}
      <p className="mt-2 text-sm leading-relaxed text-gray-700">
        {comment.content}
      </p>

      {/* Images grid: single image */}
      {comment.image && (
        <div className="mt-2">
          <div className="max-w-xs overflow-hidden rounded-lg">
            <img
              src={comment.image}
              alt="评论图片"
              className="h-full w-full object-cover"
            />
          </div>
        </div>
      )}

      {/* Actions: like + reply */}
      <div className="mt-2 flex items-center gap-4">
        <LikeButton
          count={comment.like_count}
          isLiked={comment.has_liked}
          onClick={() => onLike(comment.id)}
        />
        <button
          type="button"
          onClick={() => {
            setReplyTargetId(undefined);
            setReplyTargetName(undefined);
            setReplyBoxVisible((prev) => !prev);
          }}
          className="inline-flex items-center gap-1 text-sm text-gray-400 transition-colors duration-200 hover:text-orange-400"
        >
          <span className="text-base leading-none">{'↩'}</span>
          <span>回复</span>
        </button>
      </div>

      {/* Toggle replies */}
      {(displayReplies?.length ?? 0) > 0 && (
        <button
          type="button"
          onClick={() => setShowReplies((v) => !v)}
          className="mt-2 text-sm text-orange-500 hover:text-orange-600 transition-colors"
        >
          {showReplies ? '收起回复' : `查看全部 ${displayReplies?.length ?? 0} 条回复`}
        </button>
      )}

      {/* Replies */}
      {showReplies && (displayReplies?.length ?? 0) > 0 && (
        <div className="ml-8 mt-2 border-l-2 border-gray-100 pl-4 space-y-3">
          {(displayReplies ?? []).map((reply) => {
            const canDeleteReply = currentUserId !== null && (
              reply.user?.id === currentUserId || isAdmin
            );
            return (
              <div key={reply.id} className="py-1">
                <div className="flex items-center gap-2">
                  <Link to={`/user/${reply.user?.id}`} className="flex-shrink-0">
                    <div className="h-6 w-6 overflow-hidden rounded-full bg-gray-200">
                      {(reply.user?.avatar) ? (
                        <img
                          src={reply.user.avatar}
                          alt={(reply.user?.username ?? '')}
                          className="h-full w-full object-cover"
                        />
                      ) : (
                        <div className="flex h-full w-full items-center justify-center bg-gray-300 text-xs font-medium text-gray-600">
                          {(reply.user?.username ?? '').charAt(0)}
                        </div>
                      )}
                    </div>
                  </Link>
                  <Link to={`/user/${reply.user?.id}`} className="text-sm font-medium text-gray-800 hover:text-orange-500 transition-colors">
                    {(reply.user?.username ?? '')}
                  </Link>
                  <span className="text-xs text-gray-400">
                    {formatTime(reply.created_at)}
                  </span>
                  {/* Delete button for reply */}
                  {canDeleteReply && (
                    <button
                      type="button"
                      onClick={() => handleDeleteReply(reply.id)}
                      className="p-0.5 text-gray-400 hover:text-red-500 transition-colors"
                      title="删除回复"
                    >
                      <Trash2 size={12} />
                    </button>
                  )}
                </div>
                <p className="mt-1 text-sm leading-relaxed text-gray-600">
                  {(reply.reply_to_user?.username ?? '') && (
                    <span className="text-orange-500">@{(reply.reply_to_user?.username ?? '')} </span>
                  )}
                  {reply.content}
                </p>
                <div className="flex items-center gap-3 mt-1">
                  <button
                    type="button"
                    onClick={() => {
                      setReplyTargetId(reply.user?.id);
                      setReplyTargetName(reply.user?.username ?? '');
                      setReplyBoxVisible(true);
                    }}
                    className="text-xs text-gray-400 hover:text-orange-400 transition-colors duration-200"
                  >
                    回复
                  </button>
                  <LikeButton
                    count={reply.like_count}
                    isLiked={reply.has_liked}
                    onClick={() => handleReplyLike(reply.id)}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* ReplyBox */}
      {replyBoxVisible && (
        <div className="ml-8 mt-2">
          <ReplyBox
            parentId={comment.id}
            targetUserName={replyTargetName}
            onSubmit={handleReply}
            onCancel={() => {
              setReplyBoxVisible(false);
              setReplyTargetId(undefined);
              setReplyTargetName(undefined);
            }}
          />
        </div>
      )}

      {/* Delete confirmation dialog */}
      {deleteConfirmId !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-lg shadow-lg p-6 w-80 max-w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">确认删除</h3>
            <p className="text-sm text-gray-600 mb-4">
              {deleteType === 'comment' ? '确定要删除这条评论吗？删除后无法恢复。' : '确定要删除这条回复吗？删除后无法恢复。'}
            </p>
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={cancelDelete}
                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
              >
                取消
              </button>
              <button
                type="button"
                onClick={confirmDelete}
                className="px-4 py-2 text-sm bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
              >
                确认删除
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}