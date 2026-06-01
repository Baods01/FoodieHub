-- =====================================================
-- 食探社 基础数据种子
-- 用法：mysql -u root -p foodiehub_db < sql/seed.sql
-- =====================================================

-- 管理员账号
-- 用户名：admin  密码：admin123
INSERT INTO users (username, password, phone, email, role, is_active)
VALUES ('admin', '$2b$12$fWYsoNZSinEj49wY1xYTCuig16518HYLa8OY5plEpu2ggQ9nqTuzK',
        '13800000000', 'admin@foodiehub.com', 1, 1)
ON DUPLICATE KEY UPDATE username = username;

-- 字典类型
INSERT INTO dict_types (name, target_table, sort_order) VALUES
('品类', 'shops', 1),
('区域', 'shops', 2),
('就餐方式', 'shops', 3)
ON DUPLICATE KEY UPDATE name = name;

-- 品类数据
INSERT INTO dict_data (dict_type_id, name, sort_order) VALUES
(1, '地方菜', 1),
(1, '火锅', 2),
(1, '烧烤/烤肉', 3),
(1, '异域料理', 4),
(1, '小吃快餐', 5),
(1, '特色菜', 6),
(1, '饮品', 7),
(1, '甜点/面包', 8)
ON DUPLICATE KEY UPDATE name = name;

-- 区域数据
INSERT INTO dict_data (dict_type_id, name, sort_order) VALUES
(2, '华山区', 1),
(2, '泰山区', 2),
(2, '启林区', 3),
(2, '六一区', 4),
(2, '校外', 5),
(2, '主校区', 6)
ON DUPLICATE KEY UPDATE name = name;

-- 就餐方式数据
INSERT INTO dict_data (dict_type_id, name, sort_order) VALUES
(3, '堂食', 1),
(3, '自取', 2),
(3, '外卖', 3)
ON DUPLICATE KEY UPDATE name = name;
