import { Fragment, useState, useEffect, useCallback } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { X, AlertCircle } from 'lucide-react';
import type { Question } from '../../types/question';
import { fetchQuestions, postQuestion, postAnswer } from '../../api/questions';
import { QuestionInput } from './QuestionInput';
import { QuestionCard } from './QuestionCard';

interface AllQAModalProps {
  shopId: number;
  isOpen: boolean;
  onClose: () => void;
  isLoggedIn: boolean;
  onLoginPrompt: () => void;
}

export default function AllQAModal({
  shopId,
  isOpen,
  onClose,
  isLoggedIn,
  onLoginPrompt,
}: AllQAModalProps) {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadQuestions = useCallback(
    async (pageNum: number) => {
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
    },
    [shopId],
  );

  useEffect(() => {
    if (isOpen) {
      setPage(1);
      loadQuestions(1);
    }
  }, [isOpen, loadQuestions]);

  const handleSubmit = async (title: string, content: string) => {
    if (!isLoggedIn) {
      onLoginPrompt();
      return;
    }
    setIsSubmitting(true);
    try {
      const newQuestion = await postQuestion(shopId, title, content);
      setQuestions((prev) => [newQuestion, ...prev]);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReply = async (questionId: number, content: string, targetUserName?: string) => {
    if (!isLoggedIn) {
      onLoginPrompt();
      return;
    }
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
    const next = page + 1;
    setPage(next);
    loadQuestions(next);
  };

  return (
    <Transition show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-200"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-150"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/40" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-hidden">
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-200"
            enterFrom="opacity-0 scale-95"
            enterTo="opacity-100 scale-100"
            leave="ease-in duration-150"
            leaveFrom="opacity-100 scale-100"
            leaveTo="opacity-0 scale-95"
          >
            <Dialog.Panel className="h-full w-full bg-white flex flex-col">
              {/* Header */}
              <div className="flex items-center justify-between px-4 h-14 border-b border-gray-200 flex-shrink-0">
                <button
                  type="button"
                  onClick={onClose}
                  className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 transition-colors"
                >
                  &larr; 返回
                </button>
                <Dialog.Title className="text-base font-semibold">
                  全部问答
                </Dialog.Title>
                <button
                  type="button"
                  onClick={onClose}
                  className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <X size={20} />
                </button>
              </div>

              {/* Content */}
              <div className="flex-1 overflow-y-auto">
                {/* Question input */}
                <div className="px-4 py-3 border-b border-gray-100">
                  <QuestionInput
                    onSubmit={handleSubmit}
                    isSubmitting={isSubmitting}
                    isLoggedIn={isLoggedIn}
                    onLoginPrompt={onLoginPrompt}
                  />
                </div>

                {/* Loading */}
                {isLoading && (
                  <div className="px-4 py-8 space-y-4">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="animate-pulse space-y-2">
                        <div className="h-4 w-24 bg-gray-200 rounded" />
                        <div className="h-3 w-full bg-gray-100 rounded" />
                        <div className="h-3 w-3/4 bg-gray-100 rounded" />
                      </div>
                    ))}
                  </div>
                )}

                {/* Error */}
                {error && (
                  <div className="flex flex-col items-center py-12">
                    <AlertCircle size={40} className="text-red-400" />
                    <p className="text-gray-500 text-sm mt-3">{error}</p>
                    <button
                      type="button"
                      onClick={() => loadQuestions(1)}
                      className="px-4 py-1.5 mt-3 rounded-lg border border-orange-400 text-orange-500 text-sm hover:bg-orange-50"
                    >
                      点击重试
                    </button>
                  </div>
                )}

                {/* Empty */}
                {!isLoading && !error && questions.length === 0 && (
                  <div className="flex items-center justify-center py-20 text-sm text-gray-400">
                    还没有提问
                  </div>
                )}

                {/* Questions */}
                {!isLoading && !error && questions.length > 0 && (
                  <div className="space-y-3 p-4">
                    {questions.map((q) => (
                      <QuestionCard key={q.id} question={q} onReply={handleReply} />
                    ))}
                  </div>
                )}

                {/* Load more */}
                {!isLoading && !error && hasMore && questions.length > 0 && (
                  <div className="text-center pb-4">
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
              </div>
            </Dialog.Panel>
          </Transition.Child>
        </div>
      </Dialog>
    </Transition>
  );
}
