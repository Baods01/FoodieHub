import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { UserPlus, Eye, EyeOff } from 'lucide-react';
import { registerApi } from '../api/auth';
import { Header } from '../components/layout/Header';

type FieldName = 'username' | 'password' | 'confirmPwd' | 'phone' | 'email';

interface FieldError {
  field: FieldName;
  message: string;
}

export default function RegisterPage() {
  const navigate = useNavigate();

  const [username, setUsername] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPwd, setConfirmPwd] = useState('');
  const [showPwd, setShowPwd] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<FieldError[]>([]);

  const getError = (field: FieldName) => errors.find((e) => e.field === field);

  const validate = (): FieldError[] => {
    const errs: FieldError[] = [];
    if (!username.trim()) errs.push({ field: 'username', message: '请输入用户名' });
    else if (username.trim().length < 2) errs.push({ field: 'username', message: '用户名至少 2 个字符' });
    else if (!/^[\w\u4e00-\u9fa5]+$/.test(username.trim())) errs.push({ field: 'username', message: '只能包含字母、数字、下划线和中文' });
    if (!phone.trim()) errs.push({ field: 'phone', message: '请输入手机号' });
    else if (!/^1[3-9]\d{9}$/.test(phone.trim())) errs.push({ field: 'phone', message: '手机号格式不正确' });
    if (!email.trim()) errs.push({ field: 'email', message: '请输入邮箱' });
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) errs.push({ field: 'email', message: '邮箱格式不正确' });
    if (!password) errs.push({ field: 'password', message: '请输入密码' });
    else if (password.length < 6) errs.push({ field: 'password', message: '密码长度不能少于 6 位' });
    if (!confirmPwd) errs.push({ field: 'confirmPwd', message: '请确认密码' });
    else if (password !== confirmPwd) errs.push({ field: 'confirmPwd', message: '两次输入的密码不一致' });
    return errs;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const errs = validate();
    setErrors(errs);
    if (errs.length > 0) return;

    setLoading(true);
    try {
      await registerApi({ username: username.trim(), password, phone: phone.trim(), email: email.trim() });
      navigate('/login?registered=1');
    } catch (err: any) {
      const msg = err?.message || '注册失败，请重试';
      if (msg.includes('用户名')) setErrors([{ field: 'username', message: msg }]);
      else if (msg.includes('手机号')) setErrors([{ field: 'phone', message: msg }]);
      else if (msg.includes('邮箱')) setErrors([{ field: 'email', message: msg }]);
      else setErrors([{ field: 'password', message: msg }]);
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
              <h2 className="text-2xl font-bold text-gray-800">加入我们</h2>
              <p className="text-sm text-gray-500 mt-2 leading-relaxed max-w-[180px]">
                成为校园美食侦探
              </p>
              <div className="mt-6 space-y-3 text-left w-full max-w-[160px]">
                {['分享你发现的宝藏店铺', '点评问答，和同学真实互动', '收藏美食，随时查阅'].map((text) => (
                  <div key={text} className="flex items-start gap-2 text-xs text-gray-400">
                    <span className="mt-1.5 w-1 h-1 rounded-full bg-orange-300 flex-shrink-0" />
                    <span>{text}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Right: form area ~65% */}
            <div className="md:w-[65%] p-8 md:p-10">
              <h2 className="text-xl font-bold text-gray-800">注册</h2>
              <p className="text-sm text-gray-400 mt-1">创建账号，开始探索校园美食</p>

              <form onSubmit={handleSubmit} className="mt-6 space-y-4">
                {/* Username */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">用户名</label>
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="2-50 字符，字母/数字/中文"
                    className={`w-full px-4 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 focus:ring-orange-400 transition-all duration-200 ${
                      getError('username') ? 'border-red-400 bg-red-50' : 'border-gray-200 bg-gray-50/50 hover:border-gray-300'
                    }`}
                  />
                  {getError('username') && <p className="text-red-500 text-xs mt-1 animate-fade-in">{getError('username')!.message}</p>}
                </div>

                {/* Phone + Email row */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">手机号</label>
                    <input
                      type="tel"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      placeholder="11 位手机号"
                      className={`w-full px-4 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 focus:ring-orange-400 transition-all duration-200 ${
                        getError('phone') ? 'border-red-400 bg-red-50' : 'border-gray-200 bg-gray-50/50 hover:border-gray-300'
                      }`}
                    />
                    {getError('phone') && <p className="text-red-500 text-xs mt-1 animate-fade-in">{getError('phone')!.message}</p>}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">邮箱</label>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="example@scau.edu.cn"
                      className={`w-full px-4 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 focus:ring-orange-400 transition-all duration-200 ${
                        getError('email') ? 'border-red-400 bg-red-50' : 'border-gray-200 bg-gray-50/50 hover:border-gray-300'
                      }`}
                    />
                    {getError('email') && <p className="text-red-500 text-xs mt-1 animate-fade-in">{getError('email')!.message}</p>}
                  </div>
                </div>

                {/* Password + Confirm row */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">密码</label>
                    <div className="relative">
                      <input
                        type={showPwd ? 'text' : 'password'}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="至少 6 位"
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
                    {getError('password') && <p className="text-red-500 text-xs mt-1 animate-fade-in">{getError('password')!.message}</p>}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">确认密码</label>
                    <input
                      type="password"
                      value={confirmPwd}
                      onChange={(e) => setConfirmPwd(e.target.value)}
                      placeholder="再次输入密码"
                      className={`w-full px-4 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 focus:ring-orange-400 transition-all duration-200 ${
                        getError('confirmPwd') ? 'border-red-400 bg-red-50' : 'border-gray-200 bg-gray-50/50 hover:border-gray-300'
                      }`}
                    />
                    {getError('confirmPwd') && <p className="text-red-500 text-xs mt-1 animate-fade-in">{getError('confirmPwd')!.message}</p>}
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-2.5 rounded-xl bg-gradient-to-r from-[#FF7E3A] to-[#FF9A5C] text-white text-sm font-medium hover:shadow-lg hover:shadow-orange-200 hover:scale-[1.01] active:scale-[0.99] transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : (
                    <UserPlus size={16} />
                  )}
                  {loading ? '注册中...' : '注册'}
                </button>
              </form>

              <div className="mt-8 pt-6 border-t border-gray-100 text-center">
                <p className="text-sm text-gray-500">
                  已有账号？
                  <Link to="/login" className="text-orange-500 hover:text-orange-600 font-medium ml-1 transition-colors">
                    立即登录
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
