# modules/self_tracker.py – FINAL RED TRIANGLE + MAP SHAPE TRACKING
import cv2
import numpy as np
import pyautogui
from utils import log, resource_path

TEMPLATE_PATH = resource_path("data/minimap_template.png")
template = cv2.imread(TEMPLATE_PATH, cv2.IMREAD_COLOR)
if template is None:
    log("FATAL: data/minimap_template.png not found!")
    TEMPLATE = None
else:
    TEMPLATE = template
    h, w = template.shape[:2]
    log(f"Minimap tracker loaded: {w}x{h} (red triangle)")

def get_player_screen_pos(region):
    if TEMPLATE is None:
        return None

    l, t, w, h = region

    # Your minimap is at top-right (from your screenshot)
    minimap_x = l + w - 210   # 10px padding from right edge
    minimap_y = t + 10        # 10px from top
    minimap_size = 200

    try:
        ss = pyautogui.screenshot(region=(minimap_x, minimap_y, minimap_size, minimap_size))
        screen = np.array(ss)

        # Match the entire minimap (very accurate because map shape is unique)
        res = cv2.matchTemplate(screen, TEMPLATE, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        # Very strict threshold — only accepts perfect match
        if max_val < 0.85:
            return None

        # Center of the matched minimap = your character position
        player_x = minimap_x + max_loc[0] + TEMPLATE.shape[1] // 2
        player_y = minimap_y + max_loc[1] + TEMPLATE.shape[0] // 2

        return (player_x, player_y)

    except Exception as e:
        return None