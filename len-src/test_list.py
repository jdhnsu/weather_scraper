import requests
import time

url = "https://www.tianqihoubao.com/lishi/dujiangyan/month/202601.html"


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

def fetch_with_retry(url, headers, max_retries=3, timeout=30):
    """带重试机制的请求函数"""
    for attempt in range(1, max_retries + 1):
        try:
            print(f"尝试第 {attempt} 次请求...")
            resp = requests.get(url, headers=headers, timeout=timeout)
            resp.encoding = "utf-8"
            print(f"✅ 请求成功 (状态码: {resp.status_code})")
            return resp
        except requests.exceptions.Timeout:
            print(f"⚠️  第 {attempt} 次请求超时，等待 2 秒后重试...")
            if attempt < max_retries:
                time.sleep(2)
        except requests.exceptions.ConnectionError as e:
            print(f"❌ 第 {attempt} 次请求连接失败: {e}")
            if attempt < max_retries:
                time.sleep(2)
    
    raise Exception(f"经过 {max_retries} 次重试后仍然失败")

# 获取第一个月的数据
resp = fetch_with_retry(url, headers)

# 解析 HTML，提取天气数据
idx = resp.text.find("const weatherData")
print(f"weatherData 位置: {idx}")

start = resp.text.find("[", idx)
end = resp.text.find("];", start)

weather_json = resp.text[start:end+2]

import re

def add_quotes(match):
    return f'"{match.group(1)}":'
pattern = r'(\w+):'
weather_json = re.sub(pattern, add_quotes, weather_json)
weather_json = weather_json.rstrip(";")

print(f"✅ 1月数据解析完成")

# 获取第二个月的数据
url2 = "https://www.tianqihoubao.com/lishi/dujiangyan/month/202602.html"
resp2 = fetch_with_retry(url2, headers)

idx2 = resp2.text.find("const weatherData")
start2 = resp2.text.find("[", idx2)
end2 = resp2.text.find("];", start2)
weather_json2 = resp2.text[start2:end2+2]
weather_json2 = re.sub(pattern, add_quotes, weather_json2)
weather_json2 = weather_json2.rstrip(";")

print(f"✅ 2月数据解析完成")

# 合并两个 JSON 数据
weather_json_combined = weather_json[:-1] + "," + weather_json2[1:]
print(f"✅ 数据合并完成")

import pymysql

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
    print("---\n连接成功\n---\n")
    
    with conn.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        print(f"MySQL 版本: {cursor.fetchone()[0]}")
        
    import json
    from datetime import datetime

    rows = json.loads(weather_json_combined)
    print(f"解析到 {len(rows)} 条数据")

# 创建表结构
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS weather_daily (
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
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
    conn.commit()
# 入库数据
    now = datetime.now()
    params = []
    for item in rows:
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

except pymysql.err.OperationalError as e:
    print(f"❌ 数据库连接失败: {e}")
    print("\n可能的原因:")
    print("1. 密码错误 - 请检查并修改 password 参数")
    print("2. 用户 'root'@'localhost' 没有访问权限")
    print("3. MySQL 服务未启动")
    print("4. 数据库 'test_db' 不存在")
    
finally:
    if conn:
        conn.close()
        print("🔒 连接已关闭")