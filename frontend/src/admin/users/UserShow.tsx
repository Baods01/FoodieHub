import { useState } from 'react';
import {
  Show,
  SimpleShowLayout,
  useShowController,
  type ShowProps,
} from 'react-admin';
import {
  Box,
  Typography,
  Chip,
  Button,
  Divider,
  Avatar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField as MuiTextField,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Block as BlockIcon,
  CheckCircle as UnblockIcon,
} from '@mui/icons-material';
import apiClient from '../../api/client';

/** 用户展示页 — 嵌入封禁/解封按钮 */
function UserShowContent() {
  const { record, isLoading } = useShowController();
  const [banOpen, setBanOpen] = useState(false);
  const [banReason, setBanReason] = useState('');
  const [submitting, setSubmitting] = useState(false);

  if (isLoading || !record) return null;

  const isBanned = record.is_active === false;

  const handleBan = async () => {
    if (!banReason.trim() && !isBanned) return;
    setSubmitting(true);
    try {
      if (isBanned) {
        await apiClient.post(`/admin/users/${record.id}/unban`, null, {
          params: { reason: banReason.trim() || undefined },
        });
      } else {
        await apiClient.post(`/admin/users/${record.id}/ban`, null, {
          params: { reason: banReason.trim() },
        });
      }
      setBanOpen(false);
      window.location.reload();
    } catch {
      alert('操作失败，请重试');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <Avatar
          src={record.avatar}
          sx={{ width: 64, height: 64, bgcolor: '#FF7E3A', fontSize: 24, fontWeight: 700 }}
        >
          {record.username?.charAt(0)}
        </Avatar>
        <Box>
          <Typography variant="h6" fontWeight={700}>{record.username}</Typography>
          <Typography variant="body2" color="text.secondary">
            ID: {record.id} · {record.email}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
            {record.role === 1 ? (
              <Chip label="管理员" size="small" color="primary" variant="outlined" />
            ) : (
              <Chip label="普通用户" size="small" variant="outlined" />
            )}
            {isBanned ? (
              <Chip label="已封禁" size="small" color="error" />
            ) : (
              <Chip label="正常" size="small" color="success" />
            )}
          </Box>
        </Box>
      </Box>

      <Divider sx={{ mb: 3 }} />

      <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mb: 3 }}>
        <Box>
          <Typography variant="caption" color="text.secondary">手机号</Typography>
          <Typography variant="body2">{record.phone || '-'}</Typography>
        </Box>
        <Box>
          <Typography variant="caption" color="text.secondary">邮箱</Typography>
          <Typography variant="body2">{record.email}</Typography>
        </Box>
        <Box>
          <Typography variant="caption" color="text.secondary">注册时间</Typography>
          <Typography variant="body2">{new Date(record.created_at).toLocaleDateString()}</Typography>
        </Box>
        <Box>
          <Typography variant="caption" color="text.secondary">个人简介</Typography>
          <Typography variant="body2">{record.bio || '-'}</Typography>
        </Box>
      </Box>

      <Divider sx={{ mb: 2 }} />

      <Button
        variant="contained"
        color={isBanned ? 'success' : 'error'}
        startIcon={isBanned ? <UnblockIcon /> : <BlockIcon />}
        onClick={() => setBanOpen(true)}
        sx={{ borderRadius: 2, textTransform: 'none' }}
      >
        {isBanned ? '解封用户' : '封禁用户'}
      </Button>

      <Dialog open={banOpen} onClose={() => setBanOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {isBanned ? '解封用户' : '封禁用户'}：{record.username}
        </DialogTitle>
        <DialogContent>
          {!isBanned && (
            <Alert severity="warning" sx={{ mb: 2, borderRadius: 2 }}>
              封禁后该用户将无法登录和进行任何写操作。
            </Alert>
          )}
          <MuiTextField
            label={isBanned ? '解封原因（可选）' : '封禁原因 *'}
            value={banReason}
            onChange={(e) => setBanReason(e.target.value)}
            fullWidth
            multiline
            rows={3}
            size="small"
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions sx={{ p: 2, pt: 0 }}>
          <Button onClick={() => setBanOpen(false)} color="inherit" sx={{ borderRadius: 2 }}>取消</Button>
          <Button
            onClick={handleBan}
            variant="contained"
            color={isBanned ? 'success' : 'error'}
            disabled={submitting || (!isBanned && !banReason.trim())}
            sx={{ borderRadius: 2, textTransform: 'none' }}
          >
            {submitting ? <CircularProgress size={18} /> : isBanned ? '确认解封' : '确认封禁'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default function UserShow(props: ShowProps) {
  return (
    <Show {...props}>
      <SimpleShowLayout>
        <UserShowContent />
      </SimpleShowLayout>
    </Show>
  );
}
