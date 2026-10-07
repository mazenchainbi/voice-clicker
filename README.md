# Voice Clicker

Control your mouse with your voice. Say "hold left click for five seconds"
and it does it. Windows, works offline.

## Download
Get the latest zip from the Releases page, extract it, and run `VoiceClicker.exe`.
Windows may show a SmartScreen warning: click "More info", then "Run anyway".

## Voice commands
- click / right click / double click
- hold left click for 5 seconds
- click every 2 seconds for 10 seconds
- set interval to 0.5 seconds
- start / stop

## Run from source
1. Install Python 3.12
2. `pip install -r requirements.txt`
3. Download `vosk-model-small-en-us-0.15` from alphacephei.com/vosk/models,
   rename the folder to `model`, and place it in the project root
4. `python src/app.py`

## Build the exe
`pyinstaller --clean VoiceClicker.spec`

## Safety
Move the mouse to the top-left corner of the screen to abort.
Using auto-clickers in online games can get your account banned.
