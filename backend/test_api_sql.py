#!/usr/bin/env python3
"""
测试通过API接口生成SQL
"""
import requests
import json

def test_chat_api():
    """测试聊天API接口"""
    print("开始测试聊天API接口...")
    
    # API端点
    base_url = "http://localhost:8000/api/v1"
    
    # 测试数据
    test_data = {
        "question": "手术类型分布",
        "ds_id": 2,  # 患者的手术数据数据源ID
        "chart_type": "pie"
    }
    
    try:
        # 发送POST请求到聊天接口
        response = requests.post(
            f"{base_url}/chat/chat",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✓ API请求成功")
            result = response.json()
            print("响应结果:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"✗ API请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到API服务器，请确保服务正在运行")
    except Exception as e:
        print(f"✗ 请求失败: {e}")

def test_datasource_list():
    """测试数据源列表API"""
    print("\n=== 测试数据源列表API ===")
    
    try:
        response = requests.get("http://localhost:8000/api/v1/datasource/list")
        
        if response.status_code == 200:
            print("✓ 数据源列表获取成功")
            datasources = response.json()
            print(f"找到 {len(datasources)} 个数据源:")
            for ds in datasources:
                print(f"  - ID: {ds['id']}, 名称: {ds['name']}, 类型: {ds['type']}")
        else:
            print(f"✗ 数据源列表获取失败: {response.status_code}")
            
    except Exception as e:
        print(f"✗ 请求失败: {e}")

def test_table_schema():
    """测试表结构API"""
    print("\n=== 测试表结构API ===")
    
    try:
        # 获取表列表
        response = requests.post("http://localhost:8000/api/v1/datasource/tableList/2")
        
        if response.status_code == 200:
            print("✓ 表列表获取成功")
            tables = response.json()
            print(f"数据源2包含 {len(tables)} 个表:")
            for table in tables:
                print(f"  - 表ID: {table['id']}, 表名: {table['table_name']}, 启用: {table['checked']}")
        else:
            print(f"✗ 表列表获取失败: {response.status_code}")
            
    except Exception as e:
        print(f"✗ 请求失败: {e}")

def main():
    print("开始测试API接口...")
    
    # 测试数据源列表
    test_datasource_list()
    
    # 测试表结构
    test_table_schema()
    
    # 测试聊天API
    test_chat_api()
    
    print("\n测试完成")

if __name__ == "__main__":
    main()
