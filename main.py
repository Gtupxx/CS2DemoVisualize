import sys
import threading
from PyQt5.QtWidgets import QApplication

import src.config

src.config.DEMO_PATH = (
    # r"C:\\Users\\11523\\Downloads\\spirit-vs-the-mongolz-m3-ancient.dem"
    # r"C:\\Users\\11523\\AppData\\Roaming\\Wmpvp\\demo\\9221294950495046284_0.dem"
    r"C:\\Users\\11523\\AppData\\Roaming\\Wmpvp\\demo\\9209121187937844748_0.dem"
)

from src.overlay import KeyOverlay, MouseOverlay, VelocityOverlay
from src.key_listener import listen_for_f9
from src.log_watcher import tail_console_log
from src.demo_player import play_demo
from src.cs2_launcher import launch_cs2_with_demo
from src.state import pause_flag, skip_to_tick, skip_to_tick_lock


if __name__ == "__main__":
    # 创建 PyQt 应用
    app = QApplication(sys.argv)

    # 创建覆盖层
    keyOverlay = KeyOverlay()
    keyOverlay.show()
    mouseOverlay = MouseOverlay(size_scale=0.5, yaw_scale=2.0, pitch_scale=2.0)
    mouseOverlay.show()

    velocityOverlay = VelocityOverlay()
    velocityOverlay.show()

    # 启动后台线程
    threading.Thread(target=listen_for_f9, args=(pause_flag,), daemon=True).start()
    threading.Thread(
        target=tail_console_log,
        args=(pause_flag, skip_to_tick, skip_to_tick_lock),
        daemon=True,
    ).start()
    # 把 overlay 传进去
    threading.Thread(
        target=play_demo,
        args=(
            pause_flag,
            skip_to_tick,
            skip_to_tick_lock,
            keyOverlay,
            mouseOverlay,
            velocityOverlay,
        ),
        daemon=True,
    ).start()

    # 启动 PyQt 主循环
    sys.exit(app.exec_())
