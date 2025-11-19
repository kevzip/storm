# modules/memory.py  ← NO MORE SPAM AUTO-FIXED
import ctypes
from utils import log

X_ADDR = 0x0155A48C
Y_ADDR = 0x0155A490
kernel32 = ctypes.windll.kernel32
OpenProcess = kernel32.OpenProcess
ReadProcessMemory = kernel32.ReadProcessMemory
PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400
h_process = None
last_fixed = set()   # ← remembers already fixed tiles

def get_player_tile(walkable):
    global h_process
    import win32process, win32gui
    hwnd = win32gui.FindWindow(None, "Poring World | Gepard Shield 3.0 (^-_-^)")
    if not hwnd: return None
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    if not h_process:
        h_process = OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, pid)
        if not h_process: return None
    try:
        buffer = ctypes.c_int()
        ReadProcessMemory(h_process, X_ADDR, ctypes.byref(buffer), 4, None)
        raw_x = buffer.value
        ReadProcessMemory(h_process, Y_ADDR, ctypes.byref(buffer), 4, None)
        raw_y = buffer.value
        x, y = raw_x + 1, raw_y + 1
        if 0 <= x < 400 and 0 <= y < 400:
            tile = (x, y)
            if not walkable[y, x] and tile not in last_fixed:
                walkable[y, x] = True
                last_fixed.add(tile)
                log(f"AUTO-FIXED walkable at {tile}")   # only logs once per tile
            return (x, y)
    except: pass
    return None