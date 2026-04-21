from machine import Pin, TouchPad
import time
import sys
import select

# ── Touch Sensors ─────────────────────────────
t1 = TouchPad(Pin(4))    # Index
t2 = TouchPad(Pin(15))   # Middle
t3 = TouchPad(Pin(13))   # Ring

# ── Threshold ─────────────────────────────────
THRESHOLD = 200

def is_touched(val):
    return val < THRESHOLD

def classify():
    v1 = t1.read()
    v2 = t2.read()
    v3 = t3.read()
    i  = is_touched(v1)  # index
    m  = is_touched(v2)  # middle
    r  = is_touched(v3)  # ring

    # ROCK  → index touched (with or without others)
    if i:
        return "ROCK"
    # SCISSORS → only ring touched
    elif r and not i and not m:
        return "SCISSORS"
    # PAPER → nothing touched
    elif not i and not m and not r:
        return "PAPER"
    else:
        return None

# ── Main Loop ─────────────────────────────────
print("Glove ready!")

last = ""
while True:
    gesture = classify()
    if gesture is not None and gesture != last:
        print(gesture)
        last = gesture
    time.sleep(0.2)
