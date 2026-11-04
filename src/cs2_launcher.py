import subprocess
import os

from . import config

# Steam 路径（自己改成你的）
STEAM_PATH = r"C:\\Program Files (x86)\\Steam\\steam.exe"
CSGO_APP_ID = "730"

# 你的启动参数（可以自己加/删）
LAUNCH_OPTIONS = "-worldwide +exec hy2"


def launch_cs2_with_demo():
    demo_path = config.DEMO_PATH
    if not os.path.exists(STEAM_PATH):
        print(f"[错误] 找不到 steam.exe: {STEAM_PATH}")
        return
    if not demo_path or not os.path.exists(demo_path):
        print(f"[错误] 找不到 demo 文件: {demo_path}")
        return

    demo_path = os.path.abspath(demo_path)
    command = f'"{STEAM_PATH}" -applaunch {CSGO_APP_ID} {LAUNCH_OPTIONS} +playdemo "{demo_path}"'

    print(f"[启动命令] {command}")
    subprocess.Popen(command, shell=True)
