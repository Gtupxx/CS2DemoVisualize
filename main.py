import sys
import os
import threading
from PyQt5.QtWidgets import QApplication

import src.config

src.config.DEMO_PATH = r"C:\\Users\\11523\\Downloads\\vitality-vs-falcons-m2-train.dem"

from src.overlay import OverlayManager
from src.key_listener import listen_keyboard
from src.log_watcher import tail_console_log
from src.demo_player import play_demo
from src.config import PAUSE_KEY, SLOWMO_KEY, NORMALSPEED_KEY, FASTMO_KEY

# from src.state import pause_flag, skip_to_tick, skip_to_tick_lock


def update_cfg(cfg_path: str = "game_config.cfg") -> None:
    """
    更新 CS2 游戏配置文件
    自动绑定暂停、快进、慢放等功能键
    """
    lines = [
        f'alias "demopause" "demo_pause; bind {PAUSE_KEY} demoresume"',
        f'alias "demoresume" "demo_resume; bind {PAUSE_KEY} demopause"',
        f'bind "{PAUSE_KEY}" "demoresume"',
        "",
        'alias "slowmo" "host_timescale 0.5"',
        'alias "normalspeed" "host_timescale 1.0"',
        'alias "fastmo" "host_timescale 2.0"',
        f'bind "{SLOWMO_KEY}" "slowmo"',
        f'bind "{FASTMO_KEY}" "fastmo"',
        f'bind "{NORMALSPEED_KEY}" "normalspeed"',
    ]

    content = "\n".join(lines) + "\n"
    with open(cfg_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[OK] 配置文件已生成: {os.path.abspath(cfg_path)}")


if __name__ == "__main__":
    update_cfg()
    app = QApplication(sys.argv)

    overlay = OverlayManager()
    overlay.show()

    threading.Thread(target=listen_keyboard, args=(), daemon=True).start()
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
