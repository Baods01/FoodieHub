import {
  List,
  Datagrid,
  TextField,
  DateField,
  TextInput,
  SelectInput,
  Pagination,
  FunctionField,
} from 'react-admin';

const logFilters = [
  <TextInput source="operator_id" label="操作人ID" alwaysOn sx={{ '& .MuiInputBase-root': { backgroundColor: '#fff' } }} />,
  <SelectInput source="action" label="操作类型" choices={[
    { id: 'ban_user', name: '封禁用户' },
    { id: 'unban_user', name: '解封用户' },
    { id: 'ban_shop', name: '封禁店铺' },
    { id: 'unban_shop', name: '解封店铺' },
    { id: 'merge_shops', name: '合并店铺' },
    { id: 'approve_feedback', name: '通过反馈' },
    { id: 'reject_feedback', name: '驳回反馈' },
    { id: 'publish_announcement', name: '发布公告' },
    { id: 'create_shop', name: '创建店铺' },
    { id: 'update_shop', name: '更新店铺' },
    { id: 'delete_shop', name: '删除店铺' },
    { id: 'create_comment', name: '发表评论' },
    { id: 'update_comment', name: '更新评论' },
    { id: 'delete_comment', name: '删除评论' },
    { id: 'create_reply', name: '回复评论' },
    { id: 'delete_reply', name: '删除回复' },
    { id: 'create_question', name: '提问' },
    { id: 'delete_question', name: '删除提问' },
    { id: 'create_answer', name: '回答问题' },
    { id: 'delete_answer', name: '删除回答' },
    { id: 'toggle_like', name: '点赞/取消赞' },
    { id: 'toggle_favorite', name: '收藏/取消收藏' },
    { id: 'rate_shop', name: '评分' },
    { id: 'update_profile', name: '更新资料' },
    { id: 'create_feedback', name: '提交反馈' },
    { id: 'delete_history', name: '删除浏览记录' },
    { id: 'clear_history', name: '清空浏览记录' },
    { id: 'view_shop', name: '浏览店铺' },
  ]} />,
  <SelectInput source="target_type" label="对象类型" choices={[
    { id: 'user', name: '用户' },
    { id: 'shop', name: '店铺' },
    { id: 'comment', name: '评论' },
    { id: 'reply', name: '回复' },
    { id: 'question', name: '问题' },
    { id: 'answer', name: '回答' },
    { id: 'feedback', name: '反馈' },
    { id: 'announcement', name: '公告' },
    { id: 'history', name: '浏览记录' },
  ]} />,
];

export default function LogList() {
  return (
    <List
      resource="logs"
      perPage={20}
      filters={logFilters}
      pagination={<Pagination />}
    >
      <Datagrid bulkActionButtons={false}>
        <TextField source="id" label="ID" />
        <TextField source="operator_name" label="操作人" />
        <TextField source="action" label="操作类型" />
        <TextField source="target_type" label="对象类型" />
        <FunctionField
          label="对象 ID"
          render={(record: any) => record.target_id ?? '-'}
        />
        <DateField source="created_at" label="操作时间" showTime />
      </Datagrid>
    </List>
  );
}
