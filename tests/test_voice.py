import time
from voice import VoiceListener
from parser import parse
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

def handle(text):
    print("Heard :", text)
    print("Parsed:", parse(text))
    print()


listener = VoiceListener(on_text=handle, on_status=print)
listener.start()

try:
    while True:
        time.sleep(0.2)
except KeyboardInterrupt:
    listener.stop()
    print("Bye")