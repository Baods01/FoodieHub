import { useState } from 'react';
import { MessageCircle } from 'lucide-react';
import type { Question, Answer } from '../../types/question';

interface QuestionCardProps {
  question: Question;
  onReply: (questionId: number, content: string, targetUserName?: string) => void;
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

export function QuestionCard({ question, onReply }: QuestionCardProps) {
  const [expanded, setExpanded] = useState(false);
  const [replyVisible, setReplyVisible] = useState<Record<number, boolean>>({});
  const [replyText, setReplyText] = useState<Record<number, string>>({});

  const toggleReply = (answerId: number) => {
    setReplyVisible((prev) => ({ ...prev, [answerId]: !prev[answerId] }));
    if (!replyVisible[answerId]) {
      setReplyText((prev) => ({ ...prev, [answerId]: '' }));
    }
  };

  const handleSendReply = (answer: Answer) => {
    const text = replyText[answer.id]?.trim();
    if (!text) return;
    onReply(question.id, text, answer.userName);
    setReplyText((prev) => ({ ...prev, [answer.id]: '' }));
    setReplyVisible((prev) => ({ ...prev, [answer.id]: false }));
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      {/* Question header */}
      <div
        className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={() => setExpanded((v) => !v)}
      >
        <div className="flex items-start gap-3">
          <UserAvatar avatar={question.userAvatar} name={question.userName} />
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-orange-600 shrink-0">Q:</span>
              <span className="text-sm font-medium truncate">{question.title}</span>
            </div>
            <div className="flex items-center gap-3 mt-1">
              <span className="text-xs text-gray-500">{question.userName}</span>
              <span className="text-xs text-gray-400">{timeAgo(question.createdAt)}</span>
              <span className="flex items-center gap-1 text-xs text-gray-400">
                <MessageCircle size={12} />
                {question.answerCount}
              </span>
            </div>
          </div>
          {/* Expand indicator */}
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

      {/* Expanded content */}
      {expanded && (
        <div className="border-t border-gray-100">
          {/* Question content */}
          <div className="px-4 py-3 bg-gray-50">
            <p className="text-sm text-gray-700 whitespace-pre-wrap">{question.content}</p>
          </div>

          {/* Answers */}
          <div className="divide-y divide-gray-100">
            {question.answers.length === 0 ? (
              <p className="px-4 py-6 text-center text-sm text-gray-400">还没有回答</p>
            ) : (
              question.answers.map((answer) => (
                <div key={answer.id} className="px-4 py-3">
                  <div className="flex items-start gap-3">
                    <UserAvatar avatar={answer.userAvatar} name={answer.userName} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-medium text-gray-700">
                          {answer.userName}
                        </span>
                        {answer.targetUserName && (
                          <>
                            <span className="text-xs text-gray-400">回复</span>
                            <span className="text-xs font-medium text-orange-600">
                              @{answer.targetUserName}
                            </span>
                          </>
                        )}
                        <span className="text-xs text-gray-400">{timeAgo(answer.createdAt)}</span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1 whitespace-pre-wrap">
                        {answer.content}
                      </p>
                      {/* Reply button & inline reply box */}
                      <button
                        type="button"
                        onClick={() => toggleReply(answer.id)}
                        className="text-xs text-orange-500 hover:text-orange-600 mt-1"
                      >
                        {replyVisible[answer.id] ? '取消回复' : '回复'}
                      </button>

                      {replyVisible[answer.id] && (
                        <div className="mt-2 flex gap-2">
                          <input
                            type="text"
                            value={replyText[answer.id] || ''}
                            onChange={(e) =>
                              setReplyText((prev) => ({ ...prev, [answer.id]: e.target.value }))
                            }
                            placeholder={`回复 @${answer.userName}`}
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
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
