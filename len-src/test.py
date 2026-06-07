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
with open("len-src\\weatherData.json", "w", encoding="utf-8") as f:
    f.write(weather_json)

