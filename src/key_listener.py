import time
import keyboard
from .state import pause_flag, mouse_show_flag, key_show_flag, velocity_show_flag, tick_rate_scale
from .config import PAUSE_KEY, MOUSE_TOGGLE_KEY, KEY_TOGGLE_KEY, VELOCITY_TOGGLE_KEY, SLOWMO_KEY, NORMALSPEED_KEY, FASTMO_KEY


def listen_keyboard():
    """监听键盘，控制播放/暂停，显示/隐藏叠加层"""
    mouse_show_flag.set()
    key_show_flag.set()
    velocity_show_flag.set()

    while True:
        if keyboard.is_pressed('esc'):
            print("[键盘监听] 收到 esc，退出程序")
            # exit(0)

        if keyboard.is_pressed(PAUSE_KEY):
            if pause_flag.is_set():
                print(f"[键盘监听] 收到 {PAUSE_KEY}，开始播放")
                pause_flag.clear()
            else:
                print(f"[键盘监听] 收到 {PAUSE_KEY}，暂停播放")
                pause_flag.set()
            time.sleep(0.2)
        if keyboard.is_pressed(MOUSE_TOGGLE_KEY):
            if mouse_show_flag.is_set():
                mouse_show_flag.clear()
                print(f"[键盘监听] 收到 {MOUSE_TOGGLE_KEY}，显示鼠标叠加层")
            else:
                mouse_show_flag.set()
                print(f"[键盘监听] 收到 {MOUSE_TOGGLE_KEY}，隐藏鼠标叠加层")
            time.sleep(0.2)
        if keyboard.is_pressed(KEY_TOGGLE_KEY):
            if key_show_flag.is_set():
                key_show_flag.clear()
                print(f"[键盘监听] 收到 {KEY_TOGGLE_KEY}，显示键盘叠加层")
            else:
                key_show_flag.set()
                print(f"[键盘监听] 收到 {KEY_TOGGLE_KEY}，隐藏键盘叠加层")
            time.sleep(0.2)

        if keyboard.is_pressed(VELOCITY_TOGGLE_KEY):
            if velocity_show_flag.is_set():
                velocity_show_flag.clear()
                print(f"[键盘监听] 收到 {VELOCITY_TOGGLE_KEY}，显示速度叠加层")
            else:
                velocity_show_flag.set()
                print(f"[键盘监听] 收到 {VELOCITY_TOGGLE_KEY}，隐藏速度叠加层")
            time.sleep(0.2)
        
        if keyboard.is_pressed(SLOWMO_KEY):
            tick_rate_scale[0] = 0.5
            print(f"[键盘监听] 收到 {SLOWMO_KEY} ，当前倍速: {tick_rate_scale[0]}x")
            time.sleep(0.2)

        if keyboard.is_pressed(NORMALSPEED_KEY):
            tick_rate_scale[0] = 1.0
            print(f"[键盘监听] 收到 {NORMALSPEED_KEY} ，当前倍速: {tick_rate_scale[0]}x")
            time.sleep(0.2)
            
        if keyboard.is_pressed(FASTMO_KEY):
            tick_rate_scale[0] = 2.0
            print(f"[键盘监听] 收到 {FASTMO_KEY} ，当前倍速: {tick_rate_scale[0]}x")
            time.sleep(0.2)
