# utils.py
import time
import os
import sys
import pygetwindow as gw
import win32gui
import win32con

def resource_path(relative_path):
    try: base = sys._MEIPASS
    except Exception: base = os.path.abspath(".")
    return os.path.join(base, relative_path)

def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line)
    try:
        with open("bot_log.txt", "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except: pass

def get_ro_window():
    title = "Poring World | Gepard Shield 3.0 (^-_-^)"
    wins = [w for w in gw.getAllWindows() if title in w.title and w.width > 800]
    return (wins[0].left, wins[0].top, wins[0].width, wins[0].height) if wins else (0,0,1024,768)

def focus_ro():
    hwnd = win32gui.FindWindow(None, "Poring World | Gepard Shield 3.0 (^-_-^)")
    if hwnd:
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.06)