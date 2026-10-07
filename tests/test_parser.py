from parser import parse, parse_all, Command
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

tests = [
    ("hold left click for 5 seconds",        Command("hold", "left", 5)),
    ("hold left click for five seconds",     Command("hold", "left", 5)),
    ("hold right click for twenty five seconds", Command("hold", "right", 25)),
    ("hold for 2 minutes",                   Command("hold", "left", 120)),
    ("hold left click",                      Command("hold", "left", 1)),
    ("click",                                Command("click", "left")),
    ("right click",                          Command("click", "right")),
    ("double click",                         Command("double", "left")),
    ("click every 2 seconds for 10 seconds", Command("repeat", "left", 10, 2)),
    ("click every half a second for 5 seconds", Command("repeat", "left", 5, 0.5)),
    ("hold left click for half a minute",       Command("hold", "left", 30)),
    ("stop",                                 Command("stop")),
    ("what is the weather",                  None),
    ("set interval to 3 seconds",      Command("set", seconds=3, field="interval")),
    ("change interval to half a second", Command("set", seconds=0.5, field="interval")),
    ("set duration to twenty seconds", Command("set", seconds=20, field="duration")),
    ("start",                          Command("run")),
    ("left click every zero point zero zero one seconds fourteen seconds",Command("repeat", "left", 14, 0.001)),
    ("click every point five seconds for ten seconds",Command("repeat", "left", 10, 0.5)),
    ("set interval zero point one",Command("set", seconds=0.1, field="interval")),
    
]

for text, expected in tests:
    result = parse(text)
    status = "OK  " if result == expected else "FAIL"
    print(f"{status} {text!r} -> {result}")

print(parse_all("hold left click for 10 seconds set interval 0.1"))
print(parse_all("set interval 0.5 set duration 20 seconds"))