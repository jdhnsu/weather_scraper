"""
天气数据表Tab - 显示每日天气数据，支持年份和月份筛选
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox, QScrollArea
)
from PyQt5.QtCore import Qt
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import db


class WeatherTableTab(QWidget):
    """天气数据表Tab"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_year = 2024
        self.selected_months = list(range(1, 13))  # 默认全选
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # 筛选区域
        filter_group = QGroupBox()
        filter_layout = QHBoxLayout(filter_group)
        filter_layout.setSpacing(24)
        
        # 年份筛选
        year_layout = QHBoxLayout()
        year_layout.setSpacing(8)
        year_layout.addWidget(QLabel("年份筛选:"))
        
        self.year_combo = QComboBox()
        self.year_combo.addItems([str(year) for year in range(2020, 2031)])
        self.year_combo.setCurrentText("2024")
        self.year_combo.currentTextChanged.connect(self.on_filter_changed)
        year_layout.addWidget(self.year_combo)
        
        filter_layout.addLayout(year_layout)
        
        # 月份筛选
        month_layout = QHBoxLayout()
        month_layout.setSpacing(8)
        month_layout.addWidget(QLabel("月份筛选:"))
        
        # 全选复选框
        self.select_all_checkbox = QCheckBox("全选")
        self.select_all_checkbox.setChecked(True)
        self.select_all_checkbox.stateChanged.connect(self.on_select_all_changed)
        month_layout.addWidget(self.select_all_checkbox)
        
        # 分隔线
        separator = QLabel("|")
        separator.setStyleSheet("color: #c1c7cf;")
        month_layout.addWidget(separator)
        
        # 12个月份复选框
        self.month_checkboxes = []
        for i in range(1, 13):
            checkbox = QCheckBox(f"{i}月")
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.on_month_checkbox_changed)
            self.month_checkboxes.append(checkbox)
            month_layout.addWidget(checkbox)
        
        month_layout.addStretch()
        filter_layout.addLayout(month_layout)
        
        layout.addWidget(filter_group)
        
        # 表格区域
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "日期", "白天天气", "夜间天气", 
            "最高温(℃)", "最低温(℃)", 
            "白天风力", "夜间风力", "穿衣建议"
        ])
        
        # 设置表格属性 - 优化列宽策略
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 日期
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # 白天天气
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # 夜间天气
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 最高温
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 最低温
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)  # 白天风力
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)  # 夜间风力
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Stretch)  # 穿衣建议
        
        # 设置最小列宽，确保内容不被遮挡
        self.table.setColumnWidth(0, 120)  # 日期
        self.table.setColumnWidth(3, 100)  # 最高温
        self.table.setColumnWidth(4, 100)  # 最低温
        self.table.setColumnWidth(7, 250)  # 穿衣建议（给予更多空间）
        
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # 设置行高，避免文字垂直方向被截断
        self.table.verticalHeader().setDefaultSectionSize(40)
        
        layout.addWidget(self.table)
        
    def on_select_all_changed(self, state):
        """全选复选框状态改变"""
        is_checked = (state == Qt.Checked)
        for checkbox in self.month_checkboxes:
            checkbox.blockSignals(True)
            checkbox.setChecked(is_checked)
            checkbox.blockSignals(False)
        
        if is_checked:
            self.selected_months = list(range(1, 13))
        else:
            self.selected_months = []
        
        self.refresh_data()
    
    def on_month_checkbox_changed(self):
        """月份复选框状态改变"""
        self.selected_months = []
        all_checked = True
        
        for i, checkbox in enumerate(self.month_checkboxes):
            if checkbox.isChecked():
                self.selected_months.append(i + 1)
            else:
                all_checked = False
        
        # 更新全选复选框状态
        self.select_all_checkbox.blockSignals(True)
        self.select_all_checkbox.setChecked(all_checked)
        self.select_all_checkbox.blockSignals(False)
        
        self.refresh_data()
    
    def on_filter_changed(self):
        """筛选条件改变"""
        self.current_year = int(self.year_combo.currentText())
        self.refresh_data()
    
    def refresh_data(self):
        """刷新数据"""
        if not self.selected_months:
            self.table.setRowCount(0)
            return
        
        try:
            conn = db.connect_db()
            try:
                rows = db.query_weather_data_by_filter(conn, self.current_year, self.selected_months)
                
                self.table.setRowCount(len(rows))
                
                for row_idx, row_data in enumerate(rows):
                    date, day_weather, night_weather, temp_max, temp_min, wind_day, wind_night = row_data
                    
                    # 日期
                    self.table.setItem(row_idx, 0, QTableWidgetItem(str(date)))
                    
                    # 白天天气
                    self.table.setItem(row_idx, 1, QTableWidgetItem(day_weather or ""))
                    
                    # 夜间天气
                    self.table.setItem(row_idx, 2, QTableWidgetItem(night_weather or ""))
                    
                    # 最高温 - 修复：使用is not None判断，确保0值能正常显示
                    if temp_max is not None:
                        temp_max_item = QTableWidgetItem(str(int(temp_max)))
                        temp_max_item.setTextAlignment(Qt.AlignCenter)
                        temp_max_item.setForeground(Qt.blue)
                        self.table.setItem(row_idx, 3, temp_max_item)
                    else:
                        self.table.setItem(row_idx, 3, QTableWidgetItem(""))
                    
                    # 最低温 - 修复：使用is not None判断，确保0值能正常显示
                    if temp_min is not None:
                        temp_min_item = QTableWidgetItem(str(int(temp_min)))
                        temp_min_item.setTextAlignment(Qt.AlignCenter)
                        temp_min_item.setForeground(Qt.darkBlue)
                        self.table.setItem(row_idx, 4, temp_min_item)
                    else:
                        self.table.setItem(row_idx, 4, QTableWidgetItem(""))
                    
                    # 白天风力
                    self.table.setItem(row_idx, 5, QTableWidgetItem(wind_day or ""))
                    
                    # 夜间风力
                    self.table.setItem(row_idx, 6, QTableWidgetItem(wind_night or ""))
                    
                    # 穿衣建议（动态生成）- 修复：确保即使温度为0也能生成建议
                    if temp_max is not None and temp_min is not None:
                        advice = self.generate_clothing_advice(int(temp_min), int(temp_max))
                        self.table.setItem(row_idx, 7, QTableWidgetItem(advice))
                    else:
                        self.table.setItem(row_idx, 7, QTableWidgetItem("数据缺失"))
                        
            finally:
                db.close_db(conn)
                
        except Exception as e:
            print(f"刷新数据失败: {str(e)}")
            self.table.setRowCount(0)
    
    def generate_clothing_advice(self, temp_min, temp_max):
        """根据温度生成穿衣建议"""
        avg_temp = (temp_min + temp_max) / 2
        
        if avg_temp < 0:
            return "羽绒服 + 加厚毛衣 + 围巾手套，注意防寒"
        elif avg_temp < 10:
            return "厚外套 + 毛衣，建议加件卫衣"
        elif avg_temp < 18:
            return "夹克 / 风衣 + 长袖，薄毛衣可选"
        elif avg_temp < 25:
            return "长袖衬衫 / T恤 + 薄外套"
        elif avg_temp < 30:
            return "短袖 + 防晒，可带薄衫"
        else:
            return "轻薄短袖 + 遮阳帽，多补水"
