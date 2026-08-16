import subprocess
import shutil


class TTSEngine:
    """
    TTS engine using macOS built-in 'say' command.

    pyttsx3's nsss driver has a fatal bug: runAndWait() corrupts
    its internal run loop state after the first call, making all
    subsequent speak() calls silently fail. No amount of threading
    or engine recreation reliably fixes this.

    The macOS 'say' command is rock-solid, supports multiple voices,
    and works every time without event loop issues.
    """

    def __init__(self, config):
        self.config = config
        self._process = None

        if not shutil.which("say"):
            raise RuntimeError(
                "'say' command not found. "
                "This TTS engine requires macOS."
            )

    def speak(self, text):

        cmd = ["say"]

        # Map rate: pyttsx3 default 170 wpm → say uses ~180-220
        # say's -r flag takes words per minute directly
        if self.config.rate:
            cmd.extend(["-r", str(self.config.rate)])

        if self.config.voice:
            cmd.extend(["-v", self.config.voice])

        cmd.append(text)

        self._process = subprocess.Popen(cmd)
        self._process.wait()
        self._process = None

    def stop(self):
        if self._process:
            self._process.terminate()
            self._process = None