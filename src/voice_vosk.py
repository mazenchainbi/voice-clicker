import json
import threading
import pyaudio
from vosk import Model, KaldiRecognizer, SetLogLevel

SetLogLevel(-1)

VOCABULARY = (
    "hold left right click double every for second seconds minute minutes "
    "set change make interval duration to stop cancel abort start run now "
    "repeat half a point zero one two three four five six seven eight nine ten "
    "eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen "
    "twenty thirty forty fifty sixty"
).split() + ["[unk]"]


class VoskListener:
    """Same interface as VoiceListener, but fully offline."""

    def __init__(self, on_text, on_status=None, model_path="model", device_index=None):
        self.on_text = on_text
        self.on_status = on_status or (lambda msg: None)
        self.model_path = model_path
        self.device_index = device_index
        self._model = None
        self._thread = None
        self._stop_event = threading.Event()

    @property
    def running(self):
        return self._thread is not None and self._thread.is_alive()

    def start(self):
        if self.running:
            return
        if self._model is None:
            self.on_status("Loading model...")
            self._model = Model(self.model_path)
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        self.on_status("Voice off")

    def _loop(self):
        rec = KaldiRecognizer(self._model, 16000, json.dumps(VOCABULARY))
        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16, channels=1, rate=16000,
                         input=True, input_device_index=self.device_index,
                         frames_per_buffer=2000)
        self.on_status("Listening")
        try:
            while not self._stop_event.is_set():
                data = stream.read(2000, exception_on_overflow=False)
                if rec.AcceptWaveform(data):
                    text = json.loads(rec.Result()).get("text", "").replace("[unk]", "").strip()
                    if text:
                        self.on_text(text)
        finally:
            stream.stop_stream()
            stream.close()
            pa.terminate()