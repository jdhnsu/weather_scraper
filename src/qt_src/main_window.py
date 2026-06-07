"""
主窗口 - WeatherScrape Pro 的主界面
"""
import sys
import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QLabel, QMessageBox, QStatusBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qt_src.widgets.control_panel import ControlPanel
from qt_src.widgets.weather_table_tab import WeatherTableTab
from qt_src.widgets.monthly_stats_tab import MonthlyStatsTab
from qt_src.widgets.log_viewer_tab import LogViewerTab
from qt_src.scraper_thread import ScraperThread


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.scraper_thread = None
        self.init_ui()
        self.load_style_sheet()
        
    def init_ui(self):
        """初始化UI"""
        # 设置窗口属性
        self.setWindowTitle("WeatherScrape Pro - 都江堰气象站")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)
        
        # 顶部标题栏
        header_layout = QHBoxLayout()
        
        title_label = QLabel("都江堰年度天气数据爬取与可视化系统")
        title_label.setWordWrap(True)
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #235a84;
            padding: 16px 0px;
        """)
        title_label.setMinimumHeight(64)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.adjustSize()
        
        header_layout.addWidget(title_label)
        main_layout.addLayout(header_layout)
        
        # 控制面板
        self.control_panel = ControlPanel()
        main_layout.addWidget(self.control_panel)
        
        # 连接按钮信号
        self.control_panel.scrape_button.clicked.connect(self.on_scrape_clicked)
        
        # Tab Widget
        self.tab_widget = QTabWidget()
        
        # 天气数据表Tab
        self.weather_table_tab = WeatherTableTab()
        self.tab_widget.addTab(self.weather_table_tab, "天气数据表")
        
        # 月度统计Tab
        self.monthly_stats_tab = MonthlyStatsTab()
        self.tab_widget.addTab(self.monthly_stats_tab, "月度统计")
        
        # 运行日志Tab
        self.log_viewer_tab = LogViewerTab()
        self.tab_widget.addTab(self.log_viewer_tab, "运行日志")
        
        main_layout.addWidget(self.tab_widget)
        
        # 状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("就绪", 3000)
    
    def load_style_sheet(self):
        """加载样式表"""
        style_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'resources', 'style.qss'
        )
        
        try:
            with open(style_path, 'r', encoding='utf-8') as f:
                style_sheet = f.read()
            self.setStyleSheet(style_sheet)
        except Exception as e:
            print(f"加载样式表失败: {str(e)}")
    
    def on_scrape_clicked(self):
        """点击一键爬取按钮"""
        # 获取时间范围
        start_year, start_month = self.control_panel.get_start_time()
        end_year, end_month = self.control_panel.get_end_time()
        
        # 验证时间范围
        if start_year > end_year or (start_year == end_year and start_month > end_month):
            QMessageBox.warning(self, "警告", "起始时间不能晚于结束时间！")
            return
        
        # 禁用按钮
        self.control_panel.set_scrape_button_enabled(False)
        self.control_panel.reset_progress()
        
        # 添加日志
        self.log_viewer_tab.append_log(
            f"开始爬取任务: {start_year}年{start_month}月 至 {end_year}年{end_month}月",
            "info"
        )
        
        # 创建并启动爬虫线程
        self.scraper_thread = ScraperThread(start_year, end_year, start_month, end_month)
        self.scraper_thread.progress_updated.connect(self.on_progress_updated)
        self.scraper_thread.scraping_finished.connect(self.on_scraping_finished)
        self.scraper_thread.scraping_error.connect(self.on_scraping_error)
        self.scraper_thread.log_message.connect(self.on_log_message)
        self.scraper_thread.start()
    
    def on_progress_updated(self, current, total):
        """进度更新槽函数"""
        self.control_panel.update_progress(current, total)
    
    def on_scraping_finished(self, json_data):
        """爬取完成槽函数"""
        self.control_panel.set_scrape_button_enabled(True)
        self.log_viewer_tab.append_log("爬取任务完成，数据已入库", "success")
        self.statusBar.showMessage("爬取完成", 3000)
        
        # 刷新天气数据表
        self.weather_table_tab.refresh_data()
        
        # 显示成功消息
        QMessageBox.information(self, "成功", "数据爬取并入库成功！")
    
    def on_scraping_error(self, error_msg):
        """爬取错误槽函数"""
        self.control_panel.set_scrape_button_enabled(True)
        self.log_viewer_tab.append_log(f"爬取失败: {error_msg}", "error")
        self.statusBar.showMessage("爬取失败", 3000)
        
        # 显示错误消息
        QMessageBox.critical(self, "错误", f"爬取任务失败:\n{error_msg}")
    
    def on_log_message(self, message):
        """日志消息槽函数"""
        # 解析日志级别
        if "[SUCCESS]" in message:
            level = "success"
            message = message.replace("[SUCCESS] ", "")
        elif "[WARNING]" in message or "[WARN]" in message:
            level = "warning"
            message = message.replace("[WARNING] ", "").replace("[WARN] ", "")
        elif "[ERROR]" in message:
            level = "error"
            message = message.replace("[ERROR] ", "")
        else:
            level = "info"
            message = message.replace("[INFO] ", "")
        
        self.log_viewer_tab.append_log(message, level)
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 如果爬虫线程正在运行，等待其完成
        if self.scraper_thread and self.scraper_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "确认退出",
                "爬取任务正在进行中，确定要退出吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.scraper_thread.terminate()
                self.scraper_thread.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
