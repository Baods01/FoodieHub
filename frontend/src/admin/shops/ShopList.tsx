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
  TableSortLabel,
  InputAdornment,
} from '@mui/material';
import {
  Search as SearchIcon,
} from '@mui/icons-material';
import apiClient from '../../api/client';

interface Shop {
  id: number;
  name: string;
  category: string;
  area: string;
  average_rating: number;
  is_active: boolean;
  view_count: number;
  favorite_count: number;
  created_at: string;
}

export default function ShopList() {
  const navigate = useNavigate();
  const [shops, setShops] = useState<Shop[]>([]);
  const [loading, setLoading] = useState(true);
  const [keyword, setKeyword] = useState('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(20);
  const [orderBy, setOrderBy] = useState('favorite_count');
  const [orderDir, setOrderDir] = useState<'desc' | 'asc'>('desc');
  const [banTarget, setBanTarget] = useState<{ id: number; name: string; banned: boolean } | null>(null);
  const [banReason, setBanReason] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const loadShops = () => {
    setLoading(true);
    apiClient.get('/shops', {
      params: {
        keyword: keyword || undefined,
        page: page + 1,
        page_size: rowsPerPage,
        sort_by: orderBy,
        sort_order: orderDir,
      },
    })
      .then((res) => {
        const data = (res.data as any)?.data ?? res.data;
        const items = Array.isArray(data) ? data : data?.items ?? data?.data ?? [];
        setShops(items);
      })
      .catch(() => {
        // Mock 数据（后端未就绪时使用）
        const mockShops: Shop[] = [
          { id: 1, name: '陈记糖水铺', category: '糖水', area: '华农西门', average_rating: 4.5, is_active: true, view_count: 2500, favorite_count: 320, created_at: '2026-03-01T00:00:00Z' },
          { id: 2, name: '重庆老火锅', category: '火锅', area: '华农南门', average_rating: 4.8, is_active: true, view_count: 4200, favorite_count: 480, created_at: '2026-03-10T00:00:00Z' },
          { id: 3, name: '黑心快餐', category: '快餐', area: '华农北门', average_rating: 2.5, is_active: false, view_count: 150, favorite_count: 25, created_at: '2026-04-01T00:00:00Z' },
          { id: 4, name: '潮味粉面馆', category: '粉面', area: '校内', average_rating: 4.2, is_active: true, view_count: 1500, favorite_count: 180, created_at: '2026-03-20T00:00:00Z' },
          { id: 5, name: '深夜烧烤摊', category: '烧烤', area: '华农西门', average_rating: 4.4, is_active: true, view_count: 2900, favorite_count: 350, created_at: '2026-04-15T00:00:00Z' },
        ];
        // 按排序字段
        const sorted = [...mockShops].sort((a, b) => {
          const aVal = (a as any)[orderBy] ?? 0;
          const bVal = (b as any)[orderBy] ?? 0;
          return orderDir === 'desc' ? bVal - aVal : aVal - bVal;
        });
        setShops(sorted);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadShops(); }, [page, rowsPerPage, orderBy, orderDir]);

  const handleSearch = () => { setPage(0); loadShops(); };

  const handleSort = (field: string) => {
    if (orderBy === field) {
      setOrderDir(orderDir === 'asc' ? 'desc' : 'asc');
    } else {
      setOrderBy(field);
      setOrderDir('desc');
    }
  };

  const handleBanAction = async () => {
    if (!banTarget) return;
    if (!banTarget.banned && !banReason.trim()) return;
    setSubmitting(true);
    try {
      if (banTarget.banned) {
        await apiClient.post(`/admin/shops/${banTarget.id}/unban`, null, {
          params: { reason: banReason.trim() || undefined },
        });
      } else {
        await apiClient.post(`/admin/shops/${banTarget.id}/ban`, null, {
          params: { reason: banReason.trim() },
        });
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
      {/* Title + Search */}
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

      {/* Table */}
      {loading ? (
        <Box sx={{ p: 2 }}>
          {[1, 2, 3].map((i) => <Skeleton key={i} variant="rounded" height={48} sx={{ mb: 1 }} />)}
        </Box>
      ) : (
        <TableContainer sx={{ borderRadius: 2, border: '1px solid #e0e0e0' }}>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ backgroundColor: '#fafafa' }}>
                <TableCell sx={{ fontWeight: 600 }}>
                  <TableSortLabel active={orderBy === 'id'} direction={orderBy === 'id' ? orderDir : 'desc'} onClick={() => handleSort('id')}>
                    ID
                  </TableSortLabel>
                </TableCell>
                <TableCell sx={{ fontWeight: 600 }}>店铺名称</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>品类</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>区域</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>
                  <TableSortLabel active={orderBy === 'average_rating'} direction={orderBy === 'average_rating' ? orderDir : 'desc'} onClick={() => handleSort('average_rating')}>
                    评分
                  </TableSortLabel>
                </TableCell>
                <TableCell sx={{ fontWeight: 600 }}>状态</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>
                  <TableSortLabel active={orderBy === 'favorite_count'} direction={orderBy === 'favorite_count' ? orderDir : 'desc'} onClick={() => handleSort('favorite_count')}>
                    收藏数
                  </TableSortLabel>
                </TableCell>
                <TableCell sx={{ fontWeight: 600, width: 120 }}>操作</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {shops.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} align="center" sx={{ py: 4, color: '#888' }}>暂无数据</TableCell>
                </TableRow>
              ) : shops.map((shop) => (
                <TableRow
                  key={shop.id}
                  hover
                  sx={{ cursor: 'pointer', '&:hover': { backgroundColor: '#f5f5f5' } }}
                  onClick={() => navigate(`/admin/shops/${shop.id}`)}
                >
                  <TableCell>{shop.id}</TableCell>
                  <TableCell sx={{ fontWeight: 500 }}>{shop.name}</TableCell>
                  <TableCell>{shop.category || '-'}</TableCell>
                  <TableCell>{shop.area || '-'}</TableCell>
                  <TableCell>
                    {shop.average_rating != null
                      ? <span>{'⭐'.repeat(Math.round(shop.average_rating))} {shop.average_rating.toFixed(1)}</span>
                      : '-'}
                  </TableCell>
                  <TableCell>
                    {shop.is_active === false
                      ? <Chip label="已封禁" size="small" color="error" />
                      : <Chip label="正常" size="small" color="success" />}
                  </TableCell>
                  <TableCell>{shop.favorite_count ?? 0}</TableCell>
                  <TableCell>
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={(e) => {
                        e.stopPropagation();
                        setBanTarget({ id: shop.id, name: shop.name, banned: shop.is_active === false });
                        setBanReason('');
                      }}
                      sx={{
                        borderRadius: 2, textTransform: 'none', fontSize: 12,
                        borderColor: shop.is_active === false ? '#4caf50' : '#f44336',
                        color: shop.is_active === false ? '#4caf50' : '#f44336',
                      }}
                    >
                      {shop.is_active === false ? '解封' : '封禁'}
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <TablePagination
        component="div"
        count={-1}
        page={page}
        onPageChange={(_, p) => setPage(p)}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={(e) => { setRowsPerPage(parseInt(e.target.value, 10)); setPage(0); }}
        rowsPerPageOptions={[10, 20, 50]}
      />

      {/* Ban Dialog */}
      <Dialog open={!!banTarget} onClose={() => setBanTarget(null)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {banTarget?.banned ? '解封店铺' : '封禁店铺'}：{banTarget?.name}
        </DialogTitle>
        <DialogContent>
          {banTarget && !banTarget.banned && (
            <Alert severity="warning" sx={{ mb: 2, borderRadius: 2 }}>
              封禁后该店铺在前台标记为"已封禁"。
            </Alert>
          )}
          <MuiTextField
            label={banTarget?.banned ? '解封原因（可选）' : '封禁原因 *'}
            value={banReason}
            onChange={(e) => setBanReason(e.target.value)}
            fullWidth
            multiline
            rows={3}
            size="small"
          />
        </DialogContent>
        <DialogActions sx={{ p: 2, pt: 0 }}>
          <Button onClick={() => setBanTarget(null)} sx={{ borderRadius: 2, color: '#666' }}>取消</Button>
          {banTarget?.banned ? (
            <Button onClick={handleBanAction} variant="contained" disabled={submitting}
              sx={{ borderRadius: 2, textTransform: 'none', backgroundColor: '#4caf50', '&:hover': { backgroundColor: '#388e3c' }, color: '#fff' }}>
              {submitting ? <CircularProgress size={18} style={{ color: '#fff' }} /> : '确认解封'}
            </Button>
          ) : (
            <Button onClick={handleBanAction} variant="contained" disabled={submitting || !banReason.trim()}
              sx={{ borderRadius: 2, textTransform: 'none', backgroundColor: '#f44336', '&:hover': { backgroundColor: '#d32f2f' }, color: '#fff' }}>
              {submitting ? <CircularProgress size={18} style={{ color: '#fff' }} /> : '确认封禁'}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
}
