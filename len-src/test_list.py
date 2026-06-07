import requests

url = "https://www.tianqihoubao.com/lishi/dujiangyan/month/202601.html"


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    # 模拟浏览器身份，避免被反爬拦截
}

resp = requests.get(url, headers=headers, timeout=10)
# resp            → Response 对象
# resp.status_code → 200 表示成功，404 没找到，500 服务器炸了
# resp.text        → 页面 HTML 字符串
# resp.encoding    → 编码（设置为 'utf-8' 避免中文乱码）

resp.encoding = "utf-8"
# print(resp.text) # 输出页面 HTML 内容

# 解析 HTML，提取天气数据
# 1. 找到 const weatherData 位置
idx = resp.text.find("const weatherData")
print(f"weatherData 位置: {idx}")


start = resp.text.find("[", idx)
end = resp.text.find("];", start)

weather_json = resp.text[start:end+2]
# print(weather_json)

# with open("len-src\\weatherData.json", "w", encoding="utf-8") as f:
#     f.write(weather_json)

 
# 解析数据 转为 标准的 JSON 格式 (双引号，键名加引号)

import re
# 为 date ， weatherDay ， weatherNight ， minTemp ， maxTemp ， windDay ， windNight 加上双引号
def add_quotes(match):
    return f'"{match.group(1)}":'
pattern = r'(\w+):'
weather_json = re.sub(pattern, add_quotes, weather_json)
# 去除数据末尾的 ";"
weather_json = weather_json.rstrip(";")

print(weather_json)

import time
time.sleep(1)

url2 = "https://www.tianqihoubao.com/lishi/dujiangyan/month/202602.html"
resp2 = requests.get(url2, headers=headers, timeout=10)
resp2.encoding = "utf-8"
idx2 = resp2.text.find("const weatherData")
print(f"weatherData 位置: {idx2}")
start2 = resp2.text.find("[", idx2)
end2 = resp2.text.find("];", start2)
weather_json2 = resp2.text[start2:end2+2]
weather_json2 = re.sub(pattern, add_quotes, weather_json2)
weather_json2 = weather_json2.rstrip(";")
print(weather_json2)

# 和并 两个 JSON 数据
weather_json_combined = weather_json[:-1] + "," + weather_json2[1:]
print(weather_json_combined)
# with open("len-src\\weatherData_combined.json", "w", encoding="utf-8") as f:
#     f.write(weather_json_combined)

import pymysql

conn = None
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
        
    import json
    from datetime import datetime

    # ─── 1. 字符串 → Python 列表 ───
    rows = json.loads(weather_json_combined)  # list[dict], 已含两个月的 59 条数据
    print(f"解析到 {len(rows)} 条数据")

    # ─── 2. 建表（只执行一次） ───
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

    # ─── 3. 转换 + 批量插入 ───
    now = datetime.now()
    params = []
    for item in rows:
        # 日期: "2026年01月01日" → "2026-01-01"
        d = item['date']
        date_str = f"{d[:4]}-{d[5:7]}-{d[8:10]}"    # 切片比正则快
        params.append((
            date_str,
            date_str.replace("-", "")[:6],            # ym: "202601"
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