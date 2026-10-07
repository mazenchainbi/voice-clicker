import time
import threading
import pyautogui

pyautogui.FAILSAFE = True   # mouse to top-left corner aborts
pyautogui.PAUSE = 0         # no built-in delay between actions

MAX_SECONDS = 60            # safety cap so a typo can't hold forever

_stop_event = threading.Event()


def stop():
    """Ask any running action to stop as soon as possible."""
    _stop_event.set()


def _wait(seconds):
    """Sleep in small steps so stop() works. Returns False if stopped."""
    end = time.time() + seconds
    while True:
        remaining = end - time.time()
        if remaining <= 0:
            return True
        if _stop_event.is_set():
            return False
        time.sleep(min(0.05, remaining))


def click(button="left"):
    pyautogui.click(button=button)


def hold(button="left", seconds=1.0):
    seconds = min(seconds, MAX_SECONDS)
    _stop_event.clear()
    pyautogui.mouseDown(button=button)
    try:
        _wait(seconds)
    finally:
        pyautogui.mouseUp(button=button)   # always release, even on stop or error


def repeat(button="left", interval=1.0, total=10.0):
    total = min(total, MAX_SECONDS)
    interval = max(interval, 0.01)         # up to ~100 clicks per second
    _stop_event.clear()
    end = time.time() + total
    while time.time() < end:
        if _stop_event.is_set():
            break
        pyautogui.click(button=button)
        if not _wait(interval):
            break

def double_click(button="left"):
    pyautogui.doubleClick(button=button)