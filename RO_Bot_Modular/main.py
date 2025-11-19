# main.py - RO Bot Modular Edition
import time
import threading
import keyboard
from config.gef_fild01 import *  # ← Change this line to switch maps!
from utils import log, get_ro_window, focus_ro
from modules.map_loader import load_map
from modules.movement import patrol_walk
from modules.detection import find_monster, find_loot
from modules.actions import attack_action, loot_action, human_move, stop_walking_immediately

paused = True
stop_requested = False

def hotkeys():
    keyboard.add_hotkey('up', lambda: globals().update(paused=not paused) or log("RESUMED" if not paused else "PAUSED"))
    keyboard.add_hotkey('down', lambda: globals().update(stop_requested=True) or log("STOP REQUESTED"))
    keyboard.add_hotkey('f12', focus_ro)
    keyboard.wait()

if __name__ == "__main__":
    print("="*70)
    print(f" RO BOT MODULAR – {MAP_NAME}")
    print(" UP = Start/Pause | DOWN = Stop | F12 = Focus Window")
    print("="*70)
    time.sleep(3)
    log("=== BOT STARTED ===")

    if not load_map():
        input("Map failed to load. Press Enter to exit...")
        exit()

    threading.Thread(target=hotkeys, daemon=True).start()
    region = get_ro_window()

    try:
        while not stop_requested:
            if paused:
                time.sleep(0.1)
                continue

            region = get_ro_window()

            # Priority: Loot > Monster > Patrol
            loot = find_loot(region)
            if loot:
                stop_walking_immediately()
                human_move(loot, region)
                loot_action()
                time.sleep(0.9)
                continue

            monster = find_monster(region)
            if monster:
                stop_walking_immediately()
                human_move(monster, region)
                attack_action()
                time.sleep(ATTACK_DELAY + random.uniform(-0.15, 0.15))
                continue

            patrol_walk(region)
            time.sleep(random.uniform(0.2, 0.38))

    except Exception as e:
        log(f"CRASH: {e}")
    finally:
        log("BOT STOPPED")
        input("Press Enter to exit...")