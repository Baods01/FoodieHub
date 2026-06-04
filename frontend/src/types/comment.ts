/** 评论 — 对齐后端 CommentData */
export interface Comment {
  id: number;
  shop_id: number;
  user: { id: number; username: string; avatar: string | null } | null;
  content: string;
  like_count: number;
  reply_count: number;
  has_liked: boolean;
  created_at: string;
  /** 评论附带图片URL（后端 single image 字段） */
  image?: string | null;
  /** 本地乐观更新用：回复列表 */
  replies?: CommentReply[];
}

/** 评论回复 — 对齐后端 ReplyData */
export interface CommentReply {
  id: number;
  comment_id: number;
  user: { id: number; username: string; avatar: string | null } | null;
  content: string;
  reply_to_user: { id: number; username: string } | null;
  like_count: number;
  has_liked: boolean;
  created_at: string;
}
