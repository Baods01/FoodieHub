import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Skeleton,
  Alert,
  Divider,
} from '@mui/material';
import {
  Storefront as StoreIcon,
  People as PeopleIcon,
  Comment as CommentIcon,
  TrendingUp as TrendingUpIcon,
  Flag as FlagIcon,
  EditNote as EditIcon,
} from '@mui/icons-material';
import apiClient from '../../api/client';

// ============ 类型定义 ============

interface DailyStatsItem {
  date: string;
  new_shops: number;
  new_users: number;
  new_interactions: number;
}

interface OverviewData {
  total_shops: number;
  total_users: number;
  total_comments: number;
  total_questions: number;
  pending_complaints: number;
  pending_edits: number;
  avg_rating: number | null;
}

interface PendingCounts {
  pending_complaints: number;
  pending_edit_requests: number;
}

// ============ 组件 ============

function StatCard({
  title,
  value,
  subtitle,
  icon,
  color,
}: {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  color: string;
}) {
  return (
    <Card variant="outlined" sx={{ borderRadius: 2, height: '100%' }}>
      <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box sx={{ flex: 1 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5, fontWeight: 500 }}>
              {title}
            </Typography>
            <Typography variant="h4" fontWeight={700} color="text.primary">
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                {subtitle}
              </Typography>
            )}
          </Box>
          <Box
            sx={{
              width: 48,
              height: 48,
              borderRadius: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: `${color}15`,
              color: color,
              flexShrink: 0,
            }}
          >
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}

export default function Dashboard() {
  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [dailyTrends, setDailyTrends] = useState<DailyStatsItem[]>([]);
  const [pendingCounts, setPendingCounts] = useState<PendingCounts | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    setLoading(true);
    setError(false);
    Promise.all([
      apiClient.get('/admin/overview').catch(() => null),
      apiClient.get('/admin/daily-trends', { params: { days: 7 } }).catch(() => null),
      apiClient.get('/admin/pending-counts').catch(() => null),
    ])
      .then(([overviewRes, trendsRes, pendingRes]) => {
        const ov: any = overviewRes ? ((overviewRes.data as any)?.data ?? overviewRes.data) : null;
        const tr: any = trendsRes ? ((trendsRes.data as any)?.data ?? trendsRes.data) : null;
        const pc: any = pendingRes ? ((pendingRes.data as any)?.data ?? pendingRes.data) : null;
        setOverview(ov);
        setDailyTrends(Array.isArray(tr) ? tr : []);
        setPendingCounts(pc);
      })
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h5" fontWeight={700} sx={{ mb: 3 }}>仪表盘</Typography>
        <Grid container spacing={2}>
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Grid key={i} size={{ xs: 12, sm: 6, md: 4 }}>
              <Skeleton variant="rounded" height={110} />
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" fontWeight={700} sx={{ mb: 0.5 }}>仪表盘</Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        平台数据概览
      </Typography>

      {error && (
        <Alert severity="info" sx={{ mb: 2, borderRadius: 2 }}>
          后端接口暂未连接，以下显示模拟数据。
        </Alert>
      )}

      {/* ===== 累计数据 ===== */}
      <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1.5 }}>累计数据</Typography>
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard title="总店铺数" value={overview?.total_shops ?? '-'} icon={<StoreIcon />} color="#FF7E3A" />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard title="总用户数" value={overview?.total_users ?? '-'} icon={<PeopleIcon />} color="#3B82F6" />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard title="总互动数" value={overview?.total_comments ?? '-'} icon={<CommentIcon />} color="#10B981" />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard title="平均评分" value={overview?.avg_rating ?? '-'} subtitle="有评分的店铺" icon={<TrendingUpIcon />} color="#F59E0B" />
        </Grid>
      </Grid>

      <Divider sx={{ my: 2 }} />

      {/* ===== 待处理工单 + 每日趋势 ===== */}
      <Grid container spacing={3}>
        {/* 待处理工单 */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1.5 }}>待处理工单</Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
            <Card variant="outlined" sx={{ borderRadius: 2, borderLeft: '4px solid #ff9800' }}>
              <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                  <FlagIcon sx={{ color: '#ff9800' }} />
                  <Box>
                    <Typography variant="caption" color="text.secondary">待处理举报</Typography>
                    <Typography variant="h5" fontWeight={700} color="#ff9800">
                      {overview?.pending_complaints ?? pendingCounts?.pending_complaints ?? '-'}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
            <Card variant="outlined" sx={{ borderRadius: 2, borderLeft: '4px solid #3B82F6' }}>
              <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                  <EditIcon sx={{ color: '#3B82F6' }} />
                  <Box>
                    <Typography variant="caption" color="text.secondary">待处理勘误</Typography>
                    <Typography variant="h5" fontWeight={700} color="#3B82F6">
                      {overview?.pending_edits ?? pendingCounts?.pending_edit_requests ?? '-'}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Box>
        </Grid>

        {/* 每日趋势表 */}
        <Grid size={{ xs: 12, md: 8 }}>
          <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1.5 }}>近 7 日每日新增趋势</Typography>
          <Card variant="outlined" sx={{ borderRadius: 2 }}>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow sx={{ backgroundColor: '#fafafa' }}>
                    <TableCell sx={{ fontWeight: 600 }}>日期</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 600 }}>新增店铺</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 600 }}>新增用户</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 600 }}>新增互动</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {dailyTrends.length > 0 ? (
                    [...dailyTrends].reverse().map((row) => (
                      <TableRow key={row.date} hover>
                        <TableCell sx={{ color: 'text.secondary' }}>{row.date}</TableCell>
                        <TableCell align="right">{row.new_shops}</TableCell>
                        <TableCell align="right">{row.new_users}</TableCell>
                        <TableCell align="right">{row.new_interactions}</TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={4} align="center" sx={{ py: 3, color: '#888' }}>暂无数据</TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
