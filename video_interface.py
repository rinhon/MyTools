from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QApplication, QFileDialog,
    QLabel, QHBoxLayout, QSlider, QGridLayout
)
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from qfluentwidgets import (
    CardWidget, BodyLabel, FluentWindow, PushButton,
    InfoBar, InfoBarIcon, InfoBarPosition,
    SubtitleLabel, LineEdit, ComboBox,

)
from qfluentwidgets.multimedia import VideoWidget, MediaPlayer

import sys, os, keyboard


class VideoInterface(QWidget):

    def __init__(self):
        super().__init__()

        self.setObjectName("视频剪辑")
        self.setWindowTitle("视频剪辑工具")
        self.resize(800, 600)  # 设置窗口大小

        # 初始化变量
        self.video_path = ""
        self.time_segments = []  # 剪切时间段
        self.current_time = "00:00:00"  # 当前时间
        self.temp_start_time = "00:00:00"  # 临时开始时间
        self.temp_end_time = "00:00:00"  # 临时结束时间
        self.temp_time_stamp = ("00:00:00", "00:00:00")  # 临时时间戳
        
        # 创建媒体播放器实例
        self.media_player = MediaPlayer()
        
        # 创建定时器用于更新当前时间
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_current_time)
        self.timer.start(100)  # 每100ms更新一次
        
        self.setup_ui()

    def setup_ui(self):
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)  # 设置布局的边距
        layout.setSpacing(15)  # 设置控件之间的间距

        # 视频选择
        # 第一层
        card_video_select = CardWidget()
        # 创建卡片的布局
        card_layout = QVBoxLayout(card_video_select)
        video_select_title = BodyLabel("视频选择", card_video_select)

        card_layout.addWidget(video_select_title)

        # 用于显示选中的文件路径
        self.selected_file_label = BodyLabel("未选择任何文件", card_video_select)
        card_layout.addWidget(self.selected_file_label)

        # 创建一个 Fluent 风格的按钮
        select_video_button = PushButton("选择视频文件", card_video_select)
        # 连接按钮的点击事件到槽函数
        select_video_button.clicked.connect(self.open_video_file_dialog)
        card_layout.addWidget(select_video_button)

        # 将卡片添加到主布局
        layout.addWidget(card_video_select)

        # 初始化视频预览组件
        self.video_preview_card = CardWidget()
        self.video_preview_layout = QVBoxLayout(self.video_preview_card)
        self.video_preview_title = SubtitleLabel("视频预览")
        self.video_preview_layout.addWidget(self.video_preview_title)

        self.video_widget = VideoWidget(self.video_preview_card)
        # 将媒体播放器与视频组件关联
        # self.video_widget.setVideo()
        self.video_preview_layout.addWidget(self.video_widget)

        # 添加视频预览卡片到主布局
        layout.addWidget(self.video_preview_card)

        # 时间段选择
        self.time_segment_card = CardWidget()
        self.time_segment_card_layout = QVBoxLayout(self.time_segment_card)
        
        # 添加标题
        time_segment_title = SubtitleLabel("时间段选择")
        self.time_segment_card_layout.addWidget(time_segment_title)
        
        # 显示当前时间的标签
        self.current_time_label = BodyLabel(f"当前时间: {self.current_time}")
        self.time_segment_card_layout.addWidget(self.current_time_label)
        
        # 暂停按钮
        self.stop_label = PushButton("暂停", self.time_segment_card)
        self.stop_label.clicked.connect(self.toggle_play_pause)
        self.time_segment_card_layout.addWidget(self.stop_label)

        # 创建按钮，使用正确的父组件
        self.start_time_label = PushButton("选择开始时间", self.time_segment_card)
        self.start_time_label.clicked.connect(self.set_start_time)
        self.end_time_label = PushButton("选择结束时间", self.time_segment_card)
        self.end_time_label.clicked.connect(self.set_end_time)
        
        # 将按钮添加到布局中
        self.time_segment_card_layout.addWidget(self.start_time_label)
        self.time_segment_card_layout.addWidget(self.end_time_label)
        
        # 显示临时时间段
        self.temp_time_label = BodyLabel(f"临时时间段: {self.temp_start_time} - {self.temp_end_time}")
        self.time_segment_card_layout.addWidget(self.temp_time_label)
        
        # 添加时间段选择卡片到主布局
        layout.addWidget(self.time_segment_card)

    def ms_to_time_string(self, ms):
        """将毫秒转换为时间字符串格式 HH:MM:SS"""
        if ms < 0:
            return "00:00:00"
        
        seconds = ms // 1000
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def update_current_time(self):
        """更新当前播放时间"""
        if self.media_player:
            # 获取当前播放位置（毫秒）
            position = self.media_player.position()
            self.current_time = self.ms_to_time_string(position)
            
            # 更新界面显示
            self.current_time_label.setText(f"当前时间: {self.current_time}")

    def set_start_time(self):
        """ 设置开始时间 """
        if self.current_time and self.current_time != "00:00:00":
            self.temp_start_time = self.current_time
            self.temp_time_label.setText(f"临时时间段: {self.temp_start_time} - {self.temp_end_time}")
            
            InfoBar.success(
                title="开始时间已设置",
                content=f"开始时间: {self.temp_start_time}",
                parent=self,
                duration=2000,
                position=InfoBarPosition.BOTTOM_RIGHT
            )

    def set_end_time(self):
        """ 设置结束时间 """
        if self.current_time and self.current_time != "00:00:00":
            self.temp_end_time = self.current_time
            self.temp_time_label.setText(f"临时时间段: {self.temp_start_time} - {self.temp_end_time}")
            
            InfoBar.success(
                title="结束时间已设置",
                content=f"结束时间: {self.temp_end_time}",
                parent=self,
                duration=2000,
                position=InfoBarPosition.BOTTOM_RIGHT
            )

    def toggle_play_pause(self):
        """ 切换视频的播放/暂停状态 """
        if self.media_player:
            if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                self.media_player.pause()
                self.stop_label.setText("播放")
            else:
                self.media_player.play()
                self.stop_label.setText("暂停")

    def open_video_file_dialog(self):
        """ 打开视频文件选择对话框 """
        # 使用 QFileDialog.getOpenFileName() 来获取单个文件路径
        # self 作为父窗口，对话框标题，初始目录，文件过滤器
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择视频文件",
            "C:/Users/90708/Videos",  # 默认打开目录
            "视频文件 (*.mp4 *.avi *.mov *.mkv);;所有文件 (*.*)"
        )

        if file_path:
            print(f"选中的文件是: {file_path}")
            # 保存视频路径
            self.video_path = file_path

            # 设置媒体源并播放
            self.media_player.setSource(QUrl.fromLocalFile(self.video_path))
            self.video_widget.setVideo(self.media_player.source())
            self.media_player.play()
            
            # 更新选中的文件路径显示
            self.selected_file_label.setText(
                f"已选择: {os.path.basename(file_path)}")
            InfoBar.success(
                title="文件选择成功",
                content=f"已选择: {file_path}",
                parent=self,
                duration=3000,  # 显示3秒后自动消失
                position=InfoBarPosition.BOTTOM_RIGHT
            )

        else:
            print("取消选择文件")
            # 显示一个提示，表示用户取消了选择
            InfoBar.warning(
                title="未选择文件",
                content="您取消了文件选择。",
                parent=self,
                duration=2000,
                position=InfoBarPosition.BOTTOM_RIGHT
            )
            # 重置文件路径显示
            self.selected_file_label.setText("未选择任何文件")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = VideoInterface()
    w.show()
    sys.exit(app.exec())