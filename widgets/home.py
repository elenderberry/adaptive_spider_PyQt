from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class HomePage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.init_ui()

    def init_ui(self):
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(0)

        # 第一行按钮布局
        first_row = QHBoxLayout()
        first_row.setSpacing(20)
        first_row.setAlignment(Qt.AlignCenter)

        # 第二行按钮布局 (只包含一个按钮)
        second_row = QHBoxLayout()
        second_row.setAlignment(Qt.AlignCenter)

        # 创建三个按钮
        self.task_btn = self.create_button("任务查看", "#4285f4")
        self.article_btn = self.create_button("文章查看", "white")
        self.reader_btn = self.create_button("阅读器", "#4285f4")

        # 添加到布局
        first_row.addWidget(self.task_btn)
        first_row.addWidget(self.article_btn)

        # 第二行添加一个空白间隔使按钮居中
        second_row.addSpacerItem(QSpacerItem(320, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))
        second_row.addWidget(self.reader_btn)
        second_row.addSpacerItem(QSpacerItem(320, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))

        # 将行布局添加到主布局
        main_layout.addLayout(first_row)
        main_layout.addLayout(second_row)

        # 连接点击事件
        self.task_btn.clicked.connect(lambda: self.app.navigate_to(self.app.task_list_page))
        self.article_btn.clicked.connect(lambda: self.app.navigate_to(self.app.article_list_page))
        self.reader_btn.clicked.connect(lambda: self.app.navigate_to(self.app.reader_page))

        self.setLayout(main_layout)

        # 设置窗口背景
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
        """)

    def create_button(self, text, bg_color):
        """创建统一风格的按钮"""
        btn = QPushButton(text)
        btn.setFixedSize(300, 300)

        # 根据背景色设置文字颜色
        text_color = "white" if bg_color != "white" else "#4285f4"

        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: 2px solid #4285f4;
                border-radius: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {'#3367d6' if bg_color != 'white' else '#f0f0f0'};
            }}
        """)

        # 设置字体加粗和大小
        font = QFont()
        font.setBold(True)
        font.setPointSize(18)
        btn.setFont(font)

        return btn