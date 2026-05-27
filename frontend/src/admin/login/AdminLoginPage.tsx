import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  InputAdornment,
  IconButton,
  CircularProgress,
  Container,
} from '@mui/material';
import { Visibility, VisibilityOff, LockOutlined } from '@mui/icons-material';
import { loginApi } from '../../api/auth';

export default function AdminLoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const login = useAuthStore((s) => s.login);

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPwd, setShowPwd] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const from = (location.state as any)?.from?.pathname || '/admin';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!username.trim()) { setError('请输入管理员用户名'); return; }
    if (!password) { setError('请输入密码'); return; }

    setLoading(true);
    try {
      const result = await loginApi({
        account: username.trim(),
        password,
        loginMode: 'username',
      });

      const { access_token, user } = result;

      // 角色校验：仅管理员
      if (user.role !== 1) {
        setError('非管理员账号，无法访问后台');
        setLoading(false);
        return;
      }

      login(access_token, user);
      navigate(from, { replace: true });
    } catch (err: any) {
      setError(err?.message || '登录失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Card
          variant="outlined"
          sx={{
            width: '100%',
            maxWidth: 400,
            borderRadius: 3,
            boxShadow: '0 4px 24px rgba(0,0,0,0.08)',
          }}
        >
          <CardContent sx={{ p: 4 }}>
            {/* Logo + Title */}
            <Box sx={{ textAlign: 'center', mb: 3 }}>
              <Box
                sx={{
                  width: 56,
                  height: 56,
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #FF7E3A, #FF9A5C)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mx: 'auto',
                  mb: 2,
                }}
              >
                <LockOutlined sx={{ color: '#fff', fontSize: 28 }} />
              </Box>
              <Typography variant="h5" fontWeight={700}>
                食探社
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                管理后台
              </Typography>
            </Box>

            {/* Error */}
            {error && (
              <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>
                {error}
              </Alert>
            )}

            {/* Form */}
            <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
              <TextField
                label="管理员用户名"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                fullWidth
                size="small"
                autoFocus
                disabled={loading}
              />
              <TextField
                label="密码"
                type={showPwd ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                fullWidth
                size="small"
                disabled={loading}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={() => setShowPwd(!showPwd)} edge="end" size="small">
                        {showPwd ? <VisibilityOff fontSize="small" /> : <Visibility fontSize="small" />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
              <Button
                type="submit"
                variant="contained"
                fullWidth
                disabled={loading}
                sx={{
                  py: 1.2,
                  borderRadius: 2,
                  textTransform: 'none',
                  fontWeight: 600,
                  background: 'linear-gradient(135deg, #FF7E3A, #FF9A5C)',
                  '&:hover': { background: 'linear-gradient(135deg, #e56e30, #e88942)' },
                }}
              >
                {loading ? <CircularProgress size={20} sx={{ color: 'white' }} /> : '登录后台'}
              </Button>
            </Box>

            <Typography
              variant="caption"
              color="text.disabled"
              sx={{ display: 'block', textAlign: 'center', mt: 3 }}
            >
              仅限管理员访问
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
}
