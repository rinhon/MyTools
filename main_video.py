
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
    SubtitleLabel, LineEdit, ComboBox, TableWidget, PrimaryToolButton, FluentIcon,PrimaryPushButton ,RoundMenu,Action,Flyout,FlyoutAnimationType
)
from qfluentwidgets.multimedia import VideoWidget, MediaPlayer
from video_test import DarkMediaPlayer
import sys
import os
import tempfile
from datetime import datetime


class VideoInterface(QWidget):

    def __init__(self):
        super().__init__()

        self.setObjectName("视频剪辑")
        self.setWindowTitle("视频剪辑工具")
        self.resize(800, 1110)  # 设置窗口大小
        self.center_window() # 设置窗口居中

        # 1. 创建主窗口的垂直布局，用于容纳所有 CardWidget
        self.main_v_layout = QVBoxLayout(self)
        self.main_v_layout.setContentsMargins(10, 10, 10, 10) # 给所有卡片留点边距
        self.main_v_layout.setSpacing(15) # 卡片之间的垂直间距

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

        self.video_select_card(self)

        self.video_preview_card(self)

        self.time_select_card(self)


    # 视频选择
    def video_select_card(self, parent):

        # --- 1. 第一个 CardWidget (顶部单行区域) ---
        self.card_video_select = CardWidget()
        # 在 CardWidget 内部创建布局
        self.card_layout = QHBoxLayout(self.card_video_select)
        self.card_layout.setContentsMargins(1, 1, 1, 1) # 内部边距
        
        # 创建一个 Fluent 风格的标签
        self.time_segment_title = SubtitleLabel("视频选择")
        self.time_segment_title.setMinimumHeight(45)
        self.time_segment_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card_layout.addWidget(self.time_segment_title)

        # 显示选中的文件路径
        self.selected_file_label = BodyLabel("未选择任何文件", self.card_video_select)
        self.card_layout.addWidget(self.selected_file_label)

        # 创建一个 Fluent 风格的按钮
        self.select_video_button = PushButton("选择视频文件", self.card_video_select)
        # 连接按钮的点击事件到槽函数
        self.select_video_button.clicked.connect(self.open_video_file_dialog)
        self.card_layout.addWidget(self.select_video_button)

        # 添加视频选择卡片到主布局
        self.main_v_layout.addWidget(self.card_video_select)

    # 视频预览
    def video_preview_card(self, parent):
        # 初始化视频预览组件
        self.video_preview_card = CardWidget()
        self.video_preview_layout = QVBoxLayout(self.video_preview_card)
        self.video_preview_title = SubtitleLabel("视频预览")
        self.video_preview_layout.addWidget(self.video_preview_title)

        # self.video_widget = VideoWidget(self.video_preview_card)
        self.video_widget = DarkMediaPlayer("")
        self.video_preview_layout.addWidget(self.video_widget)

        # 添加视频预览卡片到主布局
        self.main_v_layout.addWidget(self.video_preview_card)
    
    # 时间段选择
    def time_select_card(self, parent):
        # 3时间段选择====================================================================
        self.time_segment_card = CardWidget()
        # 3-1 标题区====================================================================
        self.time_segment_card_layout = QVBoxLayout(self.time_segment_card) 
        self.time_segment_title = SubtitleLabel("时间段选择")
        self.time_segment_title.setMaximumHeight(20)
        self.time_segment_card_layout.addWidget(self.time_segment_title)
        
        # 3-2 第二层区域 (三个并排的矩形)====================================================================
        self.time_segment_card_layout2 = QHBoxLayout(self.time_segment_card)
        # 3-2-1
        self.current_time_label = BodyLabel(f"当前时间: {self.current_time}")
        
        # 3-2-2
        self.stop_label = PrimaryToolButton(
            FluentIcon.PAUSE, self.time_segment_card)
        self.stop_label.clicked.connect(self.toggle_play_pause)

        # 3-2-3
        self.start_time_label = PushButton("选择开始时间", self.time_segment_card)
        self.start_time_label.clicked.connect(self.set_start_time)
        # 3-2-4
        self.end_time_label = PushButton("选择结束时间", self.time_segment_card)
        self.end_time_label.clicked.connect(self.set_end_time)

        # 按钮添加至水平布局中
        self.time_segment_card_layout2.addWidget(self.current_time_label)
        self.time_segment_card_layout2.addWidget(self.stop_label)
        self.time_segment_card_layout2.addWidget(self.start_time_label)
        self.time_segment_card_layout2.addWidget(self.end_time_label)
        # 将水平布局添加进垂直布局中
        self.time_segment_card_layout.addLayout(self.time_segment_card_layout2)

        #表格处理====================================================================
        self.segments_label = TableWidget()

        # 设置基本属性
        self.segments_label.setBorderRadius(8)  # 设置圆角
        self.segments_label.setMinimumHeight(80)  # 设置最小高度
        self.segments_label.setMaximumHeight(160)  # 设置最大高度
        self.segments_label.setColumnCount(2)  # 设置列数
        self.segments_label.setSelectRightClickedRow(True)  # 允许选择右键行
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

        # 4====================================================================
        self.segments_back_label = QHBoxLayout(self.time_segment_card)
        # 清空所有片段按钮
        self.clear_all_button = PushButton("清空所有片段", self.time_segment_card)
        self.clear_all_button.clicked.connect(self.clear_all_segments)
        self.segments_back_label.addWidget(self.clear_all_button)

        # 提示按钮
        self.tip_button = PrimaryToolButton(FluentIcon.INFO, self.time_segment_card)
        self.tip_button.clicked.connect(self.showFlyout)
        self.segments_back_label.addWidget(self.tip_button)

        self.time_segment_card_layout.addLayout(self.segments_back_label)

        # 将第三张卡片添加到主布局中
        self.main_v_layout.addWidget(self.time_segment_card)

     #
    
    # 剪辑视频处理
    def cut_video(self,parent):
        # 命令执行卡片   
        # 水平布局
        self.command_card = CardWidget()
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
        self.main_v_layout.addWidget(self.command_card)
    
    
    
    
    
    
    
    
    
    
    
    

    def ms_to_time_string(self, ms):
        """将毫秒转换为时间字符串格式 HH:MM:SS"""
        if ms < 0:
            return "00:00:00"

        seconds = ms // 1000
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    # 更新当前播放时间
    def update_current_time(self):
        """更新当前播放时间"""
        if not self.video_widget:
            return

        try:
            # 获取当前视频时间
            current_ms = self.video_widget.get_current_time()
            if current_ms is not None:
                # self.current_time = self.ms_to_time_string(current_ms)
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

        # current_time = self.ms_to_time_string(current_ms)
        if current_ms == "00:00:00.0000":
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
                item = QTableWidgetItem(current_ms)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.segments_label.setItem(row, 0, item)

                InfoBar.success(
                    title="开始时间已设置",
                    content=f"开始时间: {current_ms}",
                    parent=self,
                    duration=2000,
                    position=InfoBarPosition.BOTTOM_RIGHT
                )
                return

            row -= 1

        # 如果所有行都已填满，添加新行
        row = self.segments_label.rowCount()
        self.segments_label.setRowCount(row + 1)
        item = QTableWidgetItem(current_ms)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.segments_label.setItem(row, 0, item)

        InfoBar.success(
            title="开始时间已设置",
            content=f"开始时间: {current_ms}",
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
                        position=InfoBarPosition.BOTTOM_RIGHT
                    )
                    return

                # 设置结束时间
                item = QTableWidgetItem(current_ms)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.segments_label.setItem(row, 1, item)

                # 将此行添加到时间片段列表
                self.time_segments.append((start_time, current_ms))

                InfoBar.success(
                    title="结束时间已设置",
                    content=f"结束时间: {current_ms}",
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

    # 功能提示
    def showFlyout(self):
        Flyout.create(
            icon=InfoBarIcon.SUCCESS,
            title='提示',
            content="可以右键单独删除时间片段",
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
            position=InfoBarPosition.BOTTOM_RIGHT
        )

    # 右键菜单
    def show_context_menu(self, position):
        """显示右键菜单"""
        # 获取当前选中的行
        row = self.segments_label.currentRow()
        # 创建菜单
        menu = RoundMenu()
        # 添加菜单动作
        menu.addAction(Action("删除",triggered=lambda: delete_segment(row)))
        # 在鼠标位置显示菜单
        menu.exec(self.segments_label.viewport().mapToGlobal(position))
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
                    position=InfoBarPosition.BOTTOM_RIGHT
                )
                self.time_segments.remove(row)
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
            # 确保至少有5行
            row_count = max(needed_rows, 3)
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

    # 将时间字符串转换为秒数    
    def time_to_seconds(self, time_str):
        """ 将时间字符串转换为秒数 """
        #time_str剪切掉后面的.0000
        time_str = time_str.split('.')[0]
        try:
            h, m, s = map(int, time_str.split(':'))
            return h * 3600 + m * 60 + s
        except:
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

    # 暂停/播放
    def toggle_play_pause(self):
        """ 切换视频的播放/暂停状态 """
        if not self.video_widget:
            return

        self.video_widget.toggle_play()
        # 更新按钮文本
        if self.video_widget.is_playing_status():
            self.stop_label = PrimaryToolButton(
                FluentIcon.PAUSE, self.time_segment_card)
        else:
            self.stop_label = PrimaryToolButton(
                FluentIcon.PLAY, self.time_segment_card)
        self.stop_label.update()

    # 选择视频文件
    def open_video_file_dialog(self):
        """ 打开视频文件选择对话框 """
        # 使用 QFileDialog.getOpenFileName() 来获取单个文件路径
        # self 作为父窗口，对话框标题，初始目录，文件过滤器
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择视频文件",
            # "G:/Nyotengu/LazyProcrast",  # 默认打开目录
            "C:/Users/90708/Videos",
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
            self.center_window()

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
    
    # 窗口居中
    def center_window(self):
        """ 带自适应调整的居中方法 """
        # 先让窗口完成布局更新
        QApplication.processEvents()
        
        # 获取精确的窗口尺寸
        window_size = self.size()
        
        # 处理多显示器情况
        current_screen = self.screen()
        screen_rect = current_screen.availableGeometry()
        
        # 计算居中坐标
        x = screen_rect.left() + (screen_rect.width() - window_size.width()) // 2
        y = screen_rect.top() + (screen_rect.height() - window_size.height()) // 2
        
        # 设置窗口位置并限制在屏幕范围内
        self.move(
            max(screen_rect.left(), min(x, screen_rect.right() - window_size.width())),
            max(screen_rect.top(), min(y, screen_rect.bottom() - window_size.height()))
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = VideoInterface()
    w.show()
    sys.exit(app.exec())
