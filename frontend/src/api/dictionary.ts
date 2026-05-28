// 字典数据接口
// 字典数据（品类、区域等）当前通过 seed SQL 预置在数据库，
// 后端尚未开放独立的字典 HTTP 接口。
//
// 前端需要字典选项时，可：
// 1. 从店铺搜索接口的 dict_data 字段间接获取
// 2. 等待后端提供 GET /dict/types 和 GET /dict/data 接口

export interface DictItem {
  id: number;
  name: string;
}

export interface DictType {
  id: number;
  name: string;
  target_table: string;
}
