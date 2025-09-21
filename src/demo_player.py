import math
import time
from demoparser2 import DemoParser
from .config import DEMO_PATH, TICKRATE
from .buttons import extract_buttons
from .state import pause_flag, skip_to_tick, skip_to_tick_lock, tick_rate_scale


def play_demo(overLay):
    keyOverlay, mouseOverlay, velocityOverlay = (
        overLay.key_overlay,
        overLay.mouse_overlay,
        overLay.velocity_overlay,
    )
    if not DEMO_PATH:
        print("DEMO路径未设置，无法播放")
        return
    parser = DemoParser(DEMO_PATH)
    print(f"正在解析 DEMO: {DEMO_PATH} , 可能需要一些时间...")
    df = parser.parse_ticks(
        [
            "tick",
            "steamid",
            "name",
            "buttons",
            "yaw",
            "pitch",
            "velocity",
            "active_weapon_name",
        ]
    )
    print(f"开始播放 DEMO: {DEMO_PATH}")

    # 玩家选择
    players = df[["steamid", "name"]].drop_duplicates().reset_index(drop=True)
    # print(players)
    print("\n=== 玩家列表 ===")
    for idx, row in players.iterrows():
        print(f"{idx}: {row['name']} ({row['steamid']})")
    try:
        selected_idx = int(input("请选择玩家编号: "))
        selected_steamid = players.iloc[selected_idx]["steamid"]
        print(f"已选择: {players.iloc[selected_idx]['name']}\n")
    except:
        print("输入有误，默认选择第一个玩家\n")
        selected_steamid = players.iloc[0]["steamid"]
    df = df[df["steamid"] == selected_steamid]

    # 等待跳转 tick
    while skip_to_tick[0] is None:
        print("[等待跳转tick，未检测到跳转指令...]")
        time.sleep(0.5)

    # 初始化索引和基准时间
    idx = 0
    tick = df.iloc[idx]["tick"]
    target_tick = skip_to_tick[0]
    while tick < target_tick:
        idx += 1
        row = df.iloc[idx]
        tick = row["tick"]
    print(f"[跳转tick] 已跳转到 tick: {skip_to_tick[0]}, index:{idx}等待 F9 开始播放")
    with skip_to_tick_lock:
        skip_to_tick[0] = None

    pause_flag.set()
    base_time = None
    tick_offset = 0

    while idx < len(df):
        row = df.iloc[idx]
        tick = row["tick"]

        # 暂停逻辑
        while pause_flag.is_set():
            time.sleep(0.05)
            base_time = None

            with skip_to_tick_lock:
                if skip_to_tick[0] is not None and skip_to_tick[0] != tick:
                    # print(tick, "   ", skip_to_tick[0])
                    target_tick = skip_to_tick[0]

                    idx = 0
                    while tick < target_tick:
                        idx += 1
                        row = df.iloc[idx]
                        tick = row["tick"]

                    row = df.iloc[idx]
                    tick = row["tick"]

                    base_time = None
                    print(f"[跳转] 跳转到 tick {target_tick} (idx={idx})")
                    skip_to_tick[0] = None  # 清掉，避免下一轮重复跳转
        # 时间轴计算
        if base_time is None:
            base_time = time.time()
            tick_offset = tick
        target_time = base_time + (tick - tick_offset) / (TICKRATE * tick_rate_scale[0])
        while time.time() < target_time and not pause_flag.is_set():
            time.sleep(0.001)

        # 解析按键
        buttons_val = row["buttons"]
        if buttons_val is None or (
            isinstance(buttons_val, float) and math.isnan(buttons_val)
        ):
            buttons_val = 0
        pressed_keys = extract_buttons(int(buttons_val))

        keyOverlay.updateKeys(pressed_keys, row["active_weapon_name"])
        mouseOverlay.update_trail(row["yaw"], row["pitch"], pressed_keys)
        velocityOverlay.update_velocity(
            row["velocity"], pressed_keys, row["active_weapon_name"]
        )

        # 下一个 tick
        idx += 1
