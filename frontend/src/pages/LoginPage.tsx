import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, LogIn, User, Smartphone, Mail } from 'lucide-react';
import { loginApi } from '../api/auth';
import { useAuthStore } from '../store/authStore';
import { Header } from '../components/layout/Header';

type LoginMode = 'username' | 'phone' | 'email';
type FieldName = 'account' | 'password';

interface FieldError {
  field: FieldName;
  message: string;
}

const modeConfig: Record<LoginMode, { icon: typeof User; label: string; placeholder: string }> = {
  username: { icon: User, label: '用户名', placeholder: '请输入用户名' },
  phone:    { icon: Smartphone, label: '手机号', placeholder: '请输入11位手机号' },
  email:    { icon: Mail, label: '邮箱', placeholder: '请输入邮箱地址' },
};

export default function LoginPage() {
  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);

  const [loginMode, setLoginMode] = useState<LoginMode>('username');
  const [account, setAccount] = useState('');
  const [password, setPassword] = useState('');
  const [showPwd, setShowPwd] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<FieldError[]>([]);

  const mode = modeConfig[loginMode];
  const ModeIcon = mode.icon;

  const getError = (field: FieldName) => errors.find((e) => e.field === field);

  const switchMode = (newMode: LoginMode) => {
    setLoginMode(newMode);
    setAccount('');
    setErrors([]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors([]);

    const newErrors: FieldError[] = [];
    if (!account.trim()) {
      newErrors.push({ field: 'account', message: `请输入${mode.label}` });
    } else if (loginMode === 'phone' && !/^1[3-9]\d{9}$/.test(account.trim())) {
      newErrors.push({ field: 'account', message: '手机号格式不正确' });
    } else if (loginMode === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(account.trim())) {
      newErrors.push({ field: 'account', message: '邮箱格式不正确' });
    }
    if (!password) newErrors.push({ field: 'password', message: '请输入密码' });
    if (newErrors.length > 0) { setErrors(newErrors); return; }

    setLoading(true);
    try {
      const result = await loginApi({ account: account.trim(), password, loginMode });
      login(result.access_token, result.user);
      navigate('/', { replace: true });
    } catch (err: any) {
      setErrors([{ field: 'password', message: err?.message || '登录失败，请重试' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#FFF9F5]">
      <Header />
      <div className="flex-1 flex items-center justify-center px-4 py-10">
        <div className="w-full max-w-[840px] bg-white rounded-2xl shadow-[0_2px_8px_rgba(0,0,0,0.04),0_8px_32px_rgba(0,0,0,0.10)] border border-gray-100/80 overflow-hidden animate-fade-slide-up">

          <div className="flex flex-col md:flex-row">
            {/* Left: brand area ~35% */}
            <div className="md:w-[35%] bg-gradient-to-b from-[#FFE8D6] to-[#FFDCC4] p-8 flex flex-col items-center justify-center text-center">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-[#FF7E3A] to-[#FF9A5C] flex items-center justify-center mb-5 shadow-lg shadow-orange-200">
                <span className="text-3xl font-bold text-white">食</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-800">食探社</h2>
              <p className="text-sm text-gray-500 mt-2 leading-relaxed max-w-[180px]">
                华农校园美食社区
              </p>
              <div className="mt-6 space-y-3 text-left w-full max-w-[160px]">
                {['用户自主上传，信息真实可靠', '小范围社区，熟人社交更可信', '去商业化点评，只讲真心话'].map((text) => (
                  <div key={text} className="flex items-start gap-2 text-xs text-gray-400">
                    <span className="mt-1.5 w-1 h-1 rounded-full bg-orange-300 flex-shrink-0" />
                    <span>{text}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Right: form area ~65% */}
            <div className="md:w-[65%] p-8 md:p-10">
              <h2 className="text-xl font-bold text-gray-800">登录</h2>
              <p className="text-sm text-gray-400 mt-1">欢迎回来，继续探索校园美食</p>

              {/* Login mode switcher */}
              <div className="flex items-center gap-3 mt-6 mb-5">
                {(Object.entries(modeConfig) as [LoginMode, typeof modeConfig['username']][]).map(([key, cfg]) => {
                  const Icon = cfg.icon;
                  const isActive = loginMode === key;
                  return (
                    <button
                      key={key}
                      type="button"
                      onClick={() => switchMode(key)}
                      className={`w-10 h-10 rounded-full flex items-center justify-center transition-all duration-200 border-2 ${
                        isActive
                          ? 'border-orange-400 bg-orange-50 text-orange-500 shadow-sm'
                          : 'border-gray-200 bg-white text-gray-400 hover:border-gray-300 hover:text-gray-500'
                      }`}
                      title={`使用${cfg.label}登录`}
                    >
                      <Icon size={18} />
                    </button>
                  );
                })}
                <span className="text-xs text-gray-400 ml-1">
                  使用{mode.label}登录
                </span>
              </div>

              <form onSubmit={handleSubmit} className="space-y-5">
                {/* Account input (label + placeholder change with mode) */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">{mode.label}</label>
                  <div className="relative">
                    <ModeIcon
                      size={16}
                      className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400"
                    />
                    <input
                      type={loginMode === 'email' ? 'email' : 'text'}
                      value={account}
                      onChange={(e) => setAccount(e.target.value)}
                      placeholder={mode.placeholder}
                      className={`w-full pl-10 pr-4 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 focus:ring-orange-400 transition-all duration-200 ${
                        getError('account') ? 'border-red-400 bg-red-50' : 'border-gray-200 bg-gray-50/50 hover:border-gray-300'
                      }`}
                    />
                  </div>
                  {getError('account') && (
                    <p className="text-red-500 text-xs mt-1.5 animate-fade-in">{getError('account')!.message}</p>
                  )}
                </div>

                {/* Password */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">密码</label>
                  <div className="relative">
                    <input
                      type={showPwd ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="请输入密码"
                      className={`w-full px-4 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 focus:ring-orange-400 transition-all duration-200 pr-10 ${
                        getError('password') ? 'border-red-400 bg-red-50' : 'border-gray-200 bg-gray-50/50 hover:border-gray-300'
                      }`}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPwd(!showPwd)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                    >
                      {showPwd ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                  {getError('password') && (
                    <p className="text-red-500 text-xs mt-1.5 animate-fade-in">{getError('password')!.message}</p>
                  )}
                </div>

                {/* Submit */}
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-2.5 rounded-xl bg-gradient-to-r from-[#FF7E3A] to-[#FF9A5C] text-white text-sm font-medium hover:shadow-lg hover:shadow-orange-200 hover:scale-[1.01] active:scale-[0.99] transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : (
                    <LogIn size={16} />
                  )}
                  {loading ? '登录中...' : '登录'}
                </button>
              </form>

              <div className="mt-8 pt-6 border-t border-gray-100 text-center">
                <p className="text-sm text-gray-500">
                  没有账号？
                  <Link to="/register" className="text-orange-500 hover:text-orange-600 font-medium ml-1 transition-colors">
                    立即注册
                  </Link>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
