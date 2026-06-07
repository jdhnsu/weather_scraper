import random
import time

import requests

import utils as utils

# 生成 URL https://www.tianqihoubao.com/lishi/dujiangyan/month/{year}{month}.html
def url_(year, month):
    return f"https://www.tianqihoubao.com/lishi/dujiangyan/month/{year}{month:02d}.html"


# 模拟浏览器请求，获取页面 HTML
def get_html(url, retries=3):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.tianqihoubao.com/",
        # 模拟浏览器身份，避免被反爬拦截
    }

    last_error = None
    for attempt in range(retries):
        if attempt > 0:
            sleep_seconds = min(8, 1.5 * (2 ** (attempt - 1))) + random.uniform(0.5, 1.5)
            time.sleep(sleep_seconds)

        try:
            resp = requests.get(url, headers=headers, timeout=(5, 15))
            if resp.status_code in {403, 429}:
                raise requests.HTTPError(f"HTTP {resp.status_code}")

            resp.raise_for_status()
            resp.encoding = "utf-8"
            return resp.text
        except requests.RequestException as exc:
            last_error = exc

    raise RuntimeError(f"获取页面失败: {url}") from last_error

# 解析 HTML，提取天气数据
def extract_weather_data(html):
    # 1. 找到 const weatherData 位置
    idx = html.find("const weatherData")
    if idx == -1:
        raise ValueError("未找到 weatherData 数据")
    
    start = html.find("[", idx)
    end = html.find("];", start)
    if start == -1 or end == -1:
        raise ValueError("未找到 weatherData 数组")
    
    weather_json = html[start:end+2]
    return weather_json

# 解析数据 转为 标准的 JSON 格式 (双引号，键名加引号)
def parse_weather_json(weather_json):
    # 为 date ， weatherDay ， weatherNight ， minTemp ， maxTemp ，
    #  windDay ， windNight 加上双引号
    weather_json = utils.re_t.to_json(weather_json)
    return weather_json

def main(start_year, end_year, start_month, end_month):
    weather_json_sources = []
    for year in range(start_year, end_year + 1):
        m_start = start_month if year == start_year else 1
        m_end = end_month if year == end_year else 12
        for month in range(m_start, m_end + 1):
            url = url_(year, month)
            print(f"正在爬取 {year}年{month}月 的天气数据...")
            html = get_html(url)
            weather_json = extract_weather_data(html)
            weather_json = parse_weather_json(weather_json)
            weather_json_sources.append(weather_json)

            if month != m_end or year != end_year:
                time.sleep(random.uniform(1.5, 3.5))

    combined_json = utils.json_t.weather_json_combined(weather_json_sources)
    with open("weatherData_combined.json", "w", encoding="utf-8") as f:
        f.write(combined_json)