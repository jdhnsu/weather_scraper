"""
测试脚本 - 验证数据库连接和基本功能
"""
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import db

def test_database_connection():
    """测试数据库连接"""
    print("=" * 50)
    print("测试1: 数据库连接")
    print("=" * 50)
    
    conn = None
    try:
        conn = db.connect_db()
        print("✓ 数据库连接成功")
        
        # 测试创建表
        db.create_table(conn)
        print("✓ 表结构创建/验证成功")
        
        return True
    except Exception as e:
        print(f"✗ 数据库连接失败: {str(e)}")
        return False
    finally:
        if conn:
            db.close_db(conn)


def test_statistics_calculation():
    """测试统计计算功能"""
    print("\n" + "=" * 50)
    print("测试2: 统计计算功能")
    print("=" * 50)
    
    conn = None
    try:
        conn = db.connect_db()
        
        # 测试2024年5月的统计数据
        stats = db.calculate_monthly_statistics(conn, 2024, 5)
        
        print(f"✓ 统计计算成功:")
        print(f"  - 总天数: {stats['total_days']}")
        print(f"  - 晴天率: {stats['sunny_rate']}%")
        print(f"  - 雨天率: {stats['rainy_rate']}%")
        print(f"  - 多云率: {stats['cloudy_rate']}%")
        print(f"  - 平均最高温: {stats['avg_temp_max']}℃")
        print(f"  - 平均最低温: {stats['avg_temp_min']}℃")
        
        return True
    except Exception as e:
        print(f"✗ 统计计算失败: {str(e)}")
        return False
    finally:
        if conn:
            db.close_db(conn)


def test_filter_query():
    """测试筛选查询功能"""
    print("\n" + "=" * 50)
    print("测试3: 筛选查询功能")
    print("=" * 50)
    
    conn = None
    try:
        conn = db.connect_db()
        
        # 测试查询2024年1月和2月的数据
        rows = db.query_weather_data_by_filter(conn, 2024, [1, 2])
        
        print(f"✓ 查询成功，共获取 {len(rows)} 条记录")
        if rows:
            print(f"  - 第一条记录: {rows[0]}")
        
        return True
    except Exception as e:
        print(f"✗ 查询失败: {str(e)}")
        return False
    finally:
        if conn:
            db.close_db(conn)


if __name__ == "__main__":
    print("\nWeatherScrape Pro - 功能测试\n")
    
    results = []
    results.append(("数据库连接", test_database_connection()))
    results.append(("统计计算", test_statistics_calculation()))
    results.append(("筛选查询", test_filter_query()))
    
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 所有测试通过！可以启动GUI程序。")
    else:
        print("\n⚠️  部分测试失败，请检查配置后重试。")
    
    sys.exit(0 if all_passed else 1)
