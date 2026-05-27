import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField as MuiTextField,
  CircularProgress,
  Alert,
  Chip,
  Skeleton,
  Avatar,
} from '@mui/material';
import {
  Block as BlockIcon,
  CheckCircle as UnblockIcon,
  ArrowBack as BackIcon,
} from '@mui/icons-material';
import apiClient from '../../api/client';

interface ShopDetail {
  id: number;
  name: string;
  description?: string;
  category?: string;
  area?: string;
  average_rating?: number;
  is_active: boolean;
  view_count: number;
  favorite_count: number;
  created_at: string;
}

export default function ShopEdit() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [shop, setShop] = useState<ShopDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [banOpen, setBanOpen] = useState(false);
  const [banReason, setBanReason] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    apiClient.get(`/shops/${id}`)
      .then((res) => {
        const data = (res.data as any)?.data ?? res.data;
        setShop(Array.isArray(data) ? data[0] : data);
      })
      .catch(() => setShop(null))
      .finally(() => setLoading(false));
  }, [id]);

  const handleBan = async () => {
    if (!shop || (!banReason.trim() && shop.is_active !== false)) return;
    setSubmitting(true);
    try {
      if (shop.is_active === false) {
        await apiClient.post(`/admin/shops/${shop.id}/unban`, null, {
          params: { reason: banReason.trim() || undefined },
        });
      } else {
        await apiClient.post(`/admin/shops/${shop.id}/ban`, null, {
          params: { reason: banReason.trim() },
        });
      }
      setBanOpen(false);
      // Reload
      window.location.reload();
    } catch {
      alert('操作失败，请重试');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Skeleton variant="rounded" height={200} />
      </Box>
    );
  }

  if (!shop) {
    return (
      <Box sx={{ p: 4, textAlign: 'center', color: '#888' }}>
        店铺不存在或加载失败
      </Box>
    );
  }

  const isBanned = shop.is_active === false;

  return (
    <Box sx={{ p: 3, maxWidth: 700, mx: 'auto' }}>
      {/* Back button */}
      <Button
        startIcon={<BackIcon />}
        onClick={() => navigate('/admin/shops')}
        sx={{ mb: 2, borderRadius: 2, textTransform: 'none', color: '#666' }}
      >
        返回店铺列表
      </Button>

      {/* Shop info card */}
      <Box sx={{ bgcolor: '#fff', borderRadius: 2, border: '1px solid #e0e0e0', p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <Avatar sx={{ bgcolor: '#FF7E3A', width: 56, height: 56, fontSize: 24 }}>
            {shop.name?.charAt(0)}
          </Avatar>
          <Box>
            <Typography variant="h6" fontWeight={700}>{shop.name}</Typography>
            <Typography variant="body2" color="text.secondary">
              ID: {shop.id} · {shop.category || '-'} · {shop.area || '-'}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
              {isBanned ? (
                <Chip label="已封禁" size="small" color="error" />
              ) : (
                <Chip label="正常" size="small" color="success" />
              )}
              <Chip label={`评分 ${shop.average_rating?.toFixed(1) || '-'}`} size="small" variant="outlined" />
            </Box>
          </Box>
        </Box>

        <Divider sx={{ mb: 2 }} />

        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mb: 2 }}>
          <Box>
            <Typography variant="caption" color="text.secondary">店铺描述</Typography>
            <Typography variant="body2">{shop.description || '暂无描述'}</Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary">浏览量</Typography>
            <Typography variant="body2">{shop.view_count ?? 0}</Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary">收藏数</Typography>
            <Typography variant="body2">{shop.favorite_count ?? 0}</Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary">创建时间</Typography>
            <Typography variant="body2">{new Date(shop.created_at).toLocaleDateString()}</Typography>
          </Box>
        </Box>

        <Divider sx={{ my: 2 }} />

        <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
          违规处置
        </Typography>
        <Button
          variant="contained"
          startIcon={isBanned ? <UnblockIcon /> : <BlockIcon />}
          onClick={() => setBanOpen(true)}
          sx={{
            borderRadius: 2, textTransform: 'none',
            backgroundColor: isBanned ? '#4caf50' : '#f44336',
            '&:hover': { backgroundColor: isBanned ? '#388e3c' : '#d32f2f' },
          }}
        >
          {isBanned ? '解封店铺' : '封禁店铺'}
        </Button>
      </Box>

      <Dialog open={banOpen} onClose={() => setBanOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {isBanned ? '解封店铺' : '封禁店铺'}：{shop.name}
        </DialogTitle>
        <DialogContent>
          {!isBanned && (
            <Alert severity="warning" sx={{ mb: 2, borderRadius: 2 }}>
              封禁后该店铺在前台标记为"已封禁"。
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
          <Button onClick={() => setBanOpen(false)} sx={{ borderRadius: 2, color: '#666' }}>取消</Button>
          {isBanned ? (
            <Button onClick={handleBan} variant="contained" disabled={submitting}
              sx={{ borderRadius: 2, textTransform: 'none', backgroundColor: '#4caf50', color: '#fff', '&:hover': { backgroundColor: '#388e3c' } }}>
              {submitting ? <CircularProgress size={18} style={{ color: '#fff' }} /> : '确认解封'}
            </Button>
          ) : (
            <Button onClick={handleBan} variant="contained" disabled={submitting || !banReason.trim()}
              sx={{ borderRadius: 2, textTransform: 'none', backgroundColor: '#f44336', color: '#fff', '&:hover': { backgroundColor: '#d32f2f' } }}>
              {submitting ? <CircularProgress size={18} style={{ color: '#fff' }} /> : '确认封禁'}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
}
