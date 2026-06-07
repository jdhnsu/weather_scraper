"""
运行日志Tab - 显示爬虫、数据库和统计的日志信息
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt5.QtCore import Qt
from datetime import datetime


class LogViewerTab(QWidget):
    """运行日志Tab"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(0)
        
        # 日志文本框
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            background-color: #1e1e1e;
            color: #d4d4d4;
            border: 1px solid #c1c7cf;
            border-radius: 6px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 13px;
            padding: 12px;
        """)
        
        layout.addWidget(self.log_text)
        
        # 添加初始日志
        self.append_log("[INFO] 系统已启动，等待操作...", "info")
    
    def append_log(self, message, level="info"):
        """
        追加日志消息
        
        Args:
            message: 日志消息内容
            level: 日志级别 (info, success, warning, error)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 根据级别设置颜色
        if level == "success":
            color = "#4caf50"  # 绿色
        elif level == "warning":
            color = "#ff9800"  # 橙色
        elif level == "error":
            color = "#f44336"  # 红色
        else:
            color = "#2196f3"  # 蓝色 (info)
        
        # 格式化日志
        log_entry = f'<span style="color: #757575;">[{timestamp}]</span> <span style="color: {color};">{message}</span><br>'
        
        # 追加到文本框
        self.log_text.append(log_entry)
        
        # 自动滚动到底部
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_logs(self):
        """清空日志"""
        self.log_text.clear()
