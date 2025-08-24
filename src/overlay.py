import time
import math
from PyQt5.QtCore import Qt, QTimer, QRect, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from PyQt5.QtWidgets import QWidget, QApplication

# from .state import current_keys, current_mouse_inputs
from .config import (
    KEY_LAYOUT,
    KEY_LAYOUT_HEIGHT,
    KEY_LAYOUT_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    MOUSE_TRAIL_DURATION,
    VELOCITY_TRAIL_DURATION,
    WEAPON_ACCURACY_VELOCITY,
    BUTTON_MAP,
    WEAPON_NAME,
)


class KeyOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground, True)  # 背景透明
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)  # 接收鼠标事件
        self.setWindowFlags(
            Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )  # 无边框 + 置顶
        self.setGeometry(300, 200, KEY_LAYOUT_WIDTH, KEY_LAYOUT_HEIGHT)
        self.setWindowTitle("CS2按键操作显示")

        self.dragging = False
        self.drag_pos = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

        self.current_keys = set()
        self.current_weapon = ""
        self.key_timers = {}  # 记录按键按下的时间点
        self.key_hold_duration = 0.2  # 按键显示持续时间（秒）

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
            return {
                "Flashbang": "C",
                "Smoke Grenade": "X",
                "Molotov": "Z",
                "Incendiary Grenade": "Z",
                "High Explosive Grenade": "V",
                "Decoy Grenade": "V",
            }.get(weapon_name, "4")
        else:
            return "4"

    def updateKeys(self, pressed_keys: list, weapon: str):
        now = time.time()

        # 武器切换才触发按键持续
        if weapon != self.current_weapon:
            key = self.weapon_to_key(weapon)
            if key in {"1", "2", "3", "4", "Z", "X", "C", "V"}:
                self.key_timers[key] = now + self.key_hold_duration
            self.current_weapon = weapon

        # 普通按键还是瞬时的
        instant_keys = {BUTTON_MAP.get(k, k) for k in pressed_keys if k in BUTTON_MAP}

        # 只保留还没过期的武器按键
        sustained_keys = {k for k, expire in self.key_timers.items() if expire > now}

        # 合并两类按键
        self.current_keys = instant_keys | sustained_keys

        self.update()  # 刷新界面

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        for key, rect in KEY_LAYOUT.items():
            is_pressed = key in self.current_keys
            color = QColor(0, 180, 0) if is_pressed else QColor(150, 150, 150)
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect, 8, 8)
            painter.setPen(Qt.white if is_pressed else Qt.black)
            painter.drawText(rect, Qt.AlignCenter, key)


class MouseOverlay(QWidget):
    def __init__(
        self,
        trail_duration=MOUSE_TRAIL_DURATION,
        yaw_scale=1,
        pitch_scale=1,
        size_scale=1,
    ):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self.setWindowFlags(
            Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )

        # 全屏

        self.width = SCREEN_WIDTH * size_scale
        self.height = SCREEN_HEIGHT * size_scale
        self.setGeometry(
            int((SCREEN_WIDTH - self.width) / 2),
            int((SCREEN_HEIGHT - self.height) / 2),
            int(self.width),
            int(self.height),
        )
        self.setWindowTitle("CS2鼠标轨迹显示")

        self.offset_x = 0
        self.offset_y = 0

        # 拖拽
        self.dragging = False
        self.drag_pos = None

        # 定时刷新
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

        # 轨迹和参数
        self.mouse_trail = []
        self.trail_duration = trail_duration
        self.yaw_scale = yaw_scale
        self.pitch_scale = pitch_scale

    def update_trail(self, yaw, pitch, pressed_keys):
        x = (1 - (yaw % 360) / 360) * self.width * self.yaw_scale
        y = (pitch + 90) / 180 * self.height * self.pitch_scale
        # print(f"Mouse pos: ({x}, {y}), yaw: {yaw}, pitch: {pitch}")
        mouse_buttons = set()
        if "IN_ATTACK" in pressed_keys:
            mouse_buttons.add("M1")
        if "IN_ATTACK2" in pressed_keys:
            mouse_buttons.add("M2")

        timestamp = time.time()
        self.mouse_trail.append((x, y, mouse_buttons, timestamp))

        # 清理过期轨迹
        self.mouse_trail = [
            p for p in self.mouse_trail if timestamp - p[3] <= self.trail_duration
        ]

    def adjust_offset_if_wrap(self, x1, x2, y1, y2):
        # 判断是否发生左右越界
        flag = False
        limit = 0.9
        if abs(x1 - x2) > self.width * limit:  # 如果两个点相差接近整个屏幕宽度
            # print("wrap detected:", x1, x2)
            if x1 < x2:
                self.offset_x += self.width / 2  # 从左边跳到右边
            else:
                self.offset_x -= self.width / 2  # 从右边跳到左边
            # print("new offset:", self.offset_x, self.offset_y)
            flag = True

        # 判断是否发生上下越界（同理）
        if abs(y1 - y2) > self.height * limit:
            if y1 < y2:
                self.offset_y += self.height / 2
            else:
                self.offset_y -= self.height / 2
            flag = True
        return flag

    def paintEvent(self, event):
        # print("offset:", self.offset_x, self.offset_y)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # painter.fillRect(self.rect(), QColor(30, 30, 30, 120))  # 半透明背景

        now = time.time()
        coords = [
            (x, y, keys)
            for x, y, keys, t in self.mouse_trail
            if now - t <= self.trail_duration
        ]

        for i in range(1, len(coords)):
            x1, y1, keys1 = coords[i - 1]
            x2, y2, keys2 = coords[i]

            # 应用偏移量
            x1 += self.offset_x
            x1 %= self.width
            y1 += self.offset_y
            y1 %= self.height
            x2 += self.offset_x
            x2 %= self.width
            y2 += self.offset_y
            y2 %= self.height

            # 调整偏移量
            if self.adjust_offset_if_wrap(x1, x2, y1, y2):
                self.mouse_trail.clear()
                coords = []
                break

            # 颜色逻辑：M1 按下时绿色，否则红色
            color = QColor(0, 255, 0) if "M1" in keys2 else QColor(255, 0, 0)
            pen = QPen(color)
            pen.setWidth(4)
            painter.setPen(pen)
            painter.drawLine(
                QPointF(float(x1), float(y1)), QPointF(float(x2), float(y2))
            )

        # 绘制当前鼠标点
        if coords:
            x, y, keys = coords[-1]
            x += self.offset_x
            x %= self.width
            y += self.offset_y
            y %= self.height

            brush_color = QColor(0, 180, 0) if "M1" in keys else QColor(255, 0, 0)
            painter.setBrush(brush_color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(float(x), float(y)), 6, 6)

            # painter.setPen(Qt.white)
            # painter.setFont(QFont("Arial", 10, QFont.Bold))
            # painter.drawText(int(x) + 10, int(y) - 10, ", ".join(keys))


class VelocityOverlay(QWidget):
    def __init__(self, trail_duration=VELOCITY_TRAIL_DURATION, max_velocity=350):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)  # 允许接收鼠标事件

        self.setWindowFlags(
            Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )

        # 小窗口，放在左下角
        self.width = 600
        self.height = 200
        self.setGeometry(
            50,
            SCREEN_HEIGHT - self.height - 100,
            self.width,
            self.height,
        )
        self.setWindowTitle("CS2速度叠加层")

        # 拖拽标记
        self.dragging = False
        self.drag_pos = None

        # 定时刷新
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

        # 数据 (velocity, timestamp, pressed_keys)
        self.velocity_data = []
        self.trail_duration = trail_duration
        self.max_velocity = max_velocity

        self.weapon = ""

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()

    def update_velocity(self, v, pressed_keys=set(), weapon_name=""):
        timestamp = time.time()
        self.weapon = weapon_name
        self.velocity_data.append((v, timestamp, pressed_keys))

        # 清理过期数据
        self.velocity_data = [
            (s, t, keys)
            for s, t, keys in self.velocity_data
            if timestamp - t <= self.trail_duration
        ]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 背景半透明
        painter.fillRect(self.rect(), QColor(20, 20, 20, 180))

        if not self.velocity_data:
            return

        now = time.time()
        coords = [
            (
                (t - (now - self.trail_duration))
                / self.trail_duration
                * self.width,  # X轴映射时间
                self.height - (s / self.max_velocity) * self.height,  # Y轴映射速度
                keys,
            )
            for s, t, keys in self.velocity_data
        ]

        # 画折线
        for i in range(1, len(coords)):
            x1, y1, keys1 = coords[i - 1]
            x2, y2, keys2 = coords[i]

            # 如果开枪，用红色，否则蓝色
            if "IN_ATTACK" in keys2:
                pen = QPen(QColor(255, 0, 0))
            else:
                pen = QPen(QColor(0, 200, 255))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # 显示当前速度数值
        current_velocity = self.velocity_data[-1][0]
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.drawText(10, 20, f"Velocity: {current_velocity:.1f}")

        # 如果当前武器在表里，画横线
        if hasattr(self, "weapon") and self.weapon in WEAPON_ACCURACY_VELOCITY:
            limit = WEAPON_ACCURACY_VELOCITY[self.weapon]
            y = self.height - (limit / self.max_velocity) * self.height

            pen = QPen(QColor(255, 255, 0, 180))  # 黄色参考线
            pen.setStyle(Qt.DashLine)  # 虚线效果
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawLine(QPointF(0, y), QPointF(self.width, y))  # ✅ 用 QPointF

            # 在横线左边标注
            painter.setPen(Qt.yellow)
            painter.setFont(QFont("Arial", 10, QFont.Bold))
            painter.drawText(10, int(y) - 5, f"{self.weapon} accuracy: {limit}")
