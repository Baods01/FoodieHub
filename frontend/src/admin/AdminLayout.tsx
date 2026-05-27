import { Layout } from 'react-admin';
import AdminMenu from './AdminMenu';

/**
 * 自定义 react-admin Layout — 使用中文自定义菜单
 */
export default function AdminLayout(props: any) {
  return <Layout {...props} menu={AdminMenu} />;
}
