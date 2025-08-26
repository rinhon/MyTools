#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI文件整理工具 - 使用 qfluentwidgets 框架
使用图形界面按文件类型分类整理指定文件夹中的所有文件
"""

import os
import shutil
import platform
import threading
import subprocess
from pathlib import Path
from collections import defaultdict

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QProgressBar
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon

from qfluentwidgets import (
    FluentWindow, PrimaryPushButton, PushButton, LineEdit, 
    BodyLabel, SubtitleLabel, CaptionLabel, CardWidget,
    ScrollArea, TextEdit, ProgressBar, InfoBar, InfoBarPosition,
    FluentIcon as FIF
)

class FileOrganizer:
    def __init__(self, target_folder):
        self.target_folder = Path(target_folder)
        
        # 文件类型分类
        self.file_categories = {
            'videos': {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.m4v', 
                      '.mpg', '.mpeg', '.3gp', '.asf', '.rm', '.rmvb', '.vob', '.ts'},
            'images': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.svg', 
                      '.ico', '.webp', '.raw', '.cr2', '.nef', '.orf', '.sr2'},
            'texts': {'.txt', '.doc', '.docx', '.pdf', '.rtf', '.odt', '.pages', '.tex',
                     '.md', '.csv', '.xls', '.xlsx', '.ppt', '.pptx', '.odp', '.ods'},
            'archives': {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.z', 
                        '.tar.gz', '.tar.bz2', '.tar.xz', '.dmg', '.iso'},
            'others': set()
        }
        
        # 获取系统文件名长度限制
        self.max_filename_length = self._get_max_filename_length()
        
    def _get_max_filename_length(self):
        """获取系统文件名长度限制"""
        system = platform.system()
        if system == "Windows":
            return 255
        elif system == "Darwin":
            return 255
        else:
            return 255
    
    def _get_file_category(self, file_extension):
        """根据文件扩展名确定文件类别"""
        file_extension = file_extension.lower()
        
        for category, extensions in self.file_categories.items():
            if category != 'others' and file_extension in extensions:
                return category
        
        return 'others'
    
    def _create_safe_filename(self, original_path, target_category):
        """创建安全的文件名，处理路径、重名和长度问题"""
        file_path = Path(original_path)
        relative_path = file_path.relative_to(self.target_folder)
        
        # 构建新文件名：文件夹路径 + 原文件名
        folder_parts = list(relative_path.parent.parts) if relative_path.parent.parts != ('.',) else []
        folder_prefix = '_'.join(folder_parts) if folder_parts else ""

        # 组合文件名
        if folder_prefix:
            new_filename = f"{folder_prefix}_{file_path.name}"
        else:
            new_filename = file_path.name
        
        # 处理文件名长度限制
        name_without_ext = file_path.stem
        extension = file_path.suffix
        
        # 确保文件名长度不超过系统限制
        if len(new_filename) > self.max_filename_length:
            # 保留扩展名
            max_name_length = self.max_filename_length - len(extension) - 10  # 预留空间
            if max_name_length <= 0:
                new_filename = f"file_{hash(str(file_path)) % 10000}{extension}"
            elif folder_prefix:
                # 如果前缀过长，优先保留文件名部分
                if len(folder_prefix) > max_name_length // 2:
                    folder_prefix = folder_prefix[:max_name_length // 2]
                remaining_length = max_name_length - len(folder_prefix) - 1
                if remaining_length > 0:
                    truncated_name = name_without_ext[:remaining_length]
                    new_filename = f"{folder_prefix}_{truncated_name}{extension}"
                else:
                    new_filename = f"{folder_prefix[:max_name_length-5]}{extension}"
            else:
                truncated_name = name_without_ext[:max_name_length]
                new_filename = f"{truncated_name}{extension}"
        
        # 处理重名问题
        target_path = self.target_folder / target_category / new_filename
        counter = 1
        original_new_filename = new_filename
        
        while target_path.exists():
            name_part = Path(original_new_filename).stem
            ext_part = Path(original_new_filename).suffix
            new_filename = f"{name_part}_{counter}{ext_part}"
            target_path = self.target_folder / target_category / new_filename
            counter += 1
            
            # 防止无限循环
            if counter > 1000:
                new_filename = f"{name_part}_{hash(str(file_path)) % 10000}{ext_part}"
                break
        
        return new_filename
    
    def _create_category_folders(self):
        """创建分类文件夹"""
        for category in self.file_categories.keys():
            category_folder = self.target_folder / category
            category_folder.mkdir(exist_ok=True)
    
    def organize_files(self):
        """主要的文件整理功能"""
        if not self.target_folder.exists():
            raise FileNotFoundError(f"目标文件夹 {self.target_folder} 不存在")
        
        # 创建分类文件夹
        self._create_category_folders()
        
        # 统计信息
        stats = defaultdict(int)
        processed_files = 0
        
        # 收集所有需要处理的文件（避免在移动过程中遍历）
        files_to_process = []
        for root, dirs, files in os.walk(self.target_folder):
            for file_name in files:
                file_path = Path(root) / file_name
                # 跳过分类文件夹中的文件
                if not any(cat in str(file_path) for cat in self.file_categories.keys()):
                    files_to_process.append(file_path)
        
        total_files = len(files_to_process)
        if total_files == 0:
            return stats, []
        
        # 处理文件
        log_messages = []
        for i, file_path in enumerate(files_to_process):
            try:
                # 检查文件是否仍然存在（防止并发问题）
                if not file_path.exists():
                    continue
                    
                # 获取文件类别
                file_extension = file_path.suffix
                category = self._get_file_category(file_extension)
                
                # 创建安全的文件名
                safe_filename = self._create_safe_filename(file_path, category)
                
                # 目标路径
                target_path = self.target_folder / category / safe_filename
                
                # 移动文件（而不是复制）
                try:
                    shutil.move(str(file_path), str(target_path))
                except Exception as e:
                    log_messages.append(f"移动文件 {file_path} 失败: {e}")
                    continue
                
                # 更新统计
                stats[category] += 1
                processed_files += 1
                log_messages.append(f"已处理: {file_path.name} -> {category}/{safe_filename}")
                
                # 计算进度
                progress = int(((i + 1) / total_files) * 100)
                
            except Exception as e:
                log_messages.append(f"处理文件 {file_path} 时出错: {e}")
        
        # 删除空的原始文件夹
        self._remove_empty_dirs(self.target_folder)
        
        log_messages.append("整理完成！统计信息:")
        log_messages.append(f"总共处理文件: {processed_files}")
        for category, count in stats.items():
            log_messages.append(f"{category}: {count} 个文件")
        
        return stats, log_messages
    
    def _remove_empty_dirs(self, path):
        """删除空的文件夹"""
        try:
            # 从最深层开始删除
            for root, dirs, files in os.walk(path, topdown=False):
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    try:
                        if os.path.isdir(dir_path) and not os.listdir(dir_path):  # 如果文件夹为空
                            try:
                                os.rmdir(dir_path)
                            except (PermissionError, OSError):
                                pass
                    except OSError:
                        pass
        except Exception:
            pass


class FileOrganizerWorker(QThread):
    """文件整理工作线程"""
    progress_updated = pyqtSignal(int)
    log_updated = pyqtSignal(str)
    finished_signal = pyqtSignal(dict, list)
    error_signal = pyqtSignal(str)

    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path

    def run(self):
        try:
            organizer = FileOrganizer(self.folder_path)
            stats, log_messages = organizer.organize_files()
            
            # 发送日志消息
            for message in log_messages:
                self.log_updated.emit(message)
            
            # 发送完成信号
            self.finished_signal.emit(stats, log_messages)
            
        except Exception as e:
            self.error_signal.emit(str(e))


class FileOrganizerInterface(QWidget):
    """文件整理主界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.folder_path = ""
        self.worker = None
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # 标题
        title_label = SubtitleLabel("文件整理工具", self)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 文件夹选择卡片
        folder_card = CardWidget(self)
        folder_layout = QVBoxLayout(folder_card)
        folder_layout.setContentsMargins(20, 20, 20, 20)
        
        folder_title = BodyLabel("选择要整理的文件夹", self)
        folder_layout.addWidget(folder_title)
        
        folder_input_layout = QHBoxLayout()
        self.folder_line_edit = LineEdit(self)
        self.folder_line_edit.setPlaceholderText("请选择要整理的文件夹")
        self.folder_line_edit.textChanged.connect(self.on_folder_text_changed)
        
        self.browse_button = PushButton("浏览", self)
        self.browse_button.clicked.connect(self.browse_folder)
        
        folder_input_layout.addWidget(self.folder_line_edit)
        folder_input_layout.addWidget(self.browse_button)
        folder_layout.addLayout(folder_input_layout)
        
        layout.addWidget(folder_card)
        
        # 操作按钮卡片
        button_card = CardWidget(self)
        button_layout = QHBoxLayout(button_card)
        button_layout.setContentsMargins(20, 20, 20, 20)
        
        self.organize_button = PrimaryPushButton("开始整理", self)
        self.organize_button.clicked.connect(self.start_organizing)
        self.organize_button.setEnabled(False)
        
        self.clear_button = PushButton("清除日志", self)
        self.clear_button.clicked.connect(self.clear_log)
        
        self.open_folder_button = PushButton("打开文件夹", self)
        self.open_folder_button.clicked.connect(self.open_target_folder)
        self.open_folder_button.setEnabled(False)
        
        button_layout.addWidget(self.organize_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.open_folder_button)
        button_layout.addStretch()
        
        layout.addWidget(button_card)
        
        # 进度条
        self.progress_bar = ProgressBar(self)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 日志区域卡片
        log_card = CardWidget(self)
        log_layout = QVBoxLayout(log_card)
        log_layout.setContentsMargins(10, 10, 10, 10)
        
        log_title = BodyLabel("处理日志", self)
        log_layout.addWidget(log_title)
        
        self.log_text = TextEdit(self)
        self.log_text.setMaximumHeight(300)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_card)
        
        # 说明文本
        info_text = """
使用说明：
1. 点击"浏览"选择要整理的文件夹
2. 点击"开始整理"开始文件分类
3. 文件将直接在原文件夹中按类型分类：videos(视频)、images(图片)、texts(文本)、archives(压缩包)、others(其他)
4. 重名文件会自动添加数字后缀，过长文件名会自动截取
5. 原始子文件夹结构会合并到文件名中
        """
        
        info_label = CaptionLabel(info_text, self)
        info_label.setStyleSheet("color: #666666;")
        layout.addWidget(info_label)
        
        layout.addStretch()
    
    def browse_folder(self):
        """浏览文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择要整理的文件夹")
        if folder:
            self.folder_path = folder
            self.folder_line_edit.setText(folder)
            self.organize_button.setEnabled(True)
            self.open_folder_button.setEnabled(True)
    
    def on_folder_text_changed(self, text):
        """文件夹路径文本改变时"""
        self.folder_path = text
        folder_exists = os.path.exists(text) and os.path.isdir(text)
        self.organize_button.setEnabled(folder_exists)
        self.open_folder_button.setEnabled(folder_exists)
    
    def start_organizing(self):
        """开始整理文件"""
        if not self.folder_path:
            self.show_error("请先选择要整理的文件夹")
            return
        
        if not os.path.exists(self.folder_path):
            self.show_error("选择的文件夹不存在")
            return
        
        # 确认操作
        reply = QMessageBox.question(
            self, 
            "确认操作", 
            f"即将整理文件夹：{self.folder_path}\n\n"
            "文件将直接在原文件夹中按类型重新分类组织。\n"
            "建议先备份重要文件。\n\n"
            "确认继续吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        # 开始整理
        self.organize_button.setEnabled(False)
        self.browse_button.setEnabled(False)
        self.open_folder_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # 启动工作线程
        self.worker = FileOrganizerWorker(self.folder_path)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.log_updated.connect(self.add_log_message)
        self.worker.finished_signal.connect(self.on_organizing_finished)
        self.worker.error_signal.connect(self.on_organizing_error)
        self.worker.start()
    
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
    
    def add_log_message(self, message):
        """添加日志消息"""
        self.log_text.append(message)
    
    def clear_log(self):
        """清除日志"""
        self.log_text.clear()
    
    def open_target_folder(self):
        """打开目标文件夹"""
        if not self.folder_path or not os.path.exists(self.folder_path):
            self.show_error("文件夹路径无效")
            return
        
        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(self.folder_path)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", self.folder_path])
            else:  # Linux和其他Unix-like系统
                subprocess.run(["xdg-open", self.folder_path])
        except Exception as e:
            self.show_error(f"无法打开文件夹: {str(e)}")
    
    def on_organizing_finished(self, stats, log_messages):
        """整理完成"""
        self.organize_button.setEnabled(True)
        self.browse_button.setEnabled(True)
        self.open_folder_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # 显示完成信息
        stats_message = "\n".join([f"{cat}: {count} 个文件" for cat, count in stats.items()])
        if not stats_message:
            stats_message = "没有找到需要整理的文件"
        
        # 显示通知
        InfoBar.success(
            title='整理完成',
            content=f'文件整理已完成！\n统计信息：\n{stats_message}',
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=5000,
            parent=self
        )
        
        # 询问是否打开文件夹
        reply = QMessageBox.question(
            self,
            "完成",
            f"文件整理完成！\n\n统计信息：\n{stats_message}\n\n是否现在打开文件夹查看结果？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            self.open_target_folder()
    
    def on_organizing_error(self, error_message):
        """整理出错"""
        self.organize_button.setEnabled(True)
        self.browse_button.setEnabled(True)
        self.open_folder_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.show_error(f"整理过程中出现错误：{error_message}")
    
    def show_error(self, message):
        """显示错误信息"""
        InfoBar.error(
            title='错误',
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=5000,
            parent=self
        )


class MainWindow(FluentWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('文件整理工具')
        self.setWindowIcon(QIcon('./resource/icon/file_icon.png'))  # 如果有图标文件的话
        self.resize(900, 700)
        
        # 居中显示
        screen = QApplication.primaryScreen().availableGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())
        
        # 创建主界面
        self.organizer_interface = FileOrganizerInterface()
        self.organizer_interface.setObjectName("文件整理")
        
        # 添加到导航
        self.addSubInterface(self.organizer_interface, FIF.FOLDER, '文件整理')
        
        # 设置主题
        from qfluentwidgets import setTheme, Theme
        setTheme(Theme.AUTO)


def main():
    """主函数"""
    import sys
    
    # 启用高DPI缩放
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()