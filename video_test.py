import sys
import base64
from PyQt6.QtCore import Qt, QByteArray, QTimer, QSize, QUrl, QPropertyAnimation
from PyQt6.QtGui import QIcon, QFontDatabase, QPixmap, QColor, QFont
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,QStyle,
                             QSlider, QPushButton, QLabel, QFileDialog, QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QApplication)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from qfluentwidgets import FluentIcon, Slider


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


        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 创建进度条
        self.progress_slider = Slider(Qt.Orientation.Horizontal)
        self.progress_slider.setFixedHeight(30)
        self.progress_slider.setRange(0, 0)  # 初始范围设为0，等待媒体加载后更新
        self.progress_slider.mousePressEvent = self.progress_slider_click

        layout.addWidget(self.video_widget)
        layout.addWidget(self.progress_slider)


    def init_media(self):
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)

        # 连接媒体播放器信号
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        self.media_player.mediaStatusChanged.connect(self.media_status_changed)
        
        # 连接进度条信号
        self.progress_slider.sliderMoved.connect(self.set_position)

        # 自动播放
        self.media_player.setSource(QUrl.fromLocalFile(self.video_path))
        self.media_player.play()

    def position_changed(self, position):
        """更新进度条位置"""
        self.progress_slider.setValue(position)

    def duration_changed(self, duration):
        """更新进度条范围"""
        self.progress_slider.setRange(0, duration)

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
        """获取当前播放位置（毫秒）"""
        return self.media_player.position()

    def get_media_player(self):
        """获取媒体播放器实例"""
        return self.media_player
    
    def media_status_changed(self, status):
        """处理媒体状态改变"""
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            # 播放结束时，重置位置并重新播放
            self.media_player.setPosition(0)
            self.media_player.play()
    
    def progress_slider_click(self, event):
        """处理进度条点击事件"""
        # 计算点击位置对应的值
        value = QStyle.sliderValueFromPosition(
            self.progress_slider.minimum(),
            self.progress_slider.maximum(),
            int(event.position().x()),
            self.progress_slider.width()
        )
        # 设置进度条值和媒体播放位置
        self.progress_slider.setValue(value)
        self.media_player.setPosition(value)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    player = DarkMediaPlayer(
        "G:/Nyotengu/LazyProcrast/1080P_4000K_289668092.mp4")
    player.show()
    sys.exit(app.exec())