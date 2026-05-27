import { useSidebarState } from 'react-admin';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import {
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Box,
  Divider,
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import PeopleIcon from '@mui/icons-material/People';
import StoreIcon from '@mui/icons-material/Storefront';
import FlagIcon from '@mui/icons-material/Flag';
import EditNoteIcon from '@mui/icons-material/EditNote';
import HistoryIcon from '@mui/icons-material/History';

interface MenuItemConfig {
  to: string;
  primaryText: string;
  icon: React.ReactNode;
}

const menuItems: MenuItemConfig[] = [
  { to: '/admin', primaryText: '仪表盘', icon: <DashboardIcon /> },
  { to: '/admin/users', primaryText: '用户管理', icon: <PeopleIcon /> },
  { to: '/admin/shops', primaryText: '店铺管理', icon: <StoreIcon /> },
  { to: '/admin/complaints', primaryText: '举报处理', icon: <FlagIcon /> },
  { to: '/admin/edit-requests', primaryText: '店铺勘误审核', icon: <EditNoteIcon /> },
  { to: '/admin/logs', primaryText: '操作日志', icon: <HistoryIcon /> },
];

function CustomMenuItem({ to, primaryText, icon }: MenuItemConfig) {
  const location = useLocation();
  const [open] = useSidebarState();
  const selected = location.pathname === to || location.pathname === to + '/';

  return (
    <ListItem disablePadding sx={{ display: 'block', mb: 0.5 }}>
      <ListItemButton
        component={RouterLink}
        to={to}
        selected={selected}
        sx={{
          minHeight: 48,
          justifyContent: open ? 'initial' : 'center',
          px: 2.5,
          mx: 1.5,
          borderRadius: 2,
          mb: 0.5,
          '&.Mui-selected': {
            backgroundColor: 'rgba(255, 126, 58, 0.1)',
            color: '#FF7E3A',
            '&:hover': { backgroundColor: 'rgba(255, 126, 58, 0.15)' },
          },
          '&:hover': {
            backgroundColor: 'rgba(0,0,0,0.04)',
          },
        }}
      >
        <ListItemIcon
          sx={{
            minWidth: 0,
            mr: open ? 2.5 : 'auto',
            justifyContent: 'center',
            color: selected ? '#FF7E3A' : 'rgba(0,0,0,0.54)',
          }}
        >
          {icon}
        </ListItemIcon>
        {open && (
          <ListItemText
            primary={primaryText}
            sx={{
              '& .MuiListItemText-primary': {
                fontSize: 15,
                fontWeight: selected ? 600 : 400,
                whiteSpace: 'nowrap',
              },
            }}
          />
        )}
      </ListItemButton>
    </ListItem>
  );
}

/**
 * 完全自定义侧边栏菜单
 * 不使用 react-admin 默认的 <Menu> 以避免 Resource 自动重复渲染
 */
export default function AdminMenu() {
  const [open] = useSidebarState();

  return (
    <Box sx={{ mt: 2 }}>
      {/* 后台标题 */}
      {open && (
        <Box sx={{ px: 3, py: 1.5 }}>
          <Box sx={{ fontSize: 13, fontWeight: 700, color: 'text.secondary', letterSpacing: 1, textTransform: 'uppercase' }}>
            食探社管理后台
          </Box>
        </Box>
      )}
      <Divider sx={{ mx: 2, mb: 1 }} />
      <List disablePadding>
        {menuItems.map((item) => (
          <CustomMenuItem key={item.to} {...item} />
        ))}
      </List>
    </Box>
  );
}
