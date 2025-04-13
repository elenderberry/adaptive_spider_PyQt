from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QScrollArea, QFrame, QMessageBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap
import requests
from urllib.parse import urljoin
import os


class ArticleDetailPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.base_url = "http://127.0.0.1:8000/"
        self.init_ui()

    def showEvent(self, event):
        """页面显示时加载数据"""
        super().showEvent(event)
        if hasattr(self.app, 'current_article'):
            self.display_article(self.app.current_article)

    def init_ui(self):
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 顶部导航栏
        top_bar = QHBoxLayout()

        # 返回首页按钮
        home_btn = QPushButton()
        home_icon_path = os.path.join("imgs", "home.png")
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

        # 返回文章列表按钮
        back_btn = QPushButton()
        back_icon_path = os.path.join("imgs", "back.png")
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
        back_btn.clicked.connect(lambda: self.app.navigate_to(self.app.article_list_page))
        back_btn.setToolTip("返回文章列表")

        top_bar.addWidget(home_btn)
        top_bar.addWidget(back_btn)
        top_bar.addStretch()
        main_layout.addLayout(top_bar)

        # 文章内容区域
        self.article_scroll = QScrollArea()
        self.article_scroll.setWidgetResizable(True)
        self.article_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
        """)

        # 文章内容容器
        self.article_container = QWidget()
        self.article_layout = QVBoxLayout(self.article_container)
        self.article_layout.setContentsMargins(20, 20, 20, 20)
        self.article_layout.setSpacing(15)

        # 文章标题
        self.title_label = QLabel()
        self.title_label.setWordWrap(True)
        self.title_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.title_label.setStyleSheet("color: #333;")
        self.article_layout.addWidget(self.title_label)

        # 分类标签
        self.category_label = QLabel()
        self.category_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.category_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: #4285f4;
                padding: 2px 8px;
                border-radius: 10px;
                max-width: 100px;
            }
        """)
        self.article_layout.addWidget(self.category_label)

        # 来源和作者信息
        self.meta_label = QLabel()
        self.meta_label.setWordWrap(True)
        self.meta_label.setFont(QFont("Arial", 10))
        self.meta_label.setStyleSheet("color: #666;")
        self.article_layout.addWidget(self.meta_label)

        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #eee;")
        self.article_layout.addWidget(separator)

        # 文章内容
        self.content_label = QLabel()
        self.content_label.setWordWrap(True)
        self.content_label.setFont(QFont("Arial", 12))
        self.content_label.setStyleSheet("color: #444;")
        self.article_layout.addWidget(self.content_label)

        # 添加拉伸项使内容顶部对齐
        self.article_layout.addStretch()

        self.article_scroll.setWidget(self.article_container)
        main_layout.addWidget(self.article_scroll)

        # 删除按钮
        delete_btn = QPushButton("删除文章")
        delete_btn.setFixedHeight(40)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ea4335;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d33426;
            }
        """)
        delete_btn.clicked.connect(self.delete_article)
        main_layout.addWidget(delete_btn)

        self.setLayout(main_layout)

    def display_article(self, article):
        """显示文章详情"""
        # 显示标题
        self.title_label.setText(article.get("title", "无标题"))

        # 显示分类
        category_map = {
            "Foreign Affairs": "外交",
            "Finance": "金融",
            "Military": "军事",
            "Technology": "科技",
            "Domestic": "国内",
            "Culture": "文化",
            "Entertainment": "娱乐",
            "Sports": "体育"
        }
        category = category_map.get(article.get("category", ""), article.get("category", "未知"))
        self.category_label.setText(category)

        # 显示元信息
        meta_parts = []
        if article.get("source_url"):
            meta_parts.append(f"来源: {article['source_url']}")
        if article.get("author"):
            meta_parts.append(f"作者: {article['author']}")
        if article.get("publish_time"):
            meta_parts.append(f"发布时间: {article['publish_time']}")

        self.meta_label.setText(" | ".join(meta_parts) if meta_parts else "无来源信息")

        # 显示内容 (使用简写后的内容)
        self.content_label.setText(article.get("content_summary", article.get("content", "无内容")))

    def delete_article(self):
        """删除当前文章"""
        if not hasattr(self.app, 'current_article'):
            QMessageBox.warning(self, "错误", "没有可删除的文章")
            return

        article_id = self.app.current_article.get("article_id")
        if not article_id:
            QMessageBox.warning(self, "错误", "无法获取文章ID")
            return

        try:
            response = requests.delete(
                urljoin(self.base_url, "delete_category_articles/"),
                json={
                    "article_ids": [article_id],
                    "user_id": self.app.user_info["userid"]
                },
                timeout=5
            )

            if response.status_code == 200:
                QMessageBox.information(self, "成功", response.json().get("message", "文章删除成功"))
                # 返回文章列表
                self.app.navigate_to(self.app.article_list_page)
            else:
                QMessageBox.warning(self, "错误", response.json().get("error", "删除文章失败"))

        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "网络错误", f"无法连接到服务器: {str(e)}")