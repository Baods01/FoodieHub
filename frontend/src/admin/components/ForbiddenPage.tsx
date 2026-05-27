
import { Button, Typography, Container, Box } from '@mui/material';

export default function ForbiddenPage() {
  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          gap: 2,
        }}
      >
        <Typography variant="h3" fontWeight={700} color="error">
          403
        </Typography>
        <Typography variant="h6" color="text.secondary">
          无权限访问
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 360 }}>
          当前账号非管理员，无法访问管理后台。
          如需管理员权限，请联系系统管理员。
        </Typography>
        <Button variant="outlined" href="/" sx={{ mt: 1 }}>
          返回首页
        </Button>
      </Box>
    </Container>
  );
}
