from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QColor, QPainter, QFont
from PyQt5.QtWidgets import QWidget
from state import current_keys
from config import KEY_LAYOUT


class KeyOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground, True)      # 背景透明
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False) # 接收鼠标事件
        self.setWindowFlags(
            Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )  # 无边框 + 置顶
        self.setGeometry(300, 200, 410, 320)
        self.setWindowTitle("CS2按键操作显示")

        self.dragging = False
        self.drag_pos = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.dragging = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        for key, rect in KEY_LAYOUT.items():
            is_pressed = key in current_keys
            color = QColor(0, 180, 0) if is_pressed else QColor(150, 150, 150)
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect, 8, 8)
            painter.setPen(Qt.white if is_pressed else Qt.black)
            painter.drawText(rect, Qt.AlignCenter, key)
