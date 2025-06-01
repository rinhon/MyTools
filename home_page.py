from qfluentwidgets import NavigationItemPosition, FluentWindow, SubtitleLabel, setFont
from qfluentwidgets import FluentIcon as FIF

import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QHBoxLayout, QFrame, QApplication

from main_video import VideoInterface


class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignmentFlag.AlignCenter)

        # 必须给子界面设置全局唯一的对象名
        self.setObjectName(text.replace(' ', '-'))


class Window(FluentWindow):
    """ 主界面 """

    def __init__(self):
        super().__init__()

        # 创建子界面，实际使用时将 Widget 换成自己的子界面
        self.homeInterface = Widget('Home Interface', self)
        self.musicInterface = Widget('Music Interface', self)
        self.videoInterface = VideoInterface()
        self.settingInterface = Widget('Setting Interface', self)
        self.albumInterface = Widget('Album Interface', self)
        self.albumInterface1 = Widget('Album Interface 1', self)

        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, 'Home')
        self.addSubInterface(self.musicInterface, FIF.MUSIC, 'Music library')
        self.addSubInterface(self.videoInterface, FIF.VIDEO, 'Video library')

        self.navigationInterface.addSeparator()

        self.addSubInterface(self.albumInterface, FIF.ALBUM,'Albums', NavigationItemPosition.SCROLL)
        self.addSubInterface(self.albumInterface1, FIF.ALBUM,'Album 1', parent=self.albumInterface)
        self.addSubInterface(self.settingInterface, FIF.SETTING,'Settings', NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('My Tools')
        # 窗口居中
    def center_window(self):
        """将窗口居中显示在屏幕中央，支持多显示器环境并确保窗口不会超出屏幕边界。
        
        该方法会先强制更新窗口布局，获取精确窗口尺寸后，计算当前屏幕的中心位置，
        并将窗口移动到该位置，同时确保窗口完全显示在屏幕可见区域内。
        
        注意:
            - 需要先调用QApplication.processEvents()确保窗口尺寸计算准确
            - 自动适应不同分辨率和多显示器配置
            - 处理了边缘情况，防止窗口部分内容超出屏幕范围
        """
        # 先让窗口完成布局更新
        QApplication.processEvents()

        # 获取精确的窗口尺寸
        window_size = self.size()

        # 处理多显示器情况
        current_screen = self.screen()
        if current_screen is not None:
            screen_rect = current_screen.availableGeometry()

            # 计算居中坐标
            x = screen_rect.left() + (screen_rect.width() - window_size.width()) // 2
            y = screen_rect.top() + (screen_rect.height() - window_size.height()) // 2

            # 设置窗口位置并限制在屏幕范围内
            self.move(
                max(screen_rect.left(), min(
                    x, screen_rect.right() - window_size.width())),
                max(screen_rect.top(), min(
                    y, screen_rect.bottom() - window_size.height()))
            )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    w.center_window()
    app.exec()
