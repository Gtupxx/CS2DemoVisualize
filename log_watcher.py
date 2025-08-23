import time
import re
from config import CONSOLE_LOG_PATH

def tail_console_log(pause_flag, skip_to_tick, skip_to_tick_lock):
    """监听 console.log 跳转 tick"""
    skip_pattern = re.compile(r"\[Demo\] Demo Skipping: skipping to demo tick (\d+)")

    with open(CONSOLE_LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue

            m_skip = skip_pattern.search(line)
            if m_skip:
                skip_tick = int(m_skip.group(1))
                print(f"[日志检测] 跳转到tick: {skip_tick}")
                with skip_to_tick_lock:
                    skip_to_tick[0] = skip_tick
                pause_flag.set()
