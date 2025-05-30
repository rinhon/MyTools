import sys
import base64
from PyQt6.QtCore import Qt, QByteArray, QTimer, QSize, QUrl, QPropertyAnimation
from PyQt6.QtGui import QIcon, QFontDatabase, QPixmap, QColor, QFont
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                             QSlider, QPushButton, QLabel, QFileDialog, QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QApplication)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget


class DarkMediaPlayer(QWidget):
    def __init__(self, video_path):
        super().__init__()

        # 图标缓存字典
        self.icons = {
            'play': self.base64_to_icon("""iVBORw0KGgoAAAANSUhEUgAAAMgAAADICAMAAACahl6sAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAbUExURQAAAICAgJ6enqSfn6GhoaOhoaGgoKKhoauqqkGbLowAAAAHdFJOUwACHTXBz/VW8SGWAAAACXBIWXMAAA7DAAAOwwHHb6hkAAAA8ElEQVR4Xu3PSQqDQAAAwYnG5f8vzmUuAWlQPFY/oKHGf5/v8ax9nYfbLedc3G2bg8tAQEBAOhAQkA4EBKQDAQHpQEBAOhAQkA4EBKQDAQHpQEBAOhAQkA4EBKQDAQHpQEBAOhAQkA4EBKQDAQHpQEBAOhAQkA4EBKQDAQHpQEBAOhAQkA4EBKQDAQHpQEBAOhAQkA4EBKQDAQHpQEBAOhAQkA4EBKQDAQHpQEBAOhAQkA4EBKQDAQHpQEBAOhAQkA4EBKQDAQHpQEBAOhAQkA4EBKQDAQHpQEBAOhAQkA4EBKQDAQHpQEBAOpB3IGP8ADrocFcHCNxUAAAAAElFTkSuQmCC"""),
            'pause': self.base64_to_icon("""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"""),
            'volume': self.base64_to_icon("""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"""),
            'volume_mute': self.base64_to_icon("""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"""),
            'volume_low': self.base64_to_icon("""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"""),
            'volume_medium': self.base64_to_icon("""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"""),
            'forward': self.base64_to_icon("""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"""),
            'rewind': self.base64_to_icon("""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"""),
            'fullscreen': self.base64_to_icon("""iVBORw0KGgoAAAANSUhEUgAAAMgAAADICAMAAACahl6sAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAADYUExURQAAAKqqqp+fn6qZmZ+fn56enp+fn6Ojo6GhoaSkpJ6enqWenqSkpKKioqOjo6CgoKOjo6CgoKOfn6SgoKGhoaKioqKioqKioqOgoKOhoaKgoKKioqOhoaGhoaGhoaKhoaKgoKKgoKGhoaOhoaGhoaGhoaKgoKKioqKioqKhoaKhoaOhoaKhoaKgoKGhoaKioqOhoaKhoaKioqKhoaOhoaKhoaKhoaOhoaGhoaKhoaKhoaKhoaKhoaKhoaKgoKKhoaKhoaKhoaKhoaKhoaKhoaKhoaKhoaKhoYP+aXIAAABHdFJOUwAGCA8QFRgZGxwdIiosMjM6O0BDTFVYWltkbnB3gIWHiYyTlZuen6GkqKqrra+xt7m7v8PExcjMz9DT1tnf6Ort7vHz9Pr8xjWmFQAAAAlwSFlzAAAOwwAADsMBx2+oZAAAA6FJREFUeF7t3WdTIkEUhWHMOaIYkCAGjIg5K8b5//9oUV9gQRy63S29tuf51j19pu6tUmamHOyEiIiI/CLTqXS+WD7obCvXS8RDT36XeJxyMZ9OTRP5jMGF7fvI3dkwOWfDp0Rd3K2l+sn5SZaeOYWrAklnBYKunktJku7GVgl7qJB1dkvQw+oYWTdd2UeCXjx/jqeJeXnMdhN3MLRHys81cWdXBP0cjxLvaLxCxFOGvLMMQU8PM+Q7mGe9r5MBTuBs4ICor0VOEGuRxTVPN5dHfKDHWZkl72V+nXico8ubJ4qpmScfY4albw5zU8x/s4mlfUp6M878h0YfWPliZ5JZEyZ3KOtFZYjZD3Qfs7DqfI5JM+YuKK1qr4vJ9rIsq9roY86QkUOKq8oy19ZY4zq4zJQxm5RXvTLGXeMb9yWbzJizTIHVuxVm2kiypPppxYxBG5QYRR/fQZZYEV2MMGNQ3zlFRiVm3umv37eb+7z62xxFRs+DzLRKsSDaYcKo+vVkgYlWaxyPTF0H35ukzGibiVZ3HN9nbFbtanLPuEX9OWeJCbNyFPrBk1z9V2SCCbOmKDRKMdEszdEnxobV7urTjJvlOXrD2LAbSs0zblbk6CVjwy4ptci4WZmjR4wNO6LUMuNmtQfoA8aGxZeqRr6eGrFGjVijRqxRI9aoEWvUiDVqxBo1Yo0asUaNWKNGrFEj1qgRa9SINWrEGjViTXypWxxdZ2zYCqXuMm5We5/A4VXU7zZLqe3/PN179nrwB/xkJRInr6We9jBsMVyoRFcZ7/epv8NA5jq6LcR8YeVfvjfzxX5QqSIiIiIiIiIiIiIiIiIiIiIi8h+F8ZpTKC+eBfMqYDAvZwbzuqzexP56asQaNWKNGrFGjVijRqxRI9aoEWvUiDVqxBo1Yo0asUaNWKNGrFEj1qgRa9SINb+kkWC27QhmI5VgtrYJZrOhYLZ/CmZDrmC2SAtn07pgthEMZmPHYLbaDGfz02C2ow1ng+BgtmwOZxPtYLY1D2ej+XC2/q+enMW+Trzf4R6oPXv7WuQEHYxXWO8pQ95ZhqCnhxnyHQ3tEfFzTdzZFUE/x6PEHXRlG1dGD57fdag/yfl4zHYTdzPWuFtxViHr7Jagh9XY63lbyVL9rt5RgaSzAkFXz6WY+8QYgwvb95zCxVnM/xFub/iUqIu7tVQ/uc+YTqXzxTIf6HG2cr1EPPTkd4nHKRfz6ZT+T7GIiMjvkUj8Aem6EFU7bMVCAAAAAElFTkSuQmCC"""),
            'reduce': self.base64_to_icon("""iVBORw0KGgoAAAANSUhEUgAAAMgAAADICAMAAACahl6sAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAACKUExURQAAAKqZmaampqampqKioqCgoKOjo6CgoKKioqSfn6GhoaOfn6KioqGhoaOgoKGhoaOhoaOgoKOgoKKioqOhoaKgoKGhoaKhoaKgoKOhoaGhoaKhoaGhoaKhoaKhoaOhoaKgoKKioqOhoaKhoaOhoaGhoaKioqKhoaKhoaKhoaKhoaKhoaKhoaKhoS4aImYAAAAtdFJOUwAPFBceIyQzNzg5QEJMTlFkZnR4enyAh4mVnqKmqq2ur7S2uLm8v8PR1NfZ+xKpnIcAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAPESURBVHhe7dxrV+IwEAZgFFQE0YpyXUG8XzD//+9tqy9pe2TdTJIhXfZ9Pm3HM2HGxVLOyaRFRESUXm/cw7+EvBNV9N6MMW8eFXkn6jjIqykc4NqZd6KSKeqZ4tqZd6KSFepZ4dqZd6KSZ9TzjGtn3olK2AgbUcJG2IgSNsJGlLARNqKEjbARJWyEjShhI2xECRthI0rYCBtRwkbYiBI2wkaUsJGmNbJGPUtcO1sicY3r1D5QzwzXzmZI/MB1Yh2UY0YIOBsh0XQQSKuPakyGgLMMiaaPQFqb/QtmgICzARIbsvXhFdWYQwScHSLRvCKQVBfFmEcEBB6RaroIpDRHLfI/kcofyRyBhM5Qitetx97wzBki6dyiEnOHgMgdks0tAslcoRCvd1blvWWuEEnkAmUY84SI0BPSjblAJA0UkTtHROgc6TlEUjhBCbkbhMRusEDuBKGdu0QBBe8PAvsxlLtEbLfO7P0qN0TQwxBLFG53fxc+tZ+DhV+IevmFRT7NTxHdhU5/9o7X/RL4qGQf1j69z/qBT/XtyeLZwXrzPaqEBbxhmdLHGi/2o8WkjQVqjrGI2D0WCHCPpcSOsUCV72LXyA9yjcWktvwS7fc8Ia8nk+/KZxWZ798tx/iJzE20LxLdyiejwBjppR5+IvHk+Vyy3Xn53OVuy8hGMcoh8hDpXVXKHrC0szdkVsn+S16GR8iL6mj4ghdws3WG5mC6wg36R8vZKBtsvYHH0R5ko9kSL/aj1bQpEzRERERERERERERERERERERERET/J8cNzJ8bz8QDbu4OnTeeRdnA/JipTHN2MjsI5yTKBua7+Jsz7ciVq0gbmBuwXZYbmL8JGIGpqo7DSMTYwAxBQzAbtWEYgfANzBURJobrozACIRuYmzMIE7yBudOf1n+FgaMw9Rv/6zR0NEmkWxsWCxqGqQ3BzHc/EF4b3wv4bKyOwCQY3yuUA8eRBiqTDR6XI8dRRlxTjh2jhNw/PXRcHTsOHgNPNnL8pRw8DhzMTzNwXGHvXQ8IiNihquRHJVQOr/AYujpCahMOryiPE/F4DrbPvA04TqR1ilrMCwICdsRtl8Pff2RHwsWjcG0kmncE0tqckhVwCJL4ZC4Ve3Ms1d4cFLY3R7ftz2F6PKeRjShhI2xECRthI0rYCBtRwkbYiBI2wkaUsBE2ooSNsBElbISNKGEjbEQJG2EjStgIG1GyQD0LXDvzTlQyQT0TXDvzTlSy2VLivRdF8TxnmeNiC/L9tqGUv/BOVNMfe24n8U4kIiKKp9X6DfcTsleW0oBiAAAAAElFTkSuQmCC""")
        }

        self.video_path = video_path
        self.hide_timer = QTimer()
        self.volume_popup = None
        self.init_ui()
        self.init_media()
        self.setup_animations()
        self.setup_hide_timer()
        self.setup_styles()
        self.setup_connections()

    def base64_to_icon(self, base64_str):
        """将base64字符串转换为QIcon"""
        # 去除可能存在的头部信息
        if base64_str.startswith('data:image'):
            base64_str = base64_str.split(',', 1)[1]

        # 解码base64
        image_data = base64.b64decode(base64_str)
        pixmap = QPixmap()
        pixmap.loadFromData(QByteArray(image_data))
        return QIcon(pixmap)

    def init_ui(self):
        # 窗口设置
        self.setWindowTitle("Dark Media Player")
        self.setWindowIcon(QIcon("dark_icon.ico"))
        self.setMinimumSize(720, 480)

        # 设置主窗口属性
        self.setObjectName("MainWidget")

        # 视频显示区域
        self.video_widget = QVideoWidget()
        self.video_widget.setStyleSheet("background: #000000;")
        self.video_widget.mousePressEvent = self.toggle_controls

        # 控制面板
        self.control_panel = QFrame()
        self.control_panel.setObjectName("ControlPanel")
        self.control_panel.setFixedHeight(100)

        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.video_widget)
        layout.addWidget(self.control_panel)

        # 初始化控制面板组件
        self.create_controls()
        self.create_volume_slider()

    def create_controls(self):
        # 进度条
        self.progress_bar = QSlider(Qt.Orientation.Horizontal)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setCursor(Qt.CursorShape.PointingHandCursor)

        # 时间显示
        time_layout = QHBoxLayout()
        self.current_time = QLabel("00:00:00")
        self.remaining_time = QLabel("00:00:00")

        # 控制按钮
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(30)

        # 按钮创建
        self.volume_btn = self.create_icon_button("volume", 24, "音量调节")
        self.rewind_btn = self.create_icon_button("rewind", 24, "快退10秒")
        self.play_btn = self.create_icon_button("play", 24, "播放/暂停")
        self.forward_btn = self.create_icon_button("forward", 24, "快进10秒")
        self.fullscreen_btn = self.create_icon_button("fullscreen", 24, "全屏切换")

        # 布局排列
        control_layout.addWidget(self.volume_btn)
        control_layout.addStretch()
        control_layout.addWidget(self.rewind_btn)
        control_layout.addWidget(self.play_btn)
        control_layout.addWidget(self.forward_btn)
        control_layout.addStretch()
        control_layout.addWidget(self.fullscreen_btn)

        # 整体布局
        panel_layout = QVBoxLayout(self.control_panel)
        panel_layout.setContentsMargins(30, 10, 30, 20)
        panel_layout.addWidget(self.progress_bar)
        panel_layout.addLayout(time_layout)
        panel_layout.addLayout(control_layout)

        # 时间标签布局
        time_layout.addWidget(self.current_time)
        time_layout.addStretch()
        time_layout.addWidget(self.remaining_time)

    def create_volume_slider(self):
        # 音量弹出面板
        self.volume_popup = QWidget(self.control_panel)  # 改为控制面板的子部件
        self.volume_popup.setObjectName("VolumePopup")
        self.volume_popup.setFixedSize(120, 40)
        self.volume_popup.hide()

        # 音量滑块
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.setCursor(Qt.CursorShape.PointingHandCursor)

        # 布局
        popup_layout = QHBoxLayout(self.volume_popup)
        popup_layout.setContentsMargins(10, 0, 10, 0)
        popup_layout.addWidget(self.volume_slider)

    def create_icon_button(self, icon_name, size, tooltip):
        btn = QPushButton()
        btn.setIcon(self.icons[icon_name])  # 从缓存获取图标
        btn.setIconSize(QSize(size, size))
        btn.setToolTip(tooltip)
        btn.setFixedSize(size + 20, size + 20)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn.setObjectName("ControlButton")
        return btn

    def setup_styles(self):
        # 字体设置
        QFontDatabase.addApplicationFont("SegoeUI.ttf")
        font = QFont("Segoe UI", 10)
        self.setFont(font)

        # 全局样式表
        self.setStyleSheet("""
            #MainWidget {
                background: #0a0a0a;
            }
            #ControlPanel {
                background: rgba(16, 16, 16, 0.95);
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
            }
            #ControlButton {
                background: transparent;
                border: none;
                border-radius: 8px;
                padding: 8px;
            }
            #ControlButton:hover {
                background: rgba(255, 255, 255, 0.1);
            }
            #ControlButton:pressed {
                background: rgba(255, 255, 255, 0.2);
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #0078d4;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 12px;
            }
            #VolumePopup {
                background: rgba(32, 32, 32, 0.9);
                border-radius: 4px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)

        # 控制面板阴影
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.control_panel.setGraphicsEffect(shadow)

        # 音量滑块阴影
        volume_shadow = QGraphicsDropShadowEffect()
        volume_shadow.setBlurRadius(15)
        volume_shadow.setColor(QColor(0, 0, 0, 60))
        volume_shadow.setOffset(2, 2)
        self.volume_popup.setGraphicsEffect(volume_shadow)

    def init_media(self):
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)

        # 自动播放
        self.media_player.setSource(QUrl.fromLocalFile(self.video_path))
        self.media_player.play()

    def setup_animations(self):
        # 控制面板透明度动画
        self.opacity_effect = QGraphicsOpacityEffect()
        self.control_panel.setGraphicsEffect(self.opacity_effect)

        self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out.setDuration(500)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)

        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(300)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)

    def setup_hide_timer(self):
        self.hide_timer.timeout.connect(self.auto_hide_controls)
        self.hide_timer.setInterval(1000)

    def setup_connections(self):
        # 媒体信号
        self.media_player.positionChanged.connect(self.update_progress)
        self.media_player.durationChanged.connect(self.update_duration)
        self.media_player.playbackStateChanged.connect(self.update_play_icon)

        # 按钮信号
        self.play_btn.clicked.connect(self.toggle_play)
        self.rewind_btn.clicked.connect(lambda: self.seek(-10))
        self.forward_btn.clicked.connect(lambda: self.seek(10))
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        self.progress_bar.sliderMoved.connect(self.set_position)
        self.volume_btn.clicked.connect(self.toggle_volume_popup)

        # 音量滑块信号
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.audio_output.volumeChanged.connect(self.update_volume_slider)

    def toggle_volume_popup(self):
        if self.volume_popup.isVisible():
            self.volume_popup.hide()
        else:
            # 计算弹出位置（在音量按钮上方）
            btn_pos = self.volume_btn.pos()
            popup_x = btn_pos.x() + self.volume_btn.width()//2 - \
                self.volume_popup.width()//3
            popup_y = btn_pos.y() - self.volume_popup.height() - 5
            self.volume_popup.move(popup_x, popup_y)
            self.volume_popup.show()

    def set_volume(self, value):
        self.audio_output.setVolume(value / 100)
        # 更新音量按钮图标
        if value <= 0:
            self.volume_btn.setIcon(self.icons["volume_mute"])
        elif value < 33:
            self.volume_btn.setIcon(self.icons["volume_low"])
        elif value < 66:
            self.volume_btn.setIcon(self.icons["volume_medium"])
        else:
            self.volume_btn.setIcon(self.icons["volume"])

    def update_volume_slider(self):
        volume = round(self.audio_output.volume() * 100)
        self.volume_slider.setValue(volume)

    def mousePressEvent(self, event):
        # 点击音量滑块外部时隐藏
        if self.volume_popup.isVisible():
            if not self.volume_popup.geometry().contains(event.pos()):
                if not self.volume_btn.geometry().contains(event.pos()):
                    self.volume_popup.hide()
        super().mousePressEvent(event)

    def toggle_controls(self, event):
        if self.fade_out.state() == QPropertyAnimation.State.Running:
            return

        if self.control_panel.isVisible():
            self.fade_out.start()
            self.control_panel.setVisible(False)
        else:
            self.control_panel.setVisible(True)
            self.fade_in.start()
            self.reset_hide_timer()

    def reset_hide_timer(self):
        if self.isFullScreen():
            self.hide_timer.start()
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def auto_hide_controls(self):
        if self.isFullScreen() and not self.underMouse():
            self.fade_out.start()
            self.control_panel.setVisible(False)
            self.setCursor(Qt.CursorShape.BlankCursor)
        self.hide_timer.stop()

    def mouseMoveEvent(self, event):
        if self.isFullScreen() and not self.control_panel.isVisible():
            self.control_panel.setVisible(True)
            self.fade_in.start()
            self.reset_hide_timer()

    def update_progress(self, position):
        self.progress_bar.setValue(position)
        self.current_time.setText(self.format_time(position))
        self.remaining_time.setText(self.format_time(
            self.media_player.duration() - position))

    def update_duration(self, duration):
        self.progress_bar.setRange(0, duration)

    def format_time(self, ms):
        seconds = ms // 1000
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    def is_playing_status(self):
        return self.media_player.isPlaying()
    def toggle_play(self):
        if self.media_player.isPlaying():
            self.media_player.pause()
        else:
            self.media_player.play()

    def update_play_icon(self):
        icon = "play" if self.media_player.isPlaying() else "pause"
        self.play_btn.setIcon(self.icons[icon])

    def seek(self, seconds):
        new_pos = self.media_player.position() + seconds * 1000
        new_pos = max(0, min(new_pos, self.media_player.duration()))
        self.media_player.setPosition(new_pos)

    def set_position(self, position):
        self.media_player.setPosition(position)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.hide_timer.stop()
            self.control_panel.show()
            self.fullscreen_btn.setIcon(self.icons["fullscreen"])
        else:
            self.showFullScreen()
            self.reset_hide_timer()
            self.fullscreen_btn.setIcon(self.icons["reduce"])

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.toggle_play()
        super().keyPressEvent(event)
        
    def get_current_time(self):
        return self.media_player.position()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    player = DarkMediaPlayer(
        "C:/Users/90708/Videos/2f3ac6295bc6c7617532ced9e6d1215b.mp4")
    player.show()
    sys.exit(app.exec())
