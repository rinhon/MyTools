# import sys
# import os
# from PyQt6.QtCore import Qt, QUrl, QTimer
# from PyQt6.QtGui import QMouseEvent
# from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
#                              QSlider, QPushButton, QLabel, QApplication, QSizePolicy)
# from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
# from PyQt6.QtMultimediaWidgets import QVideoWidget
# from qfluentwidgets import FluentIcon, Slider


# class ClickableSlider(Slider):
#     """优化的可点击滑动条"""
#     def __init__(self, orientation):
#         super().__init__(orientation)
#         self._update_timer = QTimer()
#         self._update_timer.setSingleShot(True)
#         self._update_timer.timeout.connect(self._delayed_update)
#         self._pending_value = None
        
#     def mousePressEvent(self, event):
#         if event.button() == Qt.MouseButton.LeftButton:
#             click_pos = event.position().x()
#             slider_width = self.width()
            
#             if slider_width > 0 and self.maximum() > self.minimum():
#                 percentage = max(0, min(1, click_pos / slider_width))
#                 value_range = self.maximum() - self.minimum()
#                 new_value = self.minimum() + int(percentage * value_range)
#                 new_value = max(self.minimum(), min(self.maximum(), new_value))
                
#                 # 延迟更新，避免频繁触发
#                 self._pending_value = new_value
#                 self._update_timer.start(50)  # 50ms延迟
        
#         super().mousePressEvent(event)
    
#     def _delayed_update(self):
#         """延迟更新值"""
#         if self._pending_value is not None:
#             self.setValue(self._pending_value)
#             self.valueChanged.emit(self._pending_value)
#             self._pending_value = None


# class OptimizedMediaPlayer(QWidget):
#     def __init__(self, video_path):
#         super().__init__()
#         self.video_path = video_path
#         self.media_player = None
#         self.audio_output = None
#         self.video_widget = None
#         self.is_seeking = False
#         self._last_position_update = 0  # 用于限制进度条更新频率
        
#         self.init_ui()
#         self.init_media()

#     def init_ui(self):
#         """简化的UI初始化"""
#         self.setWindowTitle("Optimized Media Player")
#         self.setMinimumSize(800, 600)
        
#         # 主布局
#         main_layout = QVBoxLayout(self)
#         main_layout.setContentsMargins(0, 0, 0, 0)
#         main_layout.setSpacing(0)
        
#         # 视频组件
#         self.video_widget = QVideoWidget()
#         self.video_widget.setStyleSheet("background: black;")
#         self.video_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
#         # 进度条
#         self.progress_slider = ClickableSlider(Qt.Orientation.Horizontal)
#         self.progress_slider.setFixedHeight(30)
#         self.progress_slider.setRange(0, 0)
        
#         # 连接信号
#         self.progress_slider.valueChanged.connect(self.on_position_change)
#         self.progress_slider.sliderPressed.connect(lambda: setattr(self, 'is_seeking', True))
#         self.progress_slider.sliderReleased.connect(self.on_seek_finished)
        
#         # 添加到布局
#         main_layout.addWidget(self.video_widget, 1)
#         main_layout.addWidget(self.progress_slider)

#     def init_media(self):
#         """优化的媒体初始化"""
#         if not os.path.exists(self.video_path):
#             print(f"视频文件不存在: {self.video_path}")
#             return
        
#         # 创建媒体播放器和音频输出
#         self.audio_output = QAudioOutput()
#         self.audio_output.setVolume(0.7)
        
#         self.media_player = QMediaPlayer()
#         self.media_player.setAudioOutput(self.audio_output)
#         self.media_player.setVideoOutput(self.video_widget)
        
#         # 连接信号 - 使用限频更新
#         self.media_player.positionChanged.connect(self.update_position)
#         self.media_player.durationChanged.connect(self.update_duration)
#         self.media_player.mediaStatusChanged.connect(self.handle_media_status)
        
#         # 设置媒体源并播放
#         self.media_player.setSource(QUrl.fromLocalFile(self.video_path))
#         self.media_player.play()

#     def update_position(self, position):
#         """限频的位置更新"""
#         # 限制更新频率为每200ms一次，减少UI刷新
#         if not self.is_seeking and abs(position - self._last_position_update) > 200:
#             self.progress_slider.setValue(position)
#             self._last_position_update = position

#     def update_duration(self, duration):
#         """更新总时长"""
#         self.progress_slider.setRange(0, duration)

#     def on_position_change(self, position):
#         """处理位置变化"""
#         if not self.is_seeking and self.media_player:
#             self.media_player.setPosition(position)

#     def on_seek_finished(self):
#         """拖拽结束处理"""
#         self.is_seeking = False
#         if self.media_player:
#             self.media_player.setPosition(self.progress_slider.value())

#     def handle_media_status(self, status):
#         """处理媒体状态"""
#         if status == QMediaPlayer.MediaStatus.EndOfMedia:
#             # 播放结束时循环播放
#             self.media_player.setPosition(0)
#             self.media_player.play()
#         elif status == QMediaPlayer.MediaStatus.InvalidMedia:
#             print("无效的媒体文件")

#     def keyPressEvent(self, event):
#         """键盘快捷键"""
#         if not self.media_player:
#             return
            
#         if event.key() == Qt.Key.Key_Space:
#             self.toggle_play()
#         elif event.key() == Qt.Key.Key_Left:
#             self.seek(-5000)  # 后退5秒
#         elif event.key() == Qt.Key.Key_Right:
#             self.seek(5000)   # 前进5秒
#         else:
#             super().keyPressEvent(event)

#     def toggle_play(self):
#         """切换播放状态"""
#         if not self.media_player:
#             return
            
#         if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
#             self.media_player.pause()
#         else:
#             self.media_player.play()

#     def seek(self, ms):
#         """跳转指定毫秒数"""
#         if not self.media_player:
#             return
            
#         current_pos = self.media_player.position()
#         new_pos = max(0, min(current_pos + ms, self.media_player.duration()))
#         self.media_player.setPosition(new_pos)

#     def closeEvent(self, event):
#         """窗口关闭时清理资源"""
#         if self.media_player:
#             self.media_player.stop()
#             self.media_player = None
#         if self.audio_output:
#             self.audio_output = None
#         event.accept()


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
    
#     # 测试视频路径 - 请替换为你的视频文件路径
#     video_path =  "G:/Nyotengu/LazyProcrast/1080P_4000K_289668092.mp4"  # 替换为实际路径
    
#     if len(sys.argv) > 1:
#         video_path = sys.argv[1]
    
#     player = OptimizedMediaPlayer(video_path)
#     player.show()
    
#     sys.exit(app.exec())




import sys
import os
import cv2
import numpy as np
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QMutex
from PyQt6.QtGui import QImage, QPixmap, QPainter, QFont
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSlider, QApplication, QSizePolicy, QPushButton)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from qfluentwidgets import Slider
import threading
import time


class VideoThread(QThread):
    """视频播放线程"""
    frameReady = pyqtSignal(np.ndarray)
    positionChanged = pyqtSignal(int)
    durationChanged = pyqtSignal(int)
    
    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.cap = None
        self.is_playing = False
        self.is_paused = False
        self.seek_frame = -1
        self.current_frame = 0
        self.total_frames = 0
        self.fps = 30
        self.mutex = QMutex()
        
    def run(self):
        """主播放循环"""
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            print("无法打开视频文件")
            return
            
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration_ms = int((self.total_frames / self.fps) * 1000)
        self.durationChanged.emit(duration_ms)
        
        frame_interval = 1.0 / self.fps
        last_time = time.time()
        
        while self.is_playing:
            current_time = time.time()
            
            # 处理跳转
            if self.seek_frame >= 0:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.seek_frame)
                self.current_frame = self.seek_frame
                self.seek_frame = -1
            
            if not self.is_paused:
                ret, frame = self.cap.read()
                if not ret:
                    # 视频结束，循环播放
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    self.current_frame = 0
                    continue
                
                # 发射帧和位置信息
                self.frameReady.emit(frame)
                position_ms = int((self.current_frame / self.fps) * 1000)
                self.positionChanged.emit(position_ms)
                
                self.current_frame += 1
                
                # 控制播放速度
                elapsed = current_time - last_time
                sleep_time = max(0, frame_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                last_time = time.time()
            else:
                time.sleep(0.01)  # 暂停时短暂休眠
                
    def play(self):
        """开始播放"""
        self.is_playing = True
        self.is_paused = False
        if not self.isRunning():
            self.start()
    
    def pause(self):
        """暂停播放"""
        self.is_paused = True
    
    def resume(self):
        """恢复播放"""
        self.is_paused = False
    
    def stop(self):
        """停止播放"""
        self.is_playing = False
        if self.cap:
            self.cap.release()
    
    def seek_to_frame(self, frame_number):
        """跳转到指定帧"""
        self.seek_frame = max(0, min(frame_number, self.total_frames - 1))
    
    def seek_to_position(self, position_ms):
        """跳转到指定时间位置"""
        frame_number = int((position_ms / 1000.0) * self.fps)
        self.seek_to_frame(frame_number)


class VolumeSlider(QSlider):
    """垂直音量滑动条"""
    def __init__(self):
        super().__init__(Qt.Orientation.Vertical)
        self.setRange(0, 100)
        self.setValue(70)
        self.setFixedWidth(30)
        self.setFixedHeight(150)
        self.setStyleSheet("""
            QSlider::groove:vertical {
                background: rgba(255, 255, 255, 0.1);
                width: 6px;
                border-radius: 3px;
            }
            QSlider::handle:vertical {
                background: #0078d4;
                border: 2px solid #ffffff;
                height: 16px;
                border-radius: 8px;
                margin: -2px 0;
            }
            QSlider::handle:vertical:hover {
                background: #106ebe;
            }
            QSlider::sub-page:vertical {
                background: #0078d4;
                border-radius: 3px;
            }
        """)


class VolumeIndicator(QLabel):
    """音量显示指示器"""
    def __init__(self):
        super().__init__()
        self.setFixedSize(120, 40)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            background: rgba(0, 0, 0, 0.7);
            color: white;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
        """)
        self.hide()
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)
    
    def show_volume(self, volume):
        """显示音量并自动隐藏"""
        self.setText(f"音量: {volume}%")
        self.show()
        self.timer.start(1500)  # 1.5秒后隐藏


class ClickableSlider(Slider):
    """可点击的进度条"""
    def __init__(self, orientation):
        super().__init__(orientation)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            click_pos = event.position().x()
            slider_width = self.width()
            
            if slider_width > 0 and self.maximum() > self.minimum():
                percentage = max(0, min(1, click_pos / slider_width))
                value_range = self.maximum() - self.minimum()
                new_value = self.minimum() + int(percentage * value_range)
                new_value = max(self.minimum(), min(self.maximum(), new_value))
                
                self.setValue(new_value)
                self.valueChanged.emit(new_value)
        
        super().mousePressEvent(event)


class OpenCVVideoPlayer(QWidget):
    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.video_thread = None
        self.audio_player = None
        self.audio_output = None
        self.is_seeking = False
        
        self.init_ui()
        self.init_media()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # 确保能接收键盘事件

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("OpenCV Video Player")
        self.setMinimumSize(900, 650)
        self.setStyleSheet("background: #1e1e1e;")
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # 视频和控制区域布局
        video_control_layout = QHBoxLayout()
        
        # 视频显示区域
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("background: black; border: 1px solid #333;")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setScaledContents(True)
        self.video_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # 右侧控制面板
        control_panel = QWidget()
        control_panel.setFixedWidth(80)
        control_panel.setStyleSheet("background: rgba(30, 30, 30, 0.8); border-radius: 8px;")
        
        control_layout = QVBoxLayout(control_panel)
        control_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        control_layout.setSpacing(20)
        
        # 音量标签
        volume_label = QLabel("音量")
        volume_label.setStyleSheet("color: white; font-size: 12px; font-weight: bold;")
        volume_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 音量滑动条
        self.volume_slider = VolumeSlider()
        self.volume_slider.valueChanged.connect(self.on_volume_change)
        
        # 音量数值显示
        self.volume_value_label = QLabel("70%")
        self.volume_value_label.setStyleSheet("color: white; font-size: 11px;")
        self.volume_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        control_layout.addStretch()
        control_layout.addWidget(volume_label)
        control_layout.addWidget(self.volume_slider)
        control_layout.addWidget(self.volume_value_label)
        control_layout.addStretch()
        
        # 添加视频和控制面板到水平布局
        video_control_layout.addWidget(self.video_label, 1)
        video_control_layout.addWidget(control_panel)
        
        # 进度条
        self.progress_slider = ClickableSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setFixedHeight(25)
        self.progress_slider.setRange(0, 0)
        self.progress_slider.valueChanged.connect(self.on_position_change)
        self.progress_slider.sliderPressed.connect(lambda: setattr(self, 'is_seeking', True))
        self.progress_slider.sliderReleased.connect(self.on_seek_finished)
        
        # 时间显示
        time_layout = QHBoxLayout()
        self.current_time_label = QLabel("00:00")
        self.total_time_label = QLabel("00:00")
        self.current_time_label.setStyleSheet("color: white; font-size: 12px;")
        self.total_time_label.setStyleSheet("color: white; font-size: 12px;")
        
        time_layout.addWidget(self.current_time_label)
        time_layout.addStretch()
        time_layout.addWidget(self.total_time_label)
        
        # 音量指示器（覆盖在视频上）
        self.volume_indicator = VolumeIndicator()
        
        # 添加到主布局
        main_layout.addLayout(video_control_layout, 1)
        main_layout.addWidget(self.progress_slider)
        main_layout.addLayout(time_layout)
        
        # 设置音量指示器位置（需要在show事件中调整）
        self.volume_indicator.setParent(self)

    def showEvent(self, event):
        """窗口显示时调整音量指示器位置"""
        super().showEvent(event)
        # 将音量指示器放在视频区域右上角
        video_rect = self.video_label.geometry()
        indicator_x = video_rect.right() - self.volume_indicator.width() - 20
        indicator_y = video_rect.top() + 20
        self.volume_indicator.move(indicator_x, indicator_y)

    def init_media(self):
        """初始化媒体播放"""
        if not os.path.exists(self.video_path):
            print(f"视频文件不存在: {self.video_path}")
            return
        
        # 初始化视频线程
        self.video_thread = VideoThread(self.video_path)
        self.video_thread.frameReady.connect(self.update_frame)
        self.video_thread.positionChanged.connect(self.update_position)
        self.video_thread.durationChanged.connect(self.update_duration)
        
        # 初始化音频播放（用于音量控制）
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(0.7)
        self.audio_player = QMediaPlayer()
        self.audio_player.setAudioOutput(self.audio_output)
        
        # 开始播放
        self.video_thread.play()

    def update_frame(self, frame):
        """更新视频帧"""
        try:
            # 转换OpenCV图像为Qt图像
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            
            # 显示图像
            pixmap = QPixmap.fromImage(qt_image)
            self.video_label.setPixmap(pixmap)
        except Exception as e:
            print(f"更新帧时出错: {e}")

    def update_position(self, position_ms):
        """更新播放位置"""
        if not self.is_seeking:
            self.progress_slider.setValue(position_ms)
            self.current_time_label.setText(self.format_time(position_ms))

    def update_duration(self, duration_ms):
        """更新总时长"""
        self.progress_slider.setRange(0, duration_ms)
        self.total_time_label.setText(self.format_time(duration_ms))

    def on_position_change(self, position):
        """处理位置变化"""
        if not self.is_seeking and self.video_thread:
            self.video_thread.seek_to_position(position)

    def on_seek_finished(self):
        """拖拽结束处理"""
        self.is_seeking = False
        if self.video_thread:
            self.video_thread.seek_to_position(self.progress_slider.value())

    def on_volume_change(self, volume):
        """音量变化处理"""
        if self.audio_output:
            self.audio_output.setVolume(volume / 100.0)
        self.volume_value_label.setText(f"{volume}%")
        self.volume_indicator.show_volume(volume)

    def format_time(self, ms):
        """格式化时间显示"""
        seconds = ms // 1000
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        if hours > 0:
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        return f"{minutes:02}:{seconds:02}"

    def wheelEvent(self, event):
        """滚轮事件 - 调节音量"""
        delta = event.angleDelta().y()
        current_volume = self.volume_slider.value()
        
        if delta > 0:
            new_volume = min(100, current_volume + 5)
        else:
            new_volume = max(0, current_volume - 5)
        
        self.volume_slider.setValue(new_volume)
        event.accept()

    def keyPressEvent(self, event):
        """键盘快捷键"""
        if not self.video_thread:
            return
            
        if event.key() == Qt.Key.Key_Space:
            self.toggle_play()
        elif event.key() == Qt.Key.Key_Left:
            self.seek(-5000)  # 后退5秒
        elif event.key() == Qt.Key.Key_Right:
            self.seek(5000)   # 前进5秒
        elif event.key() == Qt.Key.Key_Up:
            # 音量增加
            current_volume = min(100, self.volume_slider.value() + 10)
            self.volume_slider.setValue(current_volume)
        elif event.key() == Qt.Key.Key_Down:
            # 音量减小
            current_volume = max(0, self.volume_slider.value() - 10)
            self.volume_slider.setValue(current_volume)
        else:
            super().keyPressEvent(event)

    def toggle_play(self):
        """切换播放状态"""
        if not self.video_thread:
            return
            
        if self.video_thread.is_paused:
            self.video_thread.resume()
        else:
            self.video_thread.pause()

    def seek(self, ms):
        """跳转指定毫秒数"""
        if not self.video_thread:
            return
            
        current_pos = self.progress_slider.value()
        max_pos = self.progress_slider.maximum()
        new_pos = max(0, min(current_pos + ms, max_pos))
        self.progress_slider.setValue(new_pos)
        self.video_thread.seek_to_position(new_pos)

    def closeEvent(self, event):
        """窗口关闭时清理资源"""
        if self.video_thread:
            self.video_thread.stop()
            self.video_thread.wait()
        if self.audio_player:
            self.audio_player.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 测试视频路径 - 请替换为你的视频文件路径
    video_path =  "G:/Nyotengu/LazyProcrast/1080P_4000K_289668092.mp4"  # 替换为实际路径
    
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    
    player = OpenCVVideoPlayer(video_path)
    player.show()
    
    sys.exit(app.exec())