import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QPushButton, QLabel, QFrame, QSizePolicy)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize
import requests
from urllib.parse import urljoin
from utils.path_tool import resource_path

class LoginPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.base_url = "http://127.0.0.1:8000/api/"  # 根据你的后端地址修改
        self.init_ui()

    def init_ui(self):
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        # 创建中央容器
        container = QFrame()
        container.setFixedWidth(600)
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 30px;
            }
        """)

        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignCenter)
        container_layout.setSpacing(20)

        # 添加logo
        logo_path = resource_path("imgs/logo.png")
        if os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignCenter)
            container_layout.addWidget(logo_label)

        # 用户名输入框
        username_layout = QHBoxLayout()
        username_icon = QLabel()
        username_icon.setPixmap(QPixmap(resource_path("imgs/user.png")).scaled(24, 24))
        username_layout.addWidget(username_icon)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名/账号")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 16px;
            }
        """)
        username_layout.addWidget(self.username_input)
        container_layout.addLayout(username_layout)

        # 密码输入框
        password_layout = QHBoxLayout()
        password_icon = QLabel()
        password_icon.setPixmap(QPixmap(resource_path("imgs/password.png")).scaled(24, 24))
        password_layout.addWidget(password_icon)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 16px;
            }
        """)
        password_layout.addWidget(self.password_input)
        container_layout.addLayout(password_layout)

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        # 登录按钮
        self.login_btn = QPushButton("登录")
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
        """)
        self.login_btn.clicked.connect(self.on_login)
        button_layout.addWidget(self.login_btn)

        # 注册按钮
        self.register_btn = QPushButton("注册")
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
        """)
        self.register_btn.clicked.connect(self.on_register)
        button_layout.addWidget(self.register_btn)

        container_layout.addLayout(button_layout)

        # 将容器添加到主布局
        main_layout.addWidget(container)
        self.setLayout(main_layout)

        # 设置窗口背景
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
        """)

    def on_login(self):
        """处理登录逻辑"""
        useraccount = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not useraccount or not password:
            self.show_message("请输入用户名和密码")
            return

        try:
            response = requests.post(
                urljoin(self.base_url, "login/"),
                json={"useraccount": useraccount, "userpwd": password},
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                # 保存用户信息到应用全局
                self.app.user_info = {
                    "userid": data["userid"],
                    "useraccount": data["useraccount"],
                    "username": data["username"]
                }
                # 跳转到首页
                print('success')
                self.app.navigate_to(self.app.home_page)
            else:
                self.show_message(response.json().get("message", "登录失败"))

        except requests.exceptions.RequestException as e:
            self.show_message(f"网络错误: {str(e)}")

    def on_register(self):
        """处理注册逻辑"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.show_message("请输入用户名和密码")
            return

        try:
            response = requests.post(
                urljoin(self.base_url, "register/"),
                json={"username": username, "userpwd": password},
                timeout=5
            )

            if response.status_code == 201:
                data = response.json()
                self.show_message(f"注册成功! 您的账号是: {data['useraccount']}")
            else:
                self.show_message(response.json().get("message", "注册失败"))

        except requests.exceptions.RequestException as e:
            self.show_message(f"网络错误: {str(e)}")

    def show_message(self, message):
        """显示提示消息"""
        # 这里可以替换为你喜欢的消息显示方式
        print(message)  # 暂时打印到控制台
        # 实际应用中可以使用QMessageBox或自定义的提示组件