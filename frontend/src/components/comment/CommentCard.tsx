import { useState, useEffect } from 'react';
import type { Comment, CommentReply } from '../../types/comment';
import { fetchReplies, toggleLike } from '../../api/comments';
import { LikeButton } from './LikeButton';
import { ReplyBox } from './ReplyBox';

interface CommentCardProps {
  comment: Comment;
  onLike: (id: number) => void;
  onReply: (commentId: number, content: string, replyToUserId?: number) => void;
}

export function CommentCard({ comment, onLike, onReply }: CommentCardProps) {
  const [replyBoxVisible, setReplyBoxVisible] = useState(false);
  const [replyTargetId, setReplyTargetId] = useState<number | undefined>(undefined);
  const [replyTargetName, setReplyTargetName] = useState<string | undefined>(undefined);
  const [replies, setReplies] = useState<CommentReply[] | undefined>(undefined);
  const [showReplies, setShowReplies] = useState(false);

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
      {/* Header: avatar + name + time */}
      <div className="flex items-center gap-2">
        {/* Avatar */}
        <div className="h-8 w-8 flex-shrink-0 overflow-hidden rounded-full bg-gray-200">
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

        <div className="flex items-baseline gap-2">
          <span className="text-sm font-medium text-gray-800">
            {(comment.user?.username ?? '')}
          </span>
          <span className="text-xs text-gray-400">
            {formatTime(comment.created_at)}
          </span>
        </div>
      </div>

      {/* Content text */}
      <p className="mt-2 text-sm leading-relaxed text-gray-700">
        {comment.content}
      </p>

      {/* Images grid: max 3, grid-cols-3 gap-1 */}
      {(comment.images?.length ?? 0) > 0 && (
        <div className="mt-2 grid max-w-xs grid-cols-3 gap-1">
          {(comment.images?.slice(0, 3) ?? []).map((img, idx) => (
            <div key={idx} className="aspect-square overflow-hidden rounded-lg">
              <img
                src={img}
                alt={`评论图片 ${idx + 1}`}
                className="h-full w-full object-cover"
              />
            </div>
          ))}
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
          {(displayReplies ?? []).map((reply) => (
            <div key={reply.id} className="py-1">
              <div className="flex items-center gap-2">
                <div className="h-6 w-6 flex-shrink-0 overflow-hidden rounded-full bg-gray-200">
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
                <span className="text-sm font-medium text-gray-800">
                  {(reply.user?.username ?? '')}
                </span>
                <span className="text-xs text-gray-400">
                  {formatTime(reply.created_at)}
                </span>
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
          ))}
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
    </div>
  );
}
