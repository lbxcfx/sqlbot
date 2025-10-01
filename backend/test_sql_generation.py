#!/usr/bin/env python3
"""
测试SQL生成功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apps.template.generate_sql.generator import get_sql_template
from apps.datasource.crud.datasource import get_table_schema
from common.core.deps import SessionDep, CurrentUser
from apps.datasource.models.datasource import CoreDatasource
from sqlmodel import select
import json

def test_sql_generation():
    """测试SQL生成功能"""
    print("开始测试SQL生成功能...")
    
    # 模拟用户和会话
    class MockUser:
        def __init__(self):
            self.oid = 1
            self.isAdmin = True
    
    class MockSession:
        def query(self, model):
            return self
        def filter(self, condition):
            return self
        def all(self):
            return []
        def first(self):
            return None
    
    user = MockUser()
    session = MockSession()
    
    # 获取数据源
    try:
        # 这里我们需要实际的数据库连接来获取数据源
        print("需要实际的数据库连接来测试SQL生成...")
        return
    except Exception as e:
        print(f"测试失败: {e}")

def test_template_loading():
    """测试模板加载"""
    print("\n=== 测试模板加载 ===")
    try:
        template = get_sql_template()
        print("✓ SQL模板加载成功")
        print(f"模板类型: {type(template)}")
        if hasattr(template, 'system'):
            print("✓ 包含system模板")
        if hasattr(template, 'user'):
            print("✓ 包含user模板")
    except Exception as e:
        print(f"✗ 模板加载失败: {e}")

def test_direct_sql():
    """直接测试SQL查询"""
    print("\n=== 直接测试SQL查询 ===")
    
    # 使用Docker执行SQL
    import subprocess
    
    # 测试手术类型分布查询
    sql = '''
    SELECT "手术类型", COUNT(*) as count 
    FROM "Sheet1_fc32194e01" 
    GROUP BY "手术类型" 
    ORDER BY count DESC;
    '''
    
    try:
        result = subprocess.run([
            'docker', 'exec', '-i', 'sqlbot', 'psql', '-U', 'root', '-d', 'sqlbot', '-c', sql
        ], capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✓ SQL查询执行成功")
            print("查询结果:")
            print(result.stdout)
        else:
            print("✗ SQL查询执行失败")
            print("错误信息:")
            print(result.stderr)
    except Exception as e:
        print(f"✗ 执行SQL失败: {e}")

def main():
    print("开始测试SQL生成相关功能...")
    
    # 测试模板加载
    test_template_loading()
    
    # 测试直接SQL查询
    test_direct_sql()
    
    print("\n测试完成")

if __name__ == "__main__":
    main()
