from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from widgets.login import LoginPage
from widgets.home import HomePage
from widgets.task_list import TaskListPage
from widgets.task_detail import TaskDetailPage
from widgets.article_list import ArticleListPage
from widgets.article_detail import ArticleDetailPage
from widgets.reader import ReaderPage


class MainApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

        # 初始化用户信息
        self.user_info = None
        self.current_task_id = None
        # 主窗口设置
        self.main_window = QMainWindow()
        self.main_window.setWindowTitle("我的应用")
        self.main_window.resize(1920, 1080)

        # 页面堆栈
        self.pages = QStackedWidget()
        self.main_window.setCentralWidget(self.pages)

        # 初始化所有页面
        self.init_pages()

        # 显示登录页面
        self.pages.setCurrentWidget(self.login_page)
        self.main_window.show()

    def init_pages(self):
        """初始化所有页面"""
        self.login_page = LoginPage(self)
        self.home_page = HomePage(self)
        self.task_list_page = TaskListPage(self)
        self.task_detail_page = TaskDetailPage(self)
        self.article_list_page = ArticleListPage(self)
        self.article_detail_page = ArticleDetailPage(self)
        self.reader_page = ReaderPage(self)

        # 添加到堆栈
        self.pages.addWidget(self.login_page)
        self.pages.addWidget(self.home_page)
        self.pages.addWidget(self.task_list_page)
        self.pages.addWidget(self.task_detail_page)
        self.pages.addWidget(self.article_list_page)
        self.pages.addWidget(self.article_detail_page)
        self.pages.addWidget(self.reader_page)

    def navigate_to(self, page):
        """导航到指定页面"""
        self.pages.setCurrentWidget(page)