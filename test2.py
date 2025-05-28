
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QApplication, QFileDialog,
    QLabel, QHBoxLayout, QSlider, QGridLayout, QHeaderView, QTableWidgetItem
)
from PyQt6.QtCore import Qt, QUrl, QTimer, QSize
from PyQt6.QtMultimedia import QMediaPlayer, QMediaMetaData
from PyQt6.QtMultimediaWidgets import QVideoWidget
from qfluentwidgets import (
    CardWidget, BodyLabel, FluentWindow, PushButton,
    InfoBar, InfoBarIcon, InfoBarPosition,
    SubtitleLabel, LineEdit, ComboBox, TableWidget, FluentIcon

)
from qfluentwidgets.multimedia import VideoWidget, MediaPlayer
import ffmpeg
import cv2
import sys
import os
import keyboard
import subprocess
import tempfile
from datetime import datetime


class VideoInterface(QWidget):

    def __init__(self):
        super().__init__()

        self.setObjectName("视频剪辑")
        self.setWindowTitle("视频剪辑工具")
        self.resize(800, 600)  # 设置初始窗口大小
        self.setWindowIcon(FluentIcon.VIDEO.icon())
        # 初始化变量
        self.video_path = ""
        self.time_segments = []  # 剪切时间段列表，存储多个时间片段
        self.current_time = "00:00:00"  # 当前播放时间
        self.temp_start_time = "00:00:00"  # 临时开始时间
        self.temp_end_time = "00:00:00"  # 临时结束时间
        self.temp_time_stamp = ["00:00:01", "00:00:03"]  # 临时时间戳

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
        self.video_widget.resize(720, 480)
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
        self.temp_time_label = BodyLabel(
            f"时间段: {self.temp_start_time} - {self.temp_end_time}")
        self.time_segment_card_layout.addWidget(self.temp_time_label)

        # 添加时间片段按钮
        self.add_segment_button = PushButton("添加时间片段", self.time_segment_card)
        self.add_segment_button.clicked.connect(self.add_time_segment)
        self.time_segment_card_layout.addWidget(self.add_segment_button)

        # 显示已添加的时间片段
        self.segments_label = TableWidget()
        self.segments_label.setBorderRadius(8)  # 设置圆角
        self.segments_label.resizeColumnsToContents()  # 设置可调整大小True)  # 设置可调整大小
        self.segments_label.setBorderVisible(True)  # 设置边框可见
        # 设置表头填充
        self.segments_label.setRowCount(5)  # 设置行数
        # self.segments_label.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)#填充满
        # 设置表头
        self.segments_label.setColumnCount(2)  # 设置列数
        self.segments_label.setHorizontalHeaderLabels(["开始时间", "结束时间"])  # 设置表头
        # 添加进布局
        self.time_segment_card_layout.addWidget(self.segments_label)

        # 清空所有片段按钮
        self.clear_all_button = PushButton("清空所有片段", self.time_segment_card)
        self.clear_all_button.clicked.connect(self.clear_all_segments)
        self.time_segment_card_layout.addWidget(self.clear_all_button)

        # 生成ffmpeg命令按钮
        self.generate_ffmpeg_button = PushButton(
            "生成FFmpeg命令", self.time_segment_card)
        self.generate_ffmpeg_button.clicked.connect(
            self.generate_ffmpeg_command)
        self.time_segment_card_layout.addWidget(self.generate_ffmpeg_button)

        # 执行剪辑按钮
        self.execute_cut_button = PushButton("执行视频剪辑", self.time_segment_card)
        self.execute_cut_button.clicked.connect(self.execute_video_cut)
        self.time_segment_card_layout.addWidget(self.execute_cut_button)

        # 添加测试按钮用于调试
        debug_button = PushButton("调试信息", self.time_segment_card)
        debug_button.clicked.connect(self.debug_video_widget)
        self.time_segment_card_layout.addWidget(debug_button)

        # 添加时间段选择卡片到主布局
        layout.addWidget(self.time_segment_card)

    def debug_video_widget(self):
        """调试VideoWidget的属性和方法"""
        print("=== VideoWidget 调试信息 ===")
        print(f"VideoWidget 类型: {type(self.video_widget)}")
        print(f"VideoWidget 属性: {dir(self.video_widget)}")

        # 检查是否有媒体播放器相关属性
        attrs_to_check = ['mediaPlayer', 'player', '_player', 'media_player',
                          'position', 'duration', 'state', 'playbackState']

        for attr in attrs_to_check:
            if hasattr(self.video_widget, attr):
                try:
                    value = getattr(self.video_widget, attr)
                    print(f"找到属性 {attr}: {value} (类型: {type(value)})")

                    # 如果是媒体播放器对象，进一步检查
                    if hasattr(value, 'position'):
                        pos = value.position()
                        print(f"  - position(): {pos}")
                    if hasattr(value, 'duration'):
                        dur = value.duration()
                        print(f"  - duration(): {dur}")

                except Exception as e:
                    print(f"访问属性 {attr} 时出错: {e}")

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
        try:
            position = None
            # 尝试多种方式获取当前播放位置
            if hasattr(self.video_widget, 'player'):
                player = self.video_widget.player
                if player and hasattr(player, 'position'):
                    position = player.position()

            # 更新时间显示
            if position is not None:
                self.current_time = self.ms_to_time_string(position)
                self.current_time_label.setText(f"当前时间: {self.current_time}")

        except Exception as e:
            # 静默处理错误，避免频繁的错误信息
            pass

    def set_start_time(self):
        """ 设置开始时间 """
        if self.current_time and self.current_time != "00:00:00":
            self.temp_start_time = self.current_time
            self.update_temp_time_display()

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
            self.update_temp_time_display()

            InfoBar.success(
                title="结束时间已设置",
                content=f"结束时间: {self.temp_end_time}",
                parent=self,
                duration=2000,
                position=InfoBarPosition.BOTTOM_RIGHT
            )

    def update_temp_time_display(self):
        """ 更新临时时间戳显示 """
        self.temp_time_stamp = [self.temp_start_time, self.temp_end_time]
        self.temp_time_label.setText(
            f"临时时间段: {self.temp_start_time} - {self.temp_end_time}")

    def add_time_segment(self):
        """ 添加时间片段到列表中 """
        if self.temp_start_time != "00:00:00" and self.temp_end_time != "00:00:00":
            # 验证时间顺序
            if self.time_to_seconds(self.temp_start_time) > self.time_to_seconds(self.temp_end_time):
                InfoBar.error(
                    title="时间错误",
                    content="开始时间不得小于结束时间！",
                    parent=self,
                    duration=3000,
                    position=InfoBarPosition.BOTTOM_RIGHT
                )
                return

            # 添加时间片段
            segment = (self.temp_start_time, self.temp_end_time)
            self.time_segments.append(segment)

            # 更新显示
            self.update_segments_display()

            # 清空临时时间戳
            self.clear_temp_timestamp()

            InfoBar.success(
                title="片段已添加",
                content=f"时间片段 {segment[0]} - {segment[1]} 已添加到列表",
                parent=self,
                duration=2000,
                position=InfoBarPosition.BOTTOM_RIGHT
            )
        else:
            InfoBar.warning(
                title="时间未设置",
                content="请先设置开始时间和结束时间！",
                parent=self,
                duration=2000,
                position=InfoBarPosition.BOTTOM_RIGHT
            )

    def clear_temp_timestamp(self):
        """ 清空临时时间戳 """
        self.temp_start_time = "00:00:00"
        self.temp_end_time = "00:00:00"
        self.temp_time_stamp = ["00:00:00", "00:00:00"]
        self.update_temp_time_display()

    def clear_all_segments(self):
        """ 清空所有时间片段 """
        self.time_segments.clear()
        self.update_segments_display()

        InfoBar.info(
            title="片段已清空",
            content="所有时间片段已清空",
            parent=self,
            duration=2000,
            position=InfoBarPosition.BOTTOM_RIGHT
        )

    def update_segments_display(self):
        """ 更新时间片段列表显示 """
        if self.time_segments:
            for i, songInfo in enumerate(self.time_segments):
                for j in range(2):
                    self.segments_label.setItem(
                        i, j, QTableWidgetItem(songInfo[j]))

        else:
            # self.segments_label.setText("时间片段列表: 无")
            self.segments_label.setAcceptDrops(on=False)

    def time_to_seconds(self, time_str):
        """ 将时间字符串转换为秒数 """
        try:
            h, m, s = map(int, time_str.split(':'))
            return h * 3600 + m * 60 + s
        except:
            return 0

    def generate_ffmpeg_command(self):
        """ 生成FFmpeg命令 """
        if not self.video_path:
            InfoBar.warning(
                title="未选择视频",
                content="请先选择视频文件！",
                parent=self,
                duration=2000,
                position=InfoBarPosition.BOTTOM_RIGHT
            )
            return

        if not self.time_segments:
            InfoBar.warning(
                title="无时间片段",
                content="请先添加时间片段！",
                parent=self,
                duration=2000,
                position=InfoBarPosition.BOTTOM_RIGHT
            )
            return

        # 生成输出文件名
        input_name = os.path.splitext(os.path.basename(self.video_path))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(os.path.dirname(
            self.video_path), f"{input_name}_剪辑_{timestamp}.mp4")

    def generate_multi_segment_command(self, output_path):
        """ 生成多片段FFmpeg命令 """
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()

        # 生成各个片段的命令
        segment_files = []
        commands = []

        for i, (start, end) in enumerate(self.time_segments):
            duration = self.time_to_seconds(end) - self.time_to_seconds(start)
            segment_file = os.path.join(temp_dir, f"segment_{i+1}.mp4")
            segment_files.append(segment_file)

            cmd = f'ffmpeg -i "{self.video_path}" -ss {start} -t {duration} -c copy "{segment_file}"'
            commands.append(cmd)

        # 创建文件列表
        filelist_path = os.path.join(temp_dir, "filelist.txt")
        with open(filelist_path, 'w', encoding='utf-8') as f:
            for segment_file in segment_files:
                f.write(f"file '{segment_file}'\n")

        # 合并命令
        concat_cmd = f'ffmpeg -f concat -safe 0 -i "{filelist_path}" -c copy "{output_path}"'

        # 完整的批处理命令
        full_command = '\n'.join(commands) + '\n' + concat_cmd

        return full_command

    def execute_video_cut(self):
        """ 执行视频剪辑 """
        if not self.video_path or not self.time_segments:
            InfoBar.warning(
                title="条件不满足",
                content="请先选择视频文件并添加时间片段！",
                parent=self,
                duration=2000,
                position=InfoBarPosition.BOTTOM_RIGHT
            )
            return

        try:
            ffmpeg_cmd = self.generate_ffmpeg_command()

            # 这里可以添加实际执行FFmpeg的逻辑
            # 注意：实际执行时可能需要更复杂的处理
            InfoBar.info(
                title="准备执行",
                content="FFmpeg命令已准备就绪，请手动执行或集成到您的系统中",
                parent=self,
                duration=3000,
                position=InfoBarPosition.BOTTOM_RIGHT
            )

        except Exception as e:
            InfoBar.error(
                title="执行失败",
                content=f"生成命令时出错: {str(e)}",
                parent=self,
                duration=3000,
                position=InfoBarPosition.BOTTOM_RIGHT
            )

    def toggle_play_pause(self):
        """ 切换视频的播放/暂停状态 """
        try:
            # 尝试多种方式控制播放/暂停
            if hasattr(self.video_widget, 'player'):
                player = self.video_widget.player
                if player:
                    if hasattr(player, 'playbackState'):
                        if player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                            player.pause()
                            self.stop_label.setText("播放")
                        else:
                            player.play()
                            self.stop_label.setText("暂停")
                        return

        except Exception as e:
            print(f"播放控制出错: {e}")

    def adjust_window_to_video_size(self):
        """调整窗口大小以适应视频比例"""

        print("调整窗口大小")
        try:
            # 获取视频尺寸
            from moviepy import VideoFileClip

            clip = VideoFileClip(self.video_path)

            # resolution 是一个元组 (width, height)
            width, height = clip.size
            clip.close()
            print(f"视频尺寸: {width} x {height}")
            self.video_widget.resize(width, height)
            self.resize(1200, height)
            self.center_window()
        except Exception as e:
            print(f"调整窗口大小时出错: {e}")

    def open_video_file_dialog(self):
        """ 打开视频文件选择对话框 """
        # 使用 QFileDialog.getOpenFileName() 来获取单个文件路径
        # self 作为父窗口，对话框标题，初始目录，文件过滤器

        # self.video_widget.close()

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择视频文件",
            "G:/Nyotengu/LazyProcrast",  # 默认打开目录
            "视频文件 (*.mp4 *.avi *.mov *.mkv);;所有文件 (*.*)"
        )

        if file_path:
            print(f"选中的文件是: {file_path}")
            # 保存视频路径
            self.video_path = file_path

            # 视频预览 - 使用原来的方式
            self.video_widget.setVideo(QUrl.fromLocalFile(self.video_path))
            # 调整窗口大小
            self.adjust_window_to_video_size()
            self.video_widget.play()

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

    def center_window(self):
        """
        将窗口居中显示在屏幕上。
        """
        # 获取屏幕的可用几何尺寸 (排除任务栏等)
        primary_screen = QApplication.primaryScreen()

        # currentScreen() 返回当前的 QScreen 对象
        # availableGeometry() 返回屏幕可用的矩形区域
        if primary_screen:
            screen_geometry = primary_screen.availableGeometry()

            # 获取窗口自身的几何尺寸
            # frameGeometry() 返回包含窗口边框的矩形
            window_geometry = self.frameGeometry()

            # 计算居中位置
            # screen_geometry.center() 获取屏幕中心的点
            # move() 方法将窗口的左上角移动到新的位置
            # 因此，我们需要将窗口的中心点移动到屏幕的中心点
            window_geometry.moveCenter(screen_geometry.center())

            # 将窗口移动到计算出的位置
            self.move(window_geometry.topLeft())
        else:
            print("警告: 无法获取主屏幕信息，窗口可能无法居中。")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = VideoInterface()
    w.center_window()
    w.show()
    sys.exit(app.exec())
