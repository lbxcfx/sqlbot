# Excel文件上传后表结构解析问题解决方案

## 问题诊断结果

通过命令测试，我们发现了以下情况：

### ✅ 正常工作的部分
1. **Excel文件上传成功** - 表 `Sheet1_fc32194e01` 已正确创建
2. **表结构完整** - 包含"手术类型"字段，类型为text
3. **数据导入成功** - 包含15种不同的手术类型，共50条记录
4. **系统元数据同步** - core_table和core_field表记录正确
5. **SQL查询正常** - 可以直接查询手术类型分布

### ❌ 问题所在
问题不在数据库层面，而在于：
1. **前端数据源配置** - 可能数据源ID不匹配
2. **用户权限** - 可能用户没有访问该数据源的权限
3. **SQL生成逻辑** - 可能模板没有正确处理中文字段名

## 解决方案命令

### 1. 检查数据源配置
```bash
# 查看所有Excel数据源
docker exec -it sqlbot psql -U root -d sqlbot -c "SELECT id, name, type FROM core_datasource WHERE type = 'excel';"

# 查看表与数据源的关联
docker exec -it sqlbot psql -U root -d sqlbot -c "
SELECT t.id, t.table_name, t.checked, ds.name as ds_name, ds.id as ds_id
FROM core_table t
JOIN core_datasource ds ON t.ds_id = ds.id
WHERE ds.type = 'excel'
ORDER BY t.table_name;"
```

### 2. 验证表结构
```bash
# 检查表结构
docker exec -it sqlbot psql -U root -d sqlbot -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'Sheet1_fc32194e01' ORDER BY ordinal_position;"

# 检查字段记录
docker exec -it sqlbot psql -U root -d sqlbot -c "
SELECT f.field_name, f.field_type, f.checked, f.field_comment
FROM core_field f
JOIN core_table t ON f.table_id = t.id
WHERE t.table_name = 'Sheet1_fc32194e01'
ORDER BY f.field_index;"
```

### 3. 测试SQL查询
```bash
# 测试手术类型分布查询
docker exec -it sqlbot psql -U root -d sqlbot -c "
SELECT \"手术类型\", COUNT(*) as count 
FROM \"Sheet1_fc32194e01\" 
GROUP BY \"手术类型\" 
ORDER BY count DESC;"
```

### 4. 检查用户权限
```bash
# 检查用户表
docker exec -it sqlbot psql -U root -d sqlbot -c "SELECT id, name, is_admin FROM sys_user;"

# 检查数据源权限
docker exec -it sqlbot psql -U root -d sqlbot -c "SELECT * FROM ds_permission;"
```

### 5. 重启服务（如果需要）
```bash
# 重启SQLBot容器
docker-compose restart sqlbot

# 查看服务日志
docker logs sqlbot --tail 50
```

## 前端配置建议

1. **确认数据源ID** - 使用数据源ID 2（患者的手术数据）
2. **检查表名** - 确保使用正确的表名 `Sheet1_fc32194e01`
3. **验证字段名** - 确保字段名包含中文字符"手术类型"
4. **测试查询** - 先测试简单的查询，再测试复杂的分组查询

## 可能的根本原因

1. **数据源选择错误** - 前端可能选择了错误的数据源ID
2. **表名大小写** - 表名是 `Sheet1_fc32194e01`（大写S）
3. **字段名编码** - 中文字段名可能需要特殊处理
4. **权限问题** - 用户可能没有访问该数据源的权限

## 验证步骤

1. 在管理后台确认数据源配置
2. 检查用户权限设置
3. 测试简单的SQL查询
4. 逐步测试复杂的查询功能
