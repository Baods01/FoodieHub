import { useState, useEffect } from 'react';
import { MessageCircle, Trash2 } from 'lucide-react';
import type { Question, Answer } from '../../types/question';
import { fetchAnswers, toggleLike, deleteQuestion, deleteAnswer } from '../../api/comments';
import { LikeButton } from '../comment/LikeButton';

interface QuestionCardProps {
  question: Question;
  onReply: (questionId: number, content: string, replyToUserId?: number) => void;
  currentUserId: number | null;
  isAdmin: boolean;
  onDeleteQuestion: (questionId: number) => void;
  onDeleteAnswer: (answerId: number) => void;
}

function timeAgo(dateStr: string): string {
  const now = Date.now();
  const then = new Date(dateStr).getTime();
  const diff = Math.max(0, now - then);
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  if (minutes < 1) return '刚刚';
  if (minutes < 60) return `${minutes}分钟前`;
  if (hours < 24) return `${hours}小时前`;
  if (days < 30) return `${days}天前`;
  return new Date(dateStr).toLocaleDateString('zh-CN');
}

function UserAvatar({ avatar, name }: { avatar: string | null; name: string }) {
  return avatar ? (
    <img src={avatar} alt={name} className="w-5 h-5 rounded-full object-cover" />
  ) : (
    <div className="w-5 h-5 rounded-full bg-orange-100 text-orange-600 flex items-center justify-center text-xs font-medium">
      {name.charAt(0)}
    </div>
  );
}

export function QuestionCard({ question, onReply, currentUserId, isAdmin, onDeleteQuestion, onDeleteAnswer }: QuestionCardProps) {
  const [expanded, setExpanded] = useState(false);
  const [replyVisible, setReplyVisible] = useState<Record<number, boolean>>({});
  const [replyText, setReplyText] = useState<Record<number, string>>({});
  const [questionReplyVisible, setQuestionReplyVisible] = useState(false);
  const [questionReplyText, setQuestionReplyText] = useState('');
  const [answers, setAnswers] = useState<Answer[] | undefined>(undefined);
  const [deleteConfirmId, setDeleteConfirmId] = useState<number | null>(null);
  const [deleteType, setDeleteType] = useState<'question' | 'answer' | null>(null);

  // 从后端加载回答
  useEffect(() => {
    fetchAnswers(question.id).then(setAnswers).catch(() => {});
  }, []);

  // 合并父组件乐观更新到本地状态
  useEffect(() => {
    if (question.answers && question.answers.length > 0) {
      setAnswers((prev) => {
        const existingIds = new Set((prev ?? []).map((a) => a.id));
        const newOnes = question.answers!.filter((a) => !existingIds.has(a.id));
        return newOnes.length > 0 ? [...(prev ?? []), ...newOnes] : prev;
      });
    }
  }, [question.answers]);

  const displayAnswers = answers;

  const canDeleteQuestion = currentUserId !== null && (
    question.user?.id === currentUserId || isAdmin
  );

  const toggleReply = (answerId: number) => {
    setReplyVisible((prev) => ({ ...prev, [answerId]: !prev[answerId] }));
    if (!replyVisible[answerId]) {
      setReplyText((prev) => ({ ...prev, [answerId]: '' }));
    }
  };

  const handleSendReply = (answer: Answer) => {
    const text = replyText[answer.id]?.trim();
    if (!text) return;
    onReply(question.id, text, (answer.user?.id));
    setReplyText((prev) => ({ ...prev, [answer.id]: '' }));
    setReplyVisible((prev) => ({ ...prev, [answer.id]: false }));
  };

  const handleDeleteQuestion = () => {
    setDeleteType('question');
    setDeleteConfirmId(question.id);
  };

  const handleDeleteAnswer = (answerId: number) => {
    setDeleteType('answer');
    setDeleteConfirmId(answerId);
  };

  const confirmDelete = () => {
    if (deleteConfirmId === null || deleteType === null) return;
    if (deleteType === 'question') {
      deleteQuestion(deleteConfirmId).then(() => {
        onDeleteQuestion(deleteConfirmId);
      }).catch((err: any) => {
        console.error('删除问题失败:', err?.response?.data || err);
      });
    } else if (deleteType === 'answer') {
      deleteAnswer(deleteConfirmId).then(() => {
        onDeleteAnswer(deleteConfirmId);
      }).catch((err: any) => {
        console.error('删除回答失败:', err?.response?.data || err);
      });
    }
    setDeleteConfirmId(null);
    setDeleteType(null);
  };

  const cancelDelete = () => {
    setDeleteConfirmId(null);
    setDeleteType(null);
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      {/* Question header */}
      <div
        className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={() => setExpanded((v) => !v)}
      >
        <div className="flex items-start gap-3">
          <UserAvatar avatar={(question.user?.avatar ?? null)} name={(question.user?.username ?? '')} />
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-orange-600 shrink-0">Q:</span>
              <span className="text-sm font-medium truncate">{question.title}</span>
            </div>
            <div className="flex items-center gap-3 mt-1">
              <span className="text-xs text-gray-500">{(question.user?.username ?? '')}</span>
              <span className="text-xs text-gray-400">{timeAgo(question.created_at)}</span>
              <span className="flex items-center gap-1 text-xs text-gray-400">
                <MessageCircle size={12} />
              </span>
            </div>
          </div>
          {/* Expand indicator */}
          <div className="flex items-center gap-2">
            {/* Delete button for question */}
            {canDeleteQuestion && (
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  handleDeleteQuestion();
                }}
                className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                title="删除问题"
              >
                <Trash2 size={16} />
              </button>
            )}
            <svg
              className={`w-4 h-4 mt-1 text-gray-400 transition-transform ${expanded ? 'rotate-180' : ''}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
      </div>

      {/* Expanded content */}
      {expanded && (
        <div className="border-t border-gray-100">
          {/* Question content */}
          <div className="px-4 py-3 bg-gray-50">
            <p className="text-sm text-gray-700 whitespace-pre-wrap">{question.content}</p>
            {/* Reply to question button */}
            <button
              type="button"
              onClick={() => setQuestionReplyVisible((v) => !v)}
              className="text-xs text-orange-500 hover:text-orange-600 mt-2"
            >
              {questionReplyVisible ? '取消回复' : '回复'}
            </button>
            {/* Reply to question input */}
            {questionReplyVisible && (
              <div className="mt-2 flex gap-2">
                <input
                  type="text"
                  value={questionReplyText}
                  onChange={(e) => setQuestionReplyText(e.target.value)}
                  placeholder="写下你的回答..."
                  className="flex-1 px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-300 focus:border-orange-400"
                />
                <button
                  type="button"
                  disabled={!questionReplyText.trim()}
                  onClick={() => {
                    onReply(question.id, questionReplyText.trim());
                    setQuestionReplyText('');
                    setQuestionReplyVisible(false);
                  }}
                  className="px-3 py-1.5 rounded-lg text-sm bg-orange-500 text-white hover:bg-orange-600 disabled:bg-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  发送
                </button>
              </div>
            )}
          </div>

          {/* Answers */}
          <div className="divide-y divide-gray-100">
            {(displayAnswers?.length ?? 0) === 0 ? (
              <p className="px-4 py-6 text-center text-sm text-gray-400">还没有回答</p>
            ) : (
              (displayAnswers ?? []).map((answer: Answer) => {
                const canDeleteAnswer = currentUserId !== null && (
                  answer.user?.id === currentUserId || isAdmin
                );
                return (
                  <div key={answer.id} className="px-4 py-3">
                    <div className="flex items-start gap-3">
                      <UserAvatar avatar={(answer.user?.avatar ?? null)} name={(answer.user?.username ?? '')} />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-medium text-gray-700">
                            {(answer.user?.username ?? '')}
                          </span>
                          {answer.reply_to_user?.username && (
                            <>
                              <span className="text-xs text-gray-400">回复</span>
                              <span className="text-xs font-medium text-orange-600">
                                @{answer.reply_to_user.username}
                              </span>
                            </>
                          )}
                          <span className="text-xs text-gray-400">{timeAgo(answer.created_at)}</span>
                          {/* Delete button for answer */}
                          {canDeleteAnswer && (
                            <button
                              type="button"
                              onClick={() => handleDeleteAnswer(answer.id)}
                              className="p-0.5 text-gray-400 hover:text-red-500 transition-colors"
                              title="删除回答"
                            >
                              <Trash2 size={12} />
                            </button>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 mt-1 whitespace-pre-wrap">
                          {answer.content}
                        </p>
                        <div className="flex items-center gap-3 mt-1">
                          <button
                            type="button"
                            onClick={() => toggleReply(answer.id)}
                            className="text-xs text-orange-500 hover:text-orange-600"
                          >
                            {replyVisible[answer.id] ? '取消回复' : '回复'}
                          </button>
                          <LikeButton
                            count={answer.like_count}
                            isLiked={answer.has_liked}
                            onClick={() => toggleLike('question_answer', answer.id)}
                          />
                        </div>

                        {replyVisible[answer.id] && (
                          <div className="mt-2 flex gap-2">
                            <input
                              type="text"
                              value={replyText[answer.id] || ''}
                              onChange={(e) =>
                                setReplyText((prev) => ({ ...prev, [answer.id]: e.target.value }))
                              }
                              placeholder={`回复 @${(answer.user?.username ?? '')}`}
                              className="flex-1 px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-300 focus:border-orange-400"
                            />
                            <button
                              type="button"
                              disabled={!replyText[answer.id]?.trim()}
                              onClick={() => handleSendReply(answer)}
                              className="px-3 py-1.5 rounded-lg text-sm bg-orange-500 text-white hover:bg-orange-600 disabled:bg-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
                            >
                              发送
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}

      {/* Delete confirmation dialog */}
      {deleteConfirmId !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-lg shadow-lg p-6 w-80 max-w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">确认删除</h3>
            <p className="text-sm text-gray-600 mb-4">
              {deleteType === 'question' ? '确定要删除这个问题吗？删除后无法恢复。' : '确定要删除这条回答吗？删除后无法恢复。'}
            </p>
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={cancelDelete}
                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
              >
                取消
              </button>
              <button
                type="button"
                onClick={confirmDelete}
                className="px-4 py-2 text-sm bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
              >
                确认删除
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}