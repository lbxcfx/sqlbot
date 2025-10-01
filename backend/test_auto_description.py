"""
测试自动生成数据源描述功能
运行方式：
1. 进入backend目录：cd backend
2. 运行脚本：python test_auto_description.py
"""

import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from apps.datasource.crud.datasource import generate_auto_description
from apps.datasource.models.datasource import CoreDatasource
from common.core.config import settings


def test_generate_description():
    """测试为现有数据源生成描述"""

    # 创建数据库连接
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        # 获取所有数据源
        datasources = session.query(CoreDatasource).all()

        print(f"\n找到 {len(datasources)} 个数据源\n")
        print("=" * 80)

        for ds in datasources:
            print(f"\n数据源ID: {ds.id}")
            print(f"名称: {ds.name}")
            print(f"类型: {ds.type}")
            print(f"当前描述: {ds.description or '(空)'}")

            # 生成自动描述
            auto_desc = generate_auto_description(session, ds)

            if auto_desc:
                print(f"✅ 自动生成描述:")
                print(f"   {auto_desc}")

                # 如果当前描述为空，询问是否更新
                if not ds.description or ds.description.strip() == '':
                    response = input(f"\n是否更新数据源 '{ds.name}' 的描述？(y/n): ")
                    if response.lower() == 'y':
                        ds.description = auto_desc
                        session.add(ds)
                        session.commit()
                        print(f"✅ 已更新数据源 {ds.id} 的描述")
                    else:
                        print("跳过更新")
                else:
                    print("⚠️  已有描述，跳过自动更新")
            else:
                print("❌ 无法生成描述（可能没有选择表或字段）")

            print("-" * 80)

        print("\n测试完成！")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()


def batch_update_empty_descriptions():
    """批量更新所有空描述的数据源"""

    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        # 查询所有描述为空的数据源
        from sqlalchemy import or_
        datasources = session.query(CoreDatasource).filter(
            or_(CoreDatasource.description == '', CoreDatasource.description == None)
        ).all()

        print(f"\n找到 {len(datasources)} 个描述为空的数据源")

        if not datasources:
            print("✅ 所有数据源都已有描述！")
            return

        response = input(f"\n是否批量更新这 {len(datasources)} 个数据源的描述？(y/n): ")

        if response.lower() != 'y':
            print("取消操作")
            return

        updated_count = 0
        failed_count = 0

        for ds in datasources:
            try:
                auto_desc = generate_auto_description(session, ds)
                if auto_desc:
                    ds.description = auto_desc
                    session.add(ds)
                    session.commit()
                    print(f"✅ 已更新: {ds.name} - {auto_desc[:50]}...")
                    updated_count += 1
                else:
                    print(f"⚠️  跳过: {ds.name} (无法生成描述)")
                    failed_count += 1
            except Exception as e:
                print(f"❌ 失败: {ds.name} - {e}")
                failed_count += 1

        print(f"\n批量更新完成！")
        print(f"✅ 成功: {updated_count} 个")
        print(f"❌ 失败: {failed_count} 个")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()


if __name__ == "__main__":
    print("=" * 80)
    print("数据源自动描述生成测试工具")
    print("=" * 80)

    print("\n请选择操作：")
    print("1. 查看并测试生成描述（不自动更新）")
    print("2. 批量更新所有空描述的数据源")
    print("3. 退出")

    choice = input("\n请输入选项 (1/2/3): ").strip()

    if choice == '1':
        test_generate_description()
    elif choice == '2':
        batch_update_empty_descriptions()
    elif choice == '3':
        print("再见！")
    else:
        print("无效选项")