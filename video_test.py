import sys
import base64
from PyQt6.QtCore import Qt, QByteArray, QTimer, QSize, QUrl, QPropertyAnimation
from PyQt6.QtGui import QIcon, QFontDatabase, QPixmap, QColor, QFont
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                             QSlider, QPushButton, QLabel, QFileDialog, QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QApplication)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from qfluentwidgets import FluentIcon


class DarkMediaPlayer(QWidget):
    def __init__(self, video_path):
        super().__init__()

        self.video_path = video_path
        self.hide_timer = QTimer()
        self.volume_popup = None
        self.init_ui()
        self.init_media()

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

        # 控制面板
        self.control_panel = QFrame()
        self.control_panel.setObjectName("ControlPanel")
        self.control_panel.setFixedHeight(100)

        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.video_widget)

        # # 初始化控制面板组件
        self.create_controls()
        # self.create_volume_slider()

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
        # 时间标签布局
        time_layout.addWidget(self.current_time)
        time_layout.addStretch()
        time_layout.addWidget(self.remaining_time)
        
        

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


    def init_media(self):
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)

        # 自动播放
        self.media_player.setSource(QUrl.fromLocalFile(self.video_path))
        self.media_player.play()

    def reset_hide_timer(self):
        if self.isFullScreen():
            self.hide_timer.start()
            self.setCursor(Qt.CursorShape.ArrowCursor)

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


    def seek(self, seconds):
        new_pos = self.media_player.position() + seconds * 1000
        new_pos = max(0, min(new_pos, self.media_player.duration()))
        self.media_player.setPosition(new_pos)

    def set_position(self, position):
        self.media_player.setPosition(position)

    def get_current_time(self):
        return self.media_player.position()
    
    def get_media_player(self):
        """获取媒体播放器实例"""
        return self.media_player
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    player = DarkMediaPlayer(
        "G:/Nyotengu/LazyProcrast/1080P_4000K_289668092.mp4")
    player.show()
    sys.exit(app.exec())
