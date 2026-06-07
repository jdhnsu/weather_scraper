import pymysql

try:
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='test123456',      # ← 替换为你实际的密码
        database='test_db',
        charset='utf8mb4'
    )
    print("---\n连接成功\n---\n")
    
    # 测试查询
    with conn.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        print(f"MySQL 版本: {cursor.fetchone()[0]}")
        
    def delete_weather_data_all(conn):
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM weather_daily")
        conn.commit()
        print(f"已删除所有天气数据")

    delete_weather_data_all(conn)

finally:
    if conn:
        conn.close()
        print("🔒 连接已关闭")