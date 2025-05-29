
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QApplication, QFileDialog,
    QLabel, QHBoxLayout, QSlider, QGridLayout, QHeaderView, QTableWidgetItem,
    QMenu, QToolTip
)
from PyQt6.QtGui import QCursor
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from qfluentwidgets import (
    CardWidget, BodyLabel, FluentWindow, PushButton,
    InfoBar, InfoBarIcon, InfoBarPosition,
    SubtitleLabel, LineEdit, ComboBox, TableWidget, PrimaryToolButton, FluentIcon,PrimaryPushButton 
)
from qfluentwidgets.multimedia import VideoWidget, MediaPlayer
from video_test import DarkMediaPlayer
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
        self.resize(800, 600)  # 设置窗口大小

        # 初始化变量
        self.video_path = ""
        self.time_segments = []  # 剪切时间段列表，存储多个时间片段
        self.current_time = "00:00:00"  # 当前播放时间

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

        # self.video_widget = VideoWidget(self.video_preview_card)
        self.video_widget = None
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
        self.stop_label = PrimaryToolButton(
            FluentIcon.PAUSE, self.time_segment_card)
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

        # # 添加清除当前行按钮
        # self.clear_current_button = PushButton("清除当前行", self.time_segment_card)
        # self.clear_current_button.clicked.connect(self.clear_current_row)
        # self.time_segment_card_layout.addWidget(self.clear_current_button)

        # # 添加时间片段按钮
        # self.add_segment_button = PushButton("添加时间片段", self.time_segment_card)
        # self.add_segment_button.clicked.connect(self.add_time_segment)
        # self.time_segment_card_layout.addWidget(self.add_segment_button)

        # 初始化时间片段表格
        self.segments_label = TableWidget()

        # 设置基本属性
        self.segments_label.setBorderRadius(8)  # 设置圆角
        self.segments_label.setMinimumHeight(200)  # 设置最小高度
        self.segments_label.setColumnCount(2)  # 设置列数
        self.segments_label.setHorizontalHeaderLabels(['开始时间', '结束时间'])  # 设置表头

        # 隐藏垂直表头（行号）
        self.segments_label.verticalHeader().setVisible(False)

        # 设置表格大小调整策略
        self.segments_label.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)  # 列宽自适应
        self.segments_label.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Fixed)  # 固定行高
        self.segments_label.verticalHeader().setDefaultSectionSize(40)  # 设置默认行高

        # 设置表格属性
        self.segments_label.setBorderVisible(True)  # 设置边框可见
        self.segments_label.setRowCount(5)  # 设置初始行数
        self.segments_label.setEditTriggers(
            TableWidget.EditTrigger.NoEditTriggers)  # 禁止编辑
        self.segments_label.setSelectionMode(
            TableWidget.SelectionMode.SingleSelection)  # 单行选择
        self.segments_label.setSelectionBehavior(
            TableWidget.SelectionBehavior.SelectRows)  # 选择整行
        self.segments_label.setAlternatingRowColors(True)  # 启用交替行颜色

        # 优化表格性能
        self.segments_label.setVerticalScrollMode(
            TableWidget.ScrollMode.ScrollPerPixel)  # 像素级滚动
        self.segments_label.setHorizontalScrollMode(
            TableWidget.ScrollMode.ScrollPerPixel)

        # 设置表头和单元格样式
        self.segments_label.horizontalHeader().setStretchLastSection(True)  # 最后一列自动填充
        self.segments_label.horizontalHeader().setDefaultAlignment(
            Qt.AlignmentFlag.AlignCenter)  # 表头居中对齐

        # 设置表格样式
        self.segments_label.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                gridline-color: #e0e0e0;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 6px;
                border: none;
                border-bottom: 1px solid #e0e0e0;
                font-weight: bold;
                color: #424242;
            }
            QTableWidget::item {
                padding: 6px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QTableWidget::item:hover {
                background-color: #f5f5f5;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #f5f5f5;
                border: none;
            }
        """)

        # 设置空表格提示文本
        # self.segments_label.setPlaceholderText("暂无时间片段")

        # 设置单元格文本居中对齐
        def set_item_alignment(row, column, item):
            if item:
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        self.segments_label.itemChanged.connect(
            lambda item: set_item_alignment(item.row(), item.column(), item))

        # 添加右键菜单
        self.segments_label.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu)
        self.segments_label.customContextMenuRequested.connect(
            self.show_context_menu)

        # 添加双击事件
        self.segments_label.cellDoubleClicked.connect(
            self.on_segment_double_clicked)
        # 设置表头
        self.segments_label.setColumnCount(2)  # 设置列数
        self.segments_label.setHorizontalHeaderLabels(["开始时间", "结束时间"])  # 设置表头
        # 添加进布局
        self.time_segment_card_layout.addWidget(self.segments_label)

        # 清空所有片段按钮
        self.clear_all_button = PushButton("清空所有片段", self.time_segment_card)
        self.clear_all_button.clicked.connect(self.clear_all_segments)
        self.time_segment_card_layout.addWidget(self.clear_all_button)

        # 命令执行卡片
        self.command_card = CardWidget()
        # 水平布局
        self.command_layout = QHBoxLayout(self.command_card)
        # 生成ffmpeg命令按钮
        self.generate_ffmpeg_button = PrimaryPushButton ("生成FFmpeg命令", self.command_card)
        self.generate_ffmpeg_button.clicked.connect(self.generate_ffmpeg_command)
        self.command_layout.addWidget(self.generate_ffmpeg_button)

        # 执行剪辑按钮
        self.execute_cut_button = PrimaryPushButton ("执行视频剪辑", self.command_card)
        self.execute_cut_button.clicked.connect(self.execute_video_cut)
        self.command_layout.addWidget(self.execute_cut_button)

        # 添加时间段选择卡片到主布局
        layout.addWidget(self.time_segment_card)
        layout.addWidget(self.command_card)

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
        if not self.video_widget:
            return

        try:
            # 获取当前视频时间
            current_ms = self.video_widget.get_current_time()
            if current_ms is not None:
                self.current_time = self.ms_to_time_string(current_ms)
                self.current_time_label.setText(f"当前时间: {self.current_time}")
        except Exception as e:
            # 静默处理错误，避免频繁的错误信息
            pass

    def set_start_time(self):
        """ 设置开始时间 """
        if not self.video_widget:
            InfoBar.warning(
                title="无法设置时间",
                content="请先选择视频文件",
                parent=self,
                duration=2000,
                position=InfoBarPosition.BOTTOM_RIGHT
            )
            return

        # 获取当前视频时间
        current_ms = self.video_widget.get_current_time()
        if current_ms is None:
            return

        current_time = self.ms_to_time_string(current_ms)
        if current_time == "00:00:00":
            return

        # 获取表格当前行
        row = self.segments_label.rowCount() - 1
        while row >= 0:
            start_item = self.segments_label.item(row, 0)
            end_item = self.segments_label.item(row, 1)

            # 如果找到一行已经有结束时间但没有开始时间，不允许设置
            if not start_item and end_item:
                InfoBar.warning(
                    title="操作无效",
                    content="请先清除当前行的结束时间",
                    parent=self,
                    duration=2000,
                    position=InfoBarPosition.BOTTOM_RIGHT
                )
                return

            # 如果找到一行已经有开始时间但没有结束时间，不允许设置新的开始时间
            if start_item and not end_item:
                InfoBar.warning(
                    title="操作无效",
                    content="请先设置当前行的结束时间",
                    parent=self,
                    duration=2000,
                    position=InfoBarPosition.BOTTOM_RIGHT
                )
                return

            # 如果找到空行，设置开始时间
            if not start_item and not end_item:
                item = QTableWidgetItem(current_time)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.segments_label.setItem(row, 0, item)

                InfoBar.success(
                    title="开始时间已设置",
                    content=f"开始时间: {current_time}",
                    parent=self,
                    duration=2000,
                    position=InfoBarPosition.BOTTOM_RIGHT
                )
                return

            row -= 1

        # 如果所有行都已填满，添加新行
        row = self.segments_label.rowCount()
        self.segments_label.setRowCount(row + 1)
        item = QTableWidgetItem(current_time)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.segments_label.setItem(row, 0, item)

        InfoBar.success(
            title="开始时间已设置",
            content=f"开始时间: {current_time}",
            parent=self,
            duration=2000,
            position=InfoBarPosition.BOTTOM_RIGHT
        )

    def set_end_time(self):
        """ 设置结束时间 """
        if not self.video_widget:
            InfoBar.warning(
                title="无法设置时间",
                content="请先选择视频文件",
                parent=self,
                duration=2000,
                position=InfoBarPosition.BOTTOM_RIGHT
            )
            return

        # 获取当前视频时间
        current_ms = self.video_widget.get_current_time()
        if current_ms is None:
            return

        current_time = self.ms_to_time_string(current_ms)
        if current_time == "00:00:00":
            return

        # 查找有开始时间但没有结束时间的行
        row = 0
        found = False
        while row < self.segments_label.rowCount():
            start_item = self.segments_label.item(row, 0)
            end_item = self.segments_label.item(row, 1)

            if start_item and not end_item:
                found = True
                start_time = start_item.text()

                # 检查结束时间是否大于开始时间
                if self.time_to_seconds(current_time) <= self.time_to_seconds(start_time):
                    InfoBar.warning(
                        title="时间错误",
                        content="结束时间必须大于开始时间",
                        parent=self,
                        duration=2000,
                        position=InfoBarPosition.BOTTOM_RIGHT
                    )
                    return

                # 设置结束时间
                item = QTableWidgetItem(current_time)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.segments_label.setItem(row, 1, item)

                # 将此行添加到时间片段列表
                self.time_segments.append((start_time, current_time))

                InfoBar.success(
                    title="结束时间已设置",
                    content=f"结束时间: {current_time}",
                    parent=self,
                    duration=2000,
                    position=InfoBarPosition.BOTTOM_RIGHT
                )
                break

            row += 1

        if not found:
            InfoBar.warning(
                title="操作无效",
                content="请先设置开始时间",
                parent=self,
                duration=2000,
                position=InfoBarPosition.BOTTOM_RIGHT
            )

    # def add_time_segment(self):
    #     """ 添加时间片段到列表中 """
    #     # 遍历表格查找未完成的行
    #     for row in range(self.segments_label.rowCount()):
    #         start_item = self.segments_label.item(row, 0)
    #         end_item = self.segments_label.item(row, 1)

    #         # 如果找到一行同时有开始和结束时间，但还未添加到time_segments中
    #         if (start_item and end_item and
    #             (start_item.text(), end_item.text()) not in self.time_segments):

    #             start_time = start_item.text()
    #             end_time = end_item.text()

    #             # 验证时间顺序（虽然在set_end_time中已经验证过，这里作为双重保险）
    #             if self.time_to_seconds(start_time) >= self.time_to_seconds(end_time):
    #                 InfoBar.error(
    #                     title="时间错误",
    #                     content="开始时间不得大于或等于结束时间！",
    #                     parent=self,
    #                     duration=3000,
    #                     position=InfoBarPosition.BOTTOM_RIGHT
    #                 )
    #                 return

    #             # 添加时间片段
    #             segment = (start_time, end_time)
    #             self.time_segments.append(segment)

    #             # 更新显示
    #             self.update_segments_display()

    #             InfoBar.success(
    #                 title="片段已添加",
    #                 content=f"时间片段 {start_time} - {end_time} 已添加到列表",
    #                 parent=self,
    #                 duration=2000,
    #                 position=InfoBarPosition.BOTTOM_RIGHT
    #             )
    #             return

    #     # 如果没有找到可添加的时间片段
    #     InfoBar.warning(
    #         title="无可添加片段",
    #         content="请先完整设置一个时间片段（包含开始和结束时间）",
    #         parent=self,
    #         duration=2000,
    #         position=InfoBarPosition.BOTTOM_RIGHT
    #     )

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

    def show_context_menu(self, position):
        """显示右键菜单"""
        menu = QMenu(self)

        # 获取当前选中的行
        row = self.segments_label.rowAt(position.y())
        if row >= 0 and row < len(self.time_segments):
            delete_action = menu.addAction("删除此时间片段")
            delete_action.triggered.connect(lambda: self.delete_segment(row))

        # 在鼠标位置显示菜单
        menu.exec(self.segments_label.viewport().mapToGlobal(position))

    def delete_segment(self, row):
        """删除指定行的时间片段"""
        if 0 <= row < len(self.time_segments):
            # 删除时间片段
            del self.time_segments[row]
            # 更新显示
            self.update_segments_display()

    def on_segment_double_clicked(self, row, column):
        """处理双击事件"""
        if row < len(self.time_segments):
            segment = self.time_segments[row]
            start_time, end_time = segment

            # 显示时间片段详细信息
            tooltip_text = f"开始时间: {start_time}\n结束时间: {end_time}"
            QToolTip.showText(
                QCursor.pos(),
                tooltip_text,
                self.segments_label
            )

    # def clear_current_row(self):
    #     """ 清除当前未完成的行 """
    #     row = 0
    #     while row < self.segments_label.rowCount():
    #         start_item = self.segments_label.item(row, 0)
    #         end_item = self.segments_label.item(row, 1)

    #         # 如果找到只有开始时间没有结束时间的行
    #         if start_item and not end_item:
    #             self.segments_label.setItem(row, 0, None)
    #             InfoBar.success(
    #                 title="已清除",
    #                 content="已清除未完成的时间片段",
    #                 parent=self,
    #                 duration=2000,
    #                 position=InfoBarPosition.BOTTOM_RIGHT
    #             )
    #             return
    #         row += 1

    def update_segments_display(self):
        """ 更新时间片段列表显示 """
        # 暂时关闭表格更新以提高性能
        self.segments_label.setUpdatesEnabled(False)

        try:
            # 清空表格内容
            self.segments_label.clearContents()

            # 计算需要的总行数：已有片段数量 + 1（用于新片段）
            needed_rows = len(self.time_segments) + 1
            # 确保至少有5行
            row_count = max(needed_rows, 5)
            self.segments_label.setRowCount(row_count)

            # 批量添加已有时间片段
            for i, segment in enumerate(self.time_segments):
                # 创建并设置单元格
                for j, text in enumerate(segment[:2]):  # 只取前两个值（开始和结束时间）
                    item = QTableWidgetItem(text)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # 居中对齐
                    item.setFlags(item.flags() & ~
                                  Qt.ItemFlag.ItemIsEditable)  # 禁止编辑
                    self.segments_label.setItem(i, j, item)

            # 清空剩余行，确保它们是空的，可以用于新的时间片段
            for i in range(len(self.time_segments), row_count):
                for j in range(2):
                    self.segments_label.setItem(i, j, None)

        finally:
            # 重新启用表格更新
            self.segments_label.setUpdatesEnabled(True)

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
        if not self.video_widget:
            return

        self.video_widget.toggle_play()
        # 更新按钮文本
        if self.video_widget.is_playing_status():
            self.stop_label = PrimaryToolButton(
                FluentIcon.PLAY, self.time_segment_card)
        else:
            self.stop_label = PrimaryToolButton(
                FluentIcon.PAUSE, self.time_segment_card)
        self.stop_label.update()

    def open_video_file_dialog(self):
        """ 打开视频文件选择对话框 """
        # 使用 QFileDialog.getOpenFileName() 来获取单个文件路径
        # self 作为父窗口，对话框标题，初始目录，文件过滤器
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

            # 移除旧的视频组件
            if self.video_widget:
                self.video_preview_layout.removeWidget(self.video_widget)
                self.video_widget.deleteLater()

            # 创建新的视频播放器实例
            self.video_widget = DarkMediaPlayer(self.video_path)

            # 将新的视频播放器添加到布局中
            self.video_preview_layout.addWidget(self.video_widget)

            # 更新播放/暂停按钮状态
            self.toggle_play_pause()

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
            if self.video_path != "":
                return
            elif self.video_path == "":
                self.selected_file_label.setText("未选择任何文件")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = VideoInterface()
    w.show()
    sys.exit(app.exec())
