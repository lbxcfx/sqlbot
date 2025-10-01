#!/usr/bin/env python3
"""
测试聊天API并查看详细日志
"""
import requests
import json
import time

def test_chat_api_with_logs():
    """测试聊天API并查看日志"""
    print("=== 测试聊天API并查看日志 ===")
    
    # 首先获取认证token
    print("1. 获取认证token...")
    
    # 尝试登录获取token
    login_data = {
        "username": "admin",
        "password": "SQLBot@123456"
    }
    
    try:
        # 尝试登录
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            token = result.get('access_token')
            print(f"✓ 登录成功，获取到token: {token[:20]}...")
        else:
            print(f"✗ 登录失败: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"✗ 登录请求失败: {e}")
        return
    
    # 使用token测试聊天API
    print("\n2. 测试聊天API...")
    
    headers = {
        "Content-Type": "application/json",
        "X-SQLBOT-TOKEN": token
    }
    
    # 测试数据源列表
    print("2.1 获取数据源列表...")
    try:
        response = requests.get(
            "http://localhost:8000/api/v1/datasource/list",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            datasources = response.json()
            print(f"✓ 获取到 {len(datasources)} 个数据源:")
            for ds in datasources:
                print(f"  - ID: {ds['id']}, 名称: {ds['name']}, 类型: {ds['type']}")
        else:
            print(f"✗ 获取数据源失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ 获取数据源请求失败: {e}")
    
    # 测试智能匹配数据源
    print("\n2.2 测试智能匹配数据源...")
    try:
        match_data = {
            "question": "手术类型分布"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/chat/smart_match_datasource",
            json=match_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 智能匹配结果: {result}")
        else:
            print(f"✗ 智能匹配失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ 智能匹配请求失败: {e}")
    
    # 测试创建聊天
    print("\n2.3 测试创建聊天...")
    try:
        chat_data = {
            "question": "手术类型分布",
            "datasource": 2,  # 患者的手术数据
            "chart_type": "pie"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/chat/start",
            json=chat_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 创建聊天成功: {result}")
            chat_id = result.get('id')
            
            if chat_id:
                # 测试发送问题
                print(f"\n2.4 测试发送问题到聊天 {chat_id}...")
                
                question_data = {
                    "question": "手术类型分布",
                    "chart_type": "pie"
                }
                
                response = requests.post(
                    f"http://localhost:8000/api/v1/chat/chat",
                    json=question_data,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✓ 问题发送成功: {result}")
                else:
                    print(f"✗ 问题发送失败: {response.status_code} - {response.text}")
        else:
            print(f"✗ 创建聊天失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ 创建聊天请求失败: {e}")

def check_ai_model_logs():
    """检查AI模型相关日志"""
    print("\n=== 检查AI模型相关日志 ===")
    
    # 检查应用日志
    print("检查应用日志...")
    import subprocess
    
    try:
        result = subprocess.run([
            'docker', 'exec', 'sqlbot', 'tail', '-n', '100', '/opt/sqlbot/app/logs/info.log'
        ], capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("应用日志:")
            print(result.stdout)
        else:
            print(f"获取应用日志失败: {result.stderr}")
    except Exception as e:
        print(f"检查应用日志失败: {e}")
    
    # 检查错误日志
    print("\n检查错误日志...")
    try:
        result = subprocess.run([
            'docker', 'exec', 'sqlbot', 'tail', '-n', '50', '/opt/sqlbot/app/logs/error.log'
        ], capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("错误日志:")
            print(result.stdout)
        else:
            print(f"获取错误日志失败: {result.stderr}")
    except Exception as e:
        print(f"检查错误日志失败: {e}")

def main():
    print("开始测试聊天API并查看详细日志...")
    print("=" * 80)
    
    # 测试聊天API
    test_chat_api_with_logs()
    
    # 检查AI模型日志
    check_ai_model_logs()
    
    print("\n" + "=" * 80)
    print("测试完成")

if __name__ == "__main__":
    main()
