from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLineEdit, QLabel, QMessageBox, QScrollArea, QFrame, QSizePolicy)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import Qt, QUrl, pyqtSignal, QSize, QThread
from PyQt5.QtGui import QIcon, QFont
import requests
from urllib.parse import urljoin
import os

class WorkerThread(QThread):
    finished_signal = pyqtSignal(object)  # 成功信号
    error_signal = pyqtSignal(str)       # 错误信号

    def __init__(self, parent, url, user_id):
        super().__init__(parent)
        self.url = url
        self.user_id = user_id
        self.base_url = parent.base_url

    def run(self):
        try:
            response = requests.post(
                urljoin(self.base_url, "desktop/quick_task/"),
                json={
                    'user_id': self.user_id,
                    'url': self.url
                },
                timeout=30
            )
            self.finished_signal.emit(response)
        except requests.exceptions.RequestException as e:
            self.error_signal.emit(str(e))

class WebPage(QWebEnginePage):
    linkClicked = pyqtSignal(QUrl)  # 自定义信号用于链接点击

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackgroundColor(Qt.transparent)

    def acceptNavigationRequest(self, url, type_, isMainFrame):
        # 拦截所有导航请求，允许在当前页面打开所有链接
        if type_ == QWebEnginePage.NavigationTypeLinkClicked:
            self.linkClicked.emit(url)
            return False
        return True  # 允许其他类型的导航


class ReaderPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.base_url = "http://127.0.0.1:8000/"
        self.simplified_mode = False
        self.current_article = None
        self.msg_box = None
        self.worker_thread = None
        self.init_ui()

    def init_ui(self):
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 顶部控制栏容器 - 固定在顶部
        control_container = QWidget()
        control_container.setFixedHeight(50)  # 固定高度
        control_container.setStyleSheet("background-color: #f5f5f5; border-bottom: 1px solid #ddd;")
        control_layout = QHBoxLayout(control_container)
        control_layout.setContentsMargins(10, 5, 10, 5)
        control_layout.setSpacing(10)

        # 返回首页按钮
        home_btn = QPushButton()
        home_icon_path = os.path.join("imgs", "home.png")
        if os.path.exists(home_icon_path):
            home_btn.setIcon(QIcon(home_icon_path))
            home_btn.setIconSize(QSize(24, 24))
        home_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-radius: 4px;
            }
        """)
        home_btn.clicked.connect(lambda: self.app.navigate_to(self.app.home_page))
        home_btn.setToolTip("返回首页")

        # 地址栏
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("输入网址...")
        self.url_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
                background-color: white;
            }
        """)

        # 跳转按钮
        self.go_btn = QPushButton("跳转")
        self.go_btn.setFixedWidth(80)
        self.go_btn.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
        """)
        self.go_btn.clicked.connect(self.on_go_clicked)

        # 简化/恢复按钮
        self.toggle_btn = QPushButton("简化页面")
        self.toggle_btn.setFixedWidth(100)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #34a853;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2d9248;
            }
        """)
        self.toggle_btn.clicked.connect(self.on_toggle_view)

        # 添加到控制栏
        control_layout.addWidget(home_btn)
        control_layout.addWidget(self.url_input)
        control_layout.addWidget(self.go_btn)
        control_layout.addWidget(self.toggle_btn)

        main_layout.addWidget(control_container)

        # 浏览器视图 - 占据剩余所有空间
        self.browser = QWebEngineView()
        self.browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 自定义WebPage用于处理链接点击
        self.web_page = WebPage(self.browser)
        self.web_page.linkClicked.connect(self.handle_link_click)
        self.browser.setPage(self.web_page)

        # 监听URL变化
        self.browser.urlChanged.connect(self.update_url_input)

        # 加载默认页面
        self.browser.load(QUrl("https://www.google.com"))

        main_layout.addWidget(self.browser)

        # 简化模式下的文章显示区域
        self.simplified_container = QScrollArea()
        self.simplified_container.setWidgetResizable(True)
        self.simplified_container.hide()

        self.simplified_widget = QWidget()
        self.simplified_layout = QVBoxLayout(self.simplified_widget)
        self.simplified_layout.setContentsMargins(20, 20, 20, 20)
        self.simplified_layout.setSpacing(15)

        # 文章标题
        self.article_title = QLabel()
        self.article_title.setWordWrap(True)
        self.article_title.setFont(QFont("Arial", 16, QFont.Bold))
        self.article_title.setStyleSheet("color: #333;")
        self.simplified_layout.addWidget(self.article_title)

        # 来源信息
        self.article_source = QLabel()
        self.article_source.setWordWrap(True)
        self.article_source.setFont(QFont("Arial", 10))
        self.article_source.setStyleSheet("color: #666;")
        self.simplified_layout.addWidget(self.article_source)

        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #eee;")
        self.simplified_layout.addWidget(separator)

        # 文章内容
        self.article_content = QLabel()
        self.article_content.setWordWrap(True)
        self.article_content.setFont(QFont("Arial", 12))
        self.article_content.setStyleSheet("color: #444;")
        self.simplified_layout.addWidget(self.article_content)

        self.simplified_layout.addStretch()
        self.simplified_container.setWidget(self.simplified_widget)
        main_layout.addWidget(self.simplified_container)

        self.setLayout(main_layout)

    def update_url_input(self, url):
        """更新地址栏显示"""
        self.url_input.setText(url.toString())

    def handle_link_click(self, url):
        """处理浏览器内链接点击"""
        self.browser.load(url)

    def on_go_clicked(self):
        """跳转按钮点击事件"""
        url = self.url_input.text().strip()
        if url:
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            self.browser.load(QUrl(url))

    def on_toggle_view(self):
        """切换视图按钮点击事件"""
        if self.simplified_mode:
            # 恢复原始视图
            self.browser.show()
            self.simplified_container.hide()
            self.toggle_btn.setText("简化页面")
            self.simplified_mode = False
        else:
            # 确保之前的消息框已关闭
            if hasattr(self, 'msg_box') and self.msg_box:
                self.msg_box.close()

            # 创建非模态消息框
            self.msg_box = QMessageBox(self)
            self.msg_box.setWindowTitle("请等待")
            self.msg_box.setText("正在获取页面内容，请稍候...")
            self.msg_box.setStandardButtons(QMessageBox.NoButton)

            # 添加取消按钮
            cancel_btn = self.msg_box.addButton("取消", QMessageBox.RejectRole)
            cancel_btn.clicked.connect(self.cancel_task)

            # 显示消息框(非模态)
            self.msg_box.setModal(False)
            self.msg_box.show()

            # 获取当前URL
            current_url = self.browser.url().toString()

            # 创建并启动工作线程
            self.worker_thread = WorkerThread(self, current_url, self.app.user_info["userid"])
            self.worker_thread.finished_signal.connect(self.handle_task_response)
            self.worker_thread.error_signal.connect(self.handle_task_error)
            self.worker_thread.finished.connect(self.cleanup_thread)
            self.worker_thread.start()

    def cancel_task(self):
        """取消任务"""
        if hasattr(self, 'worker_thread') and self.worker_thread:
            self.worker_thread.quit()
        if hasattr(self, 'msg_box') and self.msg_box:
            self.msg_box.close()

    def cleanup_thread(self):
        """清理线程资源"""
        if hasattr(self, 'worker_thread') and self.worker_thread:
            self.worker_thread.deleteLater()
            del self.worker_thread

    def handle_task_response(self, response):
        """处理任务响应"""
        try:
            # 确保消息框存在再关闭
            if hasattr(self, 'msg_box') and self.msg_box:
                self.msg_box.close()

            if response.status_code == 200:
                data = response.json().get('data', {})
                self.current_article = data

                # 显示简化视图
                self.browser.hide()
                self.simplified_container.show()
                self.toggle_btn.setText("恢复")
                self.simplified_mode = True

                # 填充文章数据
                self.article_title.setText(data.get('title', '无标题'))

                source_parts = []
                if data.get('author'):
                    source_parts.append(f"作者: {data['author']}")
                if data.get('publish_time'):
                    source_parts.append(f"时间: {data['publish_time']}")
                if self.browser.url().toString():
                    source_parts.append(f"来源: {self.browser.url().toString()}")

                self.article_source.setText(" | ".join(source_parts) if source_parts else "无来源信息")
                self.article_content.setText(data.get('content', '无内容'))
            else:
                error_msg = response.json().get('error', '未知错误')
                QMessageBox.warning(self, "错误", f"获取内容失败: {error_msg}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"处理响应时出错: {str(e)}")
        finally:
            self.cleanup_thread()

    def handle_task_error(self, error_msg):
        """处理任务错误"""
        try:
            if hasattr(self, 'msg_box') and self.msg_box:
                self.msg_box.close()
            QMessageBox.warning(self, "网络错误", f"无法连接到服务器: {error_msg}")
        finally:
            self.cleanup_thread()

    def closeEvent(self, event):
        """窗口关闭时清理资源"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()
        if self.msg_box:
            self.msg_box.close()
        super().closeEvent(event)