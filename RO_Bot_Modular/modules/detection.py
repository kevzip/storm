# modules/detection.py
import cv2
import numpy as np
import pyautogui
import math
import time
import keyboard
from utils import focus_ro, log
from config.gef_fild01 import *
from modules.memory import get_player_tile
from modules.map_loader import get_walkable

last_target = None
last_target_time = 0
last_loot_pos = None
loot_hold_start = 0

def player_center(region):
    l, t, w, h = region
    return l + w // 2, t + h // 2

def screen_to_tile(sx, sy, region):
    player = get_player_tile(get_walkable())
    if not player: return None
    cx, cy = player_center(region)
    dx = sx - cx
    dy = sy - cy
    tx = player[0] + round(dx / PIXELS_PER_TILE)
    ty = player[1] + round(dy / PIXELS_PER_TILE)
    return (tx, ty)

def find_loot(region):
    global last_loot_pos, loot_hold_start
    l, t, w, h = region
    pcx, pcy = player_center(region)
    try:
        ss = pyautogui.screenshot(region=(l+40, t+180, w-80, h-220))
        img = np.array(ss)
        diff = np.abs(img.astype(int) - np.array([0,116,0]))
        matches = np.where(np.all(diff <= 25, axis=-1))
        if len(matches[0]) == 0: return None

        points = []
        walkable = get_walkable()
        for y, x in zip(matches[0], matches[1]):
            cx = x + l + 40
            cy = y + t + 180
            if cy >= t + 280:
                d = math.hypot(cx-pcx, cy-pcy)
                if d <= LOOT_MAX_DIST:
                    tile = screen_to_tile(cx, cy, region)
                    if tile and walkable[tile[1], tile[0]]:
                        points.append((d, cx, cy, tile))

        if not points: return None
        points.sort()
        best = points[0][1:3]
        if last_loot_pos and math.hypot(best[0]-last_loot_pos[0], best[1]-last_loot_pos[1]) < 30:
            if time.time() - loot_hold_start > LOOT_HOLD_TIME:
                return None
        else:
            loot_hold_start = time.time()
        last_loot_pos = best
        log(f"LOOT TILE {points[0][3]}")
        return best
    except: return None

def find_monster(region):
    global last_target, last_target_time
    l, t, w, h = region
    try:
        ss = pyautogui.screenshot(region=(l+25, t+25, w-50, h-50))
        img = cv2.cvtColor(np.array(ss), cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array(MONSTER_HSV_LOWER), np.array(MONSTER_HSV_UPPER))

        ui = np.zeros((h-50, w-50), np.uint8)
        ui[UI_TOP-25:h-UI_BOTTOM-25, UI_LEFT:w-UI_RIGHT] = 255
        mask = cv2.bitwise_and(mask, ui)

        kernel = np.ones((3,3), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=1)
        mask = cv2.erode(mask, kernel, iterations=1)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        candidates = []
        walkable = get_walkable()

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if MIN_AREA < area < 50000:
                M = cv2.moments(cnt)
                if M["m00"]:
                    cx = int(M["m10"]/M["m00"]) + l + 25
                    cy = int(M["m01"]/M["m00"]) + t + 25
                    tile = screen_to_tile(cx, cy, region)
                    if tile and walkable[tile[1], tile[0]]:
                        candidates.append((cx, cy, tile))

        if not candidates: return None
        pcx, pcy = player_center(region)
        candidates.sort(key=lambda p: math.hypot(p[0]-pcx, p[1]-pcy))
        best_screen = candidates[0][:2]
        best_tile = candidates[0][2]

        if last_target and math.hypot(best_screen[0]-last_target[0], best_screen[1]-last_target[1]) < 38:
            if time.time() - last_target_time > REFRESH_THRESHOLD:
                log("REFRESH TARGET ALT+2")
                focus_ro()
                keyboard.press_and_release('alt+2')
                last_target_time = time.time()
            return last_target

        last_target = best_screen
        last_target_time = time.time()
        log(f"TARGET TILE {best_tile}")
        return best_screen
    except: return None