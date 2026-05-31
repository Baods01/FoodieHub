import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  Divider,
  Alert,
  CircularProgress,
  Snackbar,
  Chip,
} from '@mui/material';
import {
  Send as SendIcon,
  ArrowBack as BackIcon,
  Preview as PreviewIcon,
} from '@mui/icons-material';
import apiClient from '../../api/client';

export default function AnnouncementCreate() {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false, message: '', severity: 'success',
  });
  const [preview, setPreview] = useState(false);

  const charCount = content.length;

  const handleSubmit = async () => {
    if (!title.trim() || !content.trim()) return;
    setSubmitting(true);
    try {
      const res = await apiClient.post('/admin/announcements', null, {
        params: { title: title.trim(), content: content.trim() },
      });
      const sentCount = (res.data as any)?.data?.sent_count ?? 0;
      setSnackbar({ open: true, message: `公告发布成功，已推送给 ${sentCount} 位用户`, severity: 'success' });
      setTitle('');
      setContent('');
    } catch {
      setSnackbar({ open: true, message: '发布失败，请重试', severity: 'error' });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box sx={{ p: { xs: 2, sm: 4 } }}>
      {/* 返回按钮 + 标题 */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 4 }}>
        <Button
          startIcon={<BackIcon />}
          onClick={() => navigate('/admin/announcements')}
          sx={{ borderRadius: 2, textTransform: 'none', color: '#666', minWidth: 0 }}
        >
          返回
        </Button>
        <Typography variant="h5" fontWeight={700}>发布公告</Typography>
      </Box>

      {/* 编辑区 */}
      <Card sx={{ borderRadius: 2, border: '1px solid #e0e0e0', mb: 3 }}>
        <CardContent sx={{ p: { xs: 2, sm: 4 } }}>
          <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 1, fontWeight: 600 }}>公告标题 *</Typography>
          <TextField
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="输入公告标题"
            fullWidth
            size="medium"
            sx={{ mb: 4 }}
            inputProps={{ maxLength: 100 }}
          />

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="subtitle1" color="text.secondary" sx={{ fontWeight: 600 }}>公告内容 *</Typography>
            <Typography variant="caption" color={charCount > 2000 ? 'error' : 'text.secondary'}>
              {charCount} / 2000
            </Typography>
          </Box>
          <TextField
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="输入公告内容，支持多行文本"
            fullWidth
            multiline
            rows={14}
            size="medium"
            inputProps={{ maxLength: 2000 }}
          />

          <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1.5, mt: 3 }}>
            <Button
              variant="outlined"
              size="large"
              startIcon={<PreviewIcon />}
              onClick={() => setPreview(!preview)}
              sx={{ borderRadius: 2, textTransform: 'none', px: 3 }}
            >
              {preview ? '隐藏预览' : '预览'}
            </Button>
            <Button
              variant="contained"
              size="large"
              startIcon={submitting ? <CircularProgress size={20} sx={{ color: '#fff' }} /> : <SendIcon />}
              onClick={handleSubmit}
              disabled={submitting || !title.trim() || !content.trim()}
              sx={{
                borderRadius: 2, textTransform: 'none', px: 4, backgroundColor: '#FF7E3A',
                '&:hover': { backgroundColor: '#e86a2a' },
                '&.Mui-disabled': { backgroundColor: '#e0e0e0' },
              }}
            >
              {submitting ? '发布中...' : '发布公告'}
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* 预览区 */}
      {preview && (
        <Card sx={{ borderRadius: 2, border: '1px solid #e0e0e0', bgcolor: '#fafafa' }}>
          <CardContent sx={{ p: { xs: 2, sm: 4 } }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <PreviewIcon fontSize="small" color="action" />
              <Typography variant="subtitle2" color="text.secondary">预览</Typography>
            </Box>
            <Divider sx={{ mb: 2 }} />
            {title.trim() ? (
              <Typography variant="h5" fontWeight={700} sx={{ mb: 1.5 }}>{title}</Typography>
            ) : (
              <Typography variant="h5" fontWeight={700} sx={{ mb: 1.5, color: '#bbb' }}>（标题）</Typography>
            )}
            <Divider sx={{ mb: 2 }} />
            {content.trim() ? (
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 2 }}>{content}</Typography>
            ) : (
              <Typography variant="body1" sx={{ color: '#bbb' }}>（输入内容后将在此显示预览）</Typography>
            )}
            <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
              <Chip label="公告" size="small" color="primary" variant="outlined" />
              <Chip label={`${charCount} 字`} size="small" variant="outlined" />
            </Box>
          </CardContent>
        </Card>
      )}

      {/* 成功/失败提示 */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          variant="filled"
          sx={{ borderRadius: 2 }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}
