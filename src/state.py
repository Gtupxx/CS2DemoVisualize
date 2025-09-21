import threading

pause_flag = threading.Event()
mouse_show_flag = threading.Event()
key_show_flag = threading.Event()
velocity_show_flag = threading.Event()

mouse_offset_flag = threading.Event()

# 跳转tick（用list存是为了能被引用修改）
skip_to_tick = [None]
skip_to_tick_lock = threading.Lock()

# 当前播放速度（tick率缩放）
tick_rate_scale = [1.0]