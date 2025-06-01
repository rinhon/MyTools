
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
    SubtitleLabel, LineEdit, ComboBox, TableWidget, 
    PrimaryToolButton, FluentIcon, PrimaryPushButton, 
    RoundMenu, Action, Flyout, FlyoutAnimationType,
)
from qfluentwidgets.multimedia import VideoWidget, MediaPlayer

from video_test import DarkMediaPlayer
from cut_flyou_view import CutFlyoutView
import sys
import os
import tempfile
from datetime import datetime


class VideoInterface(QWidget):

    def __init__(self):
        super().__init__()

        self.setObjectName("视频剪辑")
        self.setWindowTitle("视频剪辑工具")
        # self.setFixedHeight(1100)  # 设置窗口大小

        # 设置窗口焦点策略
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()  # 确保窗口获得初始焦点
        self.top_level_widget = None
        self.center_window()  # 设置窗口居中

        # 1. 创建主窗口的垂直布局，用于容纳所有
        self.main_v_layout = QVBoxLayout(self)
        self.main_v_layout.setContentsMargins(10, 10, 10, 10)  # 给所有卡片留点边距
        self.main_v_layout.setSpacing(5)  # 卡片之间的垂直间距

        # 初始化变量
        self.video_path = ""
        self.time_segments = []  # 剪切时间段列表，存储多个时间片段
        self.current_time = "00:00:00"  # 当前播放时间

        # 创建定时器用于更新当前时间
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_current_time)
        self.timer.start(100)  # 每100ms更新一次

        self.setup_ui()

    def keyPressEvent(self, event):
        """重写键盘事件处理"""
        # 只有在视频已加载且窗口有焦点时才处理快捷键
        if self.hasFocus() and self.video_widget and self.video_path:
            if event.key() == Qt.Key.Key_Space:
                self.toggle_play_pause()  # 空格键触发播放/暂停
                event.accept()  # 标记事件已处理
                return
            elif event.key() == Qt.Key.Key_Left:
                self.seek(-10)  # 左方向键后退10秒
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Right:
                self.seek(10)  # 右方向键前进10秒
                event.accept()
                return

        super().keyPressEvent(event)  # 其他按键保持默认处理

    def setup_ui(self):

        self.video_select_card(self)

        self.video_preview_card(self)

        self.time_select_card(self)

        self.cut_video(self)

    # 视频选择
    def video_select_card(self, parent):

        # --- 1. 第一个 CardWidget (顶部单行区域) ---
        self.card_video_select = CardWidget()
        # 在 CardWidget 内部创建布局
        self.card_v_layout = QVBoxLayout(self.card_video_select)

        # 创建一个 Fluent 风格的标签
        self.time_segment_title = SubtitleLabel("视频选择")
        self.time_segment_title.setMinimumHeight(20)
        # self.time_segment_title.setAlignment(Qt.AlignmentFlag.AlignCenter) # 居中
        self.card_v_layout.addWidget(self.time_segment_title)

        self.card_layout = QHBoxLayout(self.card_video_select)
        self.card_layout.setContentsMargins(1, 1, 1, 1)  # 内部边距

        # 显示选中的文件路径
        self.selected_file_label = LineEdit()
        self.selected_file_label.setText("未选择视频文件")
        self.selected_file_label.setReadOnly(True)  # 禁止编辑
        self.card_layout.addWidget(self.selected_file_label)

        # 创建一个 Fluent 风格的按钮
        self.select_video_button = PushButton("选择视频文件", self.card_video_select)
        self.select_video_button.setFocusPolicy(
            Qt.FocusPolicy.NoFocus)  # 禁止获取焦点

        self.card_v_layout.addLayout(self.card_layout)

        # 连接按钮的点击事件到槽函数
        self.select_video_button.clicked.connect(self.open_video_file_dialog)
        self.card_layout.addWidget(self.select_video_button)

        # 添加视频选择卡片到主布局
        self.main_v_layout.addWidget(self.card_video_select)

    # 视频预览
    def video_preview_card(self, parent):
        # 初始化视频预览组件
        self.video_preview_card1 = CardWidget()
        self.video_preview_layout = QVBoxLayout(self.video_preview_card1)
        self.video_preview_title = SubtitleLabel("视频预览")
        self.video_preview_layout.addWidget(self.video_preview_title)

        # self.video_widget = VideoWidget(self.video_preview_card)
        self.video_widget = DarkMediaPlayer("")
        self.video_preview_layout.addWidget(self.video_widget)

        # 添加视频预览卡片到主布局
        self.main_v_layout.addWidget(self.video_preview_card1)

    # 时间段选择
    # def time_select_card(self, parent):
    #     # 3时间段选择====================================================================
    #     self.time_segment_card = CardWidget()
    #     self.time_segment_card.setContentsMargins(1, 1, 1, 1)  # 内部边距

    #     # 3-1 标题区====================================================================
    #     self.time_segment_card_layout = QVBoxLayout(self.time_segment_card)
    #     self.time_segment_card_layout.setContentsMargins(5, 5, 5, 5)  # 减小边距
    #     self.time_segment_title = SubtitleLabel(
    #         "时间段选择", self.time_segment_card)
    #     self.time_segment_title.setFixedHeight(20)  # 减小高度
    #     self.time_segment_card_layout.addWidget(self.time_segment_title)
    #     # 3-2 第二层区域 (三个并排的矩形)====================================================================
    #     self.time_segment_card_layout2 = QHBoxLayout()
    #     self.time_segment_card_layout2.setContentsMargins(0, 2, 0, 2)  # 设置小边距
    #     self.time_segment_card_layout2.setSpacing(8)  # 减小按钮间距

    #     # 3-2-1
    #     self.current_time_label = BodyLabel(f"当前时间: {self.current_time}")
    #     self.current_time_label.setFixedHeight(28)  # 减小高度

    #     # 3-2-2
    #     self.stop_label = PrimaryToolButton(
    #         FluentIcon.PAUSE, self.time_segment_card)
    #     self.stop_label.setFixedSize(28, 28)  # 减小按钮大小
    #     self.stop_label.clicked.connect(self.toggle_play_pause)

    #     # 3-2-3
    #     self.start_time_label = PushButton("选择开始时间", self.time_segment_card)
    #     self.start_time_label.setFixedHeight(28)  # 减小高度
    #     self.start_time_label.clicked.connect(self.set_start_time)

    #     # 3-2-4
    #     self.end_time_label = PushButton("选择结束时间", self.time_segment_card)
    #     self.end_time_label.setFixedHeight(28)  # 减小高度
    #     self.end_time_label.clicked.connect(self.set_end_time)

    #     # 4====================================================================

    #     # 清空所有片段按钮
    #     self.clear_all_button = PushButton("清空所有片段", self.time_segment_card)
    #     self.clear_all_button.setFixedHeight(28)  # 减小按钮高度
    #     self.clear_all_button.clicked.connect(self.clear_all_segments)

    #     # 提示按钮
    #     self.tip_button = PrimaryToolButton(
    #         FluentIcon.INFO, self.time_segment_card)
    #     self.tip_button.setFixedSize(28, 28)  # 减小按钮大小
    #     self.tip_button.clicked.connect(self.showFlyout)

    #     # 按钮添加至水平布局中
    #     self.time_segment_card_layout2.addWidget(self.current_time_label)
    #     self.time_segment_card_layout2.addWidget(self.stop_label)
    #     self.time_segment_card_layout2.addWidget(self.start_time_label)
    #     self.time_segment_card_layout2.addWidget(self.end_time_label)
    #     self.time_segment_card_layout2.addWidget(self.clear_all_button)
    #     self.time_segment_card_layout2.addWidget(self.tip_button)
    #     # 将水平布局添加进垂直布局中
    #     self.time_segment_card_layout.addLayout(self.time_segment_card_layout2)

    #     # 表格处理====================================================================
    #     self.segments_label = TableWidget(self.time_segment_card)

    #     # 设置基本属性
    #     self.segments_label.setBorderRadius(8)  # 设置圆角
    #     self.segments_label.setMinimumHeight(60)  # 减小最小高度
    #     self.segments_label.setMaximumHeight(120)  # 减小最大高度
    #     self.segments_label.setColumnCount(2)  # 设置列数
    #     self.segments_label.setSelectRightClickedRow(True)  # 允许选择右键行
    #     self.segments_label.setHorizontalHeaderLabels(['开始时间', '结束时间'])  # 设置表头
    #     self.segments_label.setContentsMargins(2, 2, 2, 2)  # 减小内边距

    #     # 隐藏垂直表头（行号）
    #     # self.segments_label.verticalHeader().setVisible(False)

    #     # 设置表格大小调整策略
    #     self.segments_label.horizontalHeader().setSectionResizeMode(
    #         QHeaderView.ResizeMode.Stretch)  # 列宽自适应
    #     self.segments_label.verticalHeader().setSectionResizeMode(
    #         QHeaderView.ResizeMode.Fixed)  # 固定行高
    #     self.segments_label.verticalHeader().setDefaultSectionSize(30)  # 减小默认行高

    #     # 设置表格属性
    #     self.segments_label.setBorderVisible(True)  # 设置边框可见
    #     self.segments_label.setRowCount(1)  # 设置初始行数
    #     self.segments_label.setEditTriggers(
    #         TableWidget.EditTrigger.NoEditTriggers)  # 禁止编辑
    #     self.segments_label.setSelectionMode(
    #         TableWidget.SelectionMode.SingleSelection)  # 单行选择
    #     self.segments_label.setSelectionBehavior(
    #         TableWidget.SelectionBehavior.SelectRows)  # 选择整行
    #     self.segments_label.setAlternatingRowColors(True)  # 启用交替行颜色

    #     # 优化表格性能
    #     self.segments_label.setVerticalScrollMode(
    #         TableWidget.ScrollMode.ScrollPerPixel)  # 像素级滚动
    #     self.segments_label.setHorizontalScrollMode(
    #         TableWidget.ScrollMode.ScrollPerPixel)

    #     # 设置表头和单元格样式
    #     # self.segments_label.horizontalHeader().setStretchLastSection(True)  # 最后一列自动填充
    #     self.segments_label.horizontalHeader().setDefaultAlignment(
    #         Qt.AlignmentFlag.AlignCenter)  # 表头居中对齐

    #     self.segments_label.itemChanged.connect(
    #         lambda item: set_item_alignment(item.row(), item.column(), item))
    #     # 设置单元格文本居中对齐

    #     def set_item_alignment(row, column, item):
    #         if item:
    #             item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

    #     # 添加右键菜单
    #     self.segments_label.setContextMenuPolicy(
    #         Qt.ContextMenuPolicy.CustomContextMenu)
    #     self.segments_label.customContextMenuRequested.connect(
    #         self.show_context_menu)
    #     # 添加进布局
    #     self.time_segment_card_layout.addWidget(self.segments_label)

    #     # 将第三张卡片添加到主布局中
    #     self.main_v_layout.addWidget(self.time_segment_card)
    
    # 时间段选择
    def time_select_card(self, parent):
        # 3时间段选择====================================================================
        self.time_segment_card = CardWidget()
        self.time_segment_card.setContentsMargins(1, 1, 1, 1)  # 内部边距
        self.time_segment_card.setFixedHeight(300)  # 设置卡片高度
        # 3-1 标题区====================================================================
        self.time_segment_card_layout = QVBoxLayout(self.time_segment_card)
        self.time_segment_card_layout.setContentsMargins(10, 10, 10, 10)  # 统一边距
        self.time_segment_card_layout.setSpacing(8)  # 统一垂直间距
        
        self.time_segment_title = SubtitleLabel("时间段选择", self.time_segment_card)
        self.time_segment_title.setFixedHeight(30)  # 适当增加标题高度
        self.time_segment_card_layout.addWidget(self.time_segment_title)
        
        # 3-2 第二层区域 (三个并排的矩形)====================================================================
        self.time_segment_card_layout2 = QHBoxLayout()
        self.time_segment_card_layout2.setContentsMargins(0, 0, 0, 0)  # 移除多余边距
        self.time_segment_card_layout2.setSpacing(8)  # 统一水平间距

        # 3-2-1 当前时间标签
        self.current_time_label = BodyLabel(f"当前时间: {self.current_time}")
        self.current_time_label.setFixedHeight(32)  # 统一组件高度
        self.current_time_label.setMinimumWidth(120)  # 设置最小宽度确保显示完整

        # 3-2-2 播放/暂停按钮
        self.stop_label = PrimaryToolButton(FluentIcon.PAUSE, self.time_segment_card)
        self.stop_label.setFixedSize(32, 32)  # 统一按钮大小
        self.stop_label.clicked.connect(self.toggle_play_pause)

        # 3-2-3 开始时间按钮
        self.start_time_label = PushButton("选择开始时间", self.time_segment_card)
        self.start_time_label.setFixedHeight(32)  # 统一高度
        self.start_time_label.setMinimumWidth(100)  # 设置最小宽度
        self.start_time_label.clicked.connect(self.set_start_time)

        # 3-2-4 结束时间按钮
        self.end_time_label = PushButton("选择结束时间", self.time_segment_card)
        self.end_time_label.setFixedHeight(32)  # 统一高度
        self.end_time_label.setMinimumWidth(100)  # 设置最小宽度
        self.end_time_label.clicked.connect(self.set_end_time)

        # 清空所有片段按钮
        self.clear_all_button = PushButton("清空所有片段", self.time_segment_card)
        self.clear_all_button.setFixedHeight(32)  # 统一高度
        self.clear_all_button.setMinimumWidth(100)  # 设置最小宽度
        self.clear_all_button.clicked.connect(self.clear_all_segments)

        # 提示按钮
        self.tip_button = PrimaryToolButton(FluentIcon.INFO, self.time_segment_card)
        self.tip_button.setFixedSize(32, 32)  # 统一按钮大小
        self.tip_button.clicked.connect(self.showFlyout)

        # 按钮添加至水平布局中
        self.time_segment_card_layout2.addWidget(self.current_time_label)
        self.time_segment_card_layout2.addWidget(self.stop_label)
        self.time_segment_card_layout2.addWidget(self.start_time_label)
        self.time_segment_card_layout2.addWidget(self.end_time_label)
        self.time_segment_card_layout2.addWidget(self.clear_all_button)
        self.time_segment_card_layout2.addWidget(self.tip_button)
        
        # 添加弹性空间，使按钮靠左对齐
        # self.time_segment_card_layout2.addStretch()
        
        # 将水平布局添加进垂直布局中
        self.time_segment_card_layout.addLayout(self.time_segment_card_layout2)

        # 表格处理====================================================================
        self.segments_label = TableWidget(self.time_segment_card)

        # 设置基本属性
        self.segments_label.setBorderRadius(8)  # 设置圆角
        self.segments_label.setMinimumHeight(80)  # 适当增加最小高度
        self.segments_label.setMaximumHeight(200)  # 适当增加最大高度
        self.segments_label.setColumnCount(2)  # 设置列数
        self.segments_label.setSelectRightClickedRow(True)  # 允许选择右键行
        self.segments_label.setHorizontalHeaderLabels(['开始时间', '结束时间'])  # 设置表头
        self.segments_label.setContentsMargins(0, 0, 0, 0)  # 移除内边距

        # 隐藏垂直表头（行号）
        # self.segments_label.verticalHeader().setVisible(False)

        # 设置表格大小调整策略
        self.segments_label.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)  # 列宽自适应
        self.segments_label.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Fixed)  # 固定行高
        self.segments_label.verticalHeader().setDefaultSectionSize(35)  # 统一行高

        # 设置表格属性
        self.segments_label.setBorderVisible(True)  # 设置边框可见
        self.segments_label.setRowCount(1)  # 设置初始行数
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
        self.segments_label.horizontalHeader().setDefaultAlignment(
            Qt.AlignmentFlag.AlignCenter)  # 表头居中对齐

        self.segments_label.itemChanged.connect(
            lambda item: set_item_alignment(item.row(), item.column(), item))
        
        # 设置单元格文本居中对齐
        def set_item_alignment(row, column, item):
            if item:
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        # 添加右键菜单
        self.segments_label.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu)
        self.segments_label.customContextMenuRequested.connect(
            self.show_context_menu)
        
        # 添加进布局
        self.time_segment_card_layout.addWidget(self.segments_label)

        # 将第三张卡片添加到主布局中
        self.main_v_layout.addWidget(self.time_segment_card)

    # 剪辑视频处理

    def cut_video(self, parent):
        # 命令执行卡片
        # 水平布局
        self.command_card = CardWidget()
        self.command_layout = QHBoxLayout(self.command_card)
        # 剪切视频
        self.execute_cut_button = PrimaryPushButton(
            "剪切视频", self.command_card)
        self.execute_cut_button.clicked.connect(self.execute_video_cut)
        self.command_layout.addWidget(self.execute_cut_button)

        # 删除原视频
        self.generate_ffmpeg_button = PrimaryPushButton(
            "删除原视频", self.command_card)
        self.generate_ffmpeg_button.clicked.connect(
            self.generate_ffmpeg_command)
        self.command_layout.addWidget(self.generate_ffmpeg_button)

        # 添加时间段选择卡片到主布局
        self.main_v_layout.addWidget(self.command_card)

    def ms_to_time_string(self, ms):
        """将毫秒转换为时间字符串格式 HH:MM:SS.mmm"""
        if ms < 0:
            return "00:00:00.000"

        milliseconds = ms % 1000
        total_seconds = ms // 1000
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

    # 更新当前播放时间
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
                position=InfoBarPosition.TOP_RIGHT
            )
            return

        # 获取当前视频时间（毫秒）
        current_ms = self.video_widget.get_current_time()
        if current_ms is None:
            return

        # 将毫秒转换为时间字符串
        current_time = self.ms_to_time_string(current_ms)
        if current_time == "00:00:00.000":
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
                    position=InfoBarPosition.TOP_RIGHT
                )
                return

            # 如果找到一行已经有开始时间但没有结束时间，不允许设置新的开始时间
            if start_item and not end_item:
                InfoBar.warning(
                    title="操作无效",
                    content="请先设置当前行的结束时间",
                    parent=self,
                    duration=2000,
                    position=InfoBarPosition.TOP_RIGHT
                )
                return

            # 如果找到空行，设置开始时间
            if not start_item and not end_item:
                # 将毫秒转换为时间字符串
                time_str = self.ms_to_time_string(current_ms)
                item = QTableWidgetItem(time_str)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.segments_label.setItem(row, 0, item)

                InfoBar.success(
                    title="开始时间已设置",
                    content=f"开始时间: {time_str}",
                    parent=self,
                    duration=2000,
                    position=InfoBarPosition.TOP_RIGHT
                )
                self.segments_label.setCurrentCell(row, 0)

                return

            row -= 1

        # 如果所有行都已填满，添加新行
        row = self.segments_label.rowCount()
        self.segments_label.setRowCount(row + 1)
        # 将毫秒转换为时间字符串
        time_str = self.ms_to_time_string(current_ms)
        item = QTableWidgetItem(time_str)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.segments_label.setItem(row, 0, item)
        self.segments_label.setCurrentCell(row, 0)

        InfoBar.success(
            title="开始时间已设置",
            content=f"开始时间: {time_str}",
            parent=self,
            duration=2000,
            position=InfoBarPosition.TOP_RIGHT
        )

    def set_end_time(self):
        """ 设置结束时间 """
        if not self.video_widget:
            InfoBar.warning(
                title="无法设置时间",
                content="请先选择视频文件",
                parent=self,
                duration=2000,
                position=InfoBarPosition.TOP_RIGHT
            )
            return

        # 获取当前视频时间
        current_ms = self.video_widget.get_current_time()
        if current_ms is None:
            return

        # current_time = self.ms_to_time_string(current_ms)
        if current_ms == "00:00:00.0000":
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
                if self.time_to_seconds(current_ms) <= self.time_to_seconds(start_time):
                    InfoBar.warning(
                        title="时间错误",
                        content="结束时间必须大于开始时间",
                        parent=self,
                        duration=2000,
                        position=InfoBarPosition.TOP_RIGHT
                    )
                    return

                # 将毫秒转换为时间字符串
                time_str = self.ms_to_time_string(current_ms)

                # 设置结束时间
                item = QTableWidgetItem(time_str)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.segments_label.setItem(row, 1, item)
                self.segments_label.scrollToBottom()  # 自动滚动到底部
                self.segments_label.setCurrentCell(row, 0)

                # 将此行添加到时间片段列表
                self.time_segments.append((start_time, time_str))
                
                print("\n当前时间片段列表:")
                if self.time_segments.count == 0:
                    print("空列表 - 没有时间片段")
                else:
                    for i, (start, end) in enumerate(self.time_segments, 1):
                        print(f"片段 {i}: {start} -> {end}")

                InfoBar.success(
                    title="结束时间已设置",
                    content=f"结束时间: {time_str}",
                    parent=self,
                    duration=2000,
                    position=InfoBarPosition.TOP_RIGHT
                )
                break

            row += 1

        if not found:
            InfoBar.warning(
                title="操作无效",
                content="请先设置开始时间",
                parent=self,
                duration=2000,
                position=InfoBarPosition.TOP_RIGHT
            )

    # 功能提示
    def showFlyout(self):
        Flyout.create(
            icon=InfoBarIcon.SUCCESS,
            title='提示',
            content="\n" +
            "时间段表格：\n" +
            "可以右键单独删除时间片段\n" +
            "\n" +
            "视频：\n" +
            "space:暂停/播放\n" +
            "←：后退10秒\n" +
            "→：前进10秒",
            target=self.tip_button,
            parent=self,
            isClosable=False,
            aniType=FlyoutAnimationType.PULL_UP
        )

    # 清空所有片段
    def clear_all_segments(self):
        """ 清空所有时间片段 """
        self.time_segments.clear()
        self.update_segments_display()

        InfoBar.info(
            title="片段已清空",
            content="所有时间片段已清空",
            parent=self,
            duration=2000,
            position=InfoBarPosition.TOP_RIGHT
        )

    # 右键菜单
    def show_context_menu(self, position):
        """显示右键菜单"""
        # 获取当前选中的行
        row = self.segments_label.currentRow()
        # 创建菜单
        menu = RoundMenu()
        # 添加菜单动作
        menu.addAction(
            Action("删除", triggered=lambda: self.delete_segment( row)))
        # 在鼠标位置显示菜单
        menu.exec(self.segments_label.mapToGlobal(position))
        # 删除指定行的时间片段

    def delete_segment(self, row):
        """删除指定行的时间片段"""
        # 判断是否删除成功
        if 0 <= row < len(self.time_segments):
            # if after_row < row:
            InfoBar.success(
                title="操作成功",
                content="已删除时间片段",
                parent=self,
                duration=2000,
                position=InfoBarPosition.TOP_RIGHT
            ) # 输出当前时间片段列表的内容到控制台
            self.time_segments.pop(row) # 删除指定行

            print("\n当前时间片段列表:")
            if not self.time_segments:
                print("空列表 - 没有时间片段")
            else:
                for i, (start, end) in enumerate(self.time_segments, 1):
                    print(f"片段 {i}: {start} -> {end}")
                    
            # 更新显示
            self.update_segments_display()

    # 更新时间片段列表显示
    def update_segments_display(self):
        """ 更新时间片段列表显示 """
        # 暂时关闭表格更新以提高性能
        self.segments_label.setUpdatesEnabled(False)

        try:
            # 清空表格内容
            self.segments_label.clearContents()

            # 计算需要的总行数：已有片段数量 + 1（用于新片段）
            needed_rows = len(self.time_segments) + 1
            # 确保至少有3行
            row_count = max(needed_rows, 3)
            self.segments_label.setRowCount(row_count)

            # 对时间片段按开始时间排序（正序）
            sorted_segments = sorted(self.time_segments, 
                                    key=lambda segment: self.time_to_seconds(segment[0]))

            # 批量添加已排序的时间片段
            for i, segment in enumerate(sorted_segments):
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

    # 将时间字符串转换为秒数
    def time_to_seconds(self, time_input):
        """ 将时间输入转换为秒数（支持毫秒）

        Args:
            time_input: 可以是时间字符串（HH:MM:SS.mmm）或毫秒数（整数）

        Returns:
            float: 转换后的秒数（包含毫秒部分）
        """
        # 处理整数类型输入（毫秒）
        if isinstance(time_input, (int, float)):
            return time_input / 1000.0

        # 处理时间字符串
        try:
            # 处理带毫秒的时间字符串
            if '.' in time_input:
                main_time, ms_part = time_input.split('.')
                ms = int(ms_part) / 1000.0 if ms_part else 0  # 将毫秒部分转换为秒
            else:
                main_time = time_input
                ms = 0

            h, m, s = map(int, main_time.split(':'))
            return h * 3600 + m * 60 + s + ms
        except Exception as e:
            print(f"时间转换错误: {e}, 输入: {time_input}")
            return 0

    # 执行剪辑命令
    def generate_ffmpeg_command(self):
        """ 生成FFmpeg命令 """
        if not self.video_path:
            InfoBar.warning(
                title="未选择视频",
                content="请先选择视频文件！",
                parent=self,
                duration=2000,
                position=InfoBarPosition.TOP_RIGHT
            )
            return

        if not self.time_segments:
            InfoBar.warning(
                title="无时间片段",
                content="请先添加时间片段！",
                parent=self,
                duration=2000,
                position=InfoBarPosition.TOP_RIGHT
            )
            return

        # 生成输出文件名
        input_name = os.path.splitext(os.path.basename(self.video_path))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(os.path.dirname(
            self.video_path), f"{input_name}_cut_{timestamp}.mp4")

    # 执行剪辑命令
    def execute_video_cut(self):
        """ 执行视频剪辑 """
        if not self.video_path or not self.time_segments:
            InfoBar.warning(
                title="条件不满足",
                content="请先选择视频文件并添加时间片段！",
                parent=self,
                duration=2000,
                position=InfoBarPosition.TOP_RIGHT
            )
            return

        try:
       
            # 
            Flyout.make(CutFlyoutView(self),self.execute_cut_button, self, aniType=FlyoutAnimationType.PULL_UP)
            InfoBar.info(
                title="准备执行",
                content="FFmpeg命令已准备就绪，请手动执行或集成到您的系统中",
                parent=self,
                duration=3000,
                position=InfoBarPosition.TOP_RIGHT
            )

        except Exception as e:
            InfoBar.error(
                title="执行失败",
                content=f"生成命令时出错: {str(e)}",
                parent=self,
                duration=3000,
                position=InfoBarPosition.TOP_RIGHT
            )

    # 暂停/播放
    def toggle_play_pause(self):
        """切换视频的播放/暂停状态"""
        if not self.video_widget:
            return

        # 切换播放状态
        self.video_widget.toggle_play()

        # 更新按钮图标
        if self.video_widget.is_playing_status():
            self.stop_label.setIcon(FluentIcon.PAUSE)
        else:
            self.stop_label.setIcon(FluentIcon.PLAY)

    def seek(self, seconds):
        """视频快进/后退指定秒数"""
        if not self.video_widget:
            return

        # 获取当前时间（毫秒）
        current_ms = self.video_widget.get_current_time()
        if current_ms is None:
            return

        # 计算新位置（毫秒）
        new_pos = current_ms + seconds * 1000

        # 确保不超出视频范围
        if self.video_widget.media_player is not None:
            duration = self.video_widget.media_player.duration()
            new_pos = max(0, min(new_pos, duration))

            # 跳转到新位置
            self.video_widget.media_player.setPosition(new_pos)

        # 显示操作提示
        action = "后退" if seconds < 0 else "前进"
        InfoBar.info(
            title="视频跳转",
            content=f"已{action} {abs(seconds)}秒",
            parent=self,
            duration=1000,
            position=InfoBarPosition.TOP_RIGHT
        )

    # 选择视频文件
    def open_video_file_dialog(self):
        """ 打开视频文件选择对话框 """
        # 使用 QFileDialog.getOpenFileName() 来获取单个文件路径
        # self 作为父窗口，对话框标题，初始目录，文件过滤器
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择视频文件",
            "G:/Nyotengu/LazyProcrast",  # 默认打开目录
            # "C:/Users/90708/Videos",
            "视频文件 (*.mp4 *.avi *.mov *.mkv);;所有文件 (*.*)"
        )

        if file_path:
            print(f"选中的文件是: {file_path}")
            # 保存视频路径
            self.video_path = file_path

            # 移除旧的视频组件
            if self.video_widget:
                self.video_widget.deleteLater()
                self.video_preview_layout.removeWidget(self.video_widget)

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
                position=InfoBarPosition.TOP_RIGHT
            )

            # 重置焦点到主窗口
            self.setFocus()

            # 调整按钮的焦点策略，避免干扰全局快捷键
            self.select_video_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.clear_all_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.start_time_label.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.end_time_label.setFocusPolicy(Qt.FocusPolicy.NoFocus)

            self.center_window()

        else:
            print("取消选择文件")
            # 显示一个提示，表示用户取消了选择
            InfoBar.warning(
                title="未选择文件",
                content="您取消了文件选择。",
                parent=self,
                duration=2000,
                position=InfoBarPosition.TOP_RIGHT
            )
            # 重置文件路径显示
            if self.video_path != "":
                return
            elif self.video_path == "":
                self.selected_file_label.setText("未选择任何文件")

    # 窗口居中
    def center_window(self):
        """ 带自适应调整的居中方法 """
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = VideoInterface()
    w.show()
    sys.exit(app.exec())