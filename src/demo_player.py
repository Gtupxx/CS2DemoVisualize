import math
import time

import numpy as np
from demoparser2 import DemoParser
from tqdm import tqdm

from . import config
from .config import TICKRATE, DELAY_TICK_THRESHOLD, VERBOSE
from .buttons import extract_buttons
from .state import pause_flag, skip_to_tick, skip_to_tick_lock, tick_rate_scale

# 每个 usercmd 按键状态字段覆盖 32 个按键位（_1: 0-31, _2: 32-63, _3: 64-95）
BUTTON_STATE_PROPS = (
    "usercmd_buttonstate_1",
    "usercmd_buttonstate_2",
    "usercmd_buttonstate_3",
)

# 播放循环里逐 tick 读取的列，提前转成 ndarray，避免每 tick 创建一次 pandas Series
PLAYBACK_COLUMNS = (
    "tick",
    "buttons",
    "yaw",
    "pitch",
    "velocity",
    "active_weapon_name",
)

BAR_REFRESH_INTERVAL = 0.2  # 进度条刷新间隔（秒），避免每 tick 刷一次拖慢播放

PARSE_BAR_FORMAT = "{desc}: {elapsed} {postfix}"
# 不使用 {rate_fmt}/{remaining}：跳转后它们的估算会失真，这里只显示始终准确的进度与已用时间
PLAYBACK_BAR_FORMAT = (
    "{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} tick [{elapsed}]{postfix}"
)


def ensure_buttons_column(df):
    """
    "buttons" 依赖 pawn 实体的按键位，部分新版本 DEMO（如 14195+ patch）
    不再记录该字段，此时用 usercmd 的按键状态拼出同样的位掩码。
    """
    extra_cols = [c for c in BUTTON_STATE_PROPS if c in df.columns]
    if "buttons" in df.columns:
        return df.drop(columns=extra_cols)

    buttons = np.zeros(len(df), dtype=np.uint64)
    for shift, col in zip((0, 32, 64), BUTTON_STATE_PROPS):
        if col in df.columns:
            values = df[col].to_numpy(dtype=np.uint64, na_value=0)
            buttons |= values << np.uint64(shift)

    df = df.drop(columns=extra_cols)
    df["buttons"] = buttons
    return df


def load_demo_dataframe():
    demo_path = config.DEMO_PATH
    if not demo_path:
        raise RuntimeError("DEMO路径未设置，无法播放")

    parser = DemoParser(demo_path)
    print(f"正在解析 DEMO: {demo_path} , 可能需要一些时间...")

    # demoparser2 不提供解析进度回调，这里用 tqdm 显示已耗时和已读取行数
    bar = tqdm(
        desc="解析 DEMO",
        unit="row",
        dynamic_ncols=True,
        bar_format=PARSE_BAR_FORMAT,
    )
    try:
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
                *BUTTON_STATE_PROPS,
            ]
        )
        bar.set_postfix_str(f"已读取 {len(df):,} 行", refresh=False)
        bar.refresh()
        df = ensure_buttons_column(df)
        bar.set_postfix_str(f"已读取 {len(df):,} 行, 共 {df['steamid'].nunique()} 名玩家")
    finally:
        bar.close()

    print(f"开始播放 DEMO: {demo_path}")
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
    if skip_to_tick[0] is not None:
        return
    print("[等待跳转tick，未检测到跳转指令...]")
    while skip_to_tick[0] is None:
        time.sleep(0.2)


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
        if VERBOSE:
            print(f"[DELAY] tick={tick} delay={-sleep_time * 1000:.2f}ms")
    else:
        if VERBOSE:
            print(f"[SYNC] base_tick={base_tick} tick={tick} sleep={sleep_time * 1000:.2f}ms")
        if sleep_time > 0 and not pause_flag.is_set():
            time.sleep(sleep_time)

    return base_time, -sleep_time


def parse_pressed_keys(buttons_val):
    if buttons_val is None or (
        isinstance(buttons_val, float) and math.isnan(buttons_val)
    ):
        buttons_val = 0
    return extract_buttons(int(buttons_val))


def update_overlays(overlays, data, idx):
    keyOverlay, mouseOverlay, velocityOverlay = overlays
    pressed_keys = parse_pressed_keys(data["buttons"][idx])
    weapon = data["active_weapon_name"][idx]

    keyOverlay.updateKeys(pressed_keys, weapon)
    mouseOverlay.update_trail(data["yaw"][idx], data["pitch"][idx], pressed_keys)
    velocityOverlay.update_velocity(data["velocity"][idx], pressed_keys, weapon)


PLAYBACK_DESC = "播放进度"
PAUSED_DESC = "播放进度(已暂停)"


def sync_bar_position(bar, idx, tick):
    """跳转后同步进度条位置，并在角标显示当前 demo tick"""
    bar.n = idx
    bar.set_postfix_str(f"tick={tick}", refresh=False)
    bar.refresh()


def play_loop(df, start_idx, overlays, ticks):
    # 逐 tick 只做数组下标访问，不做 df.iloc / row["x"] 这类开销大的操作
    data = {name: df[name].to_numpy() for name in PLAYBACK_COLUMNS}
    total = len(df)
    idx = start_idx
    base_time = time.time()
    base_tick = ticks[idx]

    pause_flag.set()

    bar = tqdm(
        total=total,
        initial=start_idx,
        desc=PLAYBACK_DESC,
        unit="tick",
        dynamic_ncols=True,
        bar_format=PLAYBACK_BAR_FORMAT,
        leave=True,
    )
    last_refresh = 0.0

    try:
        while idx < total:
            tick = ticks[idx]
            if VERBOSE:
                print(f"tick: {tick} (index: {idx})")

            # 暂停 & 跳转处理
            while pause_flag.is_set():
                now = time.monotonic()
                if now - last_refresh >= BAR_REFRESH_INTERVAL:
                    bar.set_description_str(PAUSED_DESC, refresh=False)
                    bar.set_postfix_str(f"tick={tick}", refresh=False)
                    bar.refresh()
                    last_refresh = now
                time.sleep(0.05)

                with skip_to_tick_lock:
                    if skip_to_tick[0] is not None and skip_to_tick[0] != tick:
                        base_tick = skip_to_tick[0]
                        base_time = None
                        # 用 tqdm.write 输出，避免日志和进度条互相覆盖
                        tqdm.write(f"base_tick updated to {base_tick} due to skip")
                        idx = jump_to_tick(ticks, skip_to_tick[0])
                        tick = ticks[idx]
                        skip_to_tick[0] = None
                        sync_bar_position(bar, idx, tick)

            if bar.desc != PLAYBACK_DESC:
                bar.set_description_str(PLAYBACK_DESC, refresh=False)
                bar.refresh()

            # 时间同步
            base_time, delay = sync_tick_time(base_time, base_tick, tick)
            if delay >= DELAY_TICK_THRESHOLD / (TICKRATE * tick_rate_scale[0]):
                # 超过延迟tick阈值数，跳过对应tick
                idx += int(delay * TICKRATE * tick_rate_scale[0])
                if idx >= total:
                    break

            # 输入解析 + Overlay 更新
            update_overlays(overlays, data, idx)

            idx += 1

            now = time.monotonic()
            if now - last_refresh >= BAR_REFRESH_INTERVAL:
                sync_bar_position(bar, min(idx, total), tick)
                last_refresh = now
    finally:
        bar.n = min(idx, total)
        bar.close()

    print("播放结束")


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
