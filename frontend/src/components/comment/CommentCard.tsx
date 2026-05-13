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
          {comment.userAvatar ? (
            <img
              src={comment.userAvatar}
              alt={comment.userName}
              className="h-full w-full object-cover"
            />
          ) : (
            <div className="flex h-full w-full items-center justify-center bg-gray-300 text-sm font-medium text-gray-600">
              {comment.userName.charAt(0)}
            </div>
          )}
        </div>

        <div className="flex items-baseline gap-2">
          <span className="text-sm font-medium text-gray-800">
            {comment.userName}
          </span>
          <span className="text-xs text-gray-400">
            {formatTime(comment.createdAt)}
          </span>
        </div>
      </div>

      {/* Content text */}
      <p className="mt-2 text-sm leading-relaxed text-gray-700">
        {comment.content}
      </p>

      {/* Images grid: max 3, grid-cols-3 gap-1 */}
      {comment.images.length > 0 && (
        <div className="mt-2 grid max-w-xs grid-cols-3 gap-1">
          {comment.images.slice(0, 3).map((img, idx) => (
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
          count={comment.likeCount}
          isLiked={comment.isLiked}
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
      {comment.replies.length > 0 && (
        <div className="ml-8 mt-2 border-l-2 border-gray-100 pl-4 space-y-3">
          {comment.replies.map((reply) => (
            <div key={reply.id} className="py-1">
              <div className="flex items-center gap-2">
                <div className="h-6 w-6 flex-shrink-0 overflow-hidden rounded-full bg-gray-200">
                  {reply.userAvatar ? (
                    <img
                      src={reply.userAvatar}
                      alt={reply.userName}
                      className="h-full w-full object-cover"
                    />
                  ) : (
                    <div className="flex h-full w-full items-center justify-center bg-gray-300 text-xs font-medium text-gray-600">
                      {reply.userName.charAt(0)}
                    </div>
                  )}
                </div>
                <span className="text-sm font-medium text-gray-800">
                  {reply.userName}
                </span>
                <span className="text-xs text-gray-400">
                  {formatTime(reply.createdAt)}
                </span>
              </div>
              <p className="mt-1 text-sm leading-relaxed text-gray-600">
                {reply.targetUserName && (
                  <span className="text-orange-500">@{reply.targetUserName} </span>
                )}
                {reply.content}
              </p>
              <button
                type="button"
                onClick={() => {
                  setReplyTarget(reply.userName);
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
