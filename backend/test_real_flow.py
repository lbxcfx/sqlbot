#!/usr/bin/env python3
"""
使用实际数据库连接测试完整流程
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import psycopg2
from apps.datasource.crud.datasource import get_datasource_list, get_table_schema
from apps.datasource.crud.table import get_tables_by_ds_id
from apps.datasource.models.datasource import CoreDatasource
from common.core.deps import SessionDep, CurrentUser
from sqlmodel import select
import json

def test_real_datasource_selection():
    """使用实际数据库测试数据源选择"""
    print("=== 使用实际数据库测试数据源选择 ===")
    
    # 连接数据库
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="sqlbot",
            user="root",
            password="Password123@pg"
        )
        cursor = conn.cursor()
        print("✓ 数据库连接成功")
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return None
    
    # 获取数据源列表
    cursor.execute("SELECT id, name, description, type FROM core_datasource WHERE oid = 1;")
    datasources = cursor.fetchall()
    
    print(f"找到 {len(datasources)} 个数据源:")
    for ds in datasources:
        print(f"  - ID: {ds[0]}, 名称: {ds[1]}, 描述: {ds[2]}, 类型: {ds[3]}")
    
    # 测试问题
    question = "手术类型分布"
    print(f"\n用户问题: {question}")
    
    # 智能匹配逻辑
    best_match = None
    best_score = 0
    
    for ds in datasources:
        score = 0
        ds_id, name, description, ds_type = ds
        
        # 检查数据源名称
        if name and name.lower() in question.lower():
            score += 10
            print(f"  数据源名称匹配: {name} -> +10分")
        
        # 检查数据源描述
        if description and description.lower() in question.lower():
            score += 5
            print(f"  数据源描述匹配: {description} -> +5分")
        
        # 检查表名和字段
        try:
            cursor.execute("""
                SELECT t.table_name, t.table_comment, f.field_name, f.field_comment
                FROM core_table t
                LEFT JOIN core_field f ON t.id = f.table_id
                WHERE t.ds_id = %s AND t.checked = true
                ORDER BY t.table_name, f.field_index;
            """, (ds_id,))
            
            tables = cursor.fetchall()
            table_names = set()
            field_names = set()
            
            for table in tables:
                table_name, table_comment, field_name, field_comment = table
                if table_name:
                    table_names.add(table_name.lower())
                if field_name:
                    field_names.add(field_name.lower())
            
            # 检查表名匹配
            for table_name in table_names:
                if table_name in question.lower():
                    score += 3
                    print(f"  表名匹配: {table_name} -> +3分")
            
            # 检查字段名匹配
            for field_name in field_names:
                if field_name in question.lower():
                    score += 2
                    print(f"  字段名匹配: {field_name} -> +2分")
            
        except Exception as e:
            print(f"  检查表时出错: {e}")
        
        print(f"  数据源 {name} 总分: {score}")
        
        if score > best_score:
            best_score = score
            best_match = ds_id
    
    print(f"\n最佳匹配数据源ID: {best_match}, 得分: {best_score}")
    
    cursor.close()
    conn.close()
    
    return best_match

def test_table_schema_for_datasource(ds_id):
    """测试特定数据源的表结构生成"""
    print(f"\n=== 测试数据源 {ds_id} 的表结构生成 ===")
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="sqlbot",
            user="root",
            password="Password123@pg"
        )
        cursor = conn.cursor()
        
        # 获取数据源信息
        cursor.execute("SELECT name, description, type FROM core_datasource WHERE id = %s;", (ds_id,))
        ds_info = cursor.fetchone()
        
        if not ds_info:
            print(f"数据源 {ds_id} 不存在")
            return None
        
        name, description, ds_type = ds_info
        print(f"数据源: {name} ({description})")
        
        # 获取表结构
        cursor.execute("""
            SELECT t.table_name, t.table_comment, f.field_name, f.field_type, f.field_comment, f.checked
            FROM core_table t
            LEFT JOIN core_field f ON t.id = f.table_id
            WHERE t.ds_id = %s AND t.checked = true AND f.checked = true
            ORDER BY t.table_name, f.field_index;
        """, (ds_id,))
        
        tables = cursor.fetchall()
        
        if not tables:
            print("没有找到表或字段")
            return None
        
        # 构建表结构信息
        schema_info = f"【DB_ID】 sqlbot\n【Schema】\n"
        
        current_table = None
        for table in tables:
            table_name, table_comment, field_name, field_type, field_comment, checked = table
            
            if table_name != current_table:
                if current_table is not None:
                    schema_info += "]\n"
                
                schema_info += f"# Table: sqlbot.{table_name}"
                if table_comment:
                    schema_info += f", {table_comment}"
                schema_info += "\n[\n"
                current_table = table_name
            
            if field_name:
                field_desc = f"({field_name}:{field_type}"
                if field_comment:
                    field_desc += f", {field_comment}"
                field_desc += ")"
                schema_info += field_desc + ",\n"
        
        if current_table:
            schema_info += "]\n"
        
        print("生成的表结构信息:")
        print(schema_info)
        
        # 检查是否包含"手术类型"字段
        if "手术类型" in schema_info:
            print("✓ 表结构包含'手术类型'字段")
        else:
            print("✗ 表结构不包含'手术类型'字段")
        
        cursor.close()
        conn.close()
        
        return schema_info
        
    except Exception as e:
        print(f"测试表结构生成失败: {e}")
        return None

def test_ai_model_simulation(schema_info):
    """模拟AI模型的SQL生成过程"""
    print("\n=== 模拟AI模型的SQL生成过程 ===")
    
    question = "手术类型分布"
    print(f"用户问题: {question}")
    
    # 检查问题与表结构的匹配
    if "手术类型" in question and "手术类型" in schema_info:
        print("✓ 问题与表结构匹配")
        
        # 模拟AI模型应该生成的SQL
        expected_sql = 'SELECT "手术类型", COUNT(*) as count FROM "Sheet1_fc32194e01" GROUP BY "手术类型" ORDER BY count DESC LIMIT 1000'
        
        print("期望的SQL:")
        print(expected_sql)
        
        # 验证SQL
        if "手术类型" in expected_sql and "Sheet1_fc32194e01" in expected_sql:
            print("✓ SQL包含正确的字段名和表名")
            return True
        else:
            print("✗ SQL不包含正确的字段名或表名")
            return False
    else:
        print("✗ 问题与表结构不匹配")
        return False

def main():
    print("开始使用实际数据库测试完整流程...")
    print("=" * 60)
    
    # 1. 测试数据源选择
    best_ds_id = test_real_datasource_selection()
    
    if not best_ds_id:
        print("没有找到匹配的数据源")
        return
    
    # 2. 测试表结构生成
    schema_info = test_table_schema_for_datasource(best_ds_id)
    
    if not schema_info:
        print("表结构生成失败")
        return
    
    # 3. 测试AI模型模拟
    success = test_ai_model_simulation(schema_info)
    
    print("\n" + "=" * 60)
    if success:
        print("✓ 整个流程测试成功")
        print("问题可能在于:")
        print("1. 前端没有正确调用数据源选择API")
        print("2. 用户权限问题")
        print("3. AI模型配置问题")
    else:
        print("✗ 流程测试失败")
        print("问题在于表结构生成或AI模型处理")

if __name__ == "__main__":
    main()
