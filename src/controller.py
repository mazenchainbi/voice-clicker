import threading
import mouse_actions as m


class CommandRunner:
    """Runs one mouse action at a time in a background thread."""

    def __init__(self, on_log=print):
        self.on_log = on_log
        self._thread = None

    @property
    def busy(self):
        return self._thread is not None and self._thread.is_alive()

    def submit(self, cmd):
        if cmd.action == "stop":
            m.stop()
            self.on_log("Stopped")
            return
        if self.busy:
            self.on_log("Busy. Say 'stop' first")
            return
        self._thread = threading.Thread(target=self._run, args=(cmd,), daemon=True)
        self._thread.start()

    def _run(self, cmd):
        self.on_log(f"Running: {cmd}")
        try:
            if cmd.action == "click":
                m.click(cmd.button)
            elif cmd.action == "double":
                m.double_click(cmd.button)
            elif cmd.action == "hold":
                m.hold(cmd.button, cmd.seconds)
            elif cmd.action == "repeat":
                m.repeat(cmd.button, cmd.interval, cmd.seconds)
        except Exception as e:
            self.on_log(f"Error: {e}")
        self.on_log("Finished")