# 都江堰天气数据爬取与可视化系统

基于 **Python + PyQt5 + MySQL** 的课程项目：按时间范围爬取都江堰历史天气数据，并在图形界面中查看数据表、月度统计和日志。

## 快速开始

### 1) 安装依赖

```bash
pip install -r requirements.txt
```

### 2) MySQL 基础配置（先建库）

项目默认连接配置在 `src/db.py`：

- host: `localhost`
- port: `3306`
- user: `root`
- password: `test123456`
- database: `test_db`

请先在 MySQL 中创建数据库：

```sql
CREATE DATABASE test_db DEFAULT CHARACTER SET utf8mb4;
```

如你的本地账号或库名不同，请修改 `connect_db()` 中对应字段。

### 3) 启动程序

```bash
python src/main.py
```

> 首次运行会自动创建 `weather_daily` 表。

## 简单架构说明

- **GUI 层（`src/qt_src/`）**：负责界面展示、参数输入、进度与日志展示。
- **爬虫层（`src/WeatherScraper.py`）**：按年月抓取网页并解析天气 JSON 数据。
- **数据层（`src/db.py`）**：负责 MySQL 连接、建表、入库与查询统计。
- **工具层（`src/utils/`）**：提供 JSON 组装与文本处理辅助函数。

数据流：`用户操作 -> GUI 线程调度 -> 爬虫抓取/解析 -> MySQL 存储 -> GUI 查询展示`。

## 目录说明

- `src/`：主项目代码
- `len-src/`：实验与原理验证脚本
