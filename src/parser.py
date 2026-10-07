import re
from dataclasses import dataclass


@dataclass
class Command:
    action: str            # "click", "double", "hold", "repeat", "stop"
    button: str = "left"   # "left" or "right"
    seconds: float = 1.0   # hold duration, or total time for repeat
    interval: float = 1.0  # only used by repeat
    field: str = ""        # used by "set": "interval" or "duration"


UNITS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19,
}
TENS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
}

def merge_decimals(text):
    """Turn '0 point 0 0 1' into '0.001' and 'point 5' into '0.5'."""
    text = re.sub(
        r"\b(\d+)\s+point((?:\s+\d)+)\b",
        lambda m: m.group(1) + "." + "".join(m.group(2).split()),
        text,
    )
    text = re.sub(
        r"\bpoint((?:\s+\d)+)\b",
        lambda m: "0." + "".join(m.group(1).split()),
        text,
    )
    return text

def words_to_numbers(text):
    """Turn 'twenty five seconds' into '25 seconds'."""
    tokens = text.split()
    out = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t in TENS:
            value = TENS[t]
            if i + 1 < len(tokens) and tokens[i + 1] in UNITS and 1 <= UNITS[tokens[i + 1]] <= 9:
                value += UNITS[tokens[i + 1]]
                i += 1
            out.append(str(value))
        elif t in UNITS:
            out.append(str(UNITS[t]))
        else:
            out.append(t)
        i += 1
    return merge_decimals(" ".join(out))


DURATION = r"(\d+(?:\.\d+)?)\s*(second|sec|minute|min)s?"


def to_seconds(value, unit):
    value = float(value)
    return value * 60 if unit.startswith("min") else value


def find_duration(text, prefix=""):
    """Find '5 seconds' (optionally after a word like 'every' or 'for')."""
    m = re.search(prefix + DURATION, text)
    if not m:
        return None
    return to_seconds(m.group(1), m.group(2))

def normalize_half(text):
    """Turn 'half a second' / 'half second' into '0.5 second'."""
    return re.sub(r"\bhalf\s+(?:a\s+)?(second|minute)", r"0.5 \1", text)

def parse_set(text):
    """Read 'interval 0.1' / 'duration to 20 seconds' using the number right after the field name."""
    for field in ("interval", "duration"):
        m = re.search(
            field + r"\s*(?:to|at|of)?\s*(\d+(?:\.\d+)?)\s*(?:(second|sec|minute|min)s?)?",
            text,
        )
        if m:
            value = float(m.group(1))
            if m.group(2) and m.group(2).startswith("min"):
                value *= 60
            return Command("set", seconds=value, field=field)
    return None


def parse_all(text):
    """Split one phrase into several commands. Settings run before actions."""
    text = words_to_numbers(normalize_half(text.lower().strip()))
    parts = re.split(r"\b(?=(?:set|change|make)\b)", text)
    commands = [c for c in (parse(p) for p in parts) if c]
    commands.sort(key=lambda c: c.action != "set")   # stable: sets first
    return commands

def parse(text):
    """Return a Command, or None if nothing was understood."""
    text = normalize_half(text.lower().strip())
    text = words_to_numbers(text)
    if not text:
        return None

    button = "right" if "right" in text else "left"

    if re.search(r"\b(stop|cancel|abort)\b", text):
        return Command("stop")

    if re.search(r"\b(set|change|make)\b", text):
        cmd = parse_set(text)
        if cmd:
            return cmd

    if re.fullmatch(r"(start|run)( now)?", text):
        return Command("run")

    if "every" in text or "repeat" in text:
        durations = [to_seconds(v, u) for v, u in re.findall(DURATION, text)]
        interval = find_duration(text, r"every\s*") or 1.0
        total = find_duration(text, r"for\s*")
        if total is None and len(durations) >= 2:
            total = durations[-1]          # "every 2 seconds 14 seconds" -> total 14
        if total is None:
            total = 10.0
        return Command("repeat", button, seconds=total, interval=interval)

    if "hold" in text:
        seconds = find_duration(text) or 1.0
        return Command("hold", button, seconds=seconds)

    if "double" in text:
        return Command("double", button)

    if "click" in text:
        return Command("click", button)

    return None