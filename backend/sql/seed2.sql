-- =====================================================
-- seed2.sql — 举报与勘误原因字典数据
-- 用法：mysql -u root -p foodiehub_db < sql/seed2.sql
-- =====================================================

-- 举报原因字典类型
INSERT INTO dict_types (name, target_table, sort_order) VALUES
('举报原因', 'feedbacks', 5),
('勘误原因', 'feedbacks', 6)
ON DUPLICATE KEY UPDATE name = name;

-- 举报原因数据（dict_type_id=4，序号接在就餐方式之后）
INSERT INTO dict_data (dict_type_id, name, sort_order) VALUES
(4, '虚假信息', 1),
(4, '违规内容', 2),
(4, '恶意刷评', 3),
(4, '其他', 4)
ON DUPLICATE KEY UPDATE name = name;

-- 勘误原因数据（dict_type_id=5）
INSERT INTO dict_data (dict_type_id, name, sort_order) VALUES
(5, '名称错误', 1),
(5, '品类/区域有误', 2),
(5, '重复店铺', 3),
(5, '其他', 4)
ON DUPLICATE KEY UPDATE name = name;
