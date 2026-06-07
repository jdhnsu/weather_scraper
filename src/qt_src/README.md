# WeatherScrape Pro - PyQt5 图形界面

## 项目简介

基于PyQt5的都江堰年度天气数据爬取与可视化系统，提供友好的图形界面用于天气数据的爬取、存储和分析。

## 功能特性

- ✅ **一键爬取**：选择时间范围，自动爬取天气数据并入库
- ✅ **实时进度**：通过信号槽机制显示爬取进度
- ✅ **数据表格**：支持年份和月份筛选，动态生成穿衣建议
- ✅ **月度统计**：实时计算晴天率、雨天率、平均温度等指标
- ✅ **运行日志**：聚合显示爬虫、数据库、统计等多来源日志

## 环境要求

- Python 3.7+
- PyQt5
- pymysql
- requests

## 安装依赖

```bash
pip install PyQt5 pymysql requests
```

## 运行程序

```bash
cd src
python main.py
```

## 项目结构

```
src/
├── qt_src/                      # PyQt5 GUI模块
│   ├── main_window.py           # 主窗口
│   ├── scraper_thread.py        # 爬虫工作线程
│   ├── widgets/                 # UI组件
│   │   ├── control_panel.py     # 控制面板
│   │   ├── weather_table_tab.py # 天气数据表Tab
│   │   ├── monthly_stats_tab.py # 月度统计Tab
│   │   └── log_viewer_tab.py    # 运行日志Tab
│   └── resources/               # 资源文件
│       └── style.qss            # Qt样式表
├── WeatherScraper.py            # 爬虫核心逻辑
├── db.py                        # 数据库操作
├── utils/                       # 工具函数
└── main.py                      # 程序入口
```

## 使用说明

### 1. 爬取数据

1. 在控制面板设置起始时间和结束时间
2. 点击"一键爬取"按钮
3. 观察进度条和运行日志
4. 爬取完成后数据自动入库

### 2. 查看天气数据

1. 切换到"天气数据表"Tab
2. 选择年份和月份（支持多选）
3. 表格自动刷新显示数据
4. 穿衣建议根据温度自动生成

### 3. 查看月度统计

1. 切换到"月度统计"Tab
2. 选择年份和月份
3. 点击"确认分析"按钮
4. 查看概率统计和气温极值

### 4. 查看运行日志

1. 切换到"运行日志"Tab
2. 查看所有操作的日志记录
3. 不同级别日志用颜色区分（绿=成功，黄=警告，红=错误，蓝=信息）

## 数据库配置

默认数据库配置在 `db.py` 中：

```python
host='localhost'
port=3306
user='root'
password='test123456'
database='test_db'
```

如需修改，请编辑 `db.py` 文件中的 `connect_db()` 函数。

## 技术亮点

- **多线程架构**：使用QThread避免UI阻塞
- **信号槽机制**：实现组件间松耦合通信
- **实时进度更新**：爬取过程中动态显示进度
- **动态穿衣建议**：基于温度区间算法生成
- **响应式筛选**：筛选器改变立即刷新数据
- **统一样式系统**：基于DESIGN.md的Corporate Blue主题

## 注意事项

1. 确保MySQL服务已启动且数据库`test_db`存在
2. 首次运行会自动创建`weather_daily`表
3. 爬取过程中请勿关闭窗口，可最小化到后台
4. 网络异常时会自动重试3次

## 开发说明

### 添加新功能

1. 在 `widgets/` 目录下创建新的组件类
2. 在 `main_window.py` 中实例化并添加到TabWidget
3. 如需后台任务，在 `scraper_thread.py` 中添加相应逻辑

### 修改样式

编辑 `resources/style.qss` 文件，遵循Qt样式表语法。

## License

MIT License
