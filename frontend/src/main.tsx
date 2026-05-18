import { StrictMode, useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';
import { router } from './router';
import { Toaster } from 'react-hot-toast';
import { useAuthStore } from './store/authStore';
import './index.css';

/** App wrapper that initializes auth state before rendering */
function App() {
  const [ready, setReady] = useState(false);
  const init = useAuthStore((s) => s.init);

  useEffect(() => {
    init().then(() => setReady(true));
  }, [init]);

  if (!ready) {
    return (
      <div className="min-h-screen bg-[#FFF9F5] flex items-center justify-center">
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
