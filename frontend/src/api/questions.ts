import type { Question, Answer } from '../types/question';
import type { PaginatedResult } from '../types/common';

export async function fetchQuestions(
  shopId: number,
  page: number,
): Promise<PaginatedResult<Question>> {
  return mockFetchQuestions(shopId, page);
}

export async function postQuestion(
  shopId: number,
  title: string,
  content: string,
): Promise<Question> {
  return mockPostQuestion(shopId, title, content);
}

export async function postAnswer(
  questionId: number,
  content: string,
): Promise<Answer> {
  return mockPostAnswer(questionId, content);
}

// ===== Mock 数据 =====

const delay = () => new Promise((r) => setTimeout(r, 200 + Math.random() * 400));

const mockQuestions: Question[] = [
  {
    id: 1,
    shopId: 1,
    userId: 30,
    userName: '甜食控',
    userAvatar: null,
    title: '这里有没有空调？',
    content: '夏天快到了，想问问店里有空调吗？怕热星人很关心这个！',
    answerCount: 2,
    latestAnswerAt: '2026-05-13T16:00:00',
    createdAt: '2026-05-12T10:00:00',
    answers: [
      { id: 1, questionId: 1, userId: 31, userName: '常客小张', userAvatar: null, content: '有空调的，挺凉快！', createdAt: '2026-05-12T14:00:00' },
      { id: 2, questionId: 1, userId: 32, userName: '附近学生', userAvatar: null, content: '有的，不过下午人多的时候会热一点', createdAt: '2026-05-13T16:00:00' },
    ],
  },
  {
    id: 2,
    shopId: 1,
    userId: 33,
    userName: '减肥中',
    userAvatar: null,
    title: '有无糖选项吗？',
    content: '在控糖，想问下糖水的甜度可以调吗？有没有代糖选项？',
    answerCount: 1,
    latestAnswerAt: '2026-05-11T09:00:00',
    createdAt: '2026-05-10T20:00:00',
    answers: [
      { id: 3, questionId: 2, userId: 34, userName: '老板', userAvatar: null, content: '可以的！糖水可以选少糖、微糖，也有木糖醇选项', createdAt: '2026-05-11T09:00:00' },
    ],
  },
  {
    id: 3,
    shopId: 1,
    userId: 35,
    userName: '外卖党',
    userAvatar: null,
    title: '支持外卖吗？',
    content: '想问下有没有外卖群或者能送到宿舍楼下吗？',
    answerCount: 0,
    latestAnswerAt: '2026-05-09T18:00:00',
    createdAt: '2026-05-09T18:00:00',
    answers: [],
  },
];

const mockSorted = [...mockQuestions].sort(
  (a, b) => new Date(b.latestAnswerAt).getTime() - new Date(a.latestAnswerAt).getTime(),
);

function mockFetchQuestions(_shopId: number, page: number): Promise<PaginatedResult<Question>> {
  const pageSize = 10;
  const start = (page - 1) * pageSize;
  const data = mockSorted.slice(start, start + pageSize);
  return delay().then(() => ({
    data,
    total: mockSorted.length,
    page,
    pageSize,
    hasMore: start + pageSize < mockSorted.length,
  }));
}

function mockPostQuestion(_shopId: number, title: string, content: string): Promise<Question> {
  const now = new Date().toISOString();
  const q: Question = {
    id: Date.now(),
    shopId: _shopId,
    userId: 0,
    userName: '我',
    userAvatar: null,
    title,
    content,
    answerCount: 0,
    latestAnswerAt: now,
    createdAt: now,
    answers: [],
  };
  mockSorted.unshift(q);
  return delay().then(() => q);
}

const answerIdCounter = 100;
const qAnswerMap: Record<number, Answer[]> = {};
mockQuestions.forEach((q) => { qAnswerMap[q.id] = [...q.answers]; });

function mockPostAnswer(questionId: number, content: string): Promise<Answer> {
  const a: Answer = {
    id: ++answerIdCounter,
    questionId,
    userId: 0,
    userName: '我',
    userAvatar: null,
    content,
    createdAt: new Date().toISOString(),
  };
  if (!qAnswerMap[questionId]) qAnswerMap[questionId] = [];
  qAnswerMap[questionId].push(a);
  const q = mockSorted.find((x) => x.id === questionId);
  if (q) {
    q.answers = qAnswerMap[questionId];
    q.answerCount = q.answers.length;
    q.latestAnswerAt = a.createdAt;
  }
  return delay().then(() => a);
}
