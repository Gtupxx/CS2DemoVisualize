import sys
import os
import threading
from PyQt5.QtWidgets import QApplication

import src.config

from src.overlay import OverlayManager
from src.key_listener import listen_keyboard
from src.log_watcher import tail_console_log
from src.demo_player import play_demo
from src.config import PAUSE_KEY, SLOWMO_KEY, NORMALSPEED_KEY, FASTMO_KEY

# 优先级：命令行参数 > 环境变量 DEMO_PATH > src/config.py 里的 DEMO_PATH > 下面这个默认值
DEFAULT_DEMO_PATH = r"C:\Users\11523\AppData\Roaming\5E对战平台\demo\g161-20261104202603324790385_de_mirage.dem"


def resolve_demo_path(argv) -> str:
    """取出 DEMO 路径并规范化（避免 Windows 路径里的重复分隔符）"""
    candidates = [
        argv[1] if len(argv) > 1 else "",
        os.environ.get("DEMO_PATH", ""),
        src.config.DEMO_PATH,
        DEFAULT_DEMO_PATH,
    ]
    for candidate in candidates:
        if candidate and candidate.strip():
            return os.path.normpath(candidate.strip().strip('"'))
    return ""


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

    demo_path = resolve_demo_path(sys.argv)
    if demo_path:
        src.config.DEMO_PATH = demo_path
        if not os.path.exists(demo_path):
            print(f"[警告] DEMO 文件不存在: {demo_path}")
    else:
        print("[警告] 未指定 DEMO 路径，可用 `python main.py <demo路径>` 启动")

    app = QApplication(sys.argv[:1])

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
