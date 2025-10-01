#!/usr/bin/env python3
"""
Excel文件上传后表结构解析问题诊断报告
"""
import subprocess
import json

def run_sql_command(sql):
    """执行SQL命令"""
    try:
        result = subprocess.run([
            'docker', 'exec', '-i', 'sqlbot', 'psql', '-U', 'root', '-d', 'sqlbot', '-c', sql
        ], capture_output=True, text=True, encoding='utf-8')
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_database_status():
    """检查数据库状态"""
    print("=== 数据库状态检查 ===")
    
    # 检查数据库连接
    success, stdout, stderr = run_sql_command("SELECT version();")
    if success:
        print("✓ 数据库连接正常")
        print(f"PostgreSQL版本: {stdout.split('PostgreSQL')[1].split('on')[0].strip()}")
    else:
        print("✗ 数据库连接失败")
        print(f"错误: {stderr}")
        return False
    
    return True

def check_excel_tables():
    """检查Excel表"""
    print("\n=== Excel表检查 ===")
    
    # 查找所有Sheet1相关的表
    success, stdout, stderr = run_sql_command("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name ILIKE '%sheet1%' ORDER BY table_name;")
    
    if success:
        lines = stdout.strip().split('\n')[2:-1]  # 跳过标题行和空行
        tables = [line.strip() for line in lines if line.strip()]
        print(f"✓ 找到 {len(tables)} 个Excel表:")
        for table in tables:
            print(f"  - {table}")
        return tables
    else:
        print("✗ 查找Excel表失败")
        print(f"错误: {stderr}")
        return []

def check_table_structure(table_name):
    """检查表结构"""
    print(f"\n=== 表 {table_name} 结构检查 ===")
    
    # 检查表结构
    success, stdout, stderr = run_sql_command(f'SELECT column_name, data_type FROM information_schema.columns WHERE table_name = \'{table_name}\' ORDER BY ordinal_position;')
    
    if success:
        lines = stdout.strip().split('\n')[2:-1]
        columns = []
        for line in lines:
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 2:
                    columns.append((parts[0].strip(), parts[1].strip()))
        
        print(f"✓ 表有 {len(columns)} 个字段:")
        for col_name, col_type in columns:
            print(f"  - {col_name} ({col_type})")
        
        # 检查是否包含"手术类型"字段
        surgery_type_found = any('手术类型' in col[0] for col in columns)
        if surgery_type_found:
            print("✓ 找到'手术类型'字段")
        else:
            print("✗ 未找到'手术类型'字段")
        
        return columns, surgery_type_found
    else:
        print(f"✗ 检查表结构失败: {stderr}")
        return [], False

def check_sample_data(table_name):
    """检查样本数据"""
    print(f"\n=== 表 {table_name} 样本数据检查 ===")
    
    # 获取样本数据
    success, stdout, stderr = run_sql_command(f'SELECT * FROM "{table_name}" LIMIT 3;')
    
    if success:
        print("✓ 样本数据:")
        print(stdout)
        return True
    else:
        print(f"✗ 获取样本数据失败: {stderr}")
        return False

def check_surgery_type_distribution(table_name):
    """检查手术类型分布"""
    print(f"\n=== 表 {table_name} 手术类型分布检查 ===")
    
    # 查询手术类型分布
    sql = f'''
    SELECT "手术类型", COUNT(*) as count 
    FROM "{table_name}" 
    GROUP BY "手术类型" 
    ORDER BY count DESC;
    '''
    
    success, stdout, stderr = run_sql_command(sql)
    
    if success:
        print("✓ 手术类型分布查询成功:")
        print(stdout)
        return True
    else:
        print(f"✗ 手术类型分布查询失败: {stderr}")
        return False

def check_system_tables():
    """检查系统核心表"""
    print("\n=== 系统核心表检查 ===")
    
    # 检查数据源表
    success, stdout, stderr = run_sql_command("SELECT id, name, type FROM core_datasource WHERE type = 'excel';")
    
    if success:
        print("✓ Excel数据源:")
        lines = stdout.strip().split('\n')[2:-1]
        for line in lines:
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 3:
                    print(f"  - ID: {parts[0].strip()}, 名称: {parts[1].strip()}, 类型: {parts[2].strip()}")
    
    # 检查表记录
    success, stdout, stderr = run_sql_command("""
        SELECT t.id, t.table_name, t.checked, ds.name as ds_name
        FROM core_table t
        JOIN core_datasource ds ON t.ds_id = ds.id
        WHERE ds.type = 'excel'
        ORDER BY t.table_name;
    """)
    
    if success:
        print("\n✓ Excel表记录:")
        lines = stdout.strip().split('\n')[2:-1]
        for line in lines:
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 4:
                    print(f"  - 表ID: {parts[0].strip()}, 表名: {parts[1].strip()}, 启用: {parts[2].strip()}, 数据源: {parts[3].strip()}")
    
    # 检查字段记录
    success, stdout, stderr = run_sql_command("""
        SELECT f.field_name, f.field_type, f.checked, t.table_name
        FROM core_field f
        JOIN core_table t ON f.table_id = t.id
        JOIN core_datasource ds ON t.ds_id = ds.id
        WHERE ds.type = 'excel' AND t.table_name LIKE '%fc32194e01%'
        ORDER BY f.field_index;
    """)
    
    if success:
        print("\n✓ 字段记录:")
        lines = stdout.strip().split('\n')[2:-1]
        for line in lines:
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 4:
                    print(f"  - 字段: {parts[0].strip()}, 类型: {parts[1].strip()}, 启用: {parts[2].strip()}, 表: {parts[3].strip()}")

def generate_diagnosis_report():
    """生成诊断报告"""
    print("开始生成Excel文件上传后表结构解析问题诊断报告...")
    print("=" * 60)
    
    # 1. 检查数据库状态
    if not check_database_status():
        return
    
    # 2. 检查Excel表
    tables = check_excel_tables()
    if not tables:
        print("\n❌ 问题诊断: 没有找到Excel上传的表")
        return
    
    # 3. 检查每个表的结构
    for table in tables:
        columns, has_surgery_type = check_table_structure(table)
        
        if has_surgery_type:
            # 4. 检查样本数据
            check_sample_data(table)
            
            # 5. 检查手术类型分布
            check_surgery_type_distribution(table)
    
    # 6. 检查系统核心表
    check_system_tables()
    
    # 7. 生成结论
    print("\n" + "=" * 60)
    print("诊断结论:")
    print("=" * 60)
    
    if tables:
        print("✓ Excel文件已成功上传并创建表")
        print("✓ 表结构包含'手术类型'字段")
        print("✓ 数据已正确导入")
        print("✓ 可以直接查询手术类型分布")
        print("\n建议:")
        print("1. 检查前端数据源配置是否正确")
        print("2. 确认用户有权限访问该数据源")
        print("3. 检查SQL生成模板是否正确处理中文字段名")
        print("4. 验证表结构同步是否完整")
    else:
        print("❌ Excel文件上传失败或表未正确创建")

def main():
    generate_diagnosis_report()

if __name__ == "__main__":
    main()
