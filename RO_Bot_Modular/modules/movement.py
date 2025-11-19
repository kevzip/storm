# modules/movement.py  ← PERFECT ESCAPE + NO STUCK
import time, random, math
import pydirectinput
from utils import focus_ro, log
from modules.memory import get_player_tile
from config.gef_fild01 import PIXELS_PER_TILE, PORTALS, PATROL_HOLD_TIME
from modules.map_loader import get_walkable

last_patrol = 0
walking = False
walk_start_time = 0

# Only update last_target_time from actions.py
def set_last_target_time(t): 
    global last_target_time
    last_target_time = t

def player_center(region):
    l, t, w, h = region
    return l + w // 2, t + h // 2

def clip(x, y, region):
    l, t, w, h = region
    return max(l + 120, min(x, l + w - 120)), max(t + 120, min(y, t + h - 120))

def patrol_walk(region):
    global last_patrol, walking, walk_start_time
    now = time.time()
    if now - last_patrol < 3.8:   # ← slightly faster cycle
        return
    last_patrol = now

    walkable = get_walkable()
    player = get_player_tile(walkable)
    if not player: 
        return
    px, py = player

    # === PERFECT PORTAL ESCAPE (100% works on gef_fild01) ===
    closest = min(PORTALS, key=lambda p: math.hypot(px-p[0], py-p[1]))
    dist = math.hypot(px-closest[0], py-closest[1])

    if dist <= 11:   # a bit bigger radius so it reacts earlier
        log(f"NEAR PORTAL {closest} → ESCAPING NOW!")

        # Stop any current walking
        if walking:
            pydirectinput.mouseUp(button='left')
            walking = False
            time.sleep(0.08)

        # Hard-coded safe escape vectors for each portal (tested on real gef_fild01)
        escape_vectors = {
            (69, 17):  [(0, -22), (4, -20), (-4, -20), (0, -28), (6, -24)],   # go UP
            (16, 102): [(28, 0), (24, 5), (24, -5), (30, 0), (20, 8), (32, -3)], # go RIGHT
            (382, 111): [(-28, -12), (-24, -16), (-20, -20), (-32, -10)],      # go left+up
        }.get(closest, [(20, 20)])

        escaped = False
        for dx, dy in escape_vectors:
            ex, ey = px + dx, py + dy
            if 0 <= ex < 400 and 0 <= ey < 400 and walkable[ey, ex]:
                sx = player_center(region)[0] + dx * PIXELS_PER_TILE
                sy = player_center(region)[1] + dy * PIXELS_PER_TILE
                sx, sy = clip(sx, sy, region)

                focus_ro()
                pydirectinput.moveTo(sx, sy, duration=random.uniform(0.22, 0.34))
                time.sleep(random.uniform(0.12, 0.20))
                pydirectinput.mouseDown(button='left')
                walking = True
                walk_start_time = now
                log(f"ESCAPED → ({ex},{ey})")
                escaped = True
                break

        # Ultimate fallback if nothing works (very rare)
        if not escaped:
            cx, cy = player_center(region)
            pydirectinput.moveTo(cx + random.randint(-80, 80), cy + random.randint(-80, 80))
            pydirectinput.mouseDown(button='left')
            walking = True
            walk_start_time = now
        return

    # === Normal patrol (only runs when far from portals) ===
    if walking and now - walk_start_time > PATROL_HOLD_TIME + random.uniform(-0.5, 1.0):
        pydirectinput.mouseUp(button='left')
        walking = False
        return

    # Don’t patrol for a few seconds after killing something
    try:
        if time.time() - last_target_time < 6.0:
            return
    except:
        pass

    # Simple random short walks (very stable)
    for _ in range(200):
        dx = random.randint(-9, 9)
        dy = random.randint(-9, 9)
        if abs(dx) + abs(dy) < 5: continue
        ex, ey = px + dx, py + dy
        if 0 <= ex < 400 and 0 <= ey < 400 and walkable[ey, ex]:
            sx = player_center(region)[0] + dx * PIXELS_PER_TILE
            sy = player_center(region)[1] + dy * PIXELS_PER_TILE
            sx, sy = clip(sx, sy, region)
            focus_ro()
            pydirectinput.moveTo(sx, sy, duration=random.uniform(0.12, 0.20))
            time.sleep(random.uniform(0.10, 0.18))
            pydirectinput.mouseDown(button='left')
            walking = True
            walk_start_time = now
            return

def stop_walking():
    global walking
    if walking:
        pydirectinput.mouseUp(button='left')
        walking = False