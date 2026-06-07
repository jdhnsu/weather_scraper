"""
月度统计Tab - 显示天气概率统计、气温极值、穿衣建议分布等详细统计
采用卡片式布局，结合进度条和视觉标识
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QGridLayout, QFrame, QProgressBar,
    QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import db


class MonthlyStatsTab(QWidget):
    """月度统计Tab"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_year = 2024
        self.current_month = 5
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # ── 筛选栏 ──
        filter_bar = QFrame()
        filter_bar.setObjectName("filterBar")
        filter_layout = QHBoxLayout(filter_bar)
        filter_layout.setContentsMargins(16, 12, 16, 12)
        filter_layout.setSpacing(20)

        filter_layout.addWidget(QLabel("  年 份"))
        self.year_combo = QComboBox()
        self.year_combo.addItems([str(y) for y in range(2020, 2031)])
        self.year_combo.setCurrentText("2024")
        self.year_combo.setFixedWidth(100)
        self.year_combo.currentTextChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.year_combo)

        filter_layout.addWidget(QLabel("月 份"))
        self.month_combo = QComboBox()
        self.month_combo.addItems([f"{m}月" for m in range(1, 13)])
        self.month_combo.setCurrentIndex(4)
        self.month_combo.setFixedWidth(90)
        self.month_combo.currentIndexChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.month_combo)

        filter_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.update_time_label = QLabel("")
        self.update_time_label.setObjectName("updateTimeLabel")
        filter_layout.addWidget(self.update_time_label)

        self.analyze_button = QPushButton("确认分析")
        self.analyze_button.setObjectName("primaryButton")
        self.analyze_button.setFixedSize(110, 36)
        self.analyze_button.clicked.connect(self.on_analyze_clicked)
        filter_layout.addWidget(self.analyze_button)

        layout.addWidget(filter_bar)

        # ── 内容网格 ──
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(16)

        # 第一行：三大 KPI 卡片
        self.sunny_kpi  = self._make_kpi_card("晴 天 率",  "sunny")
        self.rainy_kpi  = self._make_kpi_card("雨 天 率",  "rainy")
        self.cloudy_kpi = self._make_kpi_card("多 云 率",  "cloudy")

        self.grid_layout.addWidget(self.sunny_kpi,  0, 0)
        self.grid_layout.addWidget(self.rainy_kpi,  0, 1)
        self.grid_layout.addWidget(self.cloudy_kpi, 0, 2)

        # 第二行：气温 & 风力
        self.temp_card  = self._make_section_card("🌡  气 温 极 值",   "temp")
        self.wind_card  = self._make_section_card("💨  风 力 统 计",   "wind")
        self.grid_layout.addWidget(self.temp_card, 1, 0)
        self.grid_layout.addWidget(self.wind_card, 1, 1)

        # 第三行：温差 + 穿衣建议
        self.diff_card     = self._make_section_card("📊  温 差 分 析",      "temp_diff")
        self.clothing_card = self._make_section_card("👔  穿 衣 建 议 分 布", "clothing")
        self.grid_layout.addWidget(self.diff_card,     2, 0)
        self.grid_layout.addWidget(self.clothing_card, 2, 1)

        # 第四行：天气类型分布（跨全宽）
        self.weather_card = self._make_section_card("🌤  天 气 类 型 分 布", "weather_types")
        self.grid_layout.addWidget(self.weather_card, 3, 0, 1, 2)

        # 让最后一行占满剩余空间
        self.grid_layout.setRowStretch(3, 1)

        layout.addLayout(self.grid_layout)
        self.refresh_stats()

    # ── 卡片构建 ────────────────────────────────────────────

    def _make_kpi_card(self, title, ktype):
        """KPI 卡片：大数字 + 进度条"""
        card = QFrame()
        card.setObjectName("kpiCard")
        card.setMinimumHeight(160)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        v = QVBoxLayout(card)
        v.setContentsMargins(20, 16, 20, 14)
        v.setSpacing(10)

        header = QLabel(title)
        header.setObjectName("kpiHeader")
        v.addWidget(header)

        value_label = QLabel("--%")
        value_label.setObjectName("kpiValue")
        v.addWidget(value_label)

        bar = QProgressBar()
        bar.setObjectName("kpiBar")
        bar.setTextVisible(False)
        bar.setFixedHeight(6)
        v.addWidget(bar)

        # 存储子控件
        card._value_label = value_label
        card._bar = bar
        card._tag = ktype
        return card

    def _make_section_card(self, title, stype):
        """内容分区卡片"""
        card = QFrame()
        card.setObjectName("sectionCard")
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        v = QVBoxLayout(card)
        v.setContentsMargins(20, 16, 20, 16)
        v.setSpacing(12)

        header = QLabel(title)
        header.setObjectName("sectionHeader")
        v.addWidget(header)

        content = QLabel("暂无数据")
        content.setObjectName("sectionContent")
        content.setWordWrap(True)
        content.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        v.addWidget(content)

        card._content = content
        card._tag = stype
        return card

    # ── 事件处理 ────────────────────────────────────────────

    def on_filter_changed(self):
        self.current_year = int(self.year_combo.currentText())
        self.current_month = self.month_combo.currentIndex() + 1
        self.refresh_stats()

    def on_analyze_clicked(self):
        self.current_year = int(self.year_combo.currentText())
        self.current_month = self.month_combo.currentIndex() + 1
        self.refresh_stats()

    # ── 数据刷新 ────────────────────────────────────────────

    def refresh_stats(self):
        try:
            conn = None
            try:
                conn = db.connect_db()
                stats = db.calculate_detailed_statistics(conn, self.current_year, self.current_month)

                if stats['basic']['total_days'] == 0:
                    self._show_empty()
                    return

                self._update_kpis(stats)
                self._update_temp_card(stats)
                self._update_wind_card(stats)
                self._update_diff_card(stats)
                self._update_clothing_card(stats)
                self._update_weather_card(stats)

                now = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
                self.update_time_label.setText(f"刷新于  {now}")

            finally:
                if conn:
                    db.close_db(conn)

        except Exception as e:
            print(f"刷新统计数据失败: {str(e)}")
            self._show_error(str(e))

    # ── 卡片更新 ────────────────────────────────────────────

    def _update_kpis(self, stats):
        basic = stats['basic']
        mapping = {
            self.sunny_kpi:  ("sunny",  basic['sunny_rate']),
            self.rainy_kpi:  ("rainy",  basic['rainy_rate']),
            self.cloudy_kpi: ("cloudy", basic['cloudy_rate']),
        }
        colors = {"sunny": "#FF9800", "rainy": "#2196F3", "cloudy": "#78909C"}
        for card, (tag, val) in mapping.items():
            card._value_label.setText(f"{val}%")
            card._bar.setValue(int(val))
            card._bar.setStyleSheet(
                f"QProgressBar::chunk {{ background-color: {colors[tag]}; border-radius: 3px; }}"
            )

    def _update_temp_card(self, stats):
        temp = stats['temperature']
        basic = stats['basic']
        high, low = temp['avg_temp_max'], temp['avg_temp_min']
        text = (
            f'<div style="line-height: 2.0; padding: 4px 0;">'
            f'<p><span style="font-size:16px;font-weight:bold;color:#e53935;">{high}℃</span>'
            f'  &nbsp;&nbsp;平均最高温</p>'
            f'<p><span style="font-size:16px;font-weight:bold;color:#1e88e5;">{low}℃</span>'
            f'  &nbsp;&nbsp;平均最低温</p>'
            f'<p style="color:#78909c;">共记录 <b>{basic["total_days"]}</b> 天</p>'
            f'</div>'
        )
        self.temp_card._content.setText(text)
        self.temp_card._content.setTextFormat(Qt.RichText)

    def _update_wind_card(self, stats):
        wind = stats['wind']
        text = (
            f'<div style="line-height: 2.0; padding: 4px 0;">'
            f'<p>微风 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
            f'<b style="font-size:15px;">{wind["light_wind_days"]}</b> 天</p>'
            f'<p>中风 3-4级 <b style="font-size:15px;">{wind["moderate_wind_days"]}</b> 天</p>'
            f'<p>大风 ≥5级 &nbsp;<b style="font-size:15px;">{wind["strong_wind_days"]}</b> 天</p>'
            f'</div>'
        )
        self.wind_card._content.setText(text)
        self.wind_card._content.setTextFormat(Qt.RichText)

    def _update_diff_card(self, stats):
        temp = stats['temperature']
        avg_d, max_d = temp['avg_temp_diff'], temp['max_temp_diff']
        text = (
            f'<div style="line-height: 2.2; padding: 4px 0;">'
            f'<p>平均温差 &nbsp;'
            f'<b style="font-size:18px;color:#5c6bc0;">{avg_d}℃</b></p>'
            f'<p>最大温差 &nbsp;'
            f'<b style="font-size:18px;color:#e53935;">{max_d}℃</b></p>'
            f'</div>'
        )
        self.diff_card._content.setText(text)
        self.diff_card._content.setTextFormat(Qt.RichText)

    def _update_clothing_card(self, stats):
        ym = f"{self.current_year}{self.current_month:02d}"
        try:
            conn = None
            try:
                conn = db.connect_db()
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT temp_max, temp_min FROM weather_daily WHERE ym = %s", (ym,)
                    )
                    rows = cursor.fetchall()
                    clothing_count = {}
                    for row in rows:
                        tmax, tmin = row
                        if tmax is not None and tmin is not None:
                            advice = self.generate_clothing_advice(int(tmin), int(tmax))
                            clothing_count[advice] = clothing_count.get(advice, 0) + 1

                    if clothing_count:
                        total = sum(clothing_count.values())
                        lines = ['<div style="line-height: 1.8;">']
                        for adv, cnt in sorted(clothing_count.items(), key=lambda x: x[1], reverse=True):
                            pct = round(cnt / total * 100, 1)
                            lines.append(
                                f'<p>{adv[:12]}  <b style="font-size:14px;">{cnt}天</b>'
                                f'  <span style="color:#9e9e9e;">({pct}%)</span></p>'
                            )
                        lines.append('</div>')
                        self.clothing_card._content.setText('\n'.join(lines))
                        self.clothing_card._content.setTextFormat(Qt.RichText)
                    else:
                        self.clothing_card._content.setText("暂无数据")
            finally:
                if conn:
                    db.close_db(conn)
        except Exception as e:
            self.clothing_card._content.setText(f"加载失败: {str(e)}")

    def _update_weather_card(self, stats):
        weather_types = stats['weather_types']
        if weather_types:
            total = sum(weather_types.values())
            lines = ['<div style="line-height: 1.8;">']
            for w, cnt in sorted(weather_types.items(), key=lambda x: x[1], reverse=True):
                pct = round(cnt / total * 100, 1)
                lines.append(
                    f'<p>{w[:16]}  <b style="font-size:14px;">{cnt}天</b>'
                    f'  <span style="color:#9e9e9e;">({pct}%)</span></p>'
                )
            lines.append('</div>')
            self.weather_card._content.setText('\n'.join(lines))
            self.weather_card._content.setTextFormat(Qt.RichText)
        else:
            self.weather_card._content.setText("暂无数据")

    # ── 状态显示 ────────────────────────────────────────────

    def _show_empty(self):
        msg = "该月份暂无数据，请先爬取数据"
        for card in [self.temp_card, self.wind_card, self.diff_card,
                      self.clothing_card, self.weather_card]:
            card._content.setText(msg)
        for kpi in [self.sunny_kpi, self.rainy_kpi, self.cloudy_kpi]:
            kpi._value_label.setText("--%")
            kpi._bar.setValue(0)
        self.update_time_label.setText("")

    def _show_error(self, err):
        msg = f"加载失败: {err}"
        for card in [self.temp_card, self.wind_card, self.diff_card,
                      self.clothing_card, self.weather_card]:
            card._content.setText(msg)
        for kpi in [self.sunny_kpi, self.rainy_kpi, self.cloudy_kpi]:
            kpi._value_label.setText("--%")
            kpi._bar.setValue(0)

    def generate_clothing_advice(self, temp_min, temp_max):
        avg_temp = (temp_min + temp_max) / 2
        if avg_temp < 0:
            return "羽绒服+加厚毛衣+围巾手套"
        elif avg_temp < 10:
            return "厚外套+毛衣+卫衣"
        elif avg_temp < 18:
            return "夹克/风衣+长袖"
        elif avg_temp < 25:
            return "长袖衬衫/T恤+薄外套"
        elif avg_temp < 30:
            return "短袖+防晒"
        else:
            return "轻薄短袖+遮阳帽"
