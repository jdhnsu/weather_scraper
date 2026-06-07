"""
爬虫工作线程 - 在后台执行爬取任务，避免阻塞UI
"""
import sys
import os
from PyQt5.QtCore import QThread, pyqtSignal

# 添加父目录到路径以导入src模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import WeatherScraper
import db


class ScraperThread(QThread):
    """爬虫工作线程"""
    
    # 信号定义
    progress_updated = pyqtSignal(int, int)  # (当前月份, 总月份数)
    scraping_finished = pyqtSignal(str)      # JSON数据
    scraping_error = pyqtSignal(str)         # 错误信息
    log_message = pyqtSignal(str)            # 日志消息
    
    def __init__(self, start_year, end_year, start_month, end_month):
        super().__init__()
        self.start_year = start_year
        self.end_year = end_year
        self.start_month = start_month
        self.end_month = end_month
        
    def run(self):
        """执行爬取任务"""
        try:
            self.log_message.emit(f"[INFO] 开始爬取 {self.start_year}年{self.start_month}月 至 {self.end_year}年{self.end_month}月 的天气数据")
            
            # 计算总月份数用于进度显示
            total_months = 0
            for year in range(self.start_year, self.end_year + 1):
                m_start = self.start_month if year == self.start_year else 1
                m_end = self.end_month if year == self.end_year else 12
                total_months += (m_end - m_start + 1)
            
            current_month = 0
            weather_json_sources = []
            
            for year in range(self.start_year, self.end_year + 1):
                m_start = self.start_month if year == self.start_year else 1
                m_end = self.end_month if year == self.end_year else 12
                
                for month in range(m_start, m_end + 1):
                    current_month += 1
                    self.log_message.emit(f"[INFO] 正在爬取 {year}年{month}月 的数据... ({current_month}/{total_months})")
                    
                    try:
                        url = WeatherScraper.url_(year, month)
                        html = WeatherScraper.get_html(url)
                        weather_json = WeatherScraper.extract_weather_data(html)
                        weather_json = WeatherScraper.parse_weather_json(weather_json)
                        weather_json_sources.append(weather_json)
                        
                        self.log_message.emit(f"[SUCCESS] {year}年{month}月 数据爬取成功")
                        self.progress_updated.emit(current_month, total_months)
                        
                    except Exception as e:
                        self.log_message.emit(f"[ERROR] {year}年{month}月 数据爬取失败: {str(e)}")
                        raise
                    
                    # 如果不是最后一个月，添加延迟
                    if month != m_end or year != self.end_year:
                        import time
                        import random
                        time.sleep(random.uniform(1.5, 3.5))
            
            # 合并数据
            self.log_message.emit("[INFO] 正在合并所有月份的数据...")
            combined_json = WeatherScraper.utils.json_t.weather_json_combined(weather_json_sources)
            
            # 写入数据库
            self.log_message.emit("[INFO] 正在将数据写入数据库...")
            conn = None
            try:
                conn = db.connect_db()
                db.create_table(conn)
                db.insert_weather_data(conn, combined_json)
                self.log_message.emit("[SUCCESS] 数据已成功入库")
            except Exception as db_error:
                self.log_message.emit(f"[ERROR] 数据库操作失败: {str(db_error)}")
                raise
            finally:
                if conn:
                    db.close_db(conn)
            
            self.log_message.emit("[SUCCESS] 爬取任务完成！")
            self.scraping_finished.emit(combined_json)
            
        except Exception as e:
            error_msg = f"爬取任务失败: {str(e)}"
            self.log_message.emit(f"[ERROR] {error_msg}")
            self.scraping_error.emit(error_msg)
