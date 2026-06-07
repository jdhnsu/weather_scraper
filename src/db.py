import pymysql
import json
from datetime import datetime


def connect_db():
    conn = None
    try:
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='test123456',
            database='test_db',
            charset='utf8mb4'
        )
        if conn:
            print("---\n连接成功\n---\n")
        return conn
    except pymysql.err.OperationalError as e:
        error_msg = f"数据库连接失败: {str(e)}\n请检查:\n1. MySQL服务是否启动\n2. 用户名密码是否正确\n3. 数据库test_db是否存在"
        print(error_msg)
        raise


def close_db(conn):
    if conn:
        conn.close()
        print("---\n连接已关闭\n---\n")


# 构建表结构
def create_table(conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS weather_daily (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            date          DATE NOT NULL UNIQUE,
            ym            VARCHAR(6) NOT NULL,
            day_weather   VARCHAR(20),
            night_weather VARCHAR(20),
            temp_max      INT,
            temp_min      INT,
            wind_day      VARCHAR(50),
            wind_night    VARCHAR(50),
            crawl_time    DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
        conn.commit()
    except Exception as e:
        print(f"创建表失败: {str(e)}")
        raise


def insert_weather_data(conn, weather_data):
    try:
        rows = json.loads(weather_data)
        
        all_items = []
        for month_data in rows:
            if isinstance(month_data, list):
                all_items.extend(month_data)
            else:
                all_items.append(month_data)
        
        print(f"解析到 {len(all_items)} 条数据")
        cursor = conn.cursor()
        now = datetime.now()
        params = []
        for item in all_items:
            d = item['date']
            date_str = f"{d[:4]}-{d[5:7]}-{d[8:10]}"
            params.append((
                date_str,
                date_str.replace("-", "")[:6],
                item['weatherDay'], item['weatherNight'],
                int(item['maxTemp']), int(item['minTemp']),
                item['windDay'], item['windNight'],
                now,
            ))

        cursor.executemany("""
            INSERT INTO weather_daily
                (date, ym, day_weather, night_weather,
                 temp_max, temp_min, wind_day, wind_night, crawl_time)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
                temp_max = VALUES(temp_max),
                temp_min = VALUES(temp_min)
        """, params)
        conn.commit()
        print(f"入库 {cursor.rowcount} 条  (去重保障)")
    except Exception as e:
        print(f"插入数据失败: {str(e)}")
        raise


# 删除所有天气数据 id 也要自增回到 1
def delete_weather_data_all(conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM weather_daily")
            cursor.execute("ALTER TABLE weather_daily AUTO_INCREMENT = 1")
        conn.commit()
        print(f"已删除所有天气数据")
    except Exception as e:
        print(f"删除数据失败: {str(e)}")
        raise


def query_weather_monthly_data(conn, month):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            SELECT date, day_weather, night_weather, temp_max, temp_min, wind_day, wind_night
            FROM weather_daily
            WHERE ym = %s
            ORDER BY date
            """, (month,))
            return cursor.fetchall()
    except Exception as e:
        print(f"查询月度数据失败: {str(e)}")
        raise


def query_weather_daily_data(conn, date):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            SELECT date, day_weather, night_weather, temp_max, temp_min, wind_day, wind_night
            FROM weather_daily
            WHERE date = %s
            """, (date,))
            return cursor.fetchone()
    except Exception as e:
        print(f"查询每日数据失败: {str(e)}")
        raise


def query_weather_data_by_filter(conn, year, months):
    """
    根据年份和月份列表查询天气数据
    
    Args:
        conn: 数据库连接
        year: 年份 (int)
        months: 月份列表 (list of int)，如 [1, 2, 3] 表示1月、2月、3月
    
    Returns:
        list: 查询结果列表，每个元素为元组
    """
    try:
        if not months:
            return []
        
        # 构建月份字符串列表，如 ['202401', '202402', '202403']
        ym_list = [f"{year}{month:02d}" for month in months]
        
        # 构建SQL查询
        placeholders = ','.join(['%s'] * len(ym_list))
        query = f"""
        SELECT date, day_weather, night_weather, temp_max, temp_min, wind_day, wind_night
        FROM weather_daily
        WHERE ym IN ({placeholders})
        ORDER BY date
        """
        
        with conn.cursor() as cursor:
            cursor.execute(query, tuple(ym_list))
            return cursor.fetchall()
    except Exception as e:
        print(f"按筛选条件查询数据失败: {str(e)}")
        raise


def calculate_monthly_statistics(conn, year, month):
    """
    计算指定年月的统计数据
    
    Args:
        conn: 数据库连接
        year: 年份 (int)
        month: 月份 (int)
    
    Returns:
        dict: 统计结果字典
            - sunny_rate: 晴天率 (%)
            - rainy_rate: 雨天率 (%)
            - cloudy_rate: 多云率 (%)
            - avg_temp_max: 平均最高温
            - avg_temp_min: 平均最低温
            - total_days: 总记录天数
    """
    try:
        ym = f"{year}{month:02d}"
        
        with conn.cursor() as cursor:
            # 获取总天数
            cursor.execute("""
            SELECT COUNT(*) FROM weather_daily WHERE ym = %s
            """, (ym,))
            total_days = cursor.fetchone()[0]
            
            if total_days == 0:
                return {
                    'sunny_rate': 0.0,
                    'rainy_rate': 0.0,
                    'cloudy_rate': 0.0,
                    'avg_temp_max': 0.0,
                    'avg_temp_min': 0.0,
                    'total_days': 0
                }
            
            # 统计各种天气类型的天数
            cursor.execute("""
            SELECT 
                SUM(CASE WHEN day_weather LIKE '%%晴%%' THEN 1 ELSE 0 END) as sunny_days,
                SUM(CASE WHEN day_weather LIKE '%%雨%%' OR day_weather LIKE '%%雪%%' THEN 1 ELSE 0 END) as rainy_days,
                SUM(CASE WHEN day_weather LIKE '%%云%%' OR day_weather LIKE '%%阴%%' THEN 1 ELSE 0 END) as cloudy_days,
                AVG(temp_max) as avg_max,
                AVG(temp_min) as avg_min
            FROM weather_daily
            WHERE ym = %s
            """, (ym,))
            
            result = cursor.fetchone()
            sunny_days = result[0] or 0
            rainy_days = result[1] or 0
            cloudy_days = result[2] or 0
            avg_temp_max = result[3] or 0.0
            avg_temp_min = result[4] or 0.0
            
            return {
                'sunny_rate': round((sunny_days / total_days) * 100, 1),
                'rainy_rate': round((rainy_days / total_days) * 100, 1),
                'cloudy_rate': round((cloudy_days / total_days) * 100, 1),
                'avg_temp_max': round(avg_temp_max, 1),
                'avg_temp_min': round(avg_temp_min, 1),
                'total_days': total_days
            }
    except Exception as e:
        print(f"计算月度统计失败: {str(e)}")
        raise


def calculate_detailed_statistics(conn, year, month):
    """
    计算详细的月度统计数据
    
    Args:
        conn: 数据库连接
        year: 年份 (int)
        month: 月份 (int)
    
    Returns:
        dict: 详细统计结果
            - basic: 基础统计（晴天率、雨天率等）
            - temperature: 温度详细统计
            - wind: 风力统计
            - weather_types: 天气类型分布
    """
    try:
        ym = f"{year}{month:02d}"
        
        with conn.cursor() as cursor:
            # 获取总天数
            cursor.execute("SELECT COUNT(*) FROM weather_daily WHERE ym = %s", (ym,))
            total_days = cursor.fetchone()[0]
            
            if total_days == 0:
                return {
                    'basic': {
                        'sunny_rate': 0.0,
                        'rainy_rate': 0.0,
                        'cloudy_rate': 0.0,
                        'total_days': 0
                    },
                    'temperature': {
                        'avg_temp_max': 0.0,
                        'avg_temp_min': 0.0,
                        'avg_temp_diff': 0.0,
                        'max_temp_diff': 0
                    },
                    'wind': {
                        'light_wind_days': 0,
                        'moderate_wind_days': 0,
                        'strong_wind_days': 0
                    },
                    'weather_types': {}
                }
            
            # 基础统计
            cursor.execute("""
            SELECT 
                SUM(CASE WHEN day_weather LIKE '%%晴%%' THEN 1 ELSE 0 END) as sunny_days,
                SUM(CASE WHEN day_weather LIKE '%%雨%%' OR day_weather LIKE '%%雪%%' THEN 1 ELSE 0 END) as rainy_days,
                SUM(CASE WHEN day_weather LIKE '%%云%%' OR day_weather LIKE '%%阴%%' THEN 1 ELSE 0 END) as cloudy_days,
                AVG(temp_max) as avg_max,
                AVG(temp_min) as avg_min,
                AVG(temp_max - temp_min) as avg_diff,
                MAX(temp_max - temp_min) as max_diff
            FROM weather_daily
            WHERE ym = %s
            """, (ym,))
            
            result = cursor.fetchone()
            sunny_days = result[0] or 0
            rainy_days = result[1] or 0
            cloudy_days = result[2] or 0
            avg_temp_max = result[3] or 0.0
            avg_temp_min = result[4] or 0.0
            avg_temp_diff = result[5] or 0.0
            max_temp_diff = result[6] or 0
            
            # 风力统计
            cursor.execute("""
            SELECT 
                SUM(CASE WHEN wind_day LIKE '%%微风%%' OR wind_day = '' THEN 1 ELSE 0 END) as light_wind,
                SUM(CASE WHEN wind_day LIKE '%%[3-4]级%%' OR wind_day LIKE '%%中风%%' THEN 1 ELSE 0 END) as moderate_wind,
                SUM(CASE WHEN wind_day REGEXP '[5-9]级|大风|狂风' THEN 1 ELSE 0 END) as strong_wind
            FROM weather_daily
            WHERE ym = %s
            """, (ym,))
            
            wind_result = cursor.fetchone()
            light_wind_days = wind_result[0] or 0
            moderate_wind_days = wind_result[1] or 0
            strong_wind_days = wind_result[2] or 0
            
            # 天气类型详细分布
            cursor.execute("""
            SELECT day_weather, COUNT(*) as count
            FROM weather_daily
            WHERE ym = %s
            GROUP BY day_weather
            ORDER BY count DESC
            """, (ym,))
            
            weather_types = {}
            for row in cursor.fetchall():
                weather_types[row[0]] = row[1]
            
            return {
                'basic': {
                    'sunny_rate': round((sunny_days / total_days) * 100, 1),
                    'rainy_rate': round((rainy_days / total_days) * 100, 1),
                    'cloudy_rate': round((cloudy_days / total_days) * 100, 1),
                    'total_days': total_days
                },
                'temperature': {
                    'avg_temp_max': round(avg_temp_max, 1),
                    'avg_temp_min': round(avg_temp_min, 1),
                    'avg_temp_diff': round(avg_temp_diff, 1),
                    'max_temp_diff': int(max_temp_diff)
                },
                'wind': {
                    'light_wind_days': light_wind_days,
                    'moderate_wind_days': moderate_wind_days,
                    'strong_wind_days': strong_wind_days
                },
                'weather_types': weather_types
            }
    except Exception as e:
        print(f"计算详细统计失败: {str(e)}")
        raise
