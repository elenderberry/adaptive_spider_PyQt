from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout, QComboBox, QLineEdit


class ArticleListPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 搜索和分类区域
        search_layout = QHBoxLayout()

        self.category_combo = QComboBox()
        self.category_combo.addItems(["全部", "技术", "生活", "其他"])

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索文章...")

        search_layout.addWidget(self.category_combo)
        search_layout.addWidget(self.search_input)

        # 文章列表
        self.article_list = QListWidget()

        # 模拟数据
        for i in range(1, 6):
            self.article_list.addItem(f"文章 {i}")

        # 返回按钮
        self.back_btn = QPushButton("返回首页")
        self.back_btn.clicked.connect(lambda: self.app.navigate_to(self.app.home_page))

        layout.addLayout(search_layout)
        layout.addWidget(self.article_list)
        layout.addWidget(self.back_btn)
        self.setLayout(layout)

        # 连接列表点击事件
        self.article_list.itemDoubleClicked.connect(self.on_article_selected)

    def on_article_selected(self, item):
        """文章项被选中"""
        # 这里可以传递文章ID或数据到详情页
        self.app.navigate_to(self.app.article_detail_page)