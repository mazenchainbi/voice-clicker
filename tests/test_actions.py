import time
import threading
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import mouse_actions as m

print("Switch to a blank Paint or text window. Starting in 3 seconds...")
time.sleep(3)

print("Test 1: single click")
m.click("left")
time.sleep(1)

print("Test 2: hold left for 3 seconds")
m.hold("left", 3)
time.sleep(1)

print("Test 3: repeat click every 0.5s for 3 seconds")
m.repeat("left", 0.5, 3)
time.sleep(1)

print("Test 4: hold for 10 seconds, but stop after 2")
threading.Timer(2, m.stop).start()
m.hold("left", 10)

print("Done")