import { Fragment } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Menu, Transition } from '@headlessui/react';
import {
  User,
  Heart,
  Clock,
  Bell,
  LogOut,
  ChevronDown,
} from 'lucide-react';
import { useAuthStore } from '../../store/authStore';

export function Header() {
  const navigate = useNavigate();
  const { isLoggedIn, userName, userAvatar, unreadCount, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const menuItems = [
    { label: '个人中心', icon: User, to: '/profile' },
    { label: '收藏夹', icon: Heart, to: '/favorites' },
    { label: '浏览历史', icon: Clock, to: '/history' },
    { label: '消息通知', icon: Bell, to: '/notifications', badge: unreadCount },
  ];

  return (
    <header className="h-14 px-4 flex items-center justify-between bg-white/70 backdrop-blur-lg border-b border-gray-100/80 sticky top-0 z-40">
      {/* Left: brand */}
      <Link to="/" className="flex items-center gap-2">
        <img src="/icon.jpg" alt="食探社" className="w-24 h-12 rounded-lg object-cover" />
        <span className="font-bold bg-gradient-to-r from-[#FF7E3A] to-[#FF9A5C] bg-clip-text text-transparent" style={{ fontSize: 20 }}>
          食探社
        </span>
      </Link>

      {/* Right: auth state */}
      {isLoggedIn ? (
        <Menu as="div" className="relative">
          <Menu.Button className="flex items-center gap-2 outline-none">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#FF7E3A] to-[#FF9A5C] flex items-center justify-center text-sm text-white font-medium overflow-hidden">
              {userAvatar ? (
                <img src={userAvatar} alt={userName} className="w-full h-full object-cover" />
              ) : (
                userName.charAt(0)
              )}
            </div>
            <span className="text-sm text-gray-700 hidden sm:inline">{userName}</span>
            <ChevronDown size={14} className="text-gray-400" />
          </Menu.Button>

          <Transition
            as={Fragment}
            enter="transition ease-out duration-150"
            enterFrom="transform opacity-0 scale-95"
            enterTo="transform opacity-100 scale-100"
            leave="transition ease-in duration-100"
            leaveFrom="transform opacity-100 scale-100"
            leaveTo="transform opacity-0 scale-95"
          >
            <Menu.Items className="absolute right-0 mt-2 w-48 bg-white/90 backdrop-blur-md border border-gray-200 rounded-xl shadow-xl z-50 overflow-hidden origin-top-right">
              {/* User info header */}
              <div className="px-4 py-3 border-b border-gray-100">
                <p className="text-sm font-medium text-gray-900 truncate">{userName}</p>
                <p className="text-xs text-gray-500 mt-0.5">食探社用户</p>
              </div>

              {/* Menu items */}
              <div className="py-1">
                {menuItems.map((item) => (
                  <Menu.Item key={item.to}>
                    {({ active }) => (
                      <Link
                        to={item.to}
                        className={`flex items-center gap-3 px-4 py-2.5 text-sm ${
                          active ? 'bg-orange-50 text-orange-600' : 'text-gray-700'
                        }`}
                      >
                        <item.icon size={16} />
                        <span className="flex-1">{item.label}</span>
                        {(item as any).badge > 0 && (
                          <span className="bg-red-500 text-white text-xs rounded-full min-w-[18px] h-[18px] flex items-center justify-center px-1">
                            {(item as any).badge > 99 ? '99+' : (item as any).badge}
                          </span>
                        )}
                      </Link>
                    )}
                  </Menu.Item>
                ))}
              </div>

              {/* Divider + Logout */}
              <div className="border-t border-gray-100">
                <Menu.Item>
                  {({ active }) => (
                    <button
                      onClick={handleLogout}
                      className={`flex items-center gap-3 px-4 py-2.5 text-sm w-full text-left ${
                        active ? 'bg-red-50 text-red-600' : 'text-gray-500'
                      }`}
                    >
                      <LogOut size={16} />
                      退出登录
                    </button>
                  )}
                </Menu.Item>
              </div>
            </Menu.Items>
          </Transition>
        </Menu>
      ) : (
        <Link
          to="/login"
          className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
        >
          登录/注册
        </Link>
      )}
    </header>
  );
}
