import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QProgressBar, QLabel, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import QTimer, QDateTime, Qt
from qfluentwidgets import (
    CardWidget, BodyLabel, FluentWindow, PushButton,
    InfoBar, InfoBarIcon, InfoBarPosition,ProgressBar,
    SubtitleLabel, LineEdit, ComboBox,TableWidget,FluentIcon

)

class TimeCounterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("瓜哥内部专用时间穿越器")
        self.setGeometry(200, 200, 500, 250)
        
        # 设置窗口图标
        self.setWindowIcon(FluentIcon.HISTORY.icon())

        self.total_duration_ms = 0  # 总时长，毫秒
        self.elapsed_time_ms = 0    # 已耗时，毫秒
        self.start_time_ms = 0      # 开始时间戳，毫秒

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # 顶部控制区
        control_layout = QHBoxLayout()
        self.time_selector = ComboBox()
        
        # 添加选项
        items = ["5秒", "10秒", "十年"]
        self.time_selector.addItems(items)
        
        # 设置对应的数据
        self.time_selector.setItemData(0, 5000)
        self.time_selector.setItemData(1, 10000)
        self.time_selector.setItemData(2, 10 * 365 * 24 * 60 * 60 * 1000)
        
        self.time_selector.setCurrentIndex(0)  # 默认选择5秒
        control_layout.addWidget(BodyLabel("选择时长:"))
        control_layout.addWidget(self.time_selector)

        self.start_button = PushButton("开始", self, icon=FluentIcon.PLAY)
        self.start_button.clicked.connect(self.start_countdown)
        control_layout.addWidget(self.start_button)
        
        control_layout.addStretch(1) # 填充空白

        main_layout.addLayout(control_layout)

        # 进度条和百分比显示
        progress_layout = QHBoxLayout()
        self.progress_bar = ProgressBar()
        self.progress_bar.setRange(0, 100)  # 进度条最大值设为100%
        self.progress_percentage = BodyLabel("0%")
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_percentage)
        main_layout.addLayout(progress_layout)

        # 时间显示
        time_display_layout = QVBoxLayout()
        self.elapsed_label = BodyLabel("已耗时: 00:00:00")
        self.remaining_label = BodyLabel("剩余时间: 00:00:00")
        self.end_time_label = BodyLabel("预计结束时间: --:--:--")
        
        time_display_layout.addWidget(self.elapsed_label)
        time_display_layout.addWidget(self.remaining_label)
        time_display_layout.addWidget(self.end_time_label)

        main_layout.addLayout(time_display_layout)
        
        main_layout.addStretch(1) # 底部填充空白

        self.setLayout(main_layout)

    def start_countdown(self):
        # 停止之前的定时器，以防重复点击
        self.timer.stop()
        
        # 获取选定的总时长 (毫秒)
        self.total_duration_ms = self.time_selector.currentData()
        if not self.total_duration_ms:  # 防止选择到没有data的项
            return

        # 重置已耗时
        self.elapsed_time_ms = 0
        
        # 记录开始时间戳
        self.start_time_ms = QDateTime.currentMSecsSinceEpoch()

        # 计算预计结束时间
        end_datetime_ms = self.start_time_ms + self.total_duration_ms
        end_datetime = QDateTime.fromMSecsSinceEpoch(end_datetime_ms)
        weekday_map = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '日'}
        weekday = weekday_map[end_datetime.date().dayOfWeek()]
        formatted_date = end_datetime.toString("yyyy年MM月dd日 HH:mm:ss")
        self.end_time_label.setText(f"预计结束时间: {formatted_date} 星期{weekday}")

        # 重置进度条、百分比和时间显示
        self.progress_bar.setValue(0)
        self.progress_percentage.setText("0%")
        self.elapsed_label.setText("已耗时: 00:00:00")
        self.remaining_label.setText("剩余时间: " + self.format_ms_to_hms(self.total_duration_ms))
        
        # 启动定时器，每50毫秒更新一次（平滑的进度条和时间显示）
        # 对于十年这种超长时间，这个更新间隔可能需要调整
        if self.total_duration_ms > 60 * 60 * 1000: # 如果总时长超过1小时，可以放慢更新频率
            self.timer.setInterval(1000) # 每秒更新一次
        else:
            self.timer.setInterval(50) # 默认每50毫秒更新一次

        self.timer.start()
        self.start_button.setEnabled(False) # 计时开始后禁用按钮
        self.time_selector.setEnabled(False) # 计时开始后禁用下拉框

    def update_timer(self):
        current_time_ms = QDateTime.currentMSecsSinceEpoch()
        self.elapsed_time_ms = current_time_ms - self.start_time_ms

        remaining_time_ms = self.total_duration_ms - self.elapsed_time_ms

        # 更新进度条和百分比显示
        if self.total_duration_ms > 0:
            progress_percentage = int((self.elapsed_time_ms / self.total_duration_ms) * 100)
            progress_percentage = min(progress_percentage, 100)  # 确保不超过100%
            self.progress_bar.setValue(progress_percentage)
            self.progress_percentage.setText(f"{progress_percentage}%")
        else:
            self.progress_bar.setValue(0)  # 避免除以零
            self.progress_percentage.setText("0%")

        # 更新已耗时和剩余时间
        # 更新预计结束时间
        current_end_datetime_ms = current_time_ms + remaining_time_ms
        end_datetime = QDateTime.fromMSecsSinceEpoch(current_end_datetime_ms)
        weekday_map = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '日'}
        weekday = weekday_map[end_datetime.date().dayOfWeek()]
        formatted_date = end_datetime.toString("yyyy年MM月dd日 HH:mm:ss")
        self.end_time_label.setText(f"预计结束时间: {formatted_date} 星期{weekday}")

        self.elapsed_label.setText("已耗时: " + self.format_ms_to_hms(self.elapsed_time_ms))
        self.remaining_label.setText("剩余时间: " + self.format_ms_to_hms(max(0, remaining_time_ms))) # 确保剩余时间不为负

        # 检查是否计时结束
        if self.elapsed_time_ms >= self.total_duration_ms:
            self.timer.stop()
            self.progress_bar.setValue(100)
            self.remaining_label.setText("剩余时间: 00:00:00")
            self.elapsed_label.setText("已耗时: " + self.format_ms_to_hms(self.total_duration_ms))
            self.start_button.setEnabled(True) # 计时结束后启用按钮
            self.time_selector.setEnabled(True) # 计时结束后启用下拉框
            self.end_time_label.setText("结束")
            InfoBar.success(
                title="启动完成",
                content="穿越成功!",
                parent=self,
                duration=2000,
                position=InfoBarPosition.BOTTOM_RIGHT
            )

    def format_ms_to_hms(self, ms):
        """将毫秒转换为 HH:MM:SS 格式"""
        if ms < 0:
            ms = 0 # 确保不显示负时间

        seconds = ms // 1000
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        remaining_seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{remaining_seconds:02d}"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimeCounterApp()
    window.show()
    sys.exit(app.exec())