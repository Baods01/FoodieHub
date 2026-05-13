import { Link } from 'react-router-dom';

export function Header() {
  // TODO: replace with actual auth state
  const isLoggedIn = false;
  const nickname = '用户';
  const avatarUrl: string | null = null;

  return (
    <header className="h-14 px-4 flex items-center justify-between bg-gradient-to-r from-[#FF7E3A] to-[#FF9A5C]">
      {/* Left: brand */}
      <Link
        to="/"
        className="font-bold text-white"
        style={{ fontSize: 20 }}
      >
        食探社
      </Link>

      {/* Right: auth state */}
      {isLoggedIn ? (
        <Link to="/profile" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center text-sm text-white font-medium overflow-hidden">
            {avatarUrl ? (
              <img src={avatarUrl} alt={nickname} className="w-full h-full object-cover" />
            ) : (
              nickname.charAt(0)
            )}
          </div>
          <span className="text-sm text-white">{nickname}</span>
        </Link>
      ) : (
        <Link
          to="/login"
          className="text-sm text-white/80 hover:text-white transition-colors"
        >
          登录/注册
        </Link>
      )}
    </header>
  );
}
