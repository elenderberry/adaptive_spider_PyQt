from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton


class TaskDetailPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 任务详情内容
        self.content_label = QLabel("这里是任务详情页面，显示任务中的所有文章")

        # 返回按钮
        self.back_btn = QPushButton("返回任务列表")
        self.back_btn.clicked.connect(lambda: self.app.navigate_to(self.app.task_list_page))

        layout.addWidget(self.content_label)
        layout.addWidget(self.back_btn)
        self.setLayout(layout)