# modules/memory.py – MINIMAP PRIMARY + MEMORY FALLBACK
from modules.self_tracker import get_player_screen_pos
from modules.map_loader import get_walkable
from utils import log, get_ro_window

PIXELS_PER_TILE = 42
last_fixed = set()

def screen_to_tile(sx, sy, region):
    l, t, w, h = region
    cx = l + w // 2
    cy = t + h // 2
    dx = sx - cx
    dy = sy - cy
    tx = 200 + round(dx / PIXELS_PER_TILE)
    ty = 200 + round(dy / PIXELS_PER_TILE)
    return (tx, ty)

def get_player_tile(walkable):
    region = get_ro_window()

    # PRIMARY: Minimap tracking (always works)
    pos = get_player_screen_pos(region)
    if pos:
        tile = screen_to_tile(pos[0], pos[1], region)
        if 0 <= tile[0] < 400 and 0 <= tile[1] < 400:
            if not walkable[tile[1], tile[0]] and tile not in last_fixed:
                walkable[tile[1], tile[0]] = True
                last_fixed.add(tile)
                log(f"AUTO-FIXED walkable at {tile}")
            return tile

    # FALLBACK: Memory reading (only when minimap fails)
    try:
        import win32process, win32gui
        hwnd = win32gui.FindWindow(None, "Poring World | Gepard Shield 3.0 (^-_-^)")
        if hwnd:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            kernel32 = ctypes.windll.kernel32
            h = kernel32.OpenProcess(0x0010 | 0x0400, False, pid)
            if h:
                buffer = ctypes.c_int()
                kernel32.ReadProcessMemory(h, 0x0155A48C, ctypes.byref(buffer), 4, None)
                x = buffer.value + 1
                kernel32.ReadProcessMemory(h, 0x0155A490, ctypes.byref(buffer), 4, None)
                y = buffer.value + 1
                kernel32.CloseHandle(h)
                if 10 <= x <= 390 and 10 <= y <= 390:
                    tile = (x, y)
                    if not walkable[y, x] and tile not in last_fixed:
                        walkable[y, x] = True
                        last_fixed.add(tile)
                    return tile
    except: pass

    return None
