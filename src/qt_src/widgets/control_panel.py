"""
控制面板组件 - 包含时间选择器、爬取按钮和进度条
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QProgressBar, QFrame
)


class ControlPanel(QWidget):
    """控制面板组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(16)

        # 用 QFrame 替代 QGroupBox，避免标题跨 DPI 裁剪
        panel = QFrame()
        panel.setObjectName("controlPanel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(20, 20, 20, 20)
        panel_layout.setSpacing(16)

        title = QLabel("  控制面板")
        title.setObjectName("panelTitle")
        title.setMinimumHeight(28)
        panel_layout.addWidget(title)

        # 时间选择器区域
        time_layout = QHBoxLayout()
        time_layout.setSpacing(32)

        # 起始时间
        start_time_layout = QHBoxLayout()
        start_time_layout.setSpacing(10)
        start_label = QLabel("起始时间:")
        start_label.setMinimumWidth(80)
        start_time_layout.addWidget(start_label)

        self.start_year_combo = QComboBox()
        self.start_year_combo.setMinimumWidth(80)
        self.start_year_combo.addItems([str(year) for year in range(2020, 2031)])
        self.start_year_combo.setCurrentText("2024")
        start_time_layout.addWidget(self.start_year_combo)

        self.start_month_combo = QComboBox()
        self.start_month_combo.setMinimumWidth(80)
        self.start_month_combo.addItems([f"{m}月" for m in range(1, 13)])
        self.start_month_combo.setCurrentIndex(4)
        start_time_layout.addWidget(self.start_month_combo)

        time_layout.addLayout(start_time_layout)

        # 结束时间
        end_time_layout = QHBoxLayout()
        end_time_layout.setSpacing(10)
        end_label = QLabel("结束时间:")
        end_label.setMinimumWidth(80)
        end_time_layout.addWidget(end_label)

        self.end_year_combo = QComboBox()
        self.end_year_combo.setMinimumWidth(80)
        self.end_year_combo.addItems([str(year) for year in range(2020, 2031)])
        self.end_year_combo.setCurrentText("2024")
        end_time_layout.addWidget(self.end_year_combo)

        self.end_month_combo = QComboBox()
        self.end_month_combo.setMinimumWidth(80)
        self.end_month_combo.addItems([f"{m}月" for m in range(1, 13)])
        self.end_month_combo.setCurrentIndex(4)
        end_time_layout.addWidget(self.end_month_combo)

        time_layout.addLayout(end_time_layout)
        time_layout.addStretch()

        panel_layout.addLayout(time_layout)

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(16)

        self.scrape_button = QPushButton("一键爬取")
        self.scrape_button.setMinimumWidth(120)
        self.scrape_button.setMinimumHeight(40)
        self.scrape_button.setObjectName("primaryButton")
        button_layout.addWidget(self.scrape_button)

        button_layout.addStretch()
        panel_layout.addLayout(button_layout)

        layout.addWidget(panel)

        # 进度条区域
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(8)

        progress_header = QHBoxLayout()
        self.progress_label = QLabel("爬取进度")
        self.progress_label.setStyleSheet("color: #41474e; font-weight: bold;")
        progress_header.addWidget(self.progress_label)

        self.progress_value_label = QLabel("0/0 (0%)")
        self.progress_value_label.setObjectName("dataLabel")
        self.progress_value_label.setStyleSheet("color: #235a84; font-weight: bold;")
        progress_header.addWidget(self.progress_value_label)

        progress_layout.addLayout(progress_header)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(12)
        progress_layout.addWidget(self.progress_bar)

        layout.addLayout(progress_layout)

    def get_start_time(self):
        year = int(self.start_year_combo.currentText())
        month = self.start_month_combo.currentIndex() + 1
        return year, month

    def get_end_time(self):
        year = int(self.end_year_combo.currentText())
        month = self.end_month_combo.currentIndex() + 1
        return year, month

    def update_progress(self, current, total):
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
            self.progress_value_label.setText(f"{current}/{total} ({percentage}%)")
        else:
            self.progress_bar.setValue(0)
            self.progress_value_label.setText("0/0 (0%)")

    def reset_progress(self):
        self.progress_bar.setValue(0)
        self.progress_value_label.setText("0/0 (0%)")

    def set_scrape_button_enabled(self, enabled):
        self.scrape_button.setEnabled(enabled)
