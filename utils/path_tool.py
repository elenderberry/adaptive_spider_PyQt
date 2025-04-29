import os
import sys


def resource_path(relative_path):
    """ 获取资源的绝对路径，打包后也能正确访问 """
    if hasattr(sys, '_MEIPASS'):
        # 打包后的运行环境
        base_path = sys._MEIPASS
    else:
        # 正常开发环境
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
