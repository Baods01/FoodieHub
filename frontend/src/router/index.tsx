import { createBrowserRouter } from 'react-router-dom';
import { RootLayout } from '../components/layout/RootLayout';
import { HomePage } from '../pages/HomePage';
import { ShopDetailPage } from '../pages/ShopDetailPage';
import ProfilePage from '../pages/ProfilePage';
import FavoritesPage from '../pages/FavoritesPage';
import HistoryPage from '../pages/HistoryPage';
import NotificationsPage from '../pages/NotificationsPage';
import LoginPage from '../pages/LoginPage';
import RegisterPage from '../pages/RegisterPage';
import UploadShopPage from '../pages/UploadShopPage';
import AdminLoginPage from '../admin/login/AdminLoginPage';
import AdminApp from '../admin/AdminApp';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'shop/:id', element: <ShopDetailPage /> },
      { path: 'profile', element: <ProfilePage /> },
      { path: 'favorites', element: <FavoritesPage /> },
      { path: 'history', element: <HistoryPage /> },
      { path: 'notifications', element: <NotificationsPage /> },
    ],
  },
  // 独立全屏页面（无 RootLayout）
  { path: '/login', element: <LoginPage /> },
  { path: '/register', element: <RegisterPage /> },
  { path: '/upload-shop', element: <UploadShopPage /> },

  // 管理后台（独立认证 + react-admin 接管）
  { path: '/admin/login', element: <AdminLoginPage /> },
  { path: '/admin/*', element: <AdminApp /> },
]);
