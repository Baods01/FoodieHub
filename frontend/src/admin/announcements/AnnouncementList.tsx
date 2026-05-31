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
  Button,
  Chip,
  Skeleton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
} from '@mui/material';
import {
  Add as AddIcon,
  InfoOutlined as InfoIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import apiClient from '../../api/client';

interface Announcement {
  title: string;
  content: string;
  sent_count: number;
  created_at: string;
}

export default function AnnouncementList() {
  const navigate = useNavigate();
  const [items, setItems] = useState<Announcement[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(20);
  const [detail, setDetail] = useState<Announcement | null>(null);

  const loadAnnouncements = () => {
    setLoading(true);
    apiClient.get('/admin/announcements', {
      params: { page: page + 1, page_size: rowsPerPage },
    })
      .then((res) => {
        const data = (res.data as any)?.data ?? res.data;
        setItems(data?.items ?? []);
      })
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadAnnouncements(); }, [page, rowsPerPage]);

  return (
    <Box sx={{ p: 2 }}>
      {/* 顶栏 */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" fontWeight={700}>公告管理</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate('/admin/announcements/create')}
          sx={{
            borderRadius: 2, textTransform: 'none', backgroundColor: '#FF7E3A',
            '&:hover': { backgroundColor: '#e86a2a' },
          }}
        >
          发布公告
        </Button>
      </Box>

      {/* 列表 */}
      {loading ? (
        <Box sx={{ p: 2 }}>
          {[1, 2, 3].map((i) => <Skeleton key={i} variant="rounded" height={48} sx={{ mb: 1 }} />)}
        </Box>
      ) : (
        <TableContainer sx={{ borderRadius: 2, border: '1px solid #e0e0e0' }}>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ backgroundColor: '#fafafa' }}>
                <TableCell sx={{ fontWeight: 600, width: '40%' }}>公告标题</TableCell>
                <TableCell sx={{ fontWeight: 600, width: '30%' }}>内容摘要</TableCell>
                <TableCell sx={{ fontWeight: 600, width: 100 }}>推送人数</TableCell>
                <TableCell sx={{ fontWeight: 600, width: 160 }}>发布时间</TableCell>
                <TableCell sx={{ fontWeight: 600, width: 60 }}>详情</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {items.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center" sx={{ py: 4, color: '#888' }}>暂无公告</TableCell>
                </TableRow>
              ) : items.map((item, idx) => (
                <TableRow key={idx} hover>
                  <TableCell sx={{ fontWeight: 500 }}>{item.title}</TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{
                      overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 300, color: '#666'
                    }}>
                      {item.content}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip label={`${item.sent_count} 人`} size="small" variant="outlined" color="primary" />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary">
                      {new Date(item.created_at).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <IconButton size="small" onClick={() => setDetail(item)}>
                      <InfoIcon fontSize="small" />
                    </IconButton>
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

      {/* 详情弹窗 */}
      <Dialog open={!!detail} onClose={() => setDetail(null)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6" fontWeight={700}>{detail?.title}</Typography>
          <IconButton onClick={() => setDetail(null)} size="small"><CloseIcon /></IconButton>
        </DialogTitle>
        <DialogContent dividers>
          <Box sx={{ mb: 2 }}>
            <Typography variant="caption" color="text.secondary">推送人数</Typography>
            <Typography variant="body2">{detail?.sent_count} 人</Typography>
          </Box>
          <Box sx={{ mb: 2 }}>
            <Typography variant="caption" color="text.secondary">发布时间</Typography>
            <Typography variant="body2">{detail?.created_at ? new Date(detail.created_at).toLocaleString() : '-'}</Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary">公告内容</Typography>
            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', mt: 0.5, lineHeight: 1.8 }}>
              {detail?.content}
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetail(null)} sx={{ borderRadius: 2, textTransform: 'none' }}>关闭</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
