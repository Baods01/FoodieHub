
import {
  List,
  Datagrid,
  TextField,
  DateField,
  FunctionField,
  TextInput,
  SelectInput,
  Pagination,
} from 'react-admin';
import {
  Chip,
} from '@mui/material';


const userFilters = [
  <TextInput source="keyword" label="搜索" alwaysOn sx={{ '& .MuiInputBase-root': { backgroundColor: '#fff' } }} />,
  <SelectInput source="is_banned" label="状态" choices={[
    { id: 'false', name: '正常' },
    { id: 'true', name: '已封禁' },
  ]} />,
];

function RoleChip({ record }: { record: any }) {
  if (record?.role === 1) {
    return <Chip label="管理员" size="small" color="primary" variant="outlined" />;
  }
  return <Chip label="普通用户" size="small" variant="outlined" />;
}

function StatusChip({ record }: { record: any }) {
  if (record?.is_banned) {
    return <Chip label="已封禁" size="small" color="error" />;
  }
  return <Chip label="正常" size="small" color="success" />;
}

function MaskedPhone({ record }: { record: any }) {
  const phone = record?.phone ?? '';
  if (!phone || phone.length < 7) return <span>{phone}</span>;
  return <span>{phone.slice(0, 3)}****{phone.slice(-4)}</span>;
}

export default function UserList() {
  return (
    <List
      resource="users"
      perPage={20}
      filters={userFilters}
      pagination={<Pagination />}
      sx={{ '& .RaList-content': { mt: 0 } }}
    >
      <Datagrid
        bulkActionButtons={false}
        rowClick="show"
        sx={{
          '& .column-role': { width: 100 },
          '& .column-is_active': { width: 90 },
        }}
      >
        <TextField source="id" label="ID" />
        <TextField source="username" label="用户名" />
        <TextField source="email" label="邮箱" />
        <FunctionField label="手机号" render={(record: any) => <MaskedPhone record={record} />} />
        <FunctionField label="角色" render={(record: any) => <RoleChip record={record} />} />
        <FunctionField label="状态" render={(record: any) => <StatusChip record={record} />} />
        <DateField source="created_at" label="注册时间" showTime={false} />
      </Datagrid>
    </List>
  );
}
