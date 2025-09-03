import sys
import threading
from PyQt5.QtWidgets import QApplication

import src.config
src.config.DEMO_PATH = r"C:\\Users\\11523\\Downloads\\vitality-vs-falcons-m2-train.dem"

from src.overlay import OverlayManager
from src.key_listener import listen_for_f9
from src.log_watcher import tail_console_log
from src.demo_player import play_demo
# from src.state import pause_flag, skip_to_tick, skip_to_tick_lock


if __name__ == "__main__":
    app = QApplication(sys.argv)

    overlay = OverlayManager()
    overlay.show()

    threading.Thread(target=listen_for_f9, args=(), daemon=True).start()
    threading.Thread(
        target=tail_console_log,
        args=(),
        daemon=True,
    ).start()
    threading.Thread(
        target=play_demo,
        args=(overlay,),
        daemon=True,
    ).start()

    sys.exit(app.exec_())
