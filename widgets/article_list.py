from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                             QListWidgetItem, QPushButton, QLabel, QMessageBox,
                             QSpacerItem, QSizePolicy, QLineEdit, QComboBox,
                             QScrollArea, QFrame, QCheckBox, QGroupBox,
                             QCompleter, QStyledItemDelegate, QGridLayout)
from PyQt5.QtCore import Qt, QSize, QStringListModel
from PyQt5.QtGui import QFont, QColor, QPixmap, QIcon
import requests
from urllib.parse import urljoin
import os

from utils.path_tool import resource_path


class ArticleListPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.base_url = "http://127.0.0.1:8000/"
        self.current_page = 1
        self.per_page = 10
        self.selected_categories = []
        self.articles = []
        self.sort_by = "updated_at"  # 默认按更新时间排序
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

        # 标题
        title_label = QLabel("文章列表")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))

        top_bar.addWidget(home_btn)
        top_bar.addWidget(title_label)
        top_bar.addStretch()
        main_layout.addLayout(top_bar)

        # 筛选控制区域
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(15)

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

        # 分类选择 (复选框组)
        category_group = QGroupBox("分类")
        category_group.setFont(QFont("Arial", 10))
        category_layout = QGridLayout()  # 使用 QGridLayout 实现多列布局

        self.category_checks = {}  # 保存所有分类复选框
        row = 0
        col = 0
        for eng, chi in self.category_map.items():
            check = QCheckBox(chi)
            check.setChecked(True)  # 默认全选
            check.category = eng  # 保存英文分类名
            self.category_checks[eng] = check
            category_layout.addWidget(check, row, col)
            col += 1
            if col == 4:  # 每 3 个复选框换一行
                col = 0
                row += 1

        # 全选/取消全选按钮
        select_all_btn = QPushButton("全选/取消全选")
        select_all_btn.setFont(QFont("Arial", 10))
        select_all_btn.setStyleSheet("""
            QPushButton {
                padding: 5px 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #f5f5f5;
            }
            QPushButton:hover {
                background-color: #e5e5e5;
            }
        """)
        select_all_btn.clicked.connect(self.toggle_all_categories)
        category_layout.addWidget(select_all_btn, row, 0, 1, 3)  # 按钮跨 3 列

        category_group.setLayout(category_layout)
        filter_layout.addWidget(category_group)

        # 排序方式选择
        sort_group = QHBoxLayout()
        sort_label = QLabel("排序:")
        sort_label.setFont(QFont("Arial", 10))

        self.sort_combo = QComboBox()
        self.sort_combo.addItem("更新时间", "updated_at")
        self.sort_combo.addItem("评分", "score")
        # 排序方向
        self.sort_order_combo = QComboBox()
        self.sort_order_combo.addItem("降序（从高到低）", "desc")
        self.sort_order_combo.addItem("升序（从低到高）", "asc")
        self.sort_order_combo.setFont(QFont("Arial", 10))
        self.sort_order_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 5px;
                min-width: 140px;
            }
        """)
        sort_group.addWidget(self.sort_order_combo)
        self.sort_combo.setCurrentIndex(0)
        self.sort_combo.setFont(QFont("Arial", 10))
        self.sort_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 5px;
                min-width: 120px;
            }
        """)

        sort_group.addWidget(sort_label)
        sort_group.addWidget(self.sort_combo)
        filter_layout.addLayout(sort_group)

        # 筛选按钮
        filter_btn = QPushButton("筛选")
        filter_btn.setFont(QFont("Arial", 10))
        filter_btn.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                padding: 5px 15px;
                border: none;
                border-radius: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
        """)
        filter_btn.clicked.connect(self.apply_filters)
        filter_layout.addWidget(filter_btn)

        main_layout.addLayout(filter_layout)

        # 搜索栏
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索文章标题...")
        self.search_input.setFont(QFont("Arial", 10))
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 5px;
                min-width: 300px;
            }
        """)
        search_btn = QPushButton("搜索")
        search_btn.setFont(QFont("Arial", 10))
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
                min-width: 80px;
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
        self.prev_btn.setFont(QFont("Arial", 10))
        self.prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f1f1;
                color: #333;
                padding: 5px 15px;
                border: 1px solid #ddd;
                border-radius: 5px;
                min-width: 80px;
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
        self.page_label.setFont(QFont("Arial", 10))
        self.page_label.setAlignment(Qt.AlignCenter)

        self.next_btn = QPushButton("下一页")
        self.next_btn.setFont(QFont("Arial", 10))
        self.next_btn.setStyleSheet(self.prev_btn.styleSheet())
        self.next_btn.clicked.connect(self.next_page)

        page_layout.addWidget(self.prev_btn)
        page_layout.addWidget(self.page_label)
        page_layout.addWidget(self.next_btn)
        main_layout.addLayout(page_layout)

        self.setLayout(main_layout)

    def toggle_all_categories(self):
        """全选/取消全选所有分类"""
        all_checked = all(check.isChecked() for check in self.category_checks.values())
        for check in self.category_checks.values():
            check.setChecked(not all_checked)

    def get_selected_categories(self):
        """获取选中的分类(英文名)"""
        return [eng for eng, check in self.category_checks.items() if check.isChecked()]

    def apply_filters(self):
        """应用筛选条件"""
        self.current_page = 1  # 重置为第一页
        self.sort_by = self.sort_combo.currentData()
        self.load_articles()  # 重新加载文章
        # 若选择评分，自动设为降序
        if self.sort_by == "score":
            self.sort_order_combo.setCurrentIndex(0)  # 0 = "desc"
        self.load_articles()
    def load_articles(self):
        """加载文章数据"""
        if not self.app.user_info:
            QMessageBox.warning(self, "错误", "用户未登录")
            self.app.navigate_to(self.app.login_page)
            return

        try:
            selected_categories = self.get_selected_categories()
            if not selected_categories:  # 如果没有选中任何分类
                QMessageBox.information(self, "提示", "请至少选择一个分类")
                return

            params = {
                "user_id": self.app.user_info["userid"],
                "category_names": selected_categories,
                "page": self.current_page,
                "per_page": self.per_page,
                "sort_by": self.sort_by,
                "sort_order": self.sort_order_combo.currentData()
            }

            search_text = self.search_input.text().strip()
            if search_text:
                params["search"] = search_text

            response = requests.get(
                urljoin(self.base_url, "get_filtered_articles/"),
                params=params,
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                self.display_articles(
                    data.get("articles_by_category", {}),
                    data.get("total_count", 0)
                )
            else:
                QMessageBox.warning(self, "错误", f"获取文章失败: {response.text}")

        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "网络错误", f"无法连接到服务器: {str(e)}")

    def display_articles(self, articles_by_category, total_count):
        """显示文章列表"""
        self.article_list.clear()
        self.articles = []

        for articles in articles_by_category.values():
            for article in articles:
                self.articles.append(article)

        # 显示当前页的文章
        for article in self.articles:
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 90))  # 增加高度以显示更多信息

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

            # 评分显示
            if "score" in article and article["score"] is not None:
                score_layout = QHBoxLayout()
                score_label = QLabel("评分:")
                score_label.setFont(QFont("Arial", 9))

                score_value = QLabel(str(article["score"]))
                score_value.setFont(QFont("Arial", 9, QFont.Bold))
                score_value.setStyleSheet("color: #FFA500;")

                score_layout.addWidget(score_label)
                score_layout.addWidget(score_value)
                score_layout.addStretch()
                layout.addLayout(score_layout)

            # 来源和时间
            meta_layout = QHBoxLayout()

            # 更新时间
            if article.get("updated_at"):
                update_label = QLabel(f"更新: {article['updated_at']}")
                update_label.setFont(QFont("Arial", 9))
                update_label.setStyleSheet("color: #666;")
                meta_layout.addWidget(update_label)

            # 来源
            if article.get("source_url"):
                source_label = QLabel(f"来源: {article['source_url']}")
                source_label.setFont(QFont("Arial", 9))
                source_label.setStyleSheet("color: #666;")
                meta_layout.addWidget(source_label)

            meta_layout.addStretch()
            layout.addLayout(meta_layout)

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

        self.update_pagination(total_count)

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
        self.app.current_article = article_data
        self.app.navigate_to(self.app.article_detail_page)

    def reload_articles(self):
        """每次进入页面都加载"""
        self.current_page = 1
        self.load_articles()