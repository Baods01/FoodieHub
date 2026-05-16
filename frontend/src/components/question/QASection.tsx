import { useState, useEffect, useCallback } from 'react';
import { AlertCircle } from 'lucide-react';
import type { Question } from '../../types/question';
import { fetchQuestions, postQuestion, postAnswer } from '../../api/questions';
import { Skeleton } from '../ui/Skeleton';
import { QuestionInput } from './QuestionInput';
import { QuestionCard } from './QuestionCard';

interface QASectionProps {
  shopId: number;
  isLoggedIn: boolean;
  onLoginPrompt: () => void;
  maxCount?: number;
  onViewAll?: () => void;
}

export function QASection({ shopId, isLoggedIn, onLoginPrompt, maxCount = 3, onViewAll }: QASectionProps) {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadQuestions = useCallback(async (pageNum: number) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await fetchQuestions(shopId, pageNum);
      if (pageNum === 1) {
        setQuestions(result.data);
      } else {
        setQuestions((prev) => [...prev, ...result.data]);
      }
      setHasMore(result.hasMore);
    } catch {
      setError('加载失败，请重试');
    } finally {
      setIsLoading(false);
    }
  }, [shopId]);

  useEffect(() => {
    loadQuestions(1);
  }, [loadQuestions]);

  const handleSubmit = async (title: string, content: string) => {
    setIsSubmitting(true);
    try {
      const newQuestion = await postQuestion(shopId, title, content);
      setQuestions((prev) => [newQuestion, ...prev]);
    } catch {
      // silently fail; could add toast notification
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReply = async (questionId: number, content: string, targetUserName?: string) => {
    const fullContent = targetUserName ? `@${targetUserName} ${content}` : content;
    try {
      const newAnswer = await postAnswer(questionId, fullContent);
      setQuestions((prev) =>
        prev.map((q) =>
          q.id === questionId
            ? {
                ...q,
                answers: [...q.answers, newAnswer],
                answerCount: q.answerCount + 1,
                latestAnswerAt: newAnswer.createdAt,
              }
            : q,
        ),
      );
    } catch {
      // silently fail
    }
  };

  const handleLoadMore = () => {
    if (!hasMore || isLoading) return;
    const nextPage = page + 1;
    setPage(nextPage);
    loadQuestions(nextPage);
  };

  return (
    <section>
      <h2 className="text-lg font-bold mb-4">问答</h2>

      <div className="mb-4">
        <QuestionInput
          onSubmit={handleSubmit}
          isSubmitting={isSubmitting}
          isLoggedIn={isLoggedIn}
          onLoginPrompt={onLoginPrompt}
        />
      </div>

      {error ? (
        <div className="flex flex-col items-center justify-center py-12">
          <AlertCircle size={40} className="text-red-400" />
          <p className="text-gray-500 text-sm mt-3">{error}</p>
          <button
            type="button"
            onClick={() => {
              setPage(1);
              loadQuestions(1);
            }}
            className="px-4 py-1.5 mt-3 rounded-lg border border-orange-400 text-orange-500 text-sm hover:bg-orange-50 transition-colors"
          >
            点击重试
          </button>
        </div>
      ) : isLoading && questions.length === 0 ? (
        <div className="space-y-3">
          <Skeleton className="h-24 w-full rounded-lg" />
          <Skeleton className="h-24 w-full rounded-lg" />
          <Skeleton className="h-24 w-full rounded-lg" />
        </div>
      ) : questions.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12">
          <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="24" cy="24" r="20" stroke="#9CA3AF" strokeWidth="2" fill="none" />
            <path d="M24 16v8M24 28v1" stroke="#9CA3AF" strokeWidth="2" strokeLinecap="round" />
          </svg>
          <p className="text-gray-500 text-sm mt-3">还没有提问</p>
        </div>
      ) : (
        <>
          <div className="space-y-3">
            {questions.slice(0, onViewAll ? maxCount : undefined).map((q) => (
              <QuestionCard key={q.id} question={q} onReply={handleReply} />
            ))}
          </div>

          {/* View all (preview mode) */}
          {onViewAll && questions.length > maxCount && (
            <div className="flex justify-center mt-4">
              <button
                type="button"
                onClick={onViewAll}
                className="px-5 py-1.5 rounded-lg border border-orange-200 text-orange-500 text-sm hover:bg-orange-50 transition-colors"
              >
                查看全部 {questions.length} 条问答 &gt;
              </button>
            </div>
          )}

          {/* Load more (full mode) */}
          {!onViewAll && hasMore && (
            <div className="flex justify-center mt-4">
              <button
                type="button"
                onClick={handleLoadMore}
                disabled={isLoading}
                className="px-5 py-1.5 rounded-lg border border-gray-300 text-gray-500 text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? '加载中...' : '加载更多'}
              </button>
            </div>
          )}
        </>
      )}
    </section>
  );
}
