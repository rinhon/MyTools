import sys
import os
import base64

from PyQt6.QtCore import Qt, QByteArray, QTimer, QSize, QUrl, QPropertyAnimation
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,QStyle,
                             QSlider, QPushButton, QLabel, QFileDialog,QSizePolicy,
                             QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QApplication)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from qfluentwidgets import FluentIcon, Slider
import os


class DarkMediaPlayer(QWidget):
    def __init__(self, video_path):
        super().__init__()

        # 初始化成员变量
        self.video_path = video_path
        self.hide_timer = QTimer()
        self.volume_popup = None
        self.media_player = None
        self.audio_output = None
        self.video_widget = None
        self._is_initialized = False
        
        try:
            self.init_ui()
            self.init_media()
            self._is_initialized = True
        except Exception as e:
            print(f"初始化视频播放器失败: {e}")
            self.cleanup_resources()
            raise

    def init_ui(self):
        # 窗口设置
        self.setWindowTitle("Dark Media Player")
        # self.setWindowIcon(QIcon("dark_icon.ico"))
        self.setMinimumSize(720, 480)

        # 设置主窗口属性
        self.setObjectName("MainWidget")

        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 创建视频容器widget
        self.video_container = QWidget()
        self.video_container.setObjectName("VideoContainer")
        self.video_container.setStyleSheet("#VideoContainer { background: #000000; }")
        
        # 创建视频容器的布局
        self.video_layout = QVBoxLayout(self.video_container)
        self.video_layout.setContentsMargins(0, 0, 0, 0)
        self.video_layout.setSpacing(0)

        # 创建进度条
        self.progress_slider = Slider(Qt.Orientation.Horizontal)
        self.progress_slider.setFixedHeight(30)
        self.progress_slider.setRange(0, 0)  # 初始范围设为0，等待媒体加载后更新
        self.progress_slider.mousePressEvent = self.progress_slider_click

        # 添加组件到主布局
        self.main_layout.addWidget(self.video_container, 1)  # 1表示拉伸因子
        self.main_layout.addWidget(self.progress_slider)


    def init_media(self):
        """初始化媒体播放器"""
        try:
            # 清理当前视频资源（如果有）
            self.clear_video()
            
            # 验证视频路径
            if not self.video_path:
                print("未设置视频路径")
                return
                
            if not os.path.exists(self.video_path):
                print(f"视频文件不存在: {self.video_path}")
                return
            
            # 创建新的视频组件
            self.video_widget = QVideoWidget()
            self.video_widget.setStyleSheet("background: #000000;")
            
            # 将视频组件添加到视频容器布局中
            if hasattr(self, 'video_layout'):
                self.video_layout.addWidget(self.video_widget)
                # 设置视频组件的大小策略
                self.video_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            
            # 创建并初始化音频输出
            self.audio_output = QAudioOutput()
            self.audio_output.setVolume(0.5)  # 设置默认音量

            # 创建媒体播放器
            self.media_player = QMediaPlayer()
            
            # 先设置音频输出
            self.media_player.setAudioOutput(self.audio_output)
            QApplication.processEvents()  # 让Qt处理待处理的事件
            
            # 再设置视频输出
            self.media_player.setVideoOutput(self.video_widget)
            QApplication.processEvents()  # 让Qt处理待处理的事件
            
            # 验证输出设置
            if not self.media_player.audioOutput():
                raise Exception("音频输出设置验证失败")
            
            if not self.media_player.videoOutput():
                raise Exception("视频输出设置验证失败")
            
            # 连接媒体播放器信号
            self.media_player.positionChanged.connect(self.position_changed)
            self.media_player.durationChanged.connect(self.duration_changed)
            self.media_player.mediaStatusChanged.connect(self.media_status_changed)
            
            # 连接进度条信号
            self.progress_slider.sliderMoved.connect(self.set_position)
            
            # 设置默认音量
            self.audio_output.setVolume(0.5)
            
            # 验证视频路径
            if not self.video_path or not os.path.exists(self.video_path):
                raise Exception("无效的视频文件路径")
            
            # 设置视频源并开始播放
            video_url = QUrl.fromLocalFile(self.video_path)
            self.media_player.setSource(video_url)
            
            # 检查媒体是否成功加载
            if self.media_player.mediaStatus() == QMediaPlayer.MediaStatus.InvalidMedia:
                raise Exception("无效的媒体文件")
            
            # 确保视频组件可见
            if self.video_widget:
                self.video_widget.show()
                
            # 强制布局更新
            if hasattr(self, 'main_layout'):
                self.main_layout.update()
                self.updateGeometry()
                QApplication.processEvents()
            
            # 开始播放
            self.media_player.play()
            
            # 设置初始化标志
            self._is_initialized = True
            
        except Exception as e:
            self._is_initialized = False
            print(f"初始化媒体播放器失败: {e}")
            # 清理已创建的资源
            self.cleanup_resources()
            raise Exception(f"初始化媒体播放器失败: {e}")

    def position_changed(self, position):
        """更新进度条位置"""
        try:
            if hasattr(self, 'progress_slider') and self.progress_slider and self._is_initialized:
                self.progress_slider.setValue(position)
        except Exception as e:
            print(f"更新进度条位置时出错: {e}")

    def duration_changed(self, duration):
        """更新进度条范围"""
        try:
            if hasattr(self, 'progress_slider') and self.progress_slider and self._is_initialized:
                self.progress_slider.setRange(0, duration)
        except Exception as e:
            print(f"更新进度条范围时出错: {e}")

    def format_time(self, ms):
        seconds = ms // 1000
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def is_playing_status(self):
        """检查是否正在播放"""
        try:
            if not self._is_initialized or not hasattr(self, 'media_player') or not self.media_player:
                return False
            return self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
        except Exception as e:
            print(f"检查播放状态时出错: {e}")
            return False

    def toggle_play(self):
        """切换播放/暂停状态"""
        try:
            if not self._is_initialized or not hasattr(self, 'media_player') or not self.media_player:
                print("媒体播放器未初始化")
                return
                
            if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                self.media_player.pause()
            else:
                # 检查媒体源是否有效
                if self.media_player.mediaStatus() != QMediaPlayer.MediaStatus.InvalidMedia:
                    self.media_player.play()
                else:
                    print("无效的媒体源")
        except Exception as e:
            print(f"切换播放状态时出错: {e}")

    def seek(self, seconds):
        """跳转指定秒数"""
        try:
            if not self._is_initialized or not hasattr(self, 'media_player') or not self.media_player:
                print("媒体播放器未初始化")
                return
                
            current_pos = self.media_player.position()
            duration = self.media_player.duration()
            
            # 计算新位置
            new_pos = current_pos + seconds * 1000
            # 确保在有效范围内
            new_pos = max(0, min(new_pos, duration))
            
            self.media_player.setPosition(new_pos)
        except Exception as e:
            print(f"跳转播放位置时出错: {e}")

    def set_position(self, position):
        """设置播放位置"""
        try:
            if not self._is_initialized or not hasattr(self, 'media_player') or not self.media_player:
                print("媒体播放器未初始化")
                return
                
            if 0 <= position <= self.media_player.duration():
                self.media_player.setPosition(position)
        except Exception as e:
            print(f"设置播放位置时出错: {e}")

    def get_current_time(self):
        """获取当前播放位置（毫秒）"""
        try:
            if not self._is_initialized or not hasattr(self, 'media_player') or not self.media_player:
                return 0
            return self.media_player.position()
        except Exception as e:
            print(f"获取当前播放位置时出错: {e}")
            return 0

    def get_media_player(self):
        """获取媒体播放器实例"""
        if not self._is_initialized:
            print("媒体播放器未初始化")
            return None
        return self.media_player
    
    def media_status_changed(self, status):
        """处理媒体状态改变"""
        try:
            if not self._is_initialized or not hasattr(self, 'media_player') or not self.media_player:
                return
                
            if status == QMediaPlayer.MediaStatus.EndOfMedia:
                # 播放结束时，重置位置并重新播放
                self.media_player.setPosition(0)
                self.media_player.play()
            elif status == QMediaPlayer.MediaStatus.InvalidMedia:
                print("无效的媒体文件")
            elif status == QMediaPlayer.MediaStatus.LoadedMedia:
                # 媒体加载完成，可以开始播放
                self.media_player.play()
        except Exception as e:
            print(f"处理媒体状态改变时出错: {e}")
    
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
    
    def __del__(self):
        """析构函数，确保资源被正确释放"""
        self.cleanup_resources()
        
    def cleanup_resources(self):
        """清理所有资源
        
        安全地释放和清理所有媒体播放相关资源，包括：
        1. 停止并销毁定时器
        2. 停止媒体播放并断开所有信号连接
        3. 清理音频输出设备
        4. 销毁视频组件
        5. 断开进度条信号连接
        6. 销毁音量弹出窗口
        7. 强制垃圾回收
        
        注意：该方法会捕获并打印所有异常，确保清理过程不会中断程序运行。
        """
        """清理所有资源"""
        try:
            # 停止所有定时器
            if hasattr(self, 'hide_timer') and self.hide_timer:
                try:
                    self.hide_timer.stop()
                    self.hide_timer.timeout.disconnect()  # 断开所有信号连接
                except Exception:
                    pass
                finally:
                    self.hide_timer.deleteLater()
                    self.hide_timer = None

            # 停止播放并清理媒体播放器
            if hasattr(self, 'media_player') and self.media_player:
                # 停止播放
                self.media_player.stop()
                
                # 断开所有信号连接
                try:
                    self.media_player.positionChanged.disconnect()
                    self.media_player.durationChanged.disconnect()
                    self.media_player.mediaStatusChanged.disconnect()
                except Exception:
                    pass

                # 清除视频输出
                if self.video_widget:
                    self.media_player.setVideoOutput(None)

                # 清除音频输出
                if self.audio_output:
                    self.media_player.setAudioOutput(None)

                # 清除媒体源
                self.media_player.setSource(QUrl())
                
                # 标记为待删除
                self.media_player.deleteLater()
                self.media_player = None

            # 清理音频输出
            if hasattr(self, 'audio_output') and self.audio_output:
                try:
                    self.audio_output.setVolume(0)  # 先将音量设为0
                except Exception:
                    pass
                finally:
                    self.audio_output.deleteLater()
                    self.audio_output = None

            # 清理视频组件
            if hasattr(self, 'video_widget') and self.video_widget:
                try:
                    # 从布局中移除
                    if hasattr(self, 'video_layout'):
                        self.video_layout.removeWidget(self.video_widget)
                    self.video_widget.setParent(None)
                    self.video_widget.hide()
                except Exception:
                    pass
                finally:
                    self.video_widget.deleteLater()
                    self.video_widget = None

            # 清理进度条连接
            if hasattr(self, 'progress_slider') and self.progress_slider:
                try:
                    self.progress_slider.sliderMoved.disconnect()
                    self.progress_slider.setValue(0)
                    self.progress_slider.setRange(0, 0)
                except Exception:
                    pass

            # 清理音量弹出窗口
            if hasattr(self, 'volume_popup') and self.volume_popup:
                try:
                    self.volume_popup.close()
                except Exception:
                    pass
                finally:
                    self.volume_popup.deleteLater()
                    self.volume_popup = None

            # 更新布局
            if hasattr(self, 'video_layout'):
                self.video_layout.update()
            if hasattr(self, 'main_layout'):
                self.main_layout.update()
            
            # 重置状态
            self._is_initialized = False
            self.video_path = None

            # 强制处理待处理的事件
            QApplication.processEvents()

            # 强制垃圾回收
            import gc
            gc.collect()

        except Exception as e:
            print(f"清理资源时出错: {e}")
    
    def stop(self):
        """停止播放"""
        if hasattr(self, 'media_player') and self.media_player:
            self.media_player.stop()
            
    def clear_video(self):
        """清理当前视频资源"""
        try:
            if not self._is_initialized:
                return
                
            # 停止播放
            if hasattr(self, 'media_player') and self.media_player:
                self.media_player.stop()
                # 清除媒体源
                self.media_player.setSource(QUrl())
                
            # 重置进度条
            if hasattr(self, 'progress_slider') and self.progress_slider:
                self.progress_slider.setValue(0)
                self.progress_slider.setRange(0, 0)
            
            # 从布局中移除并删除旧的视频组件
            if hasattr(self, 'video_widget') and self.video_widget:
                # 停止视频输出
                if hasattr(self, 'media_player') and self.media_player:
                    self.media_player.setVideoOutput(None)
                
                # 从视频容器布局中移除
                if hasattr(self, 'video_layout'):
                    self.video_layout.removeWidget(self.video_widget)
                    
                # 确保组件不可见并释放
                self.video_widget.setParent(None)
                self.video_widget.hide()
                self.video_widget.deleteLater()
                self.video_widget = None
                
                # 清理视频容器
                if hasattr(self, 'video_container'):
                    self.video_container.update()
                
                # 强制布局更新
                if hasattr(self, 'video_layout'):
                    self.video_layout.update()
                if hasattr(self, 'main_layout'):
                    self.main_layout.update()
                self.updateGeometry()
                QApplication.processEvents()
                
            # 重置视频路径
            self.video_path = None
            
            # 重置初始化标志
            self._is_initialized = False
            
            print("视频资源已清理")
            
        except Exception as e:
            print(f"清理视频资源时出错: {e}")
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    player = DarkMediaPlayer(
        "G:/Nyotengu/LazyProcrast/1080P_4000K_289668092.mp4")
    player.show()
    sys.exit(app.exec())