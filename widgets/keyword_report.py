# keyword_report.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QScrollArea, QFrame, QMessageBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont
import os

from utils.path_tool import resource_path

class KeywordReportPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.init_ui()

    def showEvent(self, event):
        """页面显示时加载数据"""
        super().showEvent(event)
        if hasattr(self.app, 'current_report'):
            self.display_report(self.app.current_report)

    def init_ui(self):
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 顶部导航栏
        top_bar = QHBoxLayout()

        # 返回首页按钮
        home_btn = QPushButton()
        home_icon_path = resource_path("imgs/home.png")
        if os.path.exists(home_icon_path):
            home_btn.setIcon(QIcon(home_icon_path))
            home_btn.setIconSize(QSize(32, 32))
        home_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border-radius: 4px;
            }
        """)
        home_btn.clicked.connect(lambda: self.app.navigate_to(self.app.home_page))
        home_btn.setToolTip("返回首页")

        # 返回任务详情按钮
        back_btn = QPushButton()
        back_icon_path = resource_path("imgs/back.png")
        if os.path.exists(back_icon_path):
            back_btn.setIcon(QIcon(back_icon_path))
            back_btn.setIconSize(QSize(32, 32))
        back_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                padding: 5px;
                margin-left: 10px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border-radius: 4px;
            }
        """)
        back_btn.clicked.connect(lambda: self.app.navigate_to(self.app.keyword_task_detail_page))
        back_btn.setToolTip("返回任务详情")

        top_bar.addWidget(home_btn)
        top_bar.addWidget(back_btn)
        top_bar.addStretch()
        main_layout.addLayout(top_bar)

        # 简报内容区域
        self.report_scroll = QScrollArea()
        self.report_scroll.setWidgetResizable(True)
        self.report_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
        """)

        # 简报内容容器
        self.report_container = QWidget()
        self.report_layout = QVBoxLayout(self.report_container)
        self.report_layout.setContentsMargins(20, 20, 20, 20)
        self.report_layout.setSpacing(15)

        # 简报标题
        self.title_label = QLabel()
        self.title_label.setWordWrap(True)
        self.title_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.title_label.setStyleSheet("color: #333;")
        self.report_layout.addWidget(self.title_label)

        # 关键词
        self.keyword_label = QLabel()
        self.keyword_label.setWordWrap(True)
        self.keyword_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.keyword_label.setStyleSheet("color: #4285f4;")
        self.report_layout.addWidget(self.keyword_label)

        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #eee;")
        self.report_layout.addWidget(separator)

        # 简报内容
        self.content_label = QLabel()
        self.content_label.setWordWrap(True)
        self.content_label.setFont(QFont("Arial", 12))
        self.content_label.setStyleSheet("color: #444;")
        self.report_layout.addWidget(self.content_label)

        # 添加拉伸项使内容顶部对齐
        self.report_layout.addStretch()

        self.report_scroll.setWidget(self.report_container)
        main_layout.addWidget(self.report_scroll)

        self.setLayout(main_layout)

    def display_report(self, report):
        """显示简报内容"""
        self.title_label.setText(report.get("title", "任务简报"))
        self.keyword_label.setText(f"关键词: {report.get('keyword', '无')}")
        self.content_label.setText(report.get("content", "无简报内容"))