# modules/actions.py
import pydirectinput
import time
import random
import math
from utils import focus_ro, log
from config.gef_fild01 import PIXELS_PER_TILE
from modules.movement import stop_walking

def human_move(target, region):
    focus_ro()
    x2, y2 = int(target[0]), int(target[1])
    pcx, pcy = region[0] + region[2]//2, region[1] + region[3]//2
    steps = max(16, int(math.hypot(x2-pcx, y2-pcy)/17))

    for i in range(steps):
        t = i / steps
        curve = math.sin(t * math.pi) * random.randint(4, 10)
        cx = int(x2 * t + curve * random.choice([-1, 1]))
        cy = int(y2 * t + random.randint(-6, 6))
        cx = max(region[0]+120, min(cx, region[0]+region[2]-120))
        cy = max(region[1]+120, min(cy, region[1]+region[3]-120))
        pydirectinput.moveTo(cx, cy, _pause=False)
    pydirectinput.moveTo(x2, y2, _pause=False)
    time.sleep(0.05)

def loot_action():
    focus_ro()
    log("LOOTING")
    pydirectinput.mouseDown(button='left')
    time.sleep(random.uniform(0.016, 0.03))
    pydirectinput.mouseUp(button='left')

def attack_action():
    from modules.movement import last_target_time
    focus_ro()
    log("ATTACKING")
    pydirectinput.mouseDown(button='left')
    time.sleep(random.uniform(0.016, 0.03))
    pydirectinput.mouseUp(button='left')
    globals()['last_target_time'] = time.time()  # update global

def stop_walking_immediately():
    stop_walking()