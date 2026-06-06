import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
  // 数组序列化使用 FastAPI 期望的 repeat 模式: ?ids=1&ids=2 而非 ?ids[]=1&ids[]=2
  paramsSerializer: {
    indexes: null, // 不添加索引（即不生成 ids[0]=1）
  },
});

// 请求拦截器：自动注入 JWT
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('foodiehub_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器：401 时自动清登录态
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('foodiehub_token');
      // 跳转到登录页（不在 api 层引入 router，直接用 window.location）
      const currentPath = window.location.pathname;
      if (currentPath !== '/login' && currentPath !== '/register') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  },
);

export default apiClient;
