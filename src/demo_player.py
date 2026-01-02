import math
import time
from demoparser2 import DemoParser
from .config import DEMO_PATH, TICKRATE, DELAY_TICK_THRESHOLD
from .buttons import extract_buttons
from .state import pause_flag, skip_to_tick, skip_to_tick_lock, tick_rate_scale


def load_demo_dataframe():
    if not DEMO_PATH:
        raise RuntimeError("DEMO路径未设置，无法播放")

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
    return df


def select_player(df):
    players = df[["steamid", "name"]].drop_duplicates().reset_index(drop=True)

    print("\n=== 玩家列表 ===")
    for idx, row in players.iterrows():
        print(f"{idx}: {row['name']} ({row['steamid']})")

    try:
        selected_idx = int(input("请选择玩家编号: "))
        steamid = players.iloc[selected_idx]["steamid"]
        print(f"已选择: {players.iloc[selected_idx]['name']}\n")
    except Exception:
        print("输入有误，默认选择第一个玩家\n")
        steamid = players.iloc[0]["steamid"]

    return df[df["steamid"] == steamid].reset_index(drop=True)


def wait_for_initial_skip():
    while skip_to_tick[0] is None:
        print("[等待跳转tick，未检测到跳转指令...]")
        time.sleep(0.5)


def jump_to_tick(ticks, target_tick):
    idx = ticks.searchsorted(target_tick, side="left")
    if idx >= len(ticks):
        idx = len(ticks) - 1

    print(
        f"[跳转tick] 已跳转到 tick: {target_tick}, "
        f"index:{idx} (actual_tick={ticks[idx]})，等待 F9 开始播放"
    )
    return idx


def sync_tick_time(base_time, base_tick, tick):
    now = time.time()
    if base_time is None:
        return now, 0.0
    target_time = base_time + (tick - base_tick) / (TICKRATE * tick_rate_scale[0])

    # ===== 单次 sleep（精准等待）=====
    sleep_time = target_time - now
    if sleep_time < 0:
        print(f"[DELAY] tick={tick} delay={-sleep_time*1000:.2f}ms")
    else:
        print(f"[SYNC] base_tick={base_tick} tick={tick} sleep={sleep_time*1000:.2f}ms")
        if sleep_time > 0 and not pause_flag.is_set():
            time.sleep(sleep_time)

    return base_time, -sleep_time


def parse_pressed_keys(buttons_val):
    if buttons_val is None or (
        isinstance(buttons_val, float) and math.isnan(buttons_val)
    ):
        buttons_val = 0
    return extract_buttons(int(buttons_val))


def log_weapon(weapon_name):
    with open("weapon.log", "a", encoding="utf-8") as f:
        print(weapon_name, file=f)


def update_overlays(row, pressed_keys, overlays):
    keyOverlay, mouseOverlay, velocityOverlay = overlays

    keyOverlay.updateKeys(pressed_keys, row["active_weapon_name"])
    mouseOverlay.update_trail(row["yaw"], row["pitch"], pressed_keys)
    velocityOverlay.update_velocity(
        row["velocity"], pressed_keys, row["active_weapon_name"]
    )


def play_loop(df, start_idx, overlays, ticks):
    idx = start_idx
    base_time = time.time()
    base_tick = ticks[idx]

    pause_flag.set()

    while idx < len(df):
        row = df.iloc[idx]
        tick = row["tick"]
        print(f"tick: {tick} (index: {idx})")
        # 暂停 & 跳转处理
        while pause_flag.is_set():
            time.sleep(0.05)

            with skip_to_tick_lock:
                if skip_to_tick[0] is not None and skip_to_tick[0] != tick:
                    base_tick = skip_to_tick[0]
                    base_time = None
                    print(f"base_tick updated to {base_tick} due to skip")
                    idx = jump_to_tick(ticks, skip_to_tick[0])
                    skip_to_tick[0] = None

        # 时间同步
        base_time, delay = sync_tick_time(base_time, base_tick, tick)
        if delay >= DELAY_TICK_THRESHOLD / (TICKRATE * tick_rate_scale[0]):
            # 超过延迟tick阈值数，跳过对应tick
            idx += int(delay * TICKRATE * tick_rate_scale[0])
        # 输入解析
        pressed_keys = parse_pressed_keys(row["buttons"])

        # Overlay 更新
        update_overlays(row, pressed_keys, overlays)

        idx += 1


def play_demo(overLay):
    overlays = (
        overLay.key_overlay,
        overLay.mouse_overlay,
        overLay.velocity_overlay,
    )

    df = load_demo_dataframe()
    df = select_player(df)

    ticks = df["tick"].values

    wait_for_initial_skip()

    with skip_to_tick_lock:
        start_idx = jump_to_tick(ticks, skip_to_tick[0])
        skip_to_tick[0] = None

    play_loop(df, start_idx, overlays, ticks)
