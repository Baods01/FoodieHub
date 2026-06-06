import { StrictMode, useEffect, useState, useRef } from 'react';
import { createRoot } from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';
import { router } from './router';
import { Toaster, toast } from 'react-hot-toast';
import { useAuthStore } from './store/authStore';
import { fetchUnreadCount } from './api/notifications';
import './index.css';

const POLL_INTERVAL = 30000; // 30 秒轮询一次未读数

/** App wrapper that initializes auth state before rendering */
function App() {
  const [ready, setReady] = useState(false);
  const init = useAuthStore((s) => s.init);
  const isLoggedIn = useAuthStore((s) => s.isLoggedIn);
  const setUnreadCount = useAuthStore((s) => s.setUnreadCount);
  const prevCountRef = useRef(-1);

  useEffect(() => {
    init().then(() => setReady(true));
  }, [init]);

  // 已登录时轮询未读数 + 新消息自动弹框
  useEffect(() => {
    if (!ready || !isLoggedIn) return;

    let timer: ReturnType<typeof setInterval>;

    const poll = async () => {
      try {
        const count = await fetchUnreadCount();
        setUnreadCount(count);

        // 首次加载只记录不弹框
        if (prevCountRef.current === -1) {
          prevCountRef.current = count;
          return;
        }

        // 检测到未读数增加 → 弹出可点击通知
        if (count > prevCountRef.current) {
          const diff = count - prevCountRef.current;
          toast.custom(
            (t) => (
              <button
                onClick={() => {
                  toast.dismiss(t.id);
                  window.location.href = '/notifications';
                }}
                className="flex items-center gap-3 bg-white rounded-xl shadow-lg border border-gray-100 px-5 py-3.5 hover:bg-orange-50 transition-colors"
              >
                <span className="text-lg">🔔</span>
                <span className="text-sm text-gray-700">
                  您有 <strong>{diff}</strong> 条新消息
                </span>
              </button>
            ),
            { duration: 4000 },
          );
        }
        prevCountRef.current = count;
      } catch {
        // 静默失败
      }
    };

    // 页面可见时才轮询；切走时暂停
    const handleVisibility = () => {
      if (document.hidden) {
        clearInterval(timer);
      } else {
        poll();
        timer = setInterval(poll, POLL_INTERVAL);
      }
    };

    handleVisibility();
    document.addEventListener('visibilitychange', handleVisibility);

    return () => {
      clearInterval(timer);
      document.removeEventListener('visibilitychange', handleVisibility);
      prevCountRef.current = -1;
    };
  }, [ready, isLoggedIn, setUnreadCount]);

  if (!ready) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="animate-pulse text-gray-400 text-sm">加载中...</div>
      </div>
    );
  }

  return (
    <StrictMode>
      <RouterProvider router={router} />
      <Toaster position="top-center" />
    </StrictMode>
  );
}

createRoot(document.getElementById('root')!).render(<App />);
