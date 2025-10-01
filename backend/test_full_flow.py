#!/usr/bin/env python3
"""
测试完整的回答流程，找出问题所在
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apps.datasource.crud.datasource import get_datasource_list, get_table_schema
from apps.datasource.crud.table import get_tables_by_ds_id
from apps.chat.api.chat import smart_match_datasource
from apps.chat.models.chat_model import SmartMatchRequest
from common.core.deps import SessionDep, CurrentUser
from sqlmodel import select
from apps.datasource.models.datasource import CoreDatasource
import json

def test_datasource_selection():
    """测试数据源选择逻辑"""
    print("=== 测试数据源选择逻辑 ===")
    
    # 模拟用户和会话
    class MockUser:
        def __init__(self):
            self.oid = 1
            self.isAdmin = True
            self.id = 1
    
    class MockSession:
        def get(self, model, id):
            if model == CoreDatasource:
                if id == 1:
                    return CoreDatasource(id=1, name="患者数据", description="患者基本信息", type="excel", oid=1)
                elif id == 2:
                    return CoreDatasource(id=2, name="患者的手术数据", description="患者手术相关信息", type="excel", oid=1)
            return None
        
        def exec(self, query):
            return self
        
        def where(self, condition):
            return self
        
        def order_by(self, field):
            return self
        
        def all(self):
            return [
                CoreDatasource(id=1, name="患者数据", description="患者基本信息", type="excel", oid=1),
                CoreDatasource(id=2, name="患者的手术数据", description="患者手术相关信息", type="excel", oid=1)
            ]
    
    user = MockUser()
    session = MockSession()
    
    # 测试问题
    question = "手术类型分布"
    
    print(f"用户问题: {question}")
    
    # 获取所有数据源
    datasources = get_datasource_list(session, user)
    print(f"找到 {len(datasources)} 个数据源:")
    for ds in datasources:
        print(f"  - ID: {ds.id}, 名称: {ds.name}, 描述: {ds.description}")
    
    # 测试智能匹配
    best_match = None
    best_score = 0
    
    for ds in datasources:
        score = 0
        
        # 检查数据源名称
        if ds.name and ds.name.lower() in question.lower():
            score += 10
            print(f"  数据源名称匹配: {ds.name} -> +10分")
        
        # 检查数据源描述
        if ds.description and ds.description.lower() in question.lower():
            score += 5
            print(f"  数据源描述匹配: {ds.description} -> +5分")
        
        # 检查表名
        try:
            tables = get_tables_by_ds_id(session, ds.id)
            for table in tables:
                if table.table_name and table.table_name.lower() in question.lower():
                    score += 3
                    print(f"  表名匹配: {table.table_name} -> +3分")
                if table.table_comment and table.table_comment.lower() in question.lower():
                    score += 2
                    print(f"  表注释匹配: {table.table_comment} -> +2分")
        except Exception as e:
            print(f"  检查表时出错: {e}")
        
        print(f"  数据源 {ds.name} 总分: {score}")
        
        if score > best_score:
            best_score = score
            best_match = ds.id
    
    print(f"最佳匹配数据源ID: {best_match}, 得分: {best_score}")
    
    return best_match

def test_table_schema_generation(ds_id):
    """测试表结构生成"""
    print(f"\n=== 测试数据源 {ds_id} 的表结构生成 ===")
    
    class MockUser:
        def __init__(self):
            self.oid = 1
            self.isAdmin = True
            self.id = 1
    
    class MockSession:
        def get(self, model, id):
            if model == CoreDatasource:
                if id == 2:
                    return CoreDatasource(id=2, name="患者的手术数据", description="患者手术相关信息", type="excel", oid=1)
            return None
        
        def query(self, model):
            return self
        
        def filter(self, condition):
            return self
        
        def all(self):
            return []
    
    user = MockUser()
    session = MockSession()
    
    # 获取数据源
    ds = session.get(CoreDatasource, ds_id)
    if not ds:
        print(f"数据源 {ds_id} 不存在")
        return None
    
    print(f"数据源: {ds.name}")
    
    # 模拟表结构生成
    try:
        # 这里我们需要实际的数据库连接来获取表结构
        print("需要实际的数据库连接来测试表结构生成...")
        return None
    except Exception as e:
        print(f"表结构生成失败: {e}")
        return None

def test_ai_model_input():
    """测试AI模型输入"""
    print("\n=== 测试AI模型输入 ===")
    
    # 模拟表结构信息
    mock_schema = """
【DB_ID】 sqlbot
【Schema】
# Table: sqlbot.Sheet1_fc32194e01, 患者手术数据
[
(就诊日期:text, 就诊日期),
(姓名:text, 姓名),
(年龄:bigint, 年龄),
(性别:text, 性别),
(手术类型:text, 手术类型),
(手术费用:bigint, 手术费用),
(手术医生:text, 手术医生),
(住院天数:bigint, 住院天数),
]
"""
    
    print("模拟的表结构信息:")
    print(mock_schema)
    
    # 检查是否包含"手术类型"字段
    if "手术类型" in mock_schema:
        print("✓ 表结构包含'手术类型'字段")
    else:
        print("✗ 表结构不包含'手术类型'字段")
    
    # 模拟AI模型输入
    question = "手术类型分布"
    print(f"\n用户问题: {question}")
    
    # 检查问题与表结构的匹配度
    if "手术类型" in question and "手术类型" in mock_schema:
        print("✓ 问题与表结构匹配")
    else:
        print("✗ 问题与表结构不匹配")

def test_sql_generation():
    """测试SQL生成"""
    print("\n=== 测试SQL生成 ===")
    
    # 模拟AI模型应该生成的SQL
    expected_sql = 'SELECT "手术类型", COUNT(*) as count FROM "Sheet1_fc32194e01" GROUP BY "手术类型" ORDER BY count DESC LIMIT 1000'
    
    print("期望的SQL:")
    print(expected_sql)
    
    # 检查SQL是否正确
    if "手术类型" in expected_sql and "Sheet1_fc32194e01" in expected_sql:
        print("✓ SQL包含正确的字段名和表名")
    else:
        print("✗ SQL不包含正确的字段名或表名")

def main():
    print("开始测试完整的回答流程...")
    print("=" * 60)
    
    # 1. 测试数据源选择
    best_ds_id = test_datasource_selection()
    
    # 2. 测试表结构生成
    if best_ds_id:
        test_table_schema_generation(best_ds_id)
    
    # 3. 测试AI模型输入
    test_ai_model_input()
    
    # 4. 测试SQL生成
    test_sql_generation()
    
    print("\n" + "=" * 60)
    print("测试完成")

if __name__ == "__main__":
    main()
