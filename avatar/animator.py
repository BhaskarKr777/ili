import threading
import time
import math
from enum import Enum, auto


class AvatarState(Enum):
    IDLE     = auto()
    TALKING  = auto()
    THINKING = auto()


class Animator:
    """
    Drives avatar animation by updating shared state variables.
    The canvas reads these values and redraws on each tick.
    """

    def __init__(self):
        self.state       = AvatarState.IDLE
        self._lock       = threading.Lock()
        self.mouth_open  = 0.0
        self.bob_offset  = 0.0
        self.blink       = False
        self.eye_dir     = (0, 0)
        self._tick       = 0
        self._running    = False
        self._thread     = None

    def set_idle(self):
        with self._lock:
            self.state = AvatarState.IDLE

    def set_talking(self):
        with self._lock:
            self.state = AvatarState.TALKING

    def set_thinking(self):
        with self._lock:
            self.state = AvatarState.THINKING

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _loop(self):
        fps = 24
        interval = 1.0 / fps
        while self._running:
            t = time.time()
            self._tick += 1
            with self._lock:
                state = self.state
            if state == AvatarState.IDLE:
                self._animate_idle()
            elif state == AvatarState.TALKING:
                self._animate_talking()
            elif state == AvatarState.THINKING:
                self._animate_thinking()
            elapsed = time.time() - t
            time.sleep(max(0, interval - elapsed))

    def _animate_idle(self):
        t = self._tick / 24.0
        self.bob_offset = math.sin(t * 0.3 * 2 * math.pi) * 3
        self.mouth_open = 0.0
        blink_cycle = int(t * 24) % (4 * 24)
        self.blink = blink_cycle < 2
        self.eye_dir = (0, 0)

    def _animate_talking(self):
        t = self._tick / 24.0
        raw = math.sin(t * 3 * 2 * math.pi)
        self.mouth_open = max(0.0, raw)
        self.bob_offset = math.sin(t * 0.5 * 2 * math.pi) * 1.5
        self.blink = False
        self.eye_dir = (0, 0)

    def _animate_thinking(self):
        t = self._tick / 24.0
        self.mouth_open = 0.0
        self.bob_offset = math.sin(t * 0.2 * 2 * math.pi) * 2
        self.eye_dir = (-3, -4)
        blink_cycle = int(t * 24) % (3 * 24)
        self.blink = blink_cycle < 2