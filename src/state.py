import threading
pause_flag = threading.Event()

# 跳转tick（用list存是为了能被引用修改）
skip_to_tick = [None]
skip_to_tick_lock = threading.Lock()