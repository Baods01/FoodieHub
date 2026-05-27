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
} from '@mui/icons-material';
import apiClient from '../../api/client';

// ============ 类型定义 ============

interface DailyStatsItem {
  date: string;
  new_shops: number;
  new_users: number;
  new_comments: number;
}

interface OverviewStats {
  total_shops: number;
  total_users: number;
  total_comments: number;
  active_shops_7d: number;
  active_users_7d: number;
  active_comments_7d: number;
  daily_stats: DailyStatsItem[];
}

interface ComplaintStats {
  pending: number;
  approved: number;
  rejected: number;
  total: number;
}

// ============ Mock 数据 ============

const mockOverview: OverviewStats = {
  total_shops: 236,
  total_users: 892,
  total_comments: 1230,
  active_shops_7d: 12,
  active_users_7d: 45,
  active_comments_7d: 128,
  daily_stats: [
    { date: '2026-05-20', new_shops: 2, new_users: 8, new_comments: 20 },
    { date: '2026-05-21', new_shops: 1, new_users: 6, new_comments: 15 },
    { date: '2026-05-22', new_shops: 3, new_users: 7, new_comments: 22 },
    { date: '2026-05-23', new_shops: 2, new_users: 5, new_comments: 18 },
    { date: '2026-05-24', new_shops: 1, new_users: 9, new_comments: 25 },
    { date: '2026-05-25', new_shops: 2, new_users: 6, new_comments: 16 },
    { date: '2026-05-26', new_shops: 1, new_users: 4, new_comments: 12 },
  ],
};

const mockComplaintStats: ComplaintStats = {
  pending: 5,
  approved: 42,
  rejected: 8,
  total: 55,
};

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
  const [overview, setOverview] = useState<OverviewStats | null>(null);
  const [complaintStats, setComplaintStats] = useState<ComplaintStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    setLoading(true);
    setError(false);
    Promise.all([
      apiClient.get('/admin/stats/overview', { params: { days: 7 } }).catch(() => null),
      apiClient.get('/complaints/admin/stats').catch(() => null),
    ])
      .then(([overviewRes, compRes]) => {
        const ovData = overviewRes ? ((overviewRes.data as any)?.data ?? overviewRes.data) : null;
        const csData = compRes ? ((compRes.data as any)?.data ?? compRes.data) : null;
        setOverview(ovData || mockOverview);
        setComplaintStats(csData || mockComplaintStats);
      })
      .catch(() => {
        setOverview(mockOverview);
        setComplaintStats(mockComplaintStats);
        setError(true);
      })
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

  const ov = overview!;
  const cs = complaintStats!;

  return (
    <Box sx={{ p: 3 }}>
      {/* 页面标题 */}
      <Typography variant="h5" fontWeight={700} sx={{ mb: 0.5 }}>仪表盘</Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        平台数据概览
      </Typography>

      {error && (
        <Alert severity="info" sx={{ mb: 2, borderRadius: 2 }}>
          后端接口暂未连接，以下显示模拟数据。
        </Alert>
      )}

      {/* ===== 第一行：总数统计 ===== */}
      <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1.5 }}>
        累计数据
      </Typography>
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <StatCard
            title="总店铺数"
            value={ov.total_shops}
            subtitle="全平台累计"
            icon={<StoreIcon />}
            color="#FF7E3A"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <StatCard
            title="总用户数"
            value={ov.total_users}
            subtitle="全平台累计"
            icon={<PeopleIcon />}
            color="#3B82F6"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <StatCard
            title="总评论数"
            value={ov.total_comments}
            subtitle="全平台累计"
            icon={<CommentIcon />}
            color="#10B981"
          />
        </Grid>
      </Grid>

      {/* ===== 第二行：近7日活跃 ===== */}
      <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1.5 }}>
        近 7 日新增
      </Typography>
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <StatCard
            title="新增店铺"
            value={ov.active_shops_7d}
            subtitle={`较上周期`}
            icon={<TrendingUpIcon />}
            color="#FF7E3A"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <StatCard
            title="新增用户"
            value={ov.active_users_7d}
            subtitle={`较上周期`}
            icon={<TrendingUpIcon />}
            color="#3B82F6"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <StatCard
            title="新增评论"
            value={ov.active_comments_7d}
            subtitle={`较上周期`}
            icon={<TrendingUpIcon />}
            color="#10B981"
          />
        </Grid>
      </Grid>

      <Divider sx={{ my: 2 }} />

      {/* ===== 第三行：举报统计 + 每日趋势表 ===== */}
      <Grid container spacing={3}>
        {/* 举报统计 */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1.5 }}>
            举报统计
          </Typography>
          <Grid container spacing={1.5}>
            <Grid size={6}>
              <Card variant="outlined" sx={{ borderRadius: 2, borderColor: '#ff9800', borderLeft: '4px solid #ff9800' }}>
                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                  <Typography variant="caption" color="text.secondary">待处理</Typography>
                  <Typography variant="h5" fontWeight={700} color="#ff9800">{cs.pending}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={6}>
              <Card variant="outlined" sx={{ borderRadius: 2, borderColor: '#4caf50', borderLeft: '4px solid #4caf50' }}>
                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                  <Typography variant="caption" color="text.secondary">已处理</Typography>
                  <Typography variant="h5" fontWeight={700} color="#4caf50">{cs.approved}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={6}>
              <Card variant="outlined" sx={{ borderRadius: 2, borderColor: '#f44336', borderLeft: '4px solid #f44336' }}>
                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                  <Typography variant="caption" color="text.secondary">已驳回</Typography>
                  <Typography variant="h5" fontWeight={700} color="#f44336">{cs.rejected}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={6}>
              <Card variant="outlined" sx={{ borderRadius: 2, borderColor: '#9e9e9e', borderLeft: '4px solid #9e9e9e' }}>
                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                  <Typography variant="caption" color="text.secondary">总计</Typography>
                  <Typography variant="h5" fontWeight={700} color="text.primary">{cs.total}</Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>

        {/* 每日趋势表 */}
        <Grid size={{ xs: 12, md: 8 }}>
          <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1.5 }}>
            近 7 日每日新增趋势
          </Typography>
          <Card variant="outlined" sx={{ borderRadius: 2 }}>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow sx={{ backgroundColor: '#fafafa' }}>
                    <TableCell sx={{ fontWeight: 600 }}>日期</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 600 }}>新增店铺</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 600 }}>新增用户</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 600 }}>新增评论</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {ov.daily_stats?.length > 0 ? (
                    [...ov.daily_stats].reverse().map((row) => (
                      <TableRow key={row.date} hover>
                        <TableCell sx={{ color: 'text.secondary' }}>{row.date}</TableCell>
                        <TableCell align="right">{row.new_shops}</TableCell>
                        <TableCell align="right">{row.new_users}</TableCell>
                        <TableCell align="right">{row.new_comments}</TableCell>
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
