/** 评论 */
export interface Comment {
  id: number;
  shopId: number;
  userId: number;
  userName: string;
  userAvatar: string | null;
  content: string;
  images: string[];
  likeCount: number;
  isLiked: boolean;
  createdAt: string;
  replies: CommentReply[];
  replyCount: number;
}

/** 评论回复 */
export interface CommentReply {
  id: number;
  commentId: number;
  userId: number;
  userName: string;
  userAvatar: string | null;
  content: string;
  targetUserName?: string;
  createdAt: string;
}
