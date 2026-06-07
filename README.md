# 都江堰年度天气数据爬取与可视化系统

这是我的课程作业项目：基于 Python + PyQt5 的天气数据爬取与可视化工具。  
你可以选择时间范围，一键抓取都江堰天气数据，并在界面中查看数据表、月度统计和运行日志。

## 软件截图

![项目界面截图](https://github.com/user-attachments/assets/5eff277f-7689-40e8-a083-e0bc976116bb)

## 快速开始

### 1) 安装依赖

```bash
pip install -r requirements.txt
```

### 2) 启动项目

```bash
python src/main.py
```

> 说明：运行前请确保本地 MySQL 已可用，并按项目中的数据库配置完成连接信息设置。

## 目录说明

- `src/`：主项目代码（GUI、爬虫逻辑、数据库交互等）
- `len-src/`：原理探索脚本（用于实验和原理验证）
