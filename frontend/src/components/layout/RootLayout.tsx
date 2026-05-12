import { Outlet } from 'react-router-dom';
import { Header } from './Header';

export function RootLayout() {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 py-6">
        <Outlet />
      </main>
      <footer className="text-center text-gray-400 text-xs py-4 border-t">
        食探社 — 华农校园美食社区
      </footer>
    </div>
  );
}
