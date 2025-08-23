from PyQt5.QtCore import QRect

DEMO_PATH = r""
CONSOLE_LOG_PATH = r"D:\\SteamLibrary\\steamapps\\common\\Counter-Strike Global Offensive\\game\\csgo\\console.log"

SCREEN_WIDTH = 2560
SCREEN_HEIGHT = 1440
KEY_LAYOUT_WIDTH = 410
KEY_LAYOUT_HEIGHT = 320
MOUSE_LAYOUT_WIDTH = 800
MOUSE_LAYOUT_HEIGHT = 600
# 可自定义的轨迹保留时间（秒）
MOUSE_TRAIL_DURATION = 0.5
# tick 率
TICKRATE = 64

# 键位布局
KEYS = [
    ("1", 20, 10),
    ("2", 80, 10),
    ("3", 140, 10),
    ("4", 200, 10),
    ("Q", 40, 70),
    ("W", 100, 70),
    ("E", 160, 70),
    ("R", 220, 70),
    ("A", 60, 130),
    ("S", 120, 130),
    ("D", 180, 130),
    ("F", 240, 130),
    ("SHIFT", 10, 190, 70),
    ("Z", 90, 190, 50),
    ("X", 150, 190, 50),
    ("C", 210, 190, 50),
    ("V", 270, 190, 50),
    ("CTRL", 10, 250, 70),
    ("SPACE", 90, 250, 230),
    ("M1", 330, 10, 60),
    ("M2", 330, 70, 60),
    ("M3", 330, 130, 60),
]
KEY_LAYOUT = {
    item[0]: QRect(item[1], item[2], item[3] if len(item) == 4 else 50, 50)
    for item in KEYS
}

# 按钮对应关系
BUTTON_MAP = {
    "IN_FORWARD": "W",
    "IN_BACK": "S",
    "IN_MOVELEFT": "A",
    "IN_MOVERIGHT": "D",
    "IN_JUMP": "SPACE",
    "IN_DUCK": "CTRL",
    "IN_SPEED": "SHIFT",
    "IN_ATTACK": "M1",
    "IN_ATTACK2": "M2",
    "IN_RELOAD": "R",
    "IN_USE": "E",
    "IN_INSPECT": "F",
}
# cs2 启动路径（根据你本地实际情况修改）
CS2_EXE_PATH = r"D:\\SteamLibrary\\steamapps\\common\\Counter-Strike Global Offensive\\game\bin\win64\\cs2.exe"
