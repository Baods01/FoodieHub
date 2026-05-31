import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField as MuiTextField,
  CircularProgress,
  Alert,
  Skeleton,
  InputAdornment,
} from '@mui/material';
import {
  Search as SearchIcon,
} from '@mui/icons-material';
import apiClient from '../../api/client';

interface Shop {
  id: number;
  name: string;
  dict_data: { id: number; name: string; dict_type_name: string }[];
  average_rating: number;
  is_banned: boolean;
  is_active: boolean;
  view_count: number;
  favorite_count: number;
  created_at: string;
}

function getDictNames(data: { dict_type_name: string; name: string }[], typeName: string): string[] {
  return data.filter(d => d.dict_type_name === typeName).map(d => d.name);
}

export default function ShopList() {
  const navigate = useNavigate();
  const [shops, setShops] = useState<Shop[]>([]);
  const [loading, setLoading] = useState(true);
  const [keyword, setKeyword] = useState('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(20);
  const [banTarget, setBanTarget] = useState<{ id: number; name: string; banned: boolean } | null>(null);
  const [banReason, setBanReason] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const loadShops = () => {
    setLoading(true);
    apiClient.get('/admin/shops', {
      params: {
        keyword: keyword || undefined,
        page: page + 1,
        page_size: rowsPerPage,
      },
    })
      .then((res) => {
        const data = (res.data as any)?.data ?? res.data;
        setShops(data?.items ?? []);
      })
      .catch(() => setShops([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadShops(); }, [page, rowsPerPage]);

  const handleSearch = () => { setPage(0); loadShops(); };

  const handleBanAction = async () => {
    if (!banTarget) return;
    if (!banTarget.banned && !banReason.trim()) return;
    setSubmitting(true);
    try {
      if (banTarget.banned) {
        await apiClient.post(`/admin/shops/${banTarget.id}/unban`, null, { params: { reason: banReason.trim() || undefined } });
      } else {
        await apiClient.post(`/admin/shops/${banTarget.id}/ban`, null, { params: { reason: banReason.trim() } });
      }
      setBanTarget(null);
      setBanReason('');
      loadShops();
    } catch {
      alert('操作失败，请重试');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" fontWeight={700} sx={{ whiteSpace: 'nowrap', flexShrink: 0, mr: 2 }}>店铺管理</Typography>
        <TextField
          size="small"
          placeholder="搜索店铺名称..."
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          slotProps={{
            input: {
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon fontSize="small" color="action" />
                </InputAdornment>
              ),
            },
          }}
          sx={{ minWidth: 280, '& .MuiOutlinedInput-root': { backgroundColor: '#fff', borderRadius: 2 } }}
        />
      </Box>

      {loading ? (
        <Box sx={{ p: 2 }}>
          {[1, 2, 3].map((i) => <Skeleton key={i} variant="rounded" height={48} sx={{ mb: 1 }} />)}
        </Box>
      ) : (
        <TableContainer sx={{ borderRadius: 2, border: '1px solid #e0e0e0' }}>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ backgroundColor: '#fafafa' }}>
                <TableCell sx={{ fontWeight: 600 }}>ID</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>店铺名称</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>品类</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>区域</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>就餐方式</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>评分</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>状态</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>收藏</TableCell>
                <TableCell sx={{ fontWeight: 600, width: 120 }}>操作</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {shops.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} align="center" sx={{ py: 4, color: '#888' }}>暂无数据</TableCell>
                </TableRow>
              ) : shops.map((shop) => {
                const categories = getDictNames(shop.dict_data || [], '品类');
                const areas = getDictNames(shop.dict_data || [], '区域');
                const dining = getDictNames(shop.dict_data || [], '就餐方式');
                const isBanned = shop.is_banned === true || shop.is_active === false;
                return (
                  <TableRow key={shop.id} hover sx={{ cursor: 'pointer', '&:hover': { backgroundColor: '#f5f5f5' } }}
                    onClick={() => navigate(`/admin/shops/${shop.id}`)}>
                    <TableCell>{shop.id}</TableCell>
                    <TableCell sx={{ fontWeight: 500 }}>{shop.name}</TableCell>
                    <TableCell>{categories[0] || '-'}</TableCell>
                    <TableCell>{areas[0] || '-'}</TableCell>
                    <TableCell>{dining.join('、') || '-'}</TableCell>
                    <TableCell>{shop.average_rating ? shop.average_rating.toFixed(1) : '-'}</TableCell>
                    <TableCell>
                      {isBanned ? <Chip label="已封禁" size="small" color="error" /> : <Chip label="正常" size="small" color="success" />}
                    </TableCell>
                    <TableCell>{shop.favorite_count ?? 0}</TableCell>
                    <TableCell>
                      <Button size="small" variant="outlined"
                        onClick={(e) => { e.stopPropagation(); setBanTarget({ id: shop.id, name: shop.name, banned: isBanned }); setBanReason(''); }}
                        sx={{ borderRadius: 2, textTransform: 'none', fontSize: 12, borderColor: isBanned ? '#4caf50' : '#f44336', color: isBanned ? '#4caf50' : '#f44336' }}>
                        {isBanned ? '解封' : '封禁'}
                      </Button>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <TablePagination
        component="div" count={-1} page={page}
        onPageChange={(_, p) => setPage(p)}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={(e) => { setRowsPerPage(parseInt(e.target.value, 10)); setPage(0); }}
        rowsPerPageOptions={[10, 20, 50]}
      />

      <Dialog open={!!banTarget} onClose={() => setBanTarget(null)} maxWidth="sm" fullWidth>
        <DialogTitle>{banTarget?.banned ? '解封店铺' : '封禁店铺'}：{banTarget?.name}</DialogTitle>
        <DialogContent>
          {banTarget && !banTarget.banned && (
            <Alert severity="warning" sx={{ mb: 2, borderRadius: 2 }}>封禁后该店铺在前台标记为"已封禁"。</Alert>
          )}
          <MuiTextField label={banTarget?.banned ? '解封原因（可选）' : '封禁原因 *'} value={banReason}
            onChange={(e) => setBanReason(e.target.value)} fullWidth multiline rows={3} size="small" />
        </DialogContent>
        <DialogActions sx={{ p: 2, pt: 0 }}>
          <Button onClick={() => setBanTarget(null)} sx={{ borderRadius: 2, color: '#666' }}>取消</Button>
          <Button onClick={handleBanAction} variant="contained" disabled={submitting || (!banTarget?.banned && !banReason.trim())}
            sx={{ borderRadius: 2, textTransform: 'none', backgroundColor: banTarget?.banned ? '#4caf50' : '#f44336', color: '#fff' }}>
            {submitting ? <CircularProgress size={18} style={{ color: '#fff' }} /> : banTarget?.banned ? '确认解封' : '确认封禁'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
