import type { Comment, CommentReply } from '../types/comment';
import type { PaginatedResult } from '../types/common';

// ===== 接口签名 =====
// 后端对接时取消注释以下行并删除 mock 分支:
// import apiClient from './client';
// import type { ApiResponse } from '../types/common';

export async function fetchComments(
  shopId: number,
  page: number,
): Promise<PaginatedResult<Comment>> {
  // const params = { page, page_size: 10, sort: 'likes' };
  // const { data } = await apiClient.get<ApiResponse<PaginatedResult<Comment>>>(`/shops/${shopId}/comments`, { params });
  // return data.data;
  return mockFetchComments(shopId, page);
}

export async function postComment(
  shopId: number,
  content: string,
  _images?: File[],
): Promise<Comment> {
  // const formData = new FormData();
  // formData.append('content', content);
  // _images?.forEach((f) => formData.append('images', f));
  // const { data } = await apiClient.post<ApiResponse<Comment>>(`/shops/${shopId}/comments`, formData);
  // return data.data;
  return mockPostComment(shopId, content);
}

export async function toggleCommentLike(commentId: number): Promise<boolean> {
  // const { data } = await apiClient.post<ApiResponse<boolean>>(`/comments/${commentId}/like`);
  // return data.data;
  return mockToggleCommentLike(commentId);
}

export async function replyComment(
  commentId: number,
  content: string,
  targetUserName?: string,
): Promise<CommentReply> {
  // const { data } = await apiClient.post<ApiResponse<CommentReply>>(`/comments/${commentId}/replies`, { content, targetUserName });
  // return data.data;
  return mockReplyComment(commentId, content, targetUserName);
}

// ===== Mock 数据 =====

const delay = () => new Promise((r) => setTimeout(r, 200 + Math.random() * 400));

const mockComments: Comment[] = Array.from({ length: 5 }, (_, i) => ({
  id: 100 + i,
  shopId: 1,
  userId: 10 + i,
  userName: ['陈同学', '李学长', '王老师', '小吃货', '美食家'][i],
  userAvatar: null,
  content: [
    '糖水很不错，芋圆很Q弹，老板人也很好！每次来都点招牌芋圆，分量足。',
    '价格实惠，分量也大，就是位置有点偏，在巷子深处。不过为了这碗糖水值得走一趟。',
    '带孩子来吃的，环境干净卫生，糖水甜度可以自己选，很贴心。推荐杨枝甘露。',
    '从大一开始吃到现在毕业，味道一直没变，每次回学校必来。满满都是回忆。',
    '一般般吧，没有传说中的那么惊艳，可能是期望太高了。但价格确实便宜。',
  ][i],
  images: i < 2
    ? [`https://picsum.photos/seed/comment${i}_1/400/300`, `https://picsum.photos/seed/comment${i}_2/400/300`].slice(0, i + 1)
    : [],
  likeCount: [15, 12, 8, 5, 3][i],
  isLiked: false,
  createdAt: ['2026-05-13T12:00:00', '2026-05-12T18:30:00', '2026-05-11T09:15:00', '2026-05-10T20:00:00', '2026-05-09T14:45:00'][i],
  replies: i === 0
    ? [
        { id: 201, commentId: 100, userId: 20, userName: '糖水老板', userAvatar: null, content: '谢谢同学支持！下次来给你多加两个芋圆 😊', createdAt: '2026-05-13T14:00:00' },
        { id: 202, commentId: 100, userId: 10, userName: '陈同学', userAvatar: null, content: '真的吗！那我明天就去 😆', targetUserName: '糖水老板', createdAt: '2026-05-13T15:00:00' },
      ]
    : [],
  replyCount: i === 0 ? 2 : 0,
}));

function mockFetchComments(_shopId: number, page: number): Promise<PaginatedResult<Comment>> {
  const pageSize = 10;
  const start = (page - 1) * pageSize;
  const data = mockComments.slice(start, start + pageSize);
  return delay().then(() => ({
    data,
    total: mockComments.length,
    page,
    pageSize,
    hasMore: start + pageSize < mockComments.length,
  }));
}

function mockPostComment(_shopId: number, content: string): Promise<Comment> {
  const newComment: Comment = {
    id: Date.now(),
    shopId: _shopId,
    userId: 0,
    userName: '我',
    userAvatar: null,
    content,
    images: [],
    likeCount: 0,
    isLiked: false,
    createdAt: new Date().toISOString(),
    replies: [],
    replyCount: 0,
  };
  mockComments.unshift(newComment);
  return delay().then(() => newComment);
}

let likeState: Record<number, boolean> = {};
let likeCountState: Record<number, number> = {};
mockComments.forEach((c) => { likeState[c.id] = false; likeCountState[c.id] = c.likeCount; });

function mockToggleCommentLike(commentId: number): Promise<boolean> {
  likeState[commentId] = !likeState[commentId];
  likeCountState[commentId] += likeState[commentId] ? 1 : -1;
  const comment = mockComments.find((c) => c.id === commentId);
  if (comment) {
    comment.isLiked = likeState[commentId];
    comment.likeCount = likeCountState[commentId];
  }
  return delay().then(() => likeState[commentId]);
}

const replyIdCounter = 500;

function mockReplyComment(commentId: number, content: string, targetUserName?: string): Promise<CommentReply> {
  const reply: CommentReply = {
    id: ++replyIdCounter,
    commentId,
    userId: 0,
    userName: '我',
    userAvatar: null,
    content,
    targetUserName,
    createdAt: new Date().toISOString(),
  };
  const comment = mockComments.find((c) => c.id === commentId);
  if (comment) {
    comment.replies.push(reply);
    comment.replyCount = comment.replies.length;
  }
  return delay().then(() => reply);
}
