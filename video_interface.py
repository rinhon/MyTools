from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QApplication, QFileDialog,
    QLabel, QHBoxLayout, QSlider, QGridLayout
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from qfluentwidgets import (
    CardWidget, BodyLabel, FluentWindow, PushButton,
    InfoBar, InfoBarIcon, InfoBarPosition,
    SubtitleLabel, LineEdit, ComboBox,

)
from qfluentwidgets.multimedia import VideoWidget

import sys
import os


class VideoInterface(QWidget):

    def __init__(self):
        super().__init__()

        self.setObjectName("视频剪辑")
        self.setWindowTitle("视频剪辑工具")
        self.resize(800, 600)  # 设置窗口大小

        # 初始化变量
        self.video_path = ""
        self.time_segments = []  # 剪切时间段
        self.current_time = ""  # 当前时间

        self.setup_ui()

    def setup_ui(self):
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)  # 设置布局的边距
        layout.setSpacing(15)  # 设置控件之间的间距

        # 视频选择
        # 第一层
        card_video_select = CardWidget()
        video_select_title = BodyLabel("视频选择", card_video_select)

        # 创建卡片的布局
        card_layout = QVBoxLayout(card_video_select)
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
        self.video_preview_layout.addWidget(self.video_widget)

        # 添加视频预览卡片到主布局
        layout.addWidget(self.video_preview_card)

        # 时间段选择
        self.time_segment_card = CardWidget()
        self.time_segment_card_layout = QVBoxLayout(self.time_segment_card)
        
        # 添加标题
        time_segment_title = SubtitleLabel("时间段选择")
        self.time_segment_card_layout.addWidget(time_segment_title)
        
        # 创建按钮，使用正确的父组件
        self.start_time_label = PushButton("选择开始时间", self.time_segment_card)
        self.end_time_label = PushButton("选择结束时间", self.time_segment_card)
        
        # 将按钮添加到布局中
        self.time_segment_card_layout.addWidget(self.start_time_label)
        self.time_segment_card_layout.addWidget(self.end_time_label)
        
        # 添加时间段选择卡片到主布局
        layout.addWidget(self.time_segment_card)
        
 

    def toggle_play_pause(self):
        """
        切换视频的播放/暂停状态
        """
        #检查鼠标是否在空格键是否在视频预览卡片上 在视频预览卡片上时空格/暂停播放视频
   
    
    def open_video_file_dialog(self):
        """ 打开视频文件选择对话框 """
        # 使用 QFileDialog.getOpenFileName() 来获取单个文件路径
        # self 作为父窗口，对话框标题，初始目录，文件过滤器
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择视频文件",
            "C:/Users/13691/Videos",  # 默认打开当前工作目录
            "视频文件 (*.mp4 *.avi *.mov *.mkv);;所有文件 (*.*)"
        )

        if file_path:
            print(f"选中的文件是: {file_path}")
            # 保存视频路径
            self.video_path = file_path

            # 视频预览
            self.video_widget.setVideo(QUrl.fromLocalFile(self.video_path))
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = VideoInterface()
    w.show()
    sys.exit(app.exec())
