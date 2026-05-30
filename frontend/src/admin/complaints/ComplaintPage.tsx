import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  Divider,
  Skeleton,
  Snackbar,
  List,
  ListItemButton,
  ListItemText,
  ListItemIcon,
  Pagination,
} from '@mui/material';
import {
  Flag as FlagIcon,
  WarningAmber as WarningIcon,
  EditNote as EditIcon,
} from '@mui/icons-material';
import apiClient from '../../api/client';

interface FeedbackItem {
  id: number;
  type: string;           // complaint / edit_request
  target_type: string;    // shop / comment / image
  target_id: number;
  reason_id: number;
  description: string | null;
  status: string;
  created_at: string;
}

const typeLabels: Record<string, Record<string, string>> = {
  complaint: {
    shop: '店铺举报',
    comment: '评论举报',
    image: '图片举报',
  },
  edit_request: {
    shop: '店铺勘误',
    comment: '评论勘误',
    image: '图片勘误',
  },
};

const typeColors: Record<string, string> = {
  complaint: '#F44336',
  edit_request: '#FF9800',
};

const statusLabels: Record<string, string> = {
  pending: '待处理',
  approved: '已通过',
  rejected: '已驳回',
};

const statusColors: Record<string, string> = {
  pending: '#FF9800',
  approved: '#4CAF50',
  rejected: '#9E9E9E',
};

export default function ComplaintPage() {
  const [feedbacks, setFeedbacks] = useState<FeedbackItem[]>([]);
  const [selected, setSelected] = useState<FeedbackItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string }>({
    open: false, message: '',
  });
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [tab, setTab] = useState<'pending' | 'approved' | 'rejected'>('pending');
  const [typeFilter, setTypeFilter] = useState<string | null>(null);

  const loadFeedbacks = () => {
    setLoading(true);
    const params: Record<string, any> = { page, page_size: pageSize, status: tab };
    if (typeFilter) params.type = typeFilter;
    apiClient.get('/admin/feedbacks', { params })
      .then((res) => {
        const data = (res.data as any)?.data ?? res.data;
        setFeedbacks(data?.items ?? []);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadFeedbacks(); }, [tab, typeFilter, page]);

  const handleApprove = async () => {
    if (!selected) return;
    setSubmitting(true);
    try {
      await apiClient.post(`/admin/feedbacks/${selected.id}/approve`);
      setSnackbar({ open: true, message: '已通过' });
      setSelected(null);
      loadFeedbacks();
    } catch {
      setSnackbar({ open: true, message: '操作失败' });
    } finally {
      setSubmitting(false);
    }
  };

  const handleReject = async () => {
    if (!selected) return;
    setSubmitting(true);
    try {
      await apiClient.post(`/admin/feedbacks/${selected.id}/reject`);
      setSnackbar({ open: true, message: '已驳回' });
      setSelected(null);
      loadFeedbacks();
    } catch {
      setSnackbar({ open: true, message: '操作失败' });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>反馈处理</Typography>

      {/* Filters */}
      <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap', alignItems: 'center' }}>
        {/* Status tabs */}
        {(['pending', 'approved', 'rejected'] as const).map((key) => (
          <Chip
            key={key}
            label={statusLabels[key]}
            color={tab === key ? 'primary' : 'default'}
            onClick={() => { setTab(key); setPage(1); }}
            clickable
            variant={tab === key ? 'filled' : 'outlined'}
            sx={{ fontWeight: 500 }}
          />
        ))}
        <Divider orientation="vertical" flexItem sx={{ mx: 1 }} />
        {/* Type filter */}
        <Chip label="全部" onClick={() => setTypeFilter(null)} clickable variant={!typeFilter ? 'filled' : 'outlined'} sx={{ fontWeight: 500 }} />
        <Chip label="举报" icon={<FlagIcon />} onClick={() => setTypeFilter('complaint')} clickable variant={typeFilter === 'complaint' ? 'filled' : 'outlined'} sx={{ fontWeight: 500 }} />
        <Chip label="勘误" icon={<EditIcon />} onClick={() => setTypeFilter('edit_request')} clickable variant={typeFilter === 'edit_request' ? 'filled' : 'outlined'} sx={{ fontWeight: 500 }} />
      </Box>

      <Grid container spacing={2}>
        {/* Left: List */}
        <Grid size={{ xs: 12, md: 5 }}>
          <Card variant="outlined" sx={{ borderRadius: 2, maxHeight: '70vh', overflow: 'auto' }}>
            {loading ? (
              <Box sx={{ p: 2 }}>
                {[1, 2, 3].map((i) => <Skeleton key={i} variant="rounded" height={72} sx={{ mb: 1 }} />)}
              </Box>
            ) : feedbacks.length === 0 ? (
              <Box sx={{ p: 4, textAlign: 'center', color: '#888' }}>暂无反馈</Box>
            ) : (
              <List disablePadding>
                {feedbacks.map((fb) => (
                  <ListItemButton
                    key={fb.id}
                    selected={selected?.id === fb.id}
                    onClick={() => setSelected(fb)}
                    sx={{ borderBottom: '1px solid #f0f0f0' }}
                  >
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      {fb.type === 'complaint' ? (
                        <WarningIcon sx={{ color: typeColors.complaint, fontSize: 20 }} />
                      ) : (
                        <EditIcon sx={{ color: typeColors.edit_request, fontSize: 20 }} />
                      )}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                          <Chip
                            label={typeLabels[fb.type]?.[fb.target_type] || fb.target_type}
                            size="small"
                            sx={{ backgroundColor: `${typeColors[fb.type]}20`, color: typeColors[fb.type], fontWeight: 500, fontSize: 11 }}
                          />
                          <Chip
                            label={statusLabels[fb.status]}
                            size="small"
                            sx={{ backgroundColor: `${statusColors[fb.status]}20`, color: statusColors[fb.status], fontWeight: 500, fontSize: 11 }}
                          />
                          <Typography variant="caption" color="text.secondary">
                            {new Date(fb.created_at).toLocaleDateString()}
                          </Typography>
                        </Box>
                      }
                      secondary={fb.description || `#${fb.target_id}`}
                      secondaryTypographyProps={{ noWrap: true }}
                    />
                  </ListItemButton>
                ))}
              </List>
            )}
          </Card>
          {feedbacks.length > 0 && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 1 }}>
              <Pagination count={Math.ceil(feedbacks.length / pageSize)} page={page} onChange={(_, p) => setPage(p)} size="small" />
            </Box>
          )}
        </Grid>

        {/* Right: Detail + Actions */}
        <Grid size={{ xs: 12, md: 7 }}>
          {!selected ? (
            <Card variant="outlined" sx={{ borderRadius: 2, p: 4, textAlign: 'center', color: '#888' }}>
              请在左侧选择一个反馈进行处理
            </Card>
          ) : (
            <Card variant="outlined" sx={{ borderRadius: 2 }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  {selected.type === 'complaint' ? (
                    <FlagIcon sx={{ color: typeColors.complaint }} />
                  ) : (
                    <EditIcon sx={{ color: typeColors.edit_request }} />
                  )}
                  <Typography variant="subtitle1" fontWeight={600}>
                    {typeLabels[selected.type]?.[selected.target_type] || selected.target_type} #{selected.id}
                  </Typography>
                </Box>

                <Box sx={{ display: 'grid', gap: 2, mb: 2 }}>
                  <Box>
                    <Typography variant="caption" color="text.secondary">反馈类型</Typography>
                    <Typography variant="body2">{selected.type === 'complaint' ? '举报' : '勘误'}</Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary">反馈对象</Typography>
                    <Typography variant="body2">{selected.target_type} #{selected.target_id}</Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary">原因 ID</Typography>
                    <Typography variant="body2">{selected.reason_id}</Typography>
                  </Box>
                  {selected.description && (
                    <Box>
                      <Typography variant="caption" color="text.secondary">补充说明</Typography>
                      <Box sx={{ p: 1.5, bgcolor: '#f9f9f9', borderRadius: 1, mt: 0.5 }}>
                        <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>{selected.description}</Typography>
                      </Box>
                    </Box>
                  )}

                  {/* Status indicator */}
                  <Chip
                    label={statusLabels[selected.status]}
                    size="small"
                    sx={{ backgroundColor: `${statusColors[selected.status]}20`, color: statusColors[selected.status], fontWeight: 500, alignSelf: 'flex-start' }}
                  />
                </Box>

                {selected.status === 'pending' && (
                  <>
                    <Divider sx={{ my: 2 }} />
                    <Box sx={{ display: 'flex', gap: 2 }}>
                      <Button
                        variant="contained"
                        onClick={handleApprove}
                        disabled={submitting}
                        fullWidth
                        sx={{ borderRadius: 2, textTransform: 'none', fontWeight: 600, backgroundColor: '#4CAF50', '&:hover': { backgroundColor: '#388E3C' } }}
                      >
                        通过
                      </Button>
                      <Button
                        variant="contained"
                        onClick={handleReject}
                        disabled={submitting}
                        fullWidth
                        sx={{ borderRadius: 2, textTransform: 'none', fontWeight: 600, backgroundColor: '#F44336', '&:hover': { backgroundColor: '#D32F2F' } }}
                      >
                        驳回
                      </Button>
                    </Box>
                  </>
                )}
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        message={snackbar.message}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      />
    </Box>
  );
}
