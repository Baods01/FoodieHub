/** 问答 - 问题 — 对齐后端 QuestionData */
export interface Question {
  id: number;
  shop_id: number;
  user: { id: number; username: string; avatar: string | null } | null;
  title: string;
  content: string | null;
  like_count: number;
  created_at: string;
  /** 本地乐观更新用：回答列表 */
  answers?: Answer[];
  /** 本地乐观更新用：回答数量 */
  answerCount?: number;
}

/** 问答 - 回答 — 对齐后端 AnswerData */
export interface Answer {
  id: number;
  question_id: number;
  user: { id: number; username: string; avatar: string | null } | null;
  content: string;
  reply_to_user: { id: number; username: string } | null;
  like_count: number;
  has_liked: boolean;
  created_at: string;
}
