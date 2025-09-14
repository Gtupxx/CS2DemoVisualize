import time
from PyQt5.QtCore import Qt, QTimer, QRect, QPointF
from PyQt5.QtGui import QPainter, QPen, QFont
from PyQt5.QtWidgets import QWidget

from .config import *

from .state import mouse_show_flag, key_show_flag, velocity_show_flag

KEY_LAYOUT_WIDTH = 410
KEY_LAYOUT_HEIGHT = 320

VELOCITY_LAYOUT_WIDTH = 600
VELOCITY_LAYOUT_HEIGHT = 200
MAX_VELOCITY = 350


class KeyOverlay:
    def __init__(self):
        self.current_keys = set()
        self.current_weapon = ""
        self.key_timers = {}

        # 初始化拖动矩形
        self.rect = QRect(
            300,
            200,
            int(KEY_LAYOUT_WIDTH * KEY_LAYOUT_SCALE),
            int(KEY_LAYOUT_HEIGHT * KEY_LAYOUT_SCALE),
        )
        self.dragging = False
        self.drag_offset = None

    def weapon_to_key(self, weapon_name: str) -> str:
        primary_weapons = WEAPON_NAME["primary"]
        secondary_weapons = WEAPON_NAME["secondary"]
        knives = WEAPON_NAME["knife"]
        utility = WEAPON_NAME["utility"]

        if weapon_name in primary_weapons:
            return "1"
        elif weapon_name in secondary_weapons:
            return "2"
        elif weapon_name in knives:
            return "3"
        elif weapon_name in utility:
            return UTILITY_WEAPON_MAP.get(weapon_name, "4")
        else:
            return "4"


    def updateKeys(self, pressed_keys: list, weapon: str):
        now = time.time()
        if weapon != self.current_weapon:
            key = self.weapon_to_key(weapon)
            if key in {"1", "2", "3", "4", "Z", "X", "C", "V"}:
                self.key_timers[key] = now + KEY_HOLD_DURATION
            self.current_weapon = weapon

        instant_keys = {BUTTON_MAP.get(k, k) for k in pressed_keys if k in BUTTON_MAP}
        sustained_keys = {k for k, expire in self.key_timers.items() if expire > now}
        self.current_keys = instant_keys | sustained_keys

    def paint(self, painter: QPainter):
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        for key, r in KEY_LAYOUT.items():
            # 平移原始按键布局到当前 rect 位置
            rect = QRect(
                r.x() + self.rect.x(),
                r.y() + self.rect.y(),
                r.width(),
                r.height(),
            )
            is_pressed = key in self.current_keys
            color = KEY_PRESSED_COLOR if is_pressed else KEY_RELEASED_COLOR
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect, 8, 8)
            painter.setPen(Qt.white if is_pressed else Qt.black)
            painter.drawText(rect, Qt.AlignCenter, key)


class MouseOverlay:
    def __init__(self):
        self.trail_duration = MOUSE_TRAIL_DURATION
        self.yaw_scale = MOUSE_YAW_SCALE
        self.pitch_scale = MOUSE_PITCH_SCALE
        self.size_scale = MOUSE_LAYOUT_SCALE

        self.width = SCREEN_WIDTH * self.size_scale
        self.height = SCREEN_HEIGHT * self.size_scale
        self.trail_duration = self.trail_duration
        self.yaw_scale = self.yaw_scale
        self.pitch_scale = self.pitch_scale

        # 定义绘制区域，放在屏幕正中
        self.rect = QRect(
            int((SCREEN_WIDTH - self.width) / 2),
            int((SCREEN_HEIGHT - self.height) / 2),
            int(self.width),
            int(self.height),
        )

        self.offset_x = 0
        self.offset_y = 0
        self.mouse_trail = []

    def update_trail(self, yaw, pitch, pressed_keys):
        x = (1 - (yaw % 360) / 360) * self.width * self.yaw_scale
        y = (pitch + 90) / 180 * self.height * self.pitch_scale
        mouse_buttons = set()
        if "IN_ATTACK" in pressed_keys:
            mouse_buttons.add("M1")
        if "IN_ATTACK2" in pressed_keys:
            mouse_buttons.add("M2")
        timestamp = time.time()
        self.mouse_trail.append((x, y, mouse_buttons, timestamp))
        self.mouse_trail = [
            p for p in self.mouse_trail if timestamp - p[3] <= self.trail_duration
        ]

    def adjust_offset_if_wrap(self, x1, x2, y1, y2):
        flag = False
        limit = 0.9
        if abs(x1 - x2) > self.width * limit:
            if x1 < x2:
                self.offset_x += self.width / 2
            else:
                self.offset_x -= self.width / 2
            flag = True
        if abs(y1 - y2) > self.height * limit:
            if y1 < y2:
                self.offset_y += self.height / 2
            else:
                self.offset_y -= self.height / 2
            flag = True
        return flag

    def paint(self, painter: QPainter):
        now = time.time()
        coords = [
            (x, y, keys)
            for x, y, keys, t in self.mouse_trail
            if now - t <= self.trail_duration
        ]

        for i in range(1, len(coords)):
            x1, y1, keys1 = coords[i - 1]
            x2, y2, keys2 = coords[i]

            # 映射到居中矩形坐标
            x1 = self.rect.x() + (x1 + self.offset_x) % self.rect.width()
            y1 = self.rect.y() + (y1 + self.offset_y) % self.rect.height()
            x2 = self.rect.x() + (x2 + self.offset_x) % self.rect.width()
            y2 = self.rect.y() + (y2 + self.offset_y) % self.rect.height()

            if self.adjust_offset_if_wrap(x1, x2, y1, y2):
                self.mouse_trail.clear()
                coords = []
                break

            color = MOUSE_PRESSED_COLOR if "M1" in keys2 else MOUSE_RELEASED_COLOR
            pen = QPen(color)
            pen.setWidth(4)
            painter.setPen(pen)
            painter.drawLine(QPointF(float(x1), float(y1)), QPointF(float(x2), float(y2)))

        if coords:
            x, y, keys = coords[-1]
            x = self.rect.x() + (x + self.offset_x) % self.rect.width()
            y = self.rect.y() + (y + self.offset_y) % self.rect.height()
            brush_color = MOUSE_PRESSED_COLOR if "M1" in keys else MOUSE_RELEASED_COLOR
            painter.setBrush(brush_color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(float(x), float(y)), 6, 6)



class VelocityOverlay:
    def __init__(self):
        self.width = int(600 * VELOCITY_LAYOUT_SCALE)
        self.height = int(200 * VELOCITY_LAYOUT_SCALE)
        self.rect = QRect(
            50, SCREEN_HEIGHT - self.height - 100, self.width, self.height
        )

        self.trail_duration = VELOCITY_TRAIL_DURATION
        self.max_velocity = MAX_VELOCITY
        self.velocity_data = []
        self.weapon = ""

        # 初始化拖动矩形
        self.rect = QRect(
            50, SCREEN_HEIGHT - self.height - 100, self.width, self.height
        )
        self.dragging = False
        self.drag_offset = None

    def update_velocity(self, v, pressed_keys=set(), weapon_name=""):
        timestamp = time.time()
        self.weapon = weapon_name
        self.velocity_data.append((v, timestamp, pressed_keys))
        self.velocity_data = [
            (s, t, keys)
            for s, t, keys in self.velocity_data
            if timestamp - t <= self.trail_duration
        ]

    def paint(self, painter: QPainter):
        # 设置裁剪区域，确保绘制不超出矩形
        painter.save()
        painter.setClipRect(self.rect)

        # 背景
        painter.fillRect(self.rect, VELOCITY_BKG_COLOR)
        if not self.velocity_data:
            painter.restore()
            return

        now = time.time()
        coords = [
            (
                self.rect.x()
                + (t - (now - self.trail_duration))
                / self.trail_duration
                * self.rect.width(),
                self.rect.y()
                + self.rect.height()
                - (s / self.max_velocity) * self.rect.height(),
                keys,
            )
            for s, t, keys in self.velocity_data
        ]

        # 绘制折线
        for i in range(1, len(coords)):
            x1, y1, keys1 = coords[i - 1]
            x2, y2, keys2 = coords[i]
            pen = QPen(
                VELOCITY_ATTACK_COLOR if "IN_ATTACK" in keys2 else VELOCITY_NORMAL_COLOR
            )
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # 当前速度文字
        current_velocity = self.velocity_data[-1][0]
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.drawText(
            self.rect.x() + 10, self.rect.y() + 20, f"Velocity: {current_velocity:.1f}"
        )

        # 武器精度参考线
        if self.weapon in WEAPON_ACCURACY_VELOCITY:
            limit = WEAPON_ACCURACY_VELOCITY[self.weapon]
            y = (
                self.rect.y()
                + self.rect.height()
                - (limit / self.max_velocity) * self.rect.height()
            )

            pen = QPen()
            pen.setStyle(Qt.DashLine)
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawLine(
                QPointF(self.rect.x(), y), QPointF(self.rect.x() + self.rect.width(), y)
            )

            painter.setPen(Qt.yellow)
            painter.setFont(QFont("Arial", 10, QFont.Bold))
            painter.drawText(
                self.rect.x() + 10, int(y) - 5, f"{self.weapon} accuracy: {limit}"
            )

        # 恢复 painter 状态，取消裁剪
        painter.restore()


class OverlayManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(
            Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )

        self.setGeometry(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.setWindowTitle("CS2 Overlay Manager")

        self.key_overlay = KeyOverlay()
        self.mouse_overlay = MouseOverlay()
        self.velocity_overlay = VelocityOverlay()

        self.dragging_overlay = None
        self.drag_offset = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

    def mousePressEvent(self, event):
        pos = event.pos()
        # 判断点击位置是否落在 Key 或 Velocity overlay 的矩形内
        if self.key_overlay.rect.contains(pos):
            self.dragging_overlay = self.key_overlay
            self.drag_offset = pos - self.key_overlay.rect.topLeft()
        elif self.velocity_overlay.rect.contains(pos):
            self.dragging_overlay = self.velocity_overlay
            self.drag_offset = pos - self.velocity_overlay.rect.topLeft()

    def mouseMoveEvent(self, event):
        if self.dragging_overlay:
            new_pos = event.pos() - self.drag_offset
            self.dragging_overlay.rect.moveTopLeft(new_pos)

    def mouseReleaseEvent(self, event):
        self.dragging_overlay = None
        self.drag_offset = None

    def paintEvent(self, event):
        painter = QPainter(self)
        # 绘制顺序：速度 → 键盘 → 鼠标（鼠标在最上层）
        if velocity_show_flag.is_set():
            self.velocity_overlay.paint(painter)
        if key_show_flag.is_set():
            self.key_overlay.paint(painter)
        if mouse_show_flag.is_set():
            self.mouse_overlay.paint(painter)
