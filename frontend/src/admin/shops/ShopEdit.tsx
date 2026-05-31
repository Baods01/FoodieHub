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
  MergeType as MergeIcon,
  Save as SaveIcon,
} from '@mui/icons-material';
import apiClient from '../../api/client';

interface DictDataItem {
  id: number;
  name: string;
  dict_type_name: string;
}

interface ShopDetail {
  id: number;
  name: string;
  dict_data: DictDataItem[];
  average_rating: number;
  is_banned: boolean;
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
  const [nameEdit, setNameEdit] = useState('');
  const [nameSaving, setNameSaving] = useState(false);
  const [mergeOpen, setMergeOpen] = useState(false);
  const [mergeTargetId, setMergeTargetId] = useState('');
  const [mergeSubmitting, setMergeSubmitting] = useState(false);
  const [dictDataOptions, setDictDataOptions] = useState<Record<string, {id: number; name: string}[]>>({});
  const [selectedDictIds, setSelectedDictIds] = useState<number[]>([]);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    apiClient.get(`/admin/shops/${id}`)
      .then((res) => {
        const data = (res.data as any)?.data ?? res.data;
        const s = Array.isArray(data) ? data[0] : data;
        setShop(s);
        setNameEdit(s?.name ?? '');
      })
      .catch(() => setShop(null))
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    if (!shop) return;
    // 加载可选字典数据
    Promise.all([
      apiClient.get('/dict/data', { params: { type_name: '品类' } }).then(r => (r.data as any)?.data ?? []),
      apiClient.get('/dict/data', { params: { type_name: '区域' } }).then(r => (r.data as any)?.data ?? []),
      apiClient.get('/dict/data', { params: { type_name: '就餐方式' } }).then(r => (r.data as any)?.data ?? []),
    ]).then(([cats, areas, dining]) => {
      setDictDataOptions({ '品类': cats, '区域': areas, '就餐方式': dining });
    });
    // 初始化选中状态
    setSelectedDictIds((shop.dict_data || []).map(d => d.id));
  }, [shop]);

  const handleBan = async () => {
    if (!shop) return;
    setSubmitting(true);
    try {
      if (shop.is_banned) {
        await apiClient.post(`/admin/shops/${shop.id}/unban`, null, { params: { reason: banReason.trim() || undefined } });
      } else {
        await apiClient.post(`/admin/shops/${shop.id}/ban`, null, { params: { reason: banReason.trim() } });
      }
      setBanOpen(false);
      window.location.reload();
    } catch { alert('操作失败'); }
    finally { setSubmitting(false); }
  };

  const handleSaveName = async () => {
    if (!shop || !nameEdit.trim()) return;
    setNameSaving(true);
    try {
      await apiClient.put(`/shops/${shop.id}`, { name: nameEdit.trim() });
      setShop({ ...shop, name: nameEdit.trim() });
    } catch { alert('保存失败'); }
    finally { setNameSaving(false); }
  };

  const handleMerge = async () => {
    if (!shop || !mergeTargetId.trim()) return;
    setMergeSubmitting(true);
    try {
      await apiClient.post('/admin/shops/merge', null, {
        params: { main_shop_id: parseInt(mergeTargetId.trim()), duplicate_shop_ids: shop.id.toString() },
      });
      setMergeOpen(false);
      alert('合并成功');
      navigate('/admin/shops');
    } catch { alert('合并失败，请确认店铺ID正确'); }
    finally { setMergeSubmitting(false); }
  };

  if (loading) return <Box sx={{ p: 3 }}><Skeleton variant="rounded" height={200} /></Box>;
  if (!shop) return <Box sx={{ p: 4, textAlign: 'center', color: '#888' }}>店铺不存在或加载失败</Box>;

  const isBanned = shop.is_banned === true;

  const handleTagToggle = (dictId: number) => {
    setSelectedDictIds(prev =>
      prev.includes(dictId) ? prev.filter(id => id !== dictId) : [...prev, dictId]
    );
  };

  const handleSaveTags = async () => {
    if (!shop) return;
    try {
      await apiClient.put(`/shops/${shop.id}`, { dict_data_ids: selectedDictIds });
    } catch { alert('保存标签失败'); }
  };

  const categories = (shop.dict_data || []).filter(d => d.dict_type_name === '品类').map(d => d.name);
  const areas = (shop.dict_data || []).filter(d => d.dict_type_name === '区域').map(d => d.name);
  const diningMethods = (shop.dict_data || []).filter(d => d.dict_type_name === '就餐方式').map(d => d.name);

  return (
    <Box sx={{ p: 3, maxWidth: 700, mx: 'auto' }}>
      <Button startIcon={<BackIcon />} onClick={() => navigate('/admin/shops')}
        sx={{ mb: 2, borderRadius: 2, textTransform: 'none', color: '#666' }}>
        返回店铺列表
      </Button>

      <Box sx={{ bgcolor: '#fff', borderRadius: 2, border: '1px solid #e0e0e0', p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <Avatar sx={{ bgcolor: '#FF7E3A', width: 56, height: 56, fontSize: 24 }}>{shop.name?.charAt(0)}</Avatar>
          <Box sx={{ flex: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <MuiTextField size="small" value={nameEdit} onChange={(e) => setNameEdit(e.target.value)}
                sx={{ '& input': { fontSize: 18, fontWeight: 700, py: 0.5 } }} />
              <Button size="small" onClick={handleSaveName} disabled={nameSaving || nameEdit === shop.name}
                startIcon={nameSaving ? <CircularProgress size={14} /> : <SaveIcon />}
                sx={{ borderRadius: 2, textTransform: 'none', whiteSpace: 'nowrap' }}>
                保存
              </Button>
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              ID: {shop.id} · {categories[0] || '-'} · {areas[0] || '-'} · {diningMethods.join('、') || '-'}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
              {isBanned ? <Chip label="已封禁" size="small" color="error" /> : <Chip label="正常" size="small" color="success" />}
              <Chip label={`评分 ${shop.average_rating?.toFixed(1) || '-'}`} size="small" variant="outlined" />
            </Box>
          </Box>
        </Box>

        <Divider sx={{ mb: 2 }} />

        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mb: 2 }}>
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
        <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>标签修改</Typography>
        {Object.entries(dictDataOptions).map(([typeName, items]) => (
          <Box key={typeName} sx={{ mb: 1.5 }}>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>{typeName}</Typography>
            <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
              {items.map((item) => {
                const selected = selectedDictIds.includes(item.id);
                return (
                  <Chip
                    key={item.id}
                    label={item.name}
                    size="small"
                    onClick={() => handleTagToggle(item.id)}
                    color={selected ? 'primary' : 'default'}
                    variant={selected ? 'filled' : 'outlined'}
                    sx={{ cursor: 'pointer' }}
                  />
                );
              })}
            </Box>
          </Box>
        ))}
        <Button size="small" onClick={handleSaveTags} variant="outlined" sx={{ borderRadius: 2, textTransform: 'none', mt: 1 }}>
          保存标签
        </Button>
        <Divider sx={{ my: 2 }} />
        <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>操作</Typography>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Button variant="contained" startIcon={isBanned ? <UnblockIcon /> : <BlockIcon />}
            onClick={() => setBanOpen(true)}
            sx={{ borderRadius: 2, textTransform: 'none', backgroundColor: isBanned ? '#4caf50' : '#f44336' }}>
            {isBanned ? '解封店铺' : '封禁店铺'}
          </Button>
          <Button variant="outlined" startIcon={<MergeIcon />} onClick={() => setMergeOpen(true)}
            sx={{ borderRadius: 2, textTransform: 'none' }}>
            合并店铺
          </Button>
        </Box>
      </Box>

      <Dialog open={banOpen} onClose={() => setBanOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{isBanned ? '解封' : '封禁'}：{shop.name}</DialogTitle>
        <DialogContent>
          {!isBanned && <Alert severity="warning" sx={{ mb: 2, borderRadius: 2 }}>封禁后前台标记为"已封禁"。</Alert>}
          <MuiTextField label={isBanned ? '解封原因（可选）' : '封禁原因 *'} value={banReason}
            onChange={(e) => setBanReason(e.target.value)} fullWidth multiline rows={3} size="small" />
        </DialogContent>
        <DialogActions sx={{ p: 2, pt: 0 }}>
          <Button onClick={() => setBanOpen(false)} sx={{ borderRadius: 2, color: '#666' }}>取消</Button>
          <Button onClick={handleBan} variant="contained" disabled={submitting || (!isBanned && !banReason.trim())}
            sx={{ borderRadius: 2, textTransform: 'none', backgroundColor: isBanned ? '#4caf50' : '#f44336', color: '#fff' }}>
            {submitting ? <CircularProgress size={18} /> : isBanned ? '确认解封' : '确认封禁'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={mergeOpen} onClose={() => setMergeOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>合并店铺</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2, borderRadius: 2 }}>
            将当前店铺 ({shop.name}, ID: {shop.id}) 合并到目标店铺，合并后当前店铺将被关闭。
          </Alert>
          <MuiTextField label="目标店铺 ID" value={mergeTargetId} onChange={(e) => setMergeTargetId(e.target.value)}
            fullWidth size="small" type="number" placeholder="输入目标店铺ID" />
        </DialogContent>
        <DialogActions sx={{ p: 2, pt: 0 }}>
          <Button onClick={() => setMergeOpen(false)} sx={{ borderRadius: 2, color: '#666' }}>取消</Button>
          <Button onClick={handleMerge} variant="contained" disabled={mergeSubmitting || !mergeTargetId.trim()}
            sx={{ borderRadius: 2, textTransform: 'none', backgroundColor: '#FF7E3A', color: '#fff' }}>
            {mergeSubmitting ? <CircularProgress size={18} style={{ color: '#fff' }} /> : '确认合并'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
