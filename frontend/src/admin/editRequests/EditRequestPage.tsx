import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField as MuiTextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Skeleton,
  Snackbar,
  Pagination,
} from '@mui/material';
import {
  CheckCircle as ApproveIcon,
  Cancel as RejectIcon,
  EditNote as EditIcon,
  ContentCopy as DuplicateIcon,
} from '@mui/icons-material';
import apiClient from '../../api/client';

interface EditRequest {
  id: number;
  shop_id: number;
  shop_name?: string;
  user_id: number;
  user_name?: string;
  request_type: 'edit' | 'duplicate';
  reason?: string;
  status: string;
  created_at: string;
  // edit fields
  name?: string;
  area_dict_data_id?: number;
  category_dict_data_id?: number;
  // duplicate fields
  candidate_shop_ids?: number[];
}

export default function EditRequestPage() {
  const [requests, setRequests] = useState<EditRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<EditRequest | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogType, setDialogType] = useState<'approve' | 'approve-correction' | 'reject' | null>(null);
  const [remark, setRemark] = useState('');
  const [rejectReason, setRejectReason] = useState('');
  const [mainShopId, setMainShopId] = useState<number | undefined>(undefined);
  const [submitting, setSubmitting] = useState(false);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false, message: '', severity: 'success',
  });
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);

  const loadRequests = () => {
    setLoading(true);
    apiClient.get('/shops/edit-requests', { params: { page, page_size: pageSize } })
      .then((res) => {
        const data = (res.data as any)?.data ?? res.data;
        const items = Array.isArray(data) ? data : data?.items ?? data?.data ?? [];
        setRequests(items);
      })
      .catch(() => { /* backend not ready */ })
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadRequests(); }, [page]);

  const handleOpenDialog = (req: EditRequest, type: 'approve' | 'approve-correction' | 'reject') => {
    setSelected(req);
    setDialogType(type);
    setRemark('');
    setRejectReason('');
    setMainShopId(undefined);
    if (type === 'approve' && req.candidate_shop_ids?.length) {
      setMainShopId(req.candidate_shop_ids[0]);
    }
    setDialogOpen(true);
  };

  const handleSubmit = async () => {
    if (!selected || !dialogType) return;
    setSubmitting(true);
    try {
      const endpoint = `/shops/edit-requests/${selected.id}/${dialogType}`;
      if (dialogType === 'reject') {
        await apiClient.post(endpoint, { reason: rejectReason.trim() || '未填写原因' });
      } else if (dialogType === 'approve') {
        await apiClient.post(endpoint, { remark: remark.trim() || undefined, main_shop_id: mainShopId });
      } else {
        await apiClient.post(endpoint, { remark: remark.trim() || undefined });
      }
      setSnackbar({ open: true, message: '审核操作成功', severity: 'success' });
      setDialogOpen(false);
      loadRequests();
    } catch {
      setSnackbar({ open: true, message: '操作失败，请重试', severity: 'error' });
    } finally {
      setSubmitting(false);
    }
  };

  const isDuplicate = (req: EditRequest) => req.request_type === 'duplicate' || req.candidate_shop_ids?.length;
  const getChangeSummary = (req: EditRequest) => {
    const changes: string[] = [];
    if (req.name) changes.push(`名称 → ${req.name}`);
    if (req.area_dict_data_id) changes.push(`区域ID → ${req.area_dict_data_id}`);
    if (req.category_dict_data_id) changes.push(`品类ID → ${req.category_dict_data_id}`);
    return changes.length ? changes.join('; ') : '-';
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>店铺勘误审核</Typography>

      <Card variant="outlined" sx={{ borderRadius: 2 }}>
        {loading ? (
          <Box sx={{ p: 2 }}>
            {[1, 2, 3].map((i) => <Skeleton key={i} variant="rounded" height={52} sx={{ mb: 1 }} />)}
          </Box>
        ) : requests.length === 0 ? (
          <Box sx={{ p: 4, textAlign: 'center', color: '#888' }}>暂无待审核的请求</Box>
        ) : (
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>类型</TableCell>
                  <TableCell>店铺</TableCell>
                  <TableCell>提交用户</TableCell>
                  <TableCell>变更内容</TableCell>
                  <TableCell>提交时间</TableCell>
                  <TableCell sx={{ width: 200 }}>操作</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {requests.map((req) => (
                  <TableRow key={req.id} hover>
                    <TableCell>{req.id}</TableCell>
                    <TableCell>
                      <Chip
                        icon={isDuplicate(req) ? <DuplicateIcon fontSize="small" /> : <EditIcon fontSize="small" />}
                        label={isDuplicate(req) ? '重复投诉' : '勘误'}
                        size="small"
                        color={isDuplicate(req) ? 'warning' : 'info'}
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>{req.shop_name || `#${req.shop_id}`}</TableCell>
                    <TableCell>{req.user_name || `#${req.user_id}`}</TableCell>
                    <TableCell sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {isDuplicate(req)
                        ? `候选店铺: ${req.candidate_shop_ids?.join(', ') || '-'}`
                        : getChangeSummary(req)}
                    </TableCell>
                    <TableCell>{new Date(req.created_at).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <Button
                          size="small"
                          variant="outlined"
                          color="success"
                          onClick={() => handleOpenDialog(
                            req,
                            isDuplicate(req) ? 'approve' : 'approve-correction'
                          )}
                          sx={{ borderRadius: 2, textTransform: 'none', fontSize: 11, minWidth: 40 }}
                          title="通过"
                        >
                          <ApproveIcon fontSize="small" />
                        </Button>
                        <Button
                          size="small"
                          variant="outlined"
                          color="error"
                          onClick={() => handleOpenDialog(req, 'reject')}
                          sx={{ borderRadius: 2, textTransform: 'none', fontSize: 11, minWidth: 40 }}
                          title="拒绝"
                        >
                          <RejectIcon fontSize="small" />
                        </Button>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Card>

      {requests.length > 0 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
          <Pagination count={Math.ceil(requests.length / pageSize) + 1} page={page} onChange={(_, p) => setPage(p)} size="small" />
        </Box>
      )}

      {/* Dialog: Approve (duplicate merge) */}
      <Dialog open={dialogOpen && dialogType === 'approve'} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>审核重复店铺投诉</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            被投诉店铺：{selected?.shop_name || `#${selected?.shop_id}`}
          </Typography>
          {selected?.candidate_shop_ids && selected.candidate_shop_ids.length > 0 && (
            <FormControl fullWidth size="small" sx={{ mb: 2 }}>
              <InputLabel>选择合并到的主店铺</InputLabel>
              <Select
                value={mainShopId ?? ''}
                label="选择合并到的主店铺"
                onChange={(e) => setMainShopId(Number(e.target.value))}
              >
                {selected.candidate_shop_ids.map((id: number) => (
                  <MenuItem key={id} value={id}>店铺 ID: {id}</MenuItem>
                ))}
              </Select>
            </FormControl>
          )}
          <MuiTextField
            label="审核备注（可选）"
            value={remark}
            onChange={(e) => setRemark(e.target.value)}
            fullWidth
            multiline
            rows={3}
            size="small"
          />
        </DialogContent>
        <DialogActions sx={{ p: 2, pt: 0 }}>
          <Button onClick={() => setDialogOpen(false)} sx={{ borderRadius: 2, color: '#666' }}>取消</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={submitting}
            sx={{ borderRadius: 2, textTransform: 'none', backgroundColor: '#4caf50', color: '#fff', '&:hover': { backgroundColor: '#388e3c' } }}
          >
            {submitting ? '处理中...' : '确认合并'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog: Approve Correction */}
      <Dialog open={dialogOpen && dialogType === 'approve-correction'} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>审核店铺勘误</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            店铺：{selected?.shop_name || `#${selected?.shop_id}`}
          </Typography>
          {selected && (
            <Box sx={{ bgcolor: '#f9f9f9', p: 1.5, borderRadius: 1, mb: 2 }}>
              <Typography variant="caption" color="text.secondary">修改项：</Typography>
              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>{getChangeSummary(selected)}</Typography>
              {selected.reason && (
                <>
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>用户修改原因：</Typography>
                  <Typography variant="body2">{selected.reason}</Typography>
                </>
              )}
            </Box>
          )}
          <MuiTextField
            label="审核备注（可选）"
            value={remark}
            onChange={(e) => setRemark(e.target.value)}
            fullWidth
            multiline
            rows={3}
            size="small"
          />
        </DialogContent>
        <DialogActions sx={{ p: 2, pt: 0 }}>
          <Button onClick={() => setDialogOpen(false)} sx={{ borderRadius: 2, color: '#666' }}>取消</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={submitting}
            sx={{ borderRadius: 2, textTransform: 'none', backgroundColor: '#4caf50', color: '#fff', '&:hover': { backgroundColor: '#388e3c' } }}
          >
            {submitting ? '处理中...' : '确认通过'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog: Reject */}
      <Dialog open={dialogOpen && dialogType === 'reject'} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>拒绝请求</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            店铺：{selected?.shop_name || `#${selected?.shop_id}`}
          </Typography>
          <MuiTextField
            label="拒绝原因 *"
            value={rejectReason}
            onChange={(e) => setRejectReason(e.target.value)}
            fullWidth
            multiline
            rows={3}
            size="small"
          />
        </DialogContent>
        <DialogActions sx={{ p: 2, pt: 0 }}>
          <Button onClick={() => setDialogOpen(false)} sx={{ borderRadius: 2, color: '#666' }}>取消</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={submitting || !rejectReason.trim()}
            sx={{ borderRadius: 2, textTransform: 'none', backgroundColor: '#f44336', color: '#fff', '&:hover': { backgroundColor: '#d32f2f' } }}
          >
            {submitting ? '处理中...' : '确认拒绝'}
          </Button>
        </DialogActions>
      </Dialog>

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
