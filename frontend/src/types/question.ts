/** 问答 - 问题 */
export interface Question {
  id: number;
  shopId: number;
  userId: number;
  userName: string;
  userAvatar: string | null;
  title: string;
  content: string;
  answerCount: number;
  latestAnswerAt: string;
  createdAt: string;
  answers: Answer[];
}

/** 问答 - 回答 */
export interface Answer {
  id: number;
  questionId: number;
  userId: number;
  userName: string;
  userAvatar: string | null;
  content: string;
  targetUserName?: string;
  createdAt: string;
}
