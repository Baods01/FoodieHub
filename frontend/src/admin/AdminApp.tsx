import { Navigate, useLocation } from 'react-router-dom';
import { CircularProgress, Box } from '@mui/material';
import { Admin, Resource, CustomRoutes } from 'react-admin';
import { Route } from 'react-router-dom';

import { dataProvider } from './dataProvider';
import { authProvider } from './authProvider';
import AdminLayout from './AdminLayout';
import Dashboard from './dashboard/Dashboard';
import ForbiddenPage from './components/ForbiddenPage';
import { useAuthStore } from '../store/authStore';

// 已实现组件
import UserList from './users/UserList';
import UserShow from './users/UserShow';
import ShopList from './shops/ShopList';
import ShopEdit from './shops/ShopEdit';
import LogList from './logs/LogList';

// 已实现组件（Phase 7-4）
import ComplaintPage from './complaints/ComplaintPage';

// 公告管理
import AnnouncementList from './announcements/AnnouncementList';
import AnnouncementCreate from './announcements/AnnouncementCreate';

/**
 * AdminGuard — 管理员路由守卫
 */
export default function AdminApp() {
  const { isLoggedIn, userRole, initialized } = useAuthStore();
  const location = useLocation();

  if (!initialized) {
    return (
      <Box sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!isLoggedIn) {
    return <Navigate to="/admin/login" state={{ from: location }} replace />;
  }

  if (userRole !== 1) {
    return <ForbiddenPage />;
  }

  return (
    <Admin
      basename="/admin"
      dataProvider={dataProvider}
      authProvider={authProvider}
      dashboard={Dashboard}
      layout={AdminLayout}
      requireAuth
    >
      {/* CRUD Resources — name 短命名，路径映射在 dataProvider 中处理 */}
      {/* options.label 用于自定义菜单显示名 */}
      <Resource name="users" list={UserList} show={UserShow} options={{ label: '用户管理' }} />
      <Resource name="logs" list={LogList} options={{ label: '操作日志' }} />

      {/* Custom Routes */}
      <CustomRoutes>
        <Route path="/shops" element={<ShopList />} />
        <Route path="/shops/:id" element={<ShopEdit />} />
        <Route path="/feedbacks" element={<ComplaintPage />} />
        <Route path="/announcements" element={<AnnouncementList />} />
        <Route path="/announcements/create" element={<AnnouncementCreate />} />
      </CustomRoutes>
    </Admin>
  );
}
