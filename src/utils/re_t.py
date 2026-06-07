import re

def to_json(s):
    # 为 date ， weatherDay ， weatherNight ， minTemp ， maxTemp ，
    #  windDay ， windNight 加上双引号 并 去除数据末尾的 ";"
    def add_quotes(match):
        return f'"{match.group(1)}":'
    s = re.sub(r'(\w+):', add_quotes, s)
    s = s.rstrip(';')
    return s