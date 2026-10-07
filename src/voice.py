import speech_recognition as sr


class VoiceListener:
    """Listens in a background thread and calls on_text(text) for each phrase."""

    def __init__(self, on_text, on_status=None, language="en-US", device_index=None):
        self.on_text = on_text
        self.on_status = on_status or (lambda msg: None)
        self.language = language
        self.device_index = device_index
        self._recognizer = sr.Recognizer()
        self._stop_listening = None

    @property
    def running(self):
        return self._stop_listening is not None

    def start(self):
        if self.running:
            return
        mic = sr.Microphone(device_index=self.device_index)
        self.on_status("Calibrating microphone...")
        with mic as source:
            self._recognizer.adjust_for_ambient_noise(source, duration=1)
        self._stop_listening = self._recognizer.listen_in_background(
            mic, self._callback, phrase_time_limit=6
        )
        self.on_status("Listening")

    def stop(self):
        if self._stop_listening:
            self._stop_listening(wait_for_stop=False)
            self._stop_listening = None
        self.on_status("Voice off")

    def _callback(self, recognizer, audio):
        try:
            text = recognizer.recognize_google(audio, language=self.language)
        except sr.UnknownValueError:
            return                      # could not understand, ignore
        except sr.RequestError:
            self.on_status("No internet or speech service unavailable")
            return
        self.on_text(text)