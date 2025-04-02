from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton


class ArticleDetailPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 文章详情内容
        self.content_label = QLabel("这里是文章详情页面，显示文章内容")

        # 返回按钮
        self.back_btn = QPushButton("返回文章列表")
        self.back_btn.clicked.connect(lambda: self.app.navigate_to(self.app.article_list_page))

        layout.addWidget(self.content_label)
        layout.addWidget(self.back_btn)
        self.setLayout(layout)