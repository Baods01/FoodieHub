import { useState } from 'react';
import type { Comment } from '../../types/comment';
import { LikeButton } from './LikeButton';
import { ReplyBox } from './ReplyBox';

interface CommentCardProps {
  comment: Comment;
  onLike: (id: number) => void;
  onReply: (commentId: number, content: string, targetUserName?: string) => void;
}

export function CommentCard({ comment, onLike, onReply }: CommentCardProps) {
  const [replyBoxVisible, setReplyBoxVisible] = useState(false);
  const [replyTarget, setReplyTarget] = useState<string | undefined>(undefined);

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
    onReply(comment.id, content, replyTarget);
    setReplyBoxVisible(false);
    setReplyTarget(undefined);
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
      {(comment as any).images.length > 0 && (
        <div className="mt-2 grid max-w-xs grid-cols-3 gap-1">
          {(comment as any).images.slice(0, 3).map((img: any, idx: any) => (
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
            setReplyTarget(undefined);
            setReplyBoxVisible((prev) => !prev);
          }}
          className="inline-flex items-center gap-1 text-sm text-gray-400 transition-colors duration-200 hover:text-orange-400"
        >
          <span className="text-base leading-none">{'↩'}</span>
          <span>回复</span>
        </button>
      </div>

      {/* Replies */}
      {(comment as any).replies.length > 0 && (
        <div className="ml-8 mt-2 border-l-2 border-gray-100 pl-4 space-y-3">
          {(comment as any).replies.map((reply: any) => (
            <div key={reply.id} className="py-1">
              <div className="flex items-center gap-2">
                <div className="h-6 w-6 flex-shrink-0 overflow-hidden rounded-full bg-gray-200">
                  {(reply.user?.avatar ?? null) ? (
                    <img
                      src={(reply.user?.avatar ?? null)}
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
              <button
                type="button"
                onClick={() => {
                  setReplyTarget((reply.user?.username ?? ''));
                  setReplyBoxVisible(true);
                }}
                className="mt-1 text-xs text-gray-400 hover:text-orange-400 transition-colors duration-200"
              >
                回复
              </button>
            </div>
          ))}
        </div>
      )}

      {/* ReplyBox */}
      {replyBoxVisible && (
        <div className="ml-8 mt-2">
          <ReplyBox
            parentId={comment.id}
            targetUserName={replyTarget}
            onSubmit={handleReply}
            onCancel={() => {
              setReplyBoxVisible(false);
              setReplyTarget(undefined);
            }}
          />
        </div>
      )}
    </div>
  );
}
