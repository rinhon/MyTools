# import sys
# from PyQt6.QtWidgets import (
#     QApplication, QWidget, QVBoxLayout, QHBoxLayout,
#     QLabel, QPushButton, QLineEdit, QTextEdit, QSpacerItem, QSizePolicy, QFrame
# )
# from PyQt6.QtCore import Qt
# from qfluentwidgets import CardWidget # 导入 CardWidget

# class FourCardLayoutApp(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("四卡片布局示例")
#         self.setGeometry(100, 100, 650, 900) # x, y, width, height

#         # 1. 创建主窗口的垂直布局，用于容纳所有 CardWidget
#         self.main_v_layout = QVBoxLayout(self)
#         self.main_v_layout.setContentsMargins(15, 15, 15, 15) # 给所有卡片留点边距
#         self.main_v_layout.setSpacing(15) # 卡片之间的垂直间距

#         self._setup_card_widgets()

#     def _setup_card_widgets(self):
#         # --- 1. 第一个 CardWidget (顶部单行区域) ---
#         card1 = CardWidget(self) # 将主窗口设为父对象
#         card1_layout = QVBoxLayout(card1) # 在 CardWidget 内部创建布局
#         card1_layout.setContentsMargins(20, 20, 20, 20) # 内部边距
        
#         top_line_edit = QLineEdit("卡片1：顶部信息区域")
#         top_line_edit.setMinimumHeight(45)
#         top_line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         card1_layout.addWidget(top_line_edit)
        
#         self.main_v_layout.addWidget(card1)

#         # --- 2. 第二个 CardWidget (三个或四个并排矩形) ---
#         card2 = CardWidget(self)
#         card2_layout = QVBoxLayout(card2)
#         card2_layout.setContentsMargins(20, 20, 20, 20)

#         middle_h_layout = QHBoxLayout()
#         # 根据图片，看起来有四个并排的矩形
#         btn1 = QPushButton("选项 A")
#         btn2 = QPushButton("选项 B")
#         btn3 = QPushButton("选项 C")
#         btn4 = QPushButton("选项 D") # 新增一个按钮

#         btn1.setFixedSize(120, 45)
#         btn2.setFixedSize(120, 45)
#         btn3.setFixedSize(120, 45)
#         btn4.setFixedSize(120, 45)

#         middle_h_layout.addStretch(1) # 左侧伸缩器，帮助居中
#         middle_h_layout.addWidget(btn1)
#         middle_h_layout.addSpacing(10)
#         middle_h_layout.addWidget(btn2)
#         middle_h_layout.addSpacing(10)
#         middle_h_layout.addWidget(btn3)
#         middle_h_layout.addSpacing(10)
#         middle_h_layout.addWidget(btn4) # 添加第四个按钮
#         middle_h_layout.addStretch(1) # 右侧伸缩器

#         card2_layout.addLayout(middle_h_layout)
        
#         self.main_v_layout.addWidget(card2)

#         # --- 3. 第三个 CardWidget (中央复杂区域：大文本区 + 底部输入/按钮) ---
#         card3 = CardWidget(self)
#         card3_layout = QVBoxLayout(card3)
#         card3_layout.setContentsMargins(20, 20, 20, 20)

#         # 3.1. 卡片内部顶部标题 (图片上部有一个小矩形)
#         card3_top_title = QLineEdit("卡片3：标题区域")
#         card3_top_title.setMinimumHeight(45)
#         card3_top_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         card3_layout.addWidget(card3_top_title)
#         card3_layout.addSpacing(15)

#         # 3.2. 中央大文本区域
#         large_content_area = QTextEdit("卡片3：这是主要内容区域，可以放置大量信息，如文章、聊天记录等。它会占据卡片内的主要空间。")
#         large_content_area.setMinimumHeight(250) # 确保初始高度
#         large_content_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
#         card3_layout.addWidget(large_content_area)
#         card3_layout.addSpacing(15)

#         # 3.3. 底部输入框和按钮
#         bottom_h_layout_in_card3 = QHBoxLayout()
#         bottom_large_input_in_card3 = QLineEdit("卡片3：底部输入框")
#         bottom_large_input_in_card3.setMinimumHeight(45)
        
#         bottom_small_button_in_card3 = QPushButton("操作")
#         bottom_small_button_in_card3.setFixedSize(100, 45)

#         bottom_h_layout_in_card3.addWidget(bottom_large_input_in_card3, stretch=1)
#         bottom_h_layout_in_card3.addSpacing(10)
#         bottom_h_layout_in_card3.addWidget(bottom_small_button_in_card3)

#         card3_layout.addLayout(bottom_h_layout_in_card3)

#         self.main_v_layout.addWidget(card3)

#         # --- 4. 第四个 CardWidget (底部单行区域) ---
#         card4 = CardWidget(self)
#         card4_layout = QVBoxLayout(card4)
#         card4_layout.setContentsMargins(20, 20, 20, 20)

#         bottom_single_line = QLineEdit("卡片4：底部版权或额外信息区域")
#         bottom_single_line.setMinimumHeight(45)
#         bottom_single_line.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         card4_layout.addWidget(bottom_single_line)

#         self.main_v_layout.addWidget(card4)

#         # 设置主窗口的布局
#         self.setLayout(self.main_v_layout)

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = FourCardLayoutApp()
#     window.show()
#     sys.exit(app.exec())


import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QSpacerItem, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt
from qfluentwidgets import CardWidget # 导入 CardWidget

class FourCardLayoutApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("四卡片布局示例")
        self.setGeometry(100, 100, 650, 900) # x, y, width, height

        # 1. 创建主窗口的垂直布局，用于容纳所有 CardWidget
        self.main_v_layout = QVBoxLayout(self)
        self.main_v_layout.setContentsMargins(15, 15, 15, 15) # 给所有卡片留点边距
        self.main_v_layout.setSpacing(15) # 卡片之间的垂直间距

        self._setup_card_widgets()

    def _setup_card_widgets(self):
        # --- 1. 第一个 CardWidget (顶部单行区域) ---
        card1 = CardWidget(self) # 将主窗口设为父对象
        card1_layout = QVBoxLayout(card1) # 在 CardWidget 内部创建布局
        card1_layout.setContentsMargins(20, 20, 20, 20) # 内部边距
        
        top_line_edit = QLineEdit("卡片1：顶部信息区域")
        top_line_edit.setMinimumHeight(45)
        top_line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card1_layout.addWidget(top_line_edit)
        
        self.main_v_layout.addWidget(card1)

        # --- 2. 第二个 CardWidget (三个或四个并排矩形) ---
        card2 = CardWidget(self)
        card2_layout = QVBoxLayout(card2)
        card2_layout.setContentsMargins(20, 20, 20, 20)

        middle_h_layout = QHBoxLayout()
        # 根据图片，看起来有四个并排的矩形
        btn1 = QPushButton("选项 A")
        btn2 = QPushButton("选项 B")
        btn3 = QPushButton("选项 C")
        btn4 = QPushButton("选项 D") # 新增一个按钮

        btn1.setFixedSize(120, 45)
        btn2.setFixedSize(120, 45)
        btn3.setFixedSize(120, 45)
        btn4.setFixedSize(120, 45)

        middle_h_layout.addStretch(1) # 左侧伸缩器，帮助居中
        middle_h_layout.addWidget(btn1)
        middle_h_layout.addSpacing(10)
        middle_h_layout.addWidget(btn2)
        middle_h_layout.addSpacing(10)
        middle_h_layout.addWidget(btn3)
        middle_h_layout.addSpacing(10)
        middle_h_layout.addWidget(btn4) # 添加第四个按钮
        middle_h_layout.addStretch(1) # 右侧伸缩器

        card2_layout.addLayout(middle_h_layout)
        
        self.main_v_layout.addWidget(card2)

        # --- 3. 第三个 CardWidget (中央复杂区域：大文本区 + 底部输入/按钮) ---
        card3 = CardWidget(self)
        card3_layout = QVBoxLayout(card3)
        card3_layout.setContentsMargins(20, 20, 20, 20)

        # 3.1. 卡片内部顶部标题 (图片上部有一个小矩形)
        card3_top_title = QLineEdit("卡片3：标题区域")
        card3_top_title.setMinimumHeight(45)
        card3_top_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card3_layout.addWidget(card3_top_title)
        card3_layout.addSpacing(15)

        # 3.2. 中央大文本区域
        large_content_area = QTextEdit("卡片3：这是主要内容区域，可以放置大量信息，如文章、聊天记录等。它会占据卡片内的主要空间。")
        large_content_area.setMinimumHeight(250) # 确保初始高度
        large_content_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        card3_layout.addWidget(large_content_area)
        card3_layout.addSpacing(15)

        # 3.3. 底部输入框和按钮
        bottom_h_layout_in_card3 = QHBoxLayout()
        bottom_large_input_in_card3 = QLineEdit("卡片3：底部输入框")
        bottom_large_input_in_card3.setMinimumHeight(45)
        
        bottom_small_button_in_card3 = QPushButton("操作")
        bottom_small_button_in_card3.setFixedSize(100, 45)

        bottom_h_layout_in_card3.addWidget(bottom_large_input_in_card3, stretch=1)
        bottom_h_layout_in_card3.addSpacing(10)
        bottom_h_layout_in_card3.addWidget(bottom_small_button_in_card3)

        card3_layout.addLayout(bottom_h_layout_in_card3)

        self.main_v_layout.addWidget(card3)

        # --- 4. 第四个 CardWidget (底部单行区域) ---
        card4 = CardWidget(self)
        card4_layout = QVBoxLayout(card4)
        card4_layout.setContentsMargins(20, 20, 20, 20)

        bottom_single_line = QLineEdit("卡片4：底部版权或额外信息区域")
        bottom_single_line.setMinimumHeight(45)
        bottom_single_line.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card4_layout.addWidget(bottom_single_line)

        self.main_v_layout.addWidget(card4)

        # 设置主窗口的布局
        self.setLayout(self.main_v_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FourCardLayoutApp()
    window.show()
    sys.exit(app.exec())