from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QScrollArea, QFrame, QMessageBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont
import requests
from urllib.parse import urljoin
import os


class TaskDetailPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.base_url = "http://127.0.0.1:8000/"
        self.current_article_index = 0
        self.articles = []
        self.init_ui()

    def showEvent(self, event):
        """页面显示时加载数据"""
        super().showEvent(event)
        if self.app.current_task_id:
            self.load_articles()

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

        # 返回任务列表按钮
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
        back_btn.clicked.connect(lambda: self.app.navigate_to(self.app.task_list_page))
        back_btn.setToolTip("返回任务列表")

        top_bar.addWidget(home_btn)
        top_bar.addWidget(back_btn)
        top_bar.addStretch()
        main_layout.addLayout(top_bar)

        # 导航按钮栏
        nav_buttons = QHBoxLayout()
        nav_buttons.setAlignment(Qt.AlignCenter)
        nav_buttons.setSpacing(20)

        # 上一篇按钮
        self.prev_btn = QPushButton("上一篇")
        self.prev_btn.setFixedSize(60, 30)
        self.prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.prev_btn.clicked.connect(self.show_prev_article)

        # 删除按钮
        self.delete_btn = QPushButton("删除")
        self.delete_btn.setFixedSize(60, 30)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ea4335;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #d33426;
            }
        """)
        self.delete_btn.clicked.connect(self.delete_current_article)

        # 下一篇按钮
        self.next_btn = QPushButton("下一篇")
        self.next_btn.setFixedSize(60, 30)
        self.next_btn.setStyleSheet(self.prev_btn.styleSheet())
        self.next_btn.clicked.connect(self.show_next_article)

        nav_buttons.addWidget(self.prev_btn)
        nav_buttons.addWidget(self.delete_btn)
        nav_buttons.addWidget(self.next_btn)
        main_layout.addLayout(nav_buttons)

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
        self.title_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.title_label.setStyleSheet("color: #333;")
        self.article_layout.addWidget(self.title_label)

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

        # 一键分类按钮
        classify_btn = QPushButton("一键分类简写")
        classify_btn.setFixedHeight(40)
        classify_btn.setStyleSheet("""
            QPushButton {
                background-color: #34a853;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2d9248;
            }
        """)
        classify_btn.clicked.connect(self.process_articles)
        main_layout.addWidget(classify_btn)

        self.setLayout(main_layout)
        self.update_nav_buttons()

    def load_articles(self):
        """加载任务下的文章"""
        if not self.app.user_info or not self.app.current_task_id:
            QMessageBox.warning(self, "错误", "无法获取用户或任务信息")
            return

        try:
            params = {
                "user_id": self.app.user_info["userid"],
                "task_id": self.app.current_task_id
            }

            response = requests.get(
                urljoin(self.base_url, "get_articles/"),
                params=params,
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                self.articles = data.get("articles", [])
                self.current_article_index = 0
                if self.articles:
                    self.display_current_article()
                else:
                    self.clear_article_display()
                    QMessageBox.information(self, "提示", "该任务下没有文章")
            else:
                QMessageBox.warning(self, "错误", f"获取文章失败: {response.text}")

        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "网络错误", f"无法连接到服务器: {str(e)}")

    def display_current_article(self):
        """显示当前文章"""
        if not self.articles or self.current_article_index >= len(self.articles):
            return

        article = self.articles[self.current_article_index]

        # 显示标题
        self.title_label.setText(article.get("title", "无标题"))

        # 显示元信息
        meta_parts = []
        if article.get("source_url"):
            meta_parts.append(f"来源: {article['source_url']}")
        if article.get("author"):
            meta_parts.append(f"作者: {article['author']}")
        if article.get("publish_time"):
            meta_parts.append(f"发布时间: {article['publish_time']}")

        self.meta_label.setText(" | ".join(meta_parts) if meta_parts else "无来源信息")

        # 显示内容
        self.content_label.setText(article.get("content", "无内容"))

        self.update_nav_buttons()

    def clear_article_display(self):
        """清空文章显示"""
        self.title_label.setText("")
        self.meta_label.setText("")
        self.content_label.setText("")
        self.update_nav_buttons()

    def update_nav_buttons(self):
        """更新导航按钮状态"""
        has_articles = bool(self.articles)
        self.prev_btn.setDisabled(self.current_article_index <= 0 or not has_articles)
        self.next_btn.setDisabled(self.current_article_index >= len(self.articles) - 1 or not has_articles)
        self.delete_btn.setDisabled(not has_articles)

    def show_prev_article(self):
        """显示上一篇文章"""
        if self.current_article_index > 0:
            self.current_article_index -= 1
            self.display_current_article()

    def show_next_article(self):
        """显示下一篇文章"""
        if self.current_article_index < len(self.articles) - 1:
            self.current_article_index += 1
            self.display_current_article()

    def delete_current_article(self):
        """删除当前文章"""
        if not self.articles or self.current_article_index >= len(self.articles):
            return

        article_id = self.articles[self.current_article_index]["article_id"]

        try:
            response = requests.delete(
                urljoin(self.base_url, "delete_articles/"),
                json={
                    "article_ids": [article_id],
                    "user_id": self.app.user_info["userid"]
                },
                timeout=5
            )

            if response.status_code == 200:
                QMessageBox.information(self, "成功", response.json().get("message", "文章删除成功"))
                # 重新加载文章列表
                self.load_articles()
            else:
                QMessageBox.warning(self, "错误", response.json().get("error", "删除文章失败"))

        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "网络错误", f"无法连接到服务器: {str(e)}")

    def process_articles(self):
        """一键分类处理"""
        if not self.app.user_info or not self.app.current_task_id:
            QMessageBox.warning(self, "错误", "无法获取用户或任务信息")
            return

        try:
            response = requests.post(
                urljoin(self.base_url, "api/process-articles/"),
                json={
                    "user_id": self.app.user_info["userid"],
                    "task_id": self.app.current_task_id
                },
                timeout=30  # 处理可能需要更长时间
            )

            if response.status_code == 200:
                result = response.json()
                if "error" in result:
                    QMessageBox.warning(self, "处理失败", result["error"])
                else:
                    QMessageBox.information(self, "成功", "文章分类处理完成")
            else:
                QMessageBox.warning(self, "错误", f"处理失败: {response.text}")

        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "网络错误", f"无法连接到服务器: {str(e)}")