from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QHBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView


class ReaderPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 地址栏
        self.url_input = QLineEdit( )
        self.url_input.setPlaceholderText("输入网址...")

        # 导航按钮
        self.go_btn = QPushButton("跳转")
        self.toggle_view_btn = QPushButton("切换视图")

        # 浏览器视图
        self.browser = QWebEngineView()
        self.browser.load(QUrl("https://www.google.com"))

        # 按钮布局
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.url_input)
        btn_layout.addWidget(self.go_btn)
        btn_layout.addWidget(self.toggle_view_btn)

        # 返回按钮
        self.back_btn = QPushButton("返回首页")
        self.back_btn.clicked.connect(lambda: self.app.navigate_to(self.app.home_page))

        layout.addLayout(btn_layout)
        layout.addWidget(self.browser)
        layout.addWidget(self.back_btn)
        self.setLayout(layout)

        # 连接按钮事件
        self.go_btn.clicked.connect(self.on_go_clicked)
        self.toggle_view_btn.clicked.connect(self.on_toggle_view)

    def on_go_clicked(self):
        """跳转按钮点击事件"""
        url = self.url_input.text()
        if url:
            if not url.startswith("http"):
                url = "https://" + url
            self.browser.load(url)

    def on_toggle_view(self):
        """切换视图按钮点击事件"""
        # 这里实现视图切换逻辑
        print("切换视图")