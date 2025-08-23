import time
from demoparser2 import DemoParser
import pandas as pd
import numpy as np
from config import (
    DEMO_PATH,
    TICKRATE,
    BUTTON_MAP,
    MOUSE_TRAIL_DURATION,
    MOUSE_LAYOUT_HEIGHT,
    MOUSE_LAYOUT_WIDTH,
)
from overlay import current_keys
from buttons import extract_buttons
from state import mouse_trail, current_mouse, current_mouse_inputs, update_mouse_inputs


def play_demo(pause_flag, skip_to_tick, skip_to_tick_lock, mouseOverlay):
    parser = DemoParser(DEMO_PATH)
    df = parser.parse_ticks(["tick", "steamid", "name", "buttons", "yaw", "pitch"])

    # 玩家选择
    players = df[["steamid", "name"]].drop_duplicates()
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
    idx = next(
        (i for i, x in enumerate(df) if df.iloc[i]["tick"] >= skip_to_tick[0]), 0
    )
    with skip_to_tick_lock:
        skip_to_tick[0] = None
    print(f"[跳转tick] 已跳转到 tick: {skip_to_tick[0]}, index:{idx}等待 F9 开始播放")

    pause_flag.set()
    base_time = None
    tick_offset = 0

    while idx < len(df):
        row = df.iloc[idx]
        tick = row["tick"]
        # print(f"tick:{tick}, index:{idx}")

        # print(skip_to_tick)
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
        target_time = base_time + (tick - tick_offset) / TICKRATE
        while time.time() < target_time and not pause_flag.is_set():
            # print(time.time())
            time.sleep(0.001)

        # 按键更新
        pressed_keys = extract_buttons(int(row["buttons"]))
        # print(pressed_keys)
        keys = {BUTTON_MAP.get(k, k) for k in pressed_keys if k in BUTTON_MAP}
        current_keys.clear()
        current_keys.update(keys)

        mouseOverlay.update_trail(row["yaw"], row["pitch"], pressed_keys)




        # 下一个 tick
        idx += 1
