import sys
import threading
from PyQt5.QtWidgets import QApplication
from overlay import KeyOverlay, MouseOverlay
from key_listener import listen_for_f9
from log_watcher import tail_console_log
from demo_player import play_demo
from cs2_launcher import launch_cs2_with_demo
from state import pause_flag, skip_to_tick, skip_to_tick_lock

if __name__ == "__main__":
    # 创建 PyQt 应用
    app = QApplication(sys.argv)

    # 创建覆盖层
    keyOverlay = KeyOverlay()
    keyOverlay.show()
    mouseOverlay = MouseOverlay()
    mouseOverlay.show()

    # 启动后台线程
    threading.Thread(target=listen_for_f9, args=(pause_flag,), daemon=True).start()
    threading.Thread(target=tail_console_log, args=(pause_flag, skip_to_tick, skip_to_tick_lock), daemon=True).start()
    # 把 mouseOverlay 传进去
    threading.Thread(target=play_demo, args=(pause_flag, skip_to_tick, skip_to_tick_lock, mouseOverlay), daemon=True).start()

    # 启动 PyQt 主循环
    sys.exit(app.exec_())

