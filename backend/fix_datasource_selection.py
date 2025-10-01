#!/usr/bin/env python3
"""
修复数据源选择逻辑问题
"""
import subprocess

def run_docker_sql(sql):
    """通过Docker执行SQL"""
    try:
        result = subprocess.run([
            'docker', 'exec', '-i', 'sqlbot', 'psql', '-U', 'root', '-d', 'sqlbot', '-c', sql
        ], capture_output=True, text=True, encoding='utf-8')
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def analyze_datasource_selection():
    """分析数据源选择逻辑"""
    print("=== 分析数据源选择逻辑 ===")
    
    # 检查数据源信息
    success, stdout, stderr = run_docker_sql("""
        SELECT id, name, description, type 
        FROM core_datasource 
        WHERE oid = 1 
        ORDER BY id;
    """)
    
    if success:
        print("数据源信息:")
        print(stdout)
    
    # 检查每个数据源的表
    print("\n=== 检查各数据源的表 ===")
    
    for ds_id in [1, 2]:
        print(f"\n数据源 {ds_id} 的表:")
        success, stdout, stderr = run_docker_sql(f"""
            SELECT t.table_name, t.table_comment, f.field_name, f.field_comment
            FROM core_table t
            LEFT JOIN core_field f ON t.id = f.table_id
            WHERE t.ds_id = {ds_id} AND t.checked = true AND f.checked = true
            ORDER BY t.table_name, f.field_index;
        """)
        
        if success:
            print(stdout)
            
            # 检查是否包含"手术类型"字段
            if "手术类型" in stdout:
                print(f"✓ 数据源 {ds_id} 包含'手术类型'字段")
            else:
                print(f"✗ 数据源 {ds_id} 不包含'手术类型'字段")

def test_smart_match_algorithm():
    """测试智能匹配算法"""
    print("\n=== 测试智能匹配算法 ===")
    
    question = "手术类型分布"
    print(f"用户问题: {question}")
    
    # 模拟智能匹配算法
    success, stdout, stderr = run_docker_sql("""
        SELECT id, name, description, type 
        FROM core_datasource 
        WHERE oid = 1 
        ORDER BY id;
    """)
    
    if not success:
        print(f"获取数据源失败: {stderr}")
        return
    
    lines = stdout.strip().split('\n')[2:-1]
    datasources = []
    for line in lines:
        if '|' in line:
            parts = line.split('|')
            if len(parts) >= 4:
                datasources.append({
                    'id': int(parts[0].strip()),
                    'name': parts[1].strip(),
                    'description': parts[2].strip(),
                    'type': parts[3].strip()
                })
    
    print(f"找到 {len(datasources)} 个数据源")
    
    # 测试匹配算法
    best_match = None
    best_score = 0
    
    for ds in datasources:
        score = 0
        
        # 检查数据源名称
        if ds['name'] and ds['name'].lower() in question.lower():
            score += 10
            print(f"  数据源名称匹配: {ds['name']} -> +10分")
        
        # 检查数据源描述
        if ds['description'] and ds['description'].lower() in question.lower():
            score += 5
            print(f"  数据源描述匹配: {ds['description']} -> +5分")
        
        # 检查表名和字段
        try:
            success, stdout, stderr = run_docker_sql(f"""
                SELECT t.table_name, f.field_name
                FROM core_table t
                LEFT JOIN core_field f ON t.id = f.table_id
                WHERE t.ds_id = {ds['id']} AND t.checked = true AND f.checked = true;
            """)
            
            if success:
                lines = stdout.strip().split('\n')[2:-1]
                table_names = set()
                field_names = set()
                
                for line in lines:
                    if '|' in line:
                        parts = line.split('|')
                        if len(parts) >= 2:
                            table_name, field_name = parts[0].strip(), parts[1].strip()
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
        
        print(f"  数据源 {ds['name']} 总分: {score}")
        
        if score > best_score:
            best_score = score
            best_match = ds['id']
    
    print(f"\n最佳匹配数据源ID: {best_match}, 得分: {best_score}")
    
    if best_match == 2:
        print("✓ 智能匹配算法正确选择了数据源2")
    else:
        print("✗ 智能匹配算法选择了错误的数据源")

def check_table_schema_generation():
    """检查表结构生成"""
    print("\n=== 检查表结构生成 ===")
    
    # 检查数据源2的表结构生成
    success, stdout, stderr = run_docker_sql("""
        SELECT t.table_name, t.table_comment, f.field_name, f.field_type, f.field_comment
        FROM core_table t
        LEFT JOIN core_field f ON t.id = f.table_id
        WHERE t.ds_id = 2 AND t.checked = true AND f.checked = true
        ORDER BY t.table_name, f.field_index;
    """)
    
    if success:
        print("数据源2的表结构:")
        print(stdout)
        
        # 检查是否包含"手术类型"字段
        if "手术类型" in stdout:
            print("✓ 表结构包含'手术类型'字段")
        else:
            print("✗ 表结构不包含'手术类型'字段")

def main():
    print("开始分析数据源选择问题...")
    print("=" * 80)
    
    # 分析数据源选择逻辑
    analyze_datasource_selection()
    
    # 测试智能匹配算法
    test_smart_match_algorithm()
    
    # 检查表结构生成
    check_table_schema_generation()
    
    print("\n" + "=" * 80)
    print("分析完成")

if __name__ == "__main__":
    main()
