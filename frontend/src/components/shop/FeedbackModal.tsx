import { useState, useEffect, Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { X, ArrowLeft, Loader2, Flag, Edit3 } from 'lucide-react';
import { submitFeedback } from '../../api/feedback';
import { fetchDictData } from '../../api/dictionary';
import type { DictItem } from '../../api/dictionary';
import toast from 'react-hot-toast';

type Step = 'select' | 'complaint' | 'edit_request';

interface FeedbackModalProps {
  shopId: number;
  isOpen: boolean;
  onClose: () => void;
}

export default function FeedbackModal({ shopId, isOpen, onClose }: FeedbackModalProps) {
  const [step, setStep] = useState<Step>('select');
  const [reasons, setReasons] = useState<DictItem[]>([]);
  const [reasonId, setReasonId] = useState<number | ''>('');
  const [description, setDescription] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen) {
      setStep('select');
      setReasonId('');
      setDescription('');
      setError('');
    }
  }, [isOpen]);

  // 切换表单时加载对应的字典
  useEffect(() => {
    if (step === 'select' || !isOpen) return;
    const dictName = step === 'complaint' ? '举报原因' : '勘误原因';
    setReasonId('');
    fetchDictData(dictName).then(setReasons).catch(() => {});
  }, [step, isOpen]);

  const handleSubmit = async () => {
    if (!reasonId) {
      setError('请选择反馈原因');
      return;
    }
    if (step === 'edit_request' && !description.trim()) {
      setError('请填写补充说明');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      await submitFeedback({
        type: step as 'complaint' | 'edit_request',
        target_type: 'shop',
        target_id: shopId,
        reason_id: reasonId as number,
        description: description.trim() || undefined,
      });
      toast.success('反馈已提交，等待管理员处理');
      onClose();
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : '提交失败，请重试');
    } finally {
      setSubmitting(false);
    }
  };

  const reasonOptions = reasons.map((r) => (
    <label
      key={r.id}
      className="flex items-center gap-3 px-4 py-3 rounded-lg border border-gray-200 cursor-pointer hover:bg-orange-50 hover:border-orange-300 transition-colors has-[:checked]:bg-orange-50 has-[:checked]:border-orange-400"
    >
      <input
        type="radio"
        name="reason"
        value={r.id}
        checked={reasonId === r.id}
        onChange={() => setReasonId(r.id)}
        className="accent-orange-500"
      />
      <span className="text-sm text-gray-700">{r.name}</span>
    </label>
  ));

  return (
    <Transition show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child as={Fragment} enter="ease-out duration-200" enterFrom="opacity-0" enterTo="opacity-100" leave="ease-in duration-150" leaveFrom="opacity-100" leaveTo="opacity-0">
          <div className="fixed inset-0 bg-black/30" />
        </Transition.Child>

        <div className="fixed inset-0 flex items-center justify-center p-4">
          <Transition.Child as={Fragment} enter="ease-out duration-200" enterFrom="opacity-0 scale-95" enterTo="opacity-100 scale-100" leave="ease-in duration-150" leaveFrom="opacity-100 scale-100" leaveTo="opacity-0 scale-95">
            <Dialog.Panel className="w-full max-w-md bg-white rounded-2xl shadow-xl overflow-hidden">
              {/* Header */}
              <div className="flex items-center justify-between px-5 pt-5 pb-3 border-b border-gray-100">
                <div className="flex items-center gap-2">
                  {step !== 'select' && (
                    <button
                      type="button"
                      onClick={() => { setStep('select'); setError(''); }}
                      className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                    >
                      <ArrowLeft size={18} />
                    </button>
                  )}
                  <Dialog.Title className="text-base font-bold">
                    {step === 'select' ? '反馈' : step === 'complaint' ? '举报店铺' : '勘误建议'}
                  </Dialog.Title>
                </div>
                <button type="button" onClick={onClose} className="p-1 text-gray-400 hover:text-gray-600 transition-colors">
                  <X size={18} />
                </button>
              </div>

              {/* Body */}
              <div className="px-5 py-4 max-h-[60vh] overflow-y-auto">
                {step === 'select' && (
                  <div className="space-y-3">
                    <button
                      type="button"
                      onClick={() => setStep('complaint')}
                      className="w-full flex items-center gap-4 px-4 py-4 rounded-xl border border-gray-200 text-left hover:bg-orange-50 hover:border-orange-300 transition-colors"
                    >
                      <Flag size={20} className="text-orange-500 flex-shrink-0" />
                      <div>
                        <p className="text-sm font-medium text-gray-800">举报该店铺</p>
                        <p className="text-xs text-gray-400 mt-0.5">发现店铺内容违规</p>
                      </div>
                    </button>
                    <button
                      type="button"
                      onClick={() => setStep('edit_request')}
                      className="w-full flex items-center gap-4 px-4 py-4 rounded-xl border border-gray-200 text-left hover:bg-orange-50 hover:border-orange-300 transition-colors"
                    >
                      <Edit3 size={20} className="text-blue-500 flex-shrink-0" />
                      <div>
                        <p className="text-sm font-medium text-gray-800">提交勘误建议</p>
                        <p className="text-xs text-gray-400 mt-0.5">店铺信息有误，建议修正</p>
                      </div>
                    </button>
                  </div>
                )}

                {step !== 'select' && (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">反馈原因</label>
                      <div className="space-y-2">{reasonOptions}</div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        补充说明{step === 'edit_request' ? '（必填）' : '（选填）'}
                      </label>
                      <textarea
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        placeholder={step === 'edit_request' ? '请描述正确的信息...' : '可选补充说明...'}
                        rows={3}
                        className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-orange-300 resize-none"
                      />
                    </div>

                    {error && <p className="text-red-500 text-sm">{error}</p>}

                    <button
                      type="button"
                      disabled={submitting}
                      onClick={handleSubmit}
                      className="w-full py-2.5 rounded-xl bg-gradient-to-r from-[#FF7E3A] to-[#FF9A5C] text-white text-sm font-medium hover:shadow-lg disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                      {submitting ? (
                        <><Loader2 size={14} className="animate-spin" /> 提交中...</>
                      ) : (
                        step === 'complaint' ? '提交举报' : '提交建议'
                      )}
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
