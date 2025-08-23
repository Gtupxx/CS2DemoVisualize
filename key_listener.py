import time
import keyboard

def listen_for_f9(pause_flag):
    """监听 F9 键，控制播放/暂停"""
    while True:
        if keyboard.is_pressed('F9'):
            if pause_flag.is_set():
                print("[键盘监听] 收到 F9，开始播放")
                pause_flag.clear()
            else:
                print("[键盘监听] 收到 F9，暂停播放")
                pause_flag.set()
            time.sleep(0.5)
