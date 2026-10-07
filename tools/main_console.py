import time
from voice import VoiceListener
from parser import parse
from controller import CommandRunner

runner = CommandRunner(on_log=print)


def handle(text):
    print("Heard:", text)
    cmd = parse(text)
    if cmd is None:
        print("Not understood")
        return
    runner.submit(cmd)


listener = VoiceListener(on_text=handle, on_status=print)
listener.start()
print("Say a command. Press Ctrl+C to quit.")

try:
    while True:
        time.sleep(0.2)
except KeyboardInterrupt:
    listener.stop()
    m_stop = __import__("mouse_actions").stop
    m_stop()
    print("Bye")