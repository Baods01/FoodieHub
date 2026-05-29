/** 问答 - 问题 — 对齐后端 QuestionData */
export interface Question {
  id: number;
  shop_id: number;
  user: { id: number; username: string; avatar: string | null } | null;
  title: string;
  content: string | null;
  like_count: number;
  created_at: string;
}

/** 问答 - 回答 — 对齐后端 AnswerData */
export interface Answer {
  id: number;
  question_id: number;
  user: { id: number; username: string; avatar: string | null } | null;
  content: string;
  reply_to_user: { id: number; username: string } | null;
  like_count: number;
  created_at: string;
}
