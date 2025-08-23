import subprocess
import os
from .config import DEMO_PATH

# Steam 路径（自己改成你的）
STEAM_PATH = r"C:\\Program Files (x86)\\Steam\\steam.exe"
CSGO_APP_ID = "730"

# 你的启动参数（可以自己加/删）
LAUNCH_OPTIONS = "-worldwide +exec hy2"


def launch_cs2_with_demo():
    if not os.path.exists(STEAM_PATH):
        print(f"[错误] 找不到 steam.exe: {STEAM_PATH}")
        return
    if not os.path.exists(DEMO_PATH):
        print(f"[错误] 找不到 demo 文件: {DEMO_PATH}")
        return

    demo_path = os.path.abspath(DEMO_PATH)
    command = f'"{STEAM_PATH}" -applaunch {CSGO_APP_ID} {LAUNCH_OPTIONS} +playdemo "{demo_path}"'

    print(f"[启动命令] {command}")
    subprocess.Popen(command, shell=True)
