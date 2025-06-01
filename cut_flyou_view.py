from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit
from PyQt6.QtCore import Qt
from qfluentwidgets import (FlyoutViewBase, PrimaryPushButton, BodyLabel, 
                           TableWidget, PushButton, ComboBox, LineEdit, 
                           InfoBar, InfoBarPosition)
from moviepy import VideoFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
from moviepy.video.io.ffmpeg_reader import ffmpeg_parse_infos as video_infos
import os
from datetime import datetime


class   CutFlyoutView(FlyoutViewBase):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.vBoxLayout = QVBoxLayout(self)
        self.params_table = TableWidget(self)
        self.setup_ui()
        self.param_options = [
            ("fps", "帧率 (fps)"),
            ("codec", "视频编码器 (codec)"),
            ("bitrate", "视频比特率 (bitrate)"),
            ("audio", "包含音频 (audio)"),
            ("audio_fps", "音频采样率 (audio_fps)"),
            ("preset", "编码预设 (preset)"),
            ("audio_nbytes", "音频字节数 (audio_nbytes)"),
            ("audio_codec", "音频编码器 (audio_codec)"),
            ("audio_bitrate", "音频比特率 (audio_bitrate)"),
            ("audio_bufsize", "音频缓冲大小 (audio_bufsize)"),
            ("temp_audiofile", "临时音频文件 (temp_audiofile)"),
            ("temp_audiofile_path", "临时音频文件路径 (temp_audiofile_path)"),
            ("remove_temp", "删除临时文件 (remove_temp)"),
            ("write_logfile", "写入日志文件 (write_logfile)"),
            ("threads", "编码线程数 (threads)"),
            ("ffmpeg_params", "FFmpeg参数 (ffmpeg_params)"),
            ("logger", "日志记录器 (logger)"),
            ("pixel_format", "像素格式 (pixel_format)")
        ]
        self.param_values = {}  # 存储用户选择的参数

    def setup_ui(self):
        # 添加说明标签
        self.label = BodyLabel("自定义输出参数（可选）")
        self.vBoxLayout.addWidget(self.label)
        
        # 设置参数表格
        self.params_table.setColumnCount(2)
        self.params_table.setHorizontalHeaderLabels(["参数", "值"])
        
        self.params_table.setRowCount(0)
        self.vBoxLayout.addWidget(self.params_table)
        
        # 添加按钮行
        self.button_layout = QHBoxLayout()
        self.add_param_button = PushButton("添加参数")
        self.add_param_button.clicked.connect(self.add_param_row)
        self.button_layout.addWidget(self.add_param_button)
        
        self.remove_param_button = PushButton("删除参数")
        self.remove_param_button.clicked.connect(self.remove_param_row)
        self.button_layout.addWidget(self.remove_param_button)
        
        self.vBoxLayout.addLayout(self.button_layout)
        
        # 添加剪辑按钮
        self.button = PrimaryPushButton('开始剪辑')
        self.button.clicked.connect(lambda: self.process_video())
        self.button.setFixedWidth(140)
        
        self.vBoxLayout.setSpacing(12)
        self.vBoxLayout.setContentsMargins(20, 16, 20, 16)
        self.vBoxLayout.addWidget(self.button)

    def add_param_row(self):
        """添加一行参数选择"""
        row = self.params_table.rowCount()
        self.params_table.setRowCount(row + 1)
        
        # 创建参数下拉框
        param_combo = ComboBox(self)
        for param_name, param_desc in self.param_options:
            param_combo.addItem(param_desc, param_name)  # 显示描述文本，存储实际参数名
        self.params_table.setCellWidget(row, 0, param_combo)
        
        # 创建值输入框
        value_input = LineEdit(self)
        # 根据选择的参数类型添加提示文本
        param_combo.currentIndexChanged.connect(
            lambda: self.update_value_input_hint(value_input, param_combo.currentData())
        )
        self.params_table.setCellWidget(row, 1, value_input)
        
    def update_value_input_hint(self, value_input, param_name):
        """更新值输入框的提示文本"""
        hints = {
            'fps': '输入数字，如: 24, 30, 60',
            'codec': '如: libx264, libx265',
            'bitrate': '如: 5000k',
            'audio': '输入 true 或 false',
            'audio_fps': '输入数字，如: 44100',
            'preset': '如: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow',
            'audio_nbytes': '输入数字，如: 4',
            'audio_codec': '如: aac, mp3',
            'audio_bitrate': '如: 192k',
            'audio_bufsize': '输入数字，如: 2000',
            'temp_audiofile': '临时音频文件名',
            'temp_audiofile_path': '临时音频文件路径',
            'remove_temp': '输入 true 或 false',
            'write_logfile': '输入 true 或 false',
            'threads': '输入数字，如: 0（自动）, 1, 2, 4',
            'ffmpeg_params': '如: ["-vf", "scale=1280:720"]',
            'logger': '如: bar, None',
            'pixel_format': '如: yuv420p, rgb24'
        }
        value_input.setPlaceholderText(hints.get(param_name, '请输入参数值'))

    def remove_param_row(self):
        """删除选中的参数行"""
        selected_rows = self.params_table.selectedIndexes()
        if not selected_rows:
            InfoBar.warning(
                title="未选择行",
                content="请先选择要删除的参数行",
                parent=self,
                duration=2000,
                position=InfoBarPosition.BOTTOM_RIGHT
            )
            return
            
        row = selected_rows[0].row()
        self.params_table.removeRow(row)

    def collect_params(self):
        """收集用户设置的参数"""
        params = {}
        for row in range(self.params_table.rowCount()):
            param_widget = self.params_table.cellWidget(row, 0)
            value_widget = self.params_table.cellWidget(row, 1)
            
            if param_widget and value_widget:
               
                # 假设value_widget是QLineEdit
                if hasattr(value_widget, 'text'):
                    param_name = value_widget.text().strip()
                else:
                    # 如果不是QLineEdit，尝试其他方式获取值
                    param_value = str(value_widget)
                
                if not param_value:  # 跳过空值
                    continue

                    
                try:
                    # 根据参数类型转换值
                    if param_name in ["fps", "audio_fps", "audio_nbytes", "audio_bufsize", "threads"]:
                        params[param_name] = int(param_value)
                    elif param_name in ["audio", "remove_temp", "write_logfile"]:
                        params[param_name] = param_value.lower() == "true"
                    elif param_name == "ffmpeg_params":
                        # 尝试将字符串转换为列表
                        import ast
                        try:
                            params[param_name] = ast.literal_eval(param_value)
                        except:
                            # 如果转换失败，保持原始字符串
                            params[param_name] = param_value
                    elif param_name == "bitrate" or param_name == "audio_bitrate":
                        # 确保比特率值包含单位（k）
                        if param_value.isdigit():
                            params[param_name] = f"{param_value}k"
                        else:
                            params[param_name] = param_value
                    else:
                        params[param_name] = param_value
                except ValueError as e:
                    InfoBar.warning(
                        title="参数格式错误",
                        content=f"参数 {param_name} 的值 '{param_value}' 格式不正确，已忽略此参数",
                        parent=self,
                        duration=3000,
                        position=InfoBarPosition.BOTTOM_RIGHT
                    )
                    continue
                        
        return params

    def time_to_seconds(self, time_str):
        """将时间字符串转换为秒数"""
        try:
            parts = time_str.split(':')
            if len(parts) == 3:  # HH:MM:SS
                hours, minutes, seconds = parts
                return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
            elif len(parts) == 2:  # MM:SS
                minutes, seconds = parts
                return int(minutes) * 60 + float(seconds)
            else:  # SS
                return float(time_str)
        except Exception:
            return 0

    def process_video(self):
        if self.parent is None:
            return
            
        # 显示处理开始消息
        InfoBar.info(
            title="开始处理",
            content="正在处理视频，请稍候...",
            parent=self.parent,
            duration=3000,
            position=InfoBarPosition.BOTTOM_RIGHT
        )
        
        try:
            # 获取文件所在路径
            file_path = self.parent.video_path

            # 1. 加载视频
            video = VideoFileClip(file_path)
            
            clips = []
            # 2. 剪切片段
            if self.parent.time_segments is not None:
                # 剪切时间段列表，存储多个时间片段
                for i in range(len(self.parent.time_segments)):
                    start_time = self.parent.time_segments[i][0]
                    end_time = self.parent.time_segments[i][1]
                    # 将时间字符串转换为秒数
                    start_seconds = self.time_to_seconds(start_time)
                    end_seconds = self.time_to_seconds(end_time)
                    clip = video.subclipped(start_seconds, end_seconds)
                    clips.append(clip)
            
            if not clips:
                InfoBar.error(
                    title="剪辑失败",
                    content="没有有效的时间片段",
                    parent=self.parent,
                    duration=3000,
                    position=InfoBarPosition.BOTTOM_RIGHT
                )
                return
                
            # 拼接剪辑
            final_video = concatenate_videoclips(clips)
            
            # 获取文件名和扩展名
            file_name, file_ext = os.path.splitext(os.path.basename(file_path))
            # 生成输出文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(os.path.dirname(file_path), 
                                      f"{file_name}_cut_{timestamp}{file_ext}")
            
            # 收集用户设置的参数
            params = self.collect_params()
            
            
            # 获取视频的参数
            video_info  = video_infos(file_path)
            if video_info is None:
                return
            
            print("视频参数: " + str(video_info))
            # 设置默认参数
            if "codec" not in params:
                # params["codec"] = "libx264"
                params["codec"] = video_info.get("video_codec_name")
            if "audio_codec" not in params:
                params["audio_codec"] = "aac"
            if "fps" not in params:
                params["fps"] = video_info.get("video_fps")
            if "bitrate" not in params:
                params["bitrate"] = video_info.get("video_bitrate")
                
            # 显示使用的参数
            param_str = ", ".join([f"{k}={v}" for k, v in params.items()])
            print(f"使用参数: {param_str}")
                
            # 写入输出文件
            final_video.write_videofile(output_path, **params)
            
            # 显示成功消息
            InfoBar.success(
                title="剪辑成功",
                content=f"视频已保存至: {output_path}",
                parent=self.parent,
                duration=5000,
                position=InfoBarPosition.BOTTOM_RIGHT
            )
            
            # 释放资源
            video.close()
            final_video.close()
            
        except Exception as e:
            error_msg = str(e)
            # 添加更多错误信息的处理
            if "codec" in error_msg.lower():
                error_msg += "\n请检查编码器设置是否正确"
            elif "audio" in error_msg.lower():
                error_msg += "\n请检查音频相关参数设置"
            elif "ffmpeg" in error_msg.lower():
                error_msg += "\n请检查FFmpeg参数设置"
                
            InfoBar.error(
                title="剪辑失败",
                content=f"错误: {error_msg}",
                parent=self.parent,
                duration=5000,
                position=InfoBarPosition.BOTTOM_RIGHT
            )