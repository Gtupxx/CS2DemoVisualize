# 保存全局状态

# 当前按下的键
current_keys = set()

# 播放/暂停状态
import threading
pause_flag = threading.Event()

# 跳转tick（用list存是为了能被引用修改）
skip_to_tick = [None]
skip_to_tick_lock = threading.Lock()
