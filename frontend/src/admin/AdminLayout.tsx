import { Layout } from 'react-admin';
import { styled } from '@mui/material/styles';
import AdminMenu from './AdminMenu';

/**
 * 自定义 react-admin Layout — 覆盖 content 区域层叠上下文，
 * 防止 content 内的 position:fixed 元素（如 Snackbar）被 AppBar 遮挡。
 */
const StyledLayout = styled(Layout)({
  [`& .RaLayout-content`]: {
    zIndex: 'unset !important',
    position: 'static !important',
  },
});

/**
 * 自定义 react-admin Layout — 使用中文自定义菜单
 */
export default function AdminLayout(props: any) {
  return <StyledLayout {...props} menu={AdminMenu} />;
}
