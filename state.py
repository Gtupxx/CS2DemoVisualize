import time
from config import (
    MOUSE_TRAIL_DURATION,
)

# 保存全局状态

# 当前按下的键
current_keys = set()

# 播放/暂停状态
import threading
pause_flag = threading.Event()

# 跳转tick（用list存是为了能被引用修改）
skip_to_tick = [None]
skip_to_tick_lock = threading.Lock()

# 模拟鼠标按钮状态集合（例如播放时根据 extract_buttons 映射更新）
current_mouse = set()  # "M1", "M2" 等
mouse_trail = []       # [(x, y, buttons_set), ...] 实时轨迹点
current_mouse_inputs = []  # 存储 (yaw, pitch, pressed_keys, timestamp)

def update_mouse_inputs(yaw, pitch, pressed_keys):
    global current_mouse_inputs
    timestamp = time.time()
    current_mouse_inputs.append((yaw, pitch, pressed_keys, timestamp))
    # 清理过期记录
    current_mouse_inputs = [
        p for p in current_mouse_inputs if timestamp - p[3] <= MOUSE_TRAIL_DURATION
    ]