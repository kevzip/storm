# modules/map_loader.py
import gzip
import numpy as np
from utils import log, resource_path
from config.gef_fild01 import CURRENT_MAP, PORTALS

walkable = None

try:
    from numba import njit
    @njit(cache=True)
    def build(d):
        w = np.ones((400,400), dtype=np.bool_)
        for y in range(400):
            for x in range(400):
                if d[y,x] in (1,3,6): w[y,x] = False
        return w
    NUMBA = True
except: NUMBA = False

def load_map():
    global walkable
    path = resource_path(f"data/maps/{CURRENT_MAP}.fld2.gz")
    if not os.path.exists(path):
        log(f"FATAL: {CURRENT_MAP}.fld2.gz not found!")
        return False

    with gzip.open(path, 'rb') as f:
        raw = f.read()

    start = 0
    while len(raw) - start != 160000 and start < 50:
        start += 1
    if len(raw) - start != 160000:
        log("FATAL: Invalid map file size")
        return False

    data = np.frombuffer(raw[start:], dtype=np.uint8).reshape((400,400))

    if NUMBA:
        walkable = build(data)
    else:
        walkable = np.ones((400,400), dtype=bool)
        walkable[data == 1] = walkable[data == 3] = walkable[data == 6] = False

    for px, py in PORTALS:
        walkable[py, px] = False

    log(f"MAP LOADED | {walkable.sum()} walkable tiles")
    return True

def get_walkable():
    return walkable