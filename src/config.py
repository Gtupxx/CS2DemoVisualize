from PyQt5.QtCore import QRect
from PyQt5.QtGui import QColor


######################### 以下为路径配置 #########################
DEMO_PATH = r""
CONSOLE_LOG_PATH = r"D:\\SteamLibrary\\steamapps\\common\\Counter-Strike Global Offensive\\game\\csgo\\console.log"
CS2_EXE_PATH = r"D:\\SteamLibrary\\steamapps\\common\\Counter-Strike Global Offensive\\game\\bin\win64\\cs2.exe"


######################### 以下为可调参数 #########################

SCREEN_WIDTH = 2560             #屏幕分辨率
SCREEN_HEIGHT = 1440

KEY_LAYOUT_SCALE = 1.0          # 键盘叠加层缩放

MOUSE_YAW_SCALE = 1.0           # 鼠标y灵敏度缩放
MOUSE_PITCH_SCALE = 1.0         # 鼠标x灵敏度缩放
MOUSE_LAYOUT_SCALE = 0.5        # 鼠标叠加层缩放

VELOCITY_LAYOUT_SCALE = 1.0     # 速度叠加层缩放

MOUSE_TRAIL_DURATION = 0.5      # 鼠标轨迹保留时间
VELOCITY_TRAIL_DURATION = 2.0   # 速度轨迹保留时间

######################### 以下为控制按键 #########################

PAUSE_KEY = 'F9'                # 播放/暂停 按键
MOUSE_TOGGLE_KEY = 'F6'         # 显示/隐藏 鼠标
KEY_TOGGLE_KEY = 'F7'           # 显示/隐藏 键盘
VELOCITY_TOGGLE_KEY = 'F8'      # 显示/隐藏 速度

SLOWMO_KEY = '['                # 0.5x播放 按键
NORMALSPEED_KEY = ']'           # 1.0x播放 按键
FASTMO_KEY = '\\'               # 2.0x播放 按键

######################### 以下为组件颜色 #########################

# QColor(R, G, B, A)  0-255, A可选，表示透明度，0完全透明，255不透明
KEY_PRESSED_COLOR = QColor(0, 180, 0)           # 按键按下颜色
KEY_RELEASED_COLOR = QColor(150, 150, 150)  # 按键未按下颜色

MOUSE_PRESSED_COLOR = QColor(0, 255, 0)     # 鼠标按下颜色
MOUSE_RELEASED_COLOR = QColor(255, 0, 0)    # 鼠标未按下颜色

VELOCITY_BKG_COLOR = QColor(0, 0, 0, 100)            # 速度叠加层背景颜色
VELOCITY_ATTACK_COLOR = QColor(255, 0, 0)           # 速度轨迹颜色
VELOCITY_NORMAL_COLOR = QColor(0, 200, 255)         # 速度轨迹颜色
VELOCITY_ACCURACY_COLOR = QColor(255, 255, 0, 180)  # 精准移速线颜色
VELOCITY_TEXT_COLOR = QColor(255, 255, 255, 200)    # 速度文字颜色


###################### 以下为按键和武器配置 #########################

# 按钮对应关系，只建议修改后面的按键映射
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
    item[0]: QRect(
        int(item[1] * KEY_LAYOUT_SCALE),
        int(item[2] * KEY_LAYOUT_SCALE),
        int((item[3] if len(item) == 4 else 50) * KEY_LAYOUT_SCALE),
        int(50 * KEY_LAYOUT_SCALE),
    )
    for item in KEYS
}

# tick 率
TICKRATE = 64

######################### 以下为固定数据 #########################

# 武器精准移速
WEAPON_ACCURACY_VELOCITY = {
    "AK-47": 73.1,
    "AUG": 74.8,
    "AWP": 33,
    "FAMAS": 74.8,
    "G3SG1": 40.8,
    "Galil AR": 73.1,
    "M249": 66.3,
    "M4A4": 76.5,
    "SG 553": 71.4,
    "SCAR-20": 40.8,
    "SSG 08": 78.2,
    "XM1014": 73.1,
    "Negev": 51,
    "Sawed-Off": 71.4,
    "MP5-SD": 79.9,
    "UMP-45": 78.2,
    "PP-Bizon": 81.6,
    "MAC-10": 81.6,
    "P90": 78.2,
    "MP7": 74.8,
    "MP9": 81.6,
    "Nova": 74.8,
    "M4A1-S": 76.5,
    "Desert Eagle": 78.2,
    "Dual Berettas": 81.6,
    "Five-SeveN": 81.6,
    "Glock-18": 81.6,
    "Tec-9": 81.6,
    "P2000": 81.6,
    "P250": 81.6,
    "USP-S": 81.6,
    "CZ75-Auto": 81.6,
    "R8 Revolver": 180,
}
WEAPON_NAME = {
    "primary": [
        "AK-47",
        "AUG",
        "AWP",
        "FAMAS",
        "G3SG1",
        "Galil AR",
        "M249",
        "M4A4",
        "MAC-10",
        "P90",
        "MP5-SD",
        "UMP-45",
        "XM1014",
        "PP-Bizon",
        "MAG-7",
        "Negev",
        "Sawed-Off",
        "MP7",
        "MP9",
        "Nova",
        "SCAR-20",
        "SG 553",
        "SSG 08",
        "M4A1-S",
    ],
    "secondary": [
        "Desert Eagle",
        "Dual Berettas",
        "Five-SeveN",
        "Glock-18",
        "Tec-9",
        "P2000",
        "P250",
        "USP-S",
        "CZ75-Auto",
        "R8 Revolver",
    ],
    "knife": [
        "Knife",
        "knife",
        "knife_t",
        "Bayonet",
        "Classic Knife",
        "Flip Knife",
        "Gut Knife",
        "Karambit",
        "M9 Bayonet",
        "Huntsman Knife",
        "Falchion Knife",
        "Bowie Knife",
        "Butterfly Knife",
        "Shadow Daggers",
        "Paracord Knife",
        "Survival Knife",
        "Ursus Knife",
        "Navaja Knife",
        "Nomad Knife",
        "Stiletto Knife",
        "Talon Knife",
        "Skeleton Knife",
        "Kukri Knife",
    ],
    "utility": [
        "Zeus x27",
        "Flashbang",
        "High Explosive Grenade",
        "Smoke Grenade",
        "Molotov",
        "Decoy Grenade",
        "Incendiary Grenade",
        "C4 Explosive",
    ],
}
