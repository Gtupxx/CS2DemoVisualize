import sys
import threading
from PyQt5.QtWidgets import QApplication
from overlay import KeyOverlay
from key_listener import listen_for_f9
from log_watcher import tail_console_log
from demo_player import play_demo
from cs2_launcher import launch_cs2_with_demo
from state import pause_flag, skip_to_tick, skip_to_tick_lock

if __name__ == "__main__":
    # 启动 CS2 并播放 demo
    # launch_cs2_with_demo()

    threading.Thread(target=listen_for_f9, args=(pause_flag,), daemon=True).start()
    threading.Thread(target=tail_console_log, args=(pause_flag, skip_to_tick, skip_to_tick_lock), daemon=True).start()
    threading.Thread(target=play_demo, args=(pause_flag, skip_to_tick, skip_to_tick_lock), daemon=True).start()

    app = QApplication(sys.argv)
    overlay = KeyOverlay()
    overlay.show()
    sys.exit(app.exec_())
