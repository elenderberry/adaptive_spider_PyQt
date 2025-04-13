from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                             QListWidgetItem, QPushButton, QLabel, QMessageBox,
                             QSpacerItem, QSizePolicy, QLineEdit, QComboBox,
                             QScrollArea, QFrame, QCheckBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPixmap, QIcon
import requests
from urllib.parse import urljoin
import os


class ArticleListPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.base_url = "http://127.0.0.1:8000/"
        self.current_page = 1
        self.per_page = 10
        self.selected_categories = []
        self.articles = []
        self.init_ui()

    def showEvent(self, event):
        """页面显示时加载数据"""
        super().showEvent(event)
        if not hasattr(self, 'initialized'):
            self.load_articles()
            self.initialized = True

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

        # 标题
        title_label = QLabel("文章列表")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))

        top_bar.addWidget(home_btn)
        top_bar.addWidget(title_label)
        top_bar.addStretch()
        main_layout.addLayout(top_bar)

        # 分类筛选区域
        category_layout = QHBoxLayout()
        category_layout.setAlignment(Qt.AlignLeft)

        category_label = QLabel("分类筛选:")
        category_label.setFont(QFont("Arial", 12))

        # 分类映射 (英文: 中文)
        self.category_map = {
            "Foreign Affairs": "外交",
            "Finance": "金融",
            "Military": "军事",
            "Technology": "科技",
            "Domestic": "国内",
            "Culture": "文化",
            "Entertainment": "娱乐",
            "Sports": "体育"
        }

        # 分类选择区域 (使用滚动区域)
        category_scroll = QScrollArea()
        category_scroll.setWidgetResizable(True)
        category_scroll.setFixedHeight(50)
        category_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
        """)

        category_widget = QWidget()
        category_btn_layout = QHBoxLayout(category_widget)
        category_btn_layout.setSpacing(10)

        # 添加全选按钮
        select_all = QCheckBox("全选")
        select_all.setChecked(True)
        select_all.stateChanged.connect(self.toggle_select_all)
        category_btn_layout.addWidget(select_all)

        # 添加分类复选框
        self.category_checks = {}
        for eng_name, chi_name in self.category_map.items():
            cb = QCheckBox(chi_name)
            cb.setChecked(True)
            cb.toggled.connect(self.on_category_toggled)
            cb.setProperty("eng_name", eng_name)
            category_btn_layout.addWidget(cb)
            self.category_checks[eng_name] = cb

        category_btn_layout.addStretch()
        category_scroll.setWidget(category_widget)

        category_layout.addWidget(category_label)
        category_layout.addWidget(category_scroll)
        main_layout.addLayout(category_layout)

        # 搜索栏
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索文章...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 14px;
                min-width: 300px;
            }
        """)
        search_btn = QPushButton("搜索")
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
        """)
        search_btn.clicked.connect(self.on_search)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        main_layout.addLayout(search_layout)

        # 文章列表
        self.article_list = QListWidget()
        self.article_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
                min-width: 600px;
                min-height: 400px;
            }
            QListWidget::item {
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
        self.article_list.itemDoubleClicked.connect(self.on_article_selected)
        main_layout.addWidget(self.article_list)

        # 分页控件
        page_layout = QHBoxLayout()
        page_layout.setAlignment(Qt.AlignCenter)

        self.prev_btn = QPushButton("上一页")
        self.prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f1f1;
                color: #333;
                padding: 8px 15px;
                border: 1px solid #ddd;
                border-radius: 5px;
                min-width: 80px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e1e1e1;
            }
            QPushButton:disabled {
                color: #aaa;
            }
        """)
        self.prev_btn.clicked.connect(self.prev_page)

        self.page_label = QLabel(f"第 {self.current_page} 页")
        self.page_label.setAlignment(Qt.AlignCenter)

        self.next_btn = QPushButton("下一页")
        self.next_btn.setStyleSheet(self.prev_btn.styleSheet())
        self.next_btn.clicked.connect(self.next_page)

        page_layout.addWidget(self.prev_btn)
        page_layout.addWidget(self.page_label)
        page_layout.addWidget(self.next_btn)
        main_layout.addLayout(page_layout)

        self.setLayout(main_layout)

    def toggle_select_all(self, state):
        """全选/取消全选"""
        for cb in self.category_checks.values():
            cb.setChecked(state == Qt.Checked)
        self.load_articles()

    def on_category_toggled(self, checked):
        """分类选择变化时重新加载数据"""
        self.load_articles()

    def get_selected_categories(self):
        """获取选中的分类(英文名)"""
        return [eng_name for eng_name, cb in self.category_checks.items() if cb.isChecked()]

    def load_articles(self):
        """加载文章数据"""
        if not self.app.user_info:
            QMessageBox.warning(self, "错误", "用户未登录")
            self.app.navigate_to(self.app.login_page)
            return

        try:
            selected_categories = self.get_selected_categories()

            params = {
                "user_id": self.app.user_info["userid"],
                "page": self.current_page,
                "per_page": self.per_page
            }

            if selected_categories:
                params["category_names"] = selected_categories

            search_text = self.search_input.text().strip()
            if search_text:
                params["search"] = search_text

            response = requests.get(
                urljoin(self.base_url, "get_articles_by_categories/"),
                params=params,
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                self.display_articles(data.get("articles_by_category", {}))
            else:
                QMessageBox.warning(self, "错误", f"获取文章失败: {response.text}")

        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "网络错误", f"无法连接到服务器: {str(e)}")

    def display_articles(self, articles_by_category):
        """显示文章列表"""
        self.article_list.clear()
        self.articles = []

        # 将分类文章合并为一个列表
        for category, articles in articles_by_category.items():
            for article in articles:
                article["category"] = category  # 添加分类信息
                self.articles.append(article)

        # 显示前10条
        for article in self.articles[:10]:
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 70))

            # 创建自定义widget
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(10, 5, 10, 5)

            # 标题和分类
            top_layout = QHBoxLayout()

            # 分类标签
            category_label = QLabel(self.category_map.get(article["category"], article["category"]))
            category_label.setFont(QFont("Arial", 10, QFont.Bold))
            category_label.setStyleSheet("""
                QLabel {
                    color: white;
                    background-color: #4285f4;
                    padding: 2px 8px;
                    border-radius: 10px;
                }
            """)

            # 文章标题
            title_label = QLabel(article["title"])
            title_label.setFont(QFont("Arial", 12))
            title_label.setStyleSheet("color: #333;")

            top_layout.addWidget(category_label)
            top_layout.addWidget(title_label, stretch=1)
            layout.addLayout(top_layout)

            # 来源和时间
            meta_label = QLabel()
            meta_parts = []
            if article.get("source_url"):
                meta_parts.append(f"来源: {article['source_url']}")
            if article.get("publish_time"):
                meta_parts.append(f"时间: {article['publish_time']}")

            meta_label.setText(" | ".join(meta_parts) if meta_parts else "无来源信息")
            meta_label.setFont(QFont("Arial", 9))
            meta_label.setStyleSheet("color: #666;")
            layout.addWidget(meta_label)

            widget.setStyleSheet("""
                QWidget {
                    background-color: white;
                    border-radius: 5px;
                }
            """)

            item.setData(Qt.UserRole, article["article_id"])  # 保存article_id
            item.setData(Qt.UserRole + 1, article)  # 保存完整文章数据

            self.article_list.addItem(item)
            self.article_list.setItemWidget(item, widget)

            self.update_pagination(len(self.articles))

    def update_pagination(self, total):
        """更新分页控件状态"""
        self.prev_btn.setDisabled(self.current_page <= 1)
        self.next_btn.setDisabled(self.current_page * self.per_page >= total)
        self.page_label.setText(f"第 {self.current_page} 页 (共 {total} 条)")

    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_articles()

    def next_page(self):
        """下一页"""
        self.current_page += 1
        self.load_articles()

    def on_search(self):
        """搜索文章"""
        self.current_page = 1
        self.load_articles()

    def on_article_selected(self, item):
        """文章项被选中"""
        article_data = item.data(Qt.UserRole + 1)  # 获取保存的完整文章数据

        # 保存当前文章数据到app，以便详情页使用
        self.app.current_article = article_data
        self.app.navigate_to(self.app.article_detail_page)