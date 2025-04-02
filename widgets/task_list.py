import os

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                             QListWidgetItem, QPushButton, QLabel, QMessageBox,
                             QSpacerItem, QSizePolicy, QLineEdit)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QIcon
import requests
from urllib.parse import urljoin


class TaskListPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.base_url = "http://127.0.0.1:8000/api/"
        self.current_page = 1
        self.per_page = 10
        self.init_ui()
        self.load_tasks()

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
        title_label = QLabel("任务列表")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))

        top_bar.addWidget(home_btn)
        top_bar.addWidget(title_label)
        top_bar.addStretch()  # 将标题推到中间

        main_layout.addLayout(top_bar)

        # 搜索栏
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索任务...")
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

        # 任务列表
        self.task_list = QListWidget()
        self.task_list.setStyleSheet("""
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
        self.task_list.itemDoubleClicked.connect(self.on_task_selected)
        main_layout.addWidget(self.task_list)

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

    def load_tasks(self):
        """加载任务数据"""
        if not self.app.user_info:
            QMessageBox.warning(self, "错误", "用户未登录")
            self.app.navigate_to(self.app.login_page)
            return

        try:
            user_id = self.app.user_info["userid"]
            search = self.search_input.text().strip()

            params = {
                "page": self.current_page,
                "per_page": self.per_page
            }
            if search:
                params["search"] = search

            response = requests.get(
                urljoin(self.base_url, f"tasks/{user_id}/"),
                params=params,
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                self.display_tasks(data["tasks"])
                self.update_pagination(data["total"])
            else:
                QMessageBox.warning(self, "错误", f"获取任务失败: {response.text}")

        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "网络错误", f"无法连接到服务器: {str(e)}")

    def display_tasks(self, tasks):
        """显示任务列表"""
        self.task_list.clear()

        for task in tasks[:9]:  # 只显示前5个任务
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 90))  # 设置行高为90

            # 根据状态设置背景色
            status = task["status"]
            bg_color = {
                "完成": "#e6f7e6",  # 浅绿
                "失败": "#ffebeb",  # 浅红
                "执行中": "#fff8e6",  # 浅黄
                "排队中": "#e6f3ff"  # 浅蓝
            }.get(status, "#ffffff")  # 默认白色

            # 创建自定义widget
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(15, 10, 15, 10)
            layout.setSpacing(8)

            # 任务ID和状态
            top_layout = QHBoxLayout()
            id_label = QLabel(f"任务ID: {task['task_id']}")
            id_label.setFont(QFont("Arial", 12, QFont.Bold))

            status_label = QLabel(status)
            status_label.setFont(QFont("Arial", 12))
            status_color = {
                "完成": "#2e7d32",
                "失败": "#c62828",
                "执行中": "#f9a825",
                "排队中": "#1565c0"
            }.get(status, "#000000")
            status_label.setStyleSheet(f"color: {status_color};")

            top_layout.addWidget(id_label)
            top_layout.addStretch()
            top_layout.addWidget(status_label)
            layout.addLayout(top_layout)

            # 创建时间
            time_label = QLabel(f"创建时间: {task['created_at']}")
            time_label.setFont(QFont("Arial", 10))
            time_label.setStyleSheet("color: #666;")
            layout.addWidget(time_label)

            widget.setStyleSheet(f"""
                QWidget {{
                    background-color: {bg_color};
                    border-radius: 5px;
                }}
            """)

            item.setData(Qt.UserRole, task["task_id"])  # 保存task_id

            self.task_list.addItem(item)
            self.task_list.setItemWidget(item, widget)

    def update_pagination(self, total):
        """更新分页控件状态"""
        self.prev_btn.setDisabled(self.current_page <= 1)
        self.next_btn.setDisabled(self.current_page * self.per_page >= total)
        self.page_label.setText(f"第 {self.current_page} 页 (共 {total} 条)")

    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_tasks()

    def next_page(self):
        """下一页"""
        self.current_page += 1
        self.load_tasks()

    def on_search(self):
        """搜索任务"""
        self.current_page = 1
        self.load_tasks()

    def on_task_selected(self, item):
        """任务项被选中"""
        task_id = item.data(Qt.UserRole)
        status = ""

        # 获取任务状态
        for i in range(self.task_list.count()):
            if self.task_list.item(i) == item:
                widget = self.task_list.itemWidget(item)
                if widget:
                    status_label = widget.findChild(QLabel, "", Qt.FindDirectChildrenOnly)
                    if status_label:
                        status = status_label.text()
                break
        print(status)
        # 根据状态处理
        if status == "完成":
            # 保存当前task_id到app，以便详情页使用
            self.app.current_task_id = task_id
            self.app.navigate_to(self.app.task_detail_page)
        else:
            message = {
                "执行中": "任务正在进行中，请等待完成",
                "排队中": "任务在队列中，请等待执行",
                "失败": "任务执行失败，无数据可用"
            }.get(status, "未知状态")

            QMessageBox.information(
                self,
                "提示",
                f"任务 {task_id}\n状态: {status}\n{message}"
            )