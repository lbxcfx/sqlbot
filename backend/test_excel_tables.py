#!/usr/bin/env python3
"""
测试Excel文件上传后的表结构问题
"""
import psycopg2
from common.core.config import settings
import os

def test_database_connection():
    """测试数据库连接"""
    try:
        # 使用Docker容器中的数据库连接信息
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="sqlbot",
            user="root",
            password="Password123@pg"
        )
        cursor = conn.cursor()
        print("✓ 数据库连接成功")
        return conn, cursor
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return None, None

def check_excel_tables(cursor):
    """检查Excel上传后的表"""
    print("\n=== 检查Excel相关表 ===")
    
    # 查看所有Sheet1相关的表
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name LIKE '%sheet1%'
        ORDER BY table_name;
    """)
    
    tables = cursor.fetchall()
    print(f"找到 {len(tables)} 个Sheet1相关表:")
    for table in tables:
        print(f"  - {table[0]}")
    
    return tables

def check_table_structure(cursor, table_name):
    """检查表结构"""
    print(f"\n=== 检查表 {table_name} 的结构 ===")
    
    # 查看表的所有列
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = %s
        ORDER BY ordinal_position;
    """, (table_name,))
    
    columns = cursor.fetchall()
    print(f"表 {table_name} 有 {len(columns)} 个字段:")
    for col in columns:
        print(f"  - {col[0]} ({col[1]}) - 可空: {col[2]}")
    
    return columns

def check_sample_data(cursor, table_name, limit=5):
    """检查样本数据"""
    print(f"\n=== 检查表 {table_name} 的样本数据 ===")
    
    try:
        cursor.execute(f"SELECT * FROM \"{table_name}\" LIMIT {limit};")
        rows = cursor.fetchall()
        
        if rows:
            print(f"前 {len(rows)} 行数据:")
            for i, row in enumerate(rows, 1):
                print(f"  行 {i}: {row}")
        else:
            print("表中没有数据")
    except Exception as e:
        print(f"查询数据失败: {e}")

def check_core_tables(cursor):
    """检查系统核心表"""
    print("\n=== 检查系统核心表 ===")
    
    # 检查core_datasource表
    cursor.execute("SELECT id, name, type FROM core_datasource WHERE type = 'excel';")
    datasources = cursor.fetchall()
    print(f"Excel数据源数量: {len(datasources)}")
    for ds in datasources:
        print(f"  - ID: {ds[0]}, 名称: {ds[1]}, 类型: {ds[2]}")
    
    # 检查core_table表
    cursor.execute("""
        SELECT t.id, t.table_name, t.checked, ds.name as ds_name
        FROM core_table t
        JOIN core_datasource ds ON t.ds_id = ds.id
        WHERE ds.type = 'excel'
        ORDER BY t.table_name;
    """)
    
    tables = cursor.fetchall()
    print(f"\nExcel相关表记录数量: {len(tables)}")
    for table in tables:
        print(f"  - 表ID: {table[0]}, 表名: {table[1]}, 启用: {table[2]}, 数据源: {table[3]}")
    
    return tables

def check_core_fields(cursor, table_id):
    """检查字段信息"""
    print(f"\n=== 检查表ID {table_id} 的字段信息 ===")
    
    cursor.execute("""
        SELECT field_name, field_type, field_comment, checked
        FROM core_field
        WHERE table_id = %s
        ORDER BY field_index;
    """, (table_id,))
    
    fields = cursor.fetchall()
    print(f"字段数量: {len(fields)}")
    for field in fields:
        print(f"  - {field[0]} ({field[1]}) - 注释: {field[2]} - 启用: {field[3]}")

def main():
    print("开始测试Excel文件上传后的表结构问题...")
    
    # 连接数据库
    conn, cursor = test_database_connection()
    if not conn:
        return
    
    try:
        # 检查Excel相关表
        excel_tables = check_excel_tables(cursor)
        
        # 检查系统核心表
        core_tables = check_core_tables(cursor)
        
        # 如果有Excel表，检查其结构
        if excel_tables:
            for table in excel_tables:
                table_name = table[0]
                check_table_structure(cursor, table_name)
                check_sample_data(cursor, table_name)
        
        # 检查字段信息
        if core_tables:
            for table in core_tables:
                table_id = table[0]
                check_core_fields(cursor, table_id)
        
    except Exception as e:
        print(f"测试过程中出错: {e}")
    finally:
        cursor.close()
        conn.close()
        print("\n测试完成")

if __name__ == "__main__":
    main()
