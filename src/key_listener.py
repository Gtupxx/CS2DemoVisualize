import time
import keyboard
from .state import pause_flag, mouse_show_flag, key_show_flag, velocity_show_flag
from .config import PAUSE_KEY, MOUSE_TOGGLE_KEY, KEY_TOGGLE_KEY, VELOCITY_TOGGLE_KEY


def listen_for_f9():
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
            time.sleep(0.5)
        if keyboard.is_pressed(MOUSE_TOGGLE_KEY):
            if mouse_show_flag.is_set():
                mouse_show_flag.clear()
                print(f"[键盘监听] 收到 {MOUSE_TOGGLE_KEY}，显示鼠标叠加层")
            else:
                mouse_show_flag.set()
                print(f"[键盘监听] 收到 {MOUSE_TOGGLE_KEY}，隐藏鼠标叠加层")
            time.sleep(0.5)
        if keyboard.is_pressed(KEY_TOGGLE_KEY):
            if key_show_flag.is_set():
                key_show_flag.clear()
                print(f"[键盘监听] 收到 {KEY_TOGGLE_KEY}，显示键盘叠加层")
            else:
                key_show_flag.set()
                print(f"[键盘监听] 收到 {KEY_TOGGLE_KEY}，隐藏键盘叠加层")
            time.sleep(0.5)

        if keyboard.is_pressed(VELOCITY_TOGGLE_KEY):
            if velocity_show_flag.is_set():
                velocity_show_flag.clear()
                print(f"[键盘监听] 收到 {VELOCITY_TOGGLE_KEY}，显示速度叠加层")
            else:
                velocity_show_flag.set()
                print(f"[键盘监听] 收到 {VELOCITY_TOGGLE_KEY}，隐藏速度叠加层")
            time.sleep(0.5)
