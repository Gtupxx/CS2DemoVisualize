import os
import re
import time

from .config import CONSOLE_LOG_PATH
from .state import pause_flag, skip_to_tick, skip_to_tick_lock

# 游戏内会打印 "skipping to demo tick N" 或 "skipping forward to demo tick N"
SKIP_PATTERN = re.compile(
    r"\[Demo\] Demo Skipping: skipping (?:forward )?to demo tick (\d+)"
)


def tail_console_log():
    """监听 console.log 跳转 tick"""
    with open(CONSOLE_LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                # CS2 重启后 console.log 会被截断/重建，读指针要拉回开头
                try:
                    if os.path.getsize(CONSOLE_LOG_PATH) < f.tell():
                        f.seek(0)
                except OSError:
                    pass
                continue

            m_skip = SKIP_PATTERN.search(line)
            if not m_skip:
                continue

            skip_tick = int(m_skip.group(1))
            print(f"[日志检测] 跳转到tick: {skip_tick}")
            with skip_to_tick_lock:
                skip_to_tick[0] = skip_tick
            pause_flag.set()
