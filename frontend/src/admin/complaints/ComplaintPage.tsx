import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  FormLabel,
  TextField as MuiTextField,
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
} from '@mui/icons-material';
import apiClient from '../../api/client';

interface ComplaintItem {
  id: number;
  complainant_type: string;
  complainant_id: number;
  reason_code: string;
  description: string;
  status: string;
  created_at: string;
  reporter_name?: string;
  target_summary?: string;
}

interface ComplaintStats {
  pending: number;
  approved: number;
  rejected: number;
  total: number;
}

const actionOptions = [
  { value: 'delete_comment', label: '删除评论', description: '删除被举报的评论内容' },
  { value: 'ban_shop', label: '封禁店铺', description: '封禁被举报的店铺' },
  { value: 'remove_image', label: '移除图片', description: '移除被举报的图片' },
  { value: 'dismiss', label: '驳回举报', description: '举报不成立，不做处理' },
];

const typeLabels: Record<string, string> = {
  comment: '评论举报',
  shop: '店铺举报',
  image: '图片举报',
};

const typeColors: Record<string, string> = {
  comment: '#FF9800',
  shop: '#F44336',
  image: '#2196F3',
};

export default function ComplaintPage() {
  const [complaints, setComplaints] = useState<ComplaintItem[]>([]);
  const [selected, setSelected] = useState<ComplaintItem | null>(null);
  const [stats, setStats] = useState<ComplaintStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [action, setAction] = useState('dismiss');
  const [resultDesc, setResultDesc] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false, message: '', severity: 'success',
  });
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [tab, setTab] = useState<'pending' | 'approved' | 'rejected'>('pending');

  const loadComplaints = () => {
    setLoading(true);
    const endpoint = tab === 'pending'
      ? `/complaints/admin/pending`
      : `/complaints?status=${tab}`;
    Promise.all([
      apiClient.get(endpoint, { params: { page, page_size: pageSize } }),
      apiClient.get('/complaints/admin/stats'),
    ]).then(([listRes, statsRes]) => {
      const listData = (listRes.data as any)?.data ?? listRes.data;
      const items = Array.isArray(listData) ? listData : listData?.items ?? listData?.data ?? [];
      setComplaints(items);
      setStats((statsRes.data as any)?.data ?? statsRes.data);
      setSelected(null);
      setAction('dismiss');
      setResultDesc('');
    }).catch(() => {
      // Silent - backend not ready
    }).finally(() => setLoading(false));
  };

  useEffect(() => { loadComplaints(); }, [tab, page]);

  const handleSubmit = async () => {
    if (!selected) return;
    setSubmitting(true);
    try {
      await apiClient.post(`/complaints/${selected.id}/handle`, {
        action,
        result_description: resultDesc.trim() || undefined,
      });
      setSnackbar({ open: true, message: '处理成功', severity: 'success' });
      setSelected(null);
      setAction('dismiss');
      setResultDesc('');
      loadComplaints();
    } catch {
      setSnackbar({ open: true, message: '处理失败，请重试', severity: 'error' });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box sx={{ p: 2 }}>
      {/* Title */}
      <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>举报处理</Typography>

      {/* Stats tabs */}
      {stats && (
        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
          {(['pending', 'approved', 'rejected'] as const).map((key) => (
            <Chip
              key={key}
              label={`${key === 'pending' ? '待处理' : key === 'approved' ? '已处理' : '已驳回'} (${stats[key]})`}
              color={tab === key ? 'primary' : 'default'}
              onClick={() => { setTab(key); setPage(1); }}
              clickable
              variant={tab === key ? 'filled' : 'outlined'}
              sx={{ fontWeight: 500 }}
            />
          ))}
        </Box>
      )}

      <Grid container spacing={2}>
        {/* Left: Complaint list */}
        <Grid size={{ xs: 12, md: 5 }}>
          <Card variant="outlined" sx={{ borderRadius: 2, maxHeight: '70vh', overflow: 'auto' }}>
            {loading ? (
              <Box sx={{ p: 2 }}>
                {[1, 2, 3].map((i) => <Skeleton key={i} variant="rounded" height={72} sx={{ mb: 1 }} />)}
              </Box>
            ) : complaints.length === 0 ? (
              <Box sx={{ p: 4, textAlign: 'center', color: '#888' }}>暂无{tab === 'pending' ? '待处理' : ''}举报</Box>
            ) : (
              <List disablePadding>
                {complaints.map((c) => (
                  <ListItemButton
                    key={c.id}
                    selected={selected?.id === c.id}
                    onClick={() => { setSelected(c); setAction('dismiss'); setResultDesc(''); }}
                    sx={{ borderBottom: '1px solid #f0f0f0' }}
                  >
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <WarningIcon sx={{ color: typeColors[c.complainant_type] || '#888', fontSize: 20 }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Chip
                            label={typeLabels[c.complainant_type] || c.complainant_type}
                            size="small"
                            sx={{ backgroundColor: `${typeColors[c.complainant_type] || '#888'}20`, color: typeColors[c.complainant_type] || '#888', fontWeight: 500, fontSize: 11 }}
                          />
                          <Typography variant="caption" color="text.secondary">
                            {new Date(c.created_at).toLocaleDateString()}
                          </Typography>
                        </Box>
                      }
                      secondary={c.target_summary || `#${c.complainant_id}`}
                      secondaryTypographyProps={{ noWrap: true }}
                    />
                  </ListItemButton>
                ))}
              </List>
            )}
          </Card>
          {complaints.length > 0 && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 1 }}>
              <Pagination count={Math.ceil((stats?.pending ?? 10) / pageSize)} page={page} onChange={(_, p) => setPage(p)} size="small" />
            </Box>
          )}
        </Grid>

        {/* Right: Detail + Action */}
        <Grid size={{ xs: 12, md: 7 }}>
          {!selected ? (
            <Card variant="outlined" sx={{ borderRadius: 2, p: 4, textAlign: 'center', color: '#888' }}>
              请在左侧选择一个举报进行处理
            </Card>
          ) : (
            <Card variant="outlined" sx={{ borderRadius: 2 }}>
              <CardContent sx={{ p: 3 }}>
                {/* Header */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <FlagIcon sx={{ color: typeColors[selected.complainant_type] || '#888' }} />
                  <Typography variant="subtitle1" fontWeight={600}>
                    {(typeLabels[selected.complainant_type] || selected.complainant_type)} #{selected.id}
                  </Typography>
                </Box>

                {/* Detail fields */}
                <Box sx={{ display: 'grid', gap: 2, mb: 2 }}>
                  <Box>
                    <Typography variant="caption" color="text.secondary">被举报对象</Typography>
                    <Typography variant="body2">{selected.target_summary || `ID: ${selected.complainant_id}`}</Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary">举报原因</Typography>
                    <Typography variant="body2">{selected.reason_code}</Typography>
                  </Box>
                  {selected.description && (
                    <Box>
                      <Typography variant="caption" color="text.secondary">举报描述</Typography>
                      <Box sx={{ p: 1.5, bgcolor: '#f9f9f9', borderRadius: 1, mt: 0.5 }}>
                        <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>{selected.description}</Typography>
                      </Box>
                    </Box>
                  )}
                </Box>

                <Divider sx={{ my: 2 }} />

                {/* Action form */}
                <FormControl>
                  <FormLabel sx={{ fontWeight: 600, fontSize: 14, mb: 1 }}>处理动作</FormLabel>
                  <RadioGroup value={action} onChange={(e) => setAction(e.target.value)}>
                    {actionOptions.map((opt) => (
                      <FormControlLabel
                        key={opt.value}
                        value={opt.value}
                        control={<Radio size="small" />}
                        label={
                          <Box>
                            <Typography variant="body2" fontWeight={500}>{opt.label}</Typography>
                            <Typography variant="caption" color="text.secondary">{opt.description}</Typography>
                          </Box>
                        }
                        sx={{ mb: 0.5 }}
                      />
                    ))}
                  </RadioGroup>
                </FormControl>

                <MuiTextField
                  label="处理说明（可选）"
                  value={resultDesc}
                  onChange={(e) => setResultDesc(e.target.value)}
                  fullWidth
                  multiline
                  rows={2}
                  size="small"
                  sx={{ mt: 2, mb: 2 }}
                />

                <Button
                  variant="contained"
                  onClick={handleSubmit}
                  disabled={submitting}
                  fullWidth
                  sx={{
                    borderRadius: 2,
                    textTransform: 'none',
                    fontWeight: 600,
                    backgroundColor: '#FF7E3A',
                    '&:hover': { backgroundColor: '#e56e30' },
                    '&.Mui-disabled': { backgroundColor: '#ccc' },
                  }}
                >
                  {submitting ? '处理中...' : '确认处理'}
                </Button>
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
