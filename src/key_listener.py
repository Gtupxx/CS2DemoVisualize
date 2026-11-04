import time

import keyboard

from .config import (
    PAUSE_KEY,
    MOUSE_TOGGLE_KEY,
    KEY_TOGGLE_KEY,
    VELOCITY_TOGGLE_KEY,
    SLOWMO_KEY,
    NORMALSPEED_KEY,
    FASTMO_KEY,
    MOUSE_CENTER_KEY,
)
from .state import (
    pause_flag,
    mouse_show_flag,
    key_show_flag,
    velocity_show_flag,
    tick_rate_scale,
    mouse_offset_flag,
)

POLL_INTERVAL = 0.01  # 空闲轮询间隔，避免忙等占满一个 CPU 核心
DEBOUNCE_INTERVAL = 0.2


def _toggle(flag, key: str, name: str) -> None:
    if flag.is_set():
        flag.clear()
        action = "隐藏"
    else:
        flag.set()
        action = "显示"
    print(f"[键盘监听] 收到 {key}，{action}{name}")
    time.sleep(DEBOUNCE_INTERVAL)


def _set_speed(scale: float) -> None:
    tick_rate_scale[0] = scale
    print(f"[键盘监听] 倍速切换为 {scale}x")
    time.sleep(DEBOUNCE_INTERVAL)


def listen_keyboard():
    """监听键盘，控制播放/暂停，显示/隐藏叠加层"""
    mouse_show_flag.set()
    key_show_flag.set()
    velocity_show_flag.set()

    while True:
        if keyboard.is_pressed(PAUSE_KEY):
            if pause_flag.is_set():
                print(f"[键盘监听] 收到 {PAUSE_KEY}，开始播放")
                pause_flag.clear()
            else:
                print(f"[键盘监听] 收到 {PAUSE_KEY}，暂停播放")
                pause_flag.set()
            time.sleep(DEBOUNCE_INTERVAL)
        elif keyboard.is_pressed(MOUSE_TOGGLE_KEY):
            _toggle(mouse_show_flag, MOUSE_TOGGLE_KEY, "鼠标叠加层")
        elif keyboard.is_pressed(KEY_TOGGLE_KEY):
            _toggle(key_show_flag, KEY_TOGGLE_KEY, "键盘叠加层")
        elif keyboard.is_pressed(VELOCITY_TOGGLE_KEY):
            _toggle(velocity_show_flag, VELOCITY_TOGGLE_KEY, "速度叠加层")
        elif keyboard.is_pressed(SLOWMO_KEY):
            _set_speed(0.5)
        elif keyboard.is_pressed(NORMALSPEED_KEY):
            _set_speed(1.0)
        elif keyboard.is_pressed(FASTMO_KEY):
            _set_speed(2.0)
        elif keyboard.is_pressed(MOUSE_CENTER_KEY):
            mouse_offset_flag.set()
            print(f"[键盘监听] 收到 {MOUSE_CENTER_KEY}，触发鼠标叠加层回中")
            time.sleep(DEBOUNCE_INTERVAL)
        else:
            time.sleep(POLL_INTERVAL)
