"""
OffTute Avatar — Pygame Edition (Fixed Gesture System)
======================================================
Fixes:
- Gesture state is now atomic using a simple string variable
- set_gesture() no longer fights with start_thinking/stop_thinking
- Gesture persists correctly after thinking state ends
- Image switching is smooth and immediate
"""

import pygame
import pygame.locals as pl
import os
import math
import threading

from avatar.animator import Animator, AvatarState

# ─── Paths ────────────────────────────────────────────────────────────────────
_AVATAR_DIR = os.path.dirname(os.path.abspath(__file__))
_ASSETS_DIR = os.path.join(_AVATAR_DIR, "assets")

# ─── Window ───────────────────────────────────────────────────────────────────
WIN_W    = 300
WIN_H    = 360
FPS      = 30
IMG_SIZE = (260, 290)
IMG_X    = 20
IMG_Y    = 10

# ─── Colors ───────────────────────────────────────────────────────────────────
C_BG       = (13,  13,  26)
C_CARD     = (18,  22,  40)
C_BORDER   = (40,  60,  90)
C_THINK    = (0,   200, 100)
C_SPEAK    = (255, 60,  120)
C_HAPPY    = (255, 200, 0)
C_CONFUSED = (255, 140, 0)
C_POINT    = (100, 180, 255)
C_NOD      = (180, 100, 255)
C_IDLE_DOT = (74,  96,  128)
C_WHITE    = (255, 255, 255)

# ─── Gesture → image filenames ────────────────────────────────────────────────
GESTURE_IMAGES = {
    "idle":      ["idle.png", "idle_breathe.png"],
    "talking":   ["talking_1.png", "talking_2.png"],
    "talking_1": ["talking_1.png", "talking_2.png"],
    "talking_2": ["talking_1.png", "talking_2.png"],
    "thinking":  ["thinking.png"],
    "happy":     ["happy.png"],
    "confused":  ["confused.png"],
    "pointing":  ["pointing.png"],
    "nodding":   ["nodding.png", "idle.png"],
}

# ─── Gesture → glow color ─────────────────────────────────────────────────────
GESTURE_COLORS = {
    "idle":      C_BORDER,
    "talking":   C_SPEAK,
    "talking_1": C_SPEAK,
    "talking_2": C_SPEAK,
    "thinking":  C_THINK,
    "happy":     C_HAPPY,
    "confused":  C_CONFUSED,
    "pointing":  C_POINT,
    "nodding":   C_NOD,
}

# ─── Status labels ────────────────────────────────────────────────────────────
GESTURE_STATUS = {
    "idle":      "OffTute  ◆",
    "talking":   "Speaking",
    "talking_1": "Speaking",
    "talking_2": "Speaking",
    "thinking":  "Thinking",
    "happy":     "Yay! ★",
    "confused":  "Hmm...?",
    "pointing":  "Listen up!",
    "nodding":   "Got it!",
}


class AvatarWindow:

    def __init__(self):
        self.animator    = Animator()
        self._running    = False
        self._screen     = None
        self._hwnd       = None
        self._tick       = 0

        # Drag
        self._dragging   = False
        self._drag_off_x = 0
        self._drag_off_y = 0
        self._win_x      = 0
        self._win_y      = 0

        # Gesture state — single string, written from CLI thread, read from main thread
        # Using a list so mutation is atomic in CPython
        self._gesture    = ["idle"]

        # Images
        self._images     = {}
        self._fallback   = None

    # ─── Public control API ───────────────────────────────────────────────
    # Called from CLI thread (background)

    def start_talking(self):
        """Called when TTS starts playing."""
        self._gesture[0] = "talking"
        self.animator.set_talking()

    def stop_talking(self):
        """Called when TTS finishes."""
        self._gesture[0] = "idle"
        self.animator.set_idle()

    def start_thinking(self):
        """Called while waiting for LLM."""
        self._gesture[0] = "thinking"
        self.animator.set_thinking()

    def stop_thinking(self):
        """Called when LLM responds — keep gesture set by tutor."""
        # Do NOT reset to idle here — tutor.ask() will call set_gesture()
        # immediately after, so we just stop the animator thinking state
        self.animator.set_idle()

    def set_gesture(self, gesture: str):
        """
        Called by tutor after parsing LLM response gesture tag.
        This sets the VISUAL pose — which image to show.
        """
        if gesture in GESTURE_IMAGES:
            self._gesture[0] = gesture
        else:
            self._gesture[0] = "idle"

    # ─── Launch ───────────────────────────────────────────────────────────

    def launch(self):
        """Run pygame — MUST be called from main thread."""
        sw, sh = self._get_screen_size()
        self._win_x = sw - WIN_W - 20
        self._win_y = sh - WIN_H - 60

        os.environ["SDL_VIDEO_WINDOW_POS"] = f"{self._win_x},{self._win_y}"

        pygame.init()
        pygame.display.set_caption("OffTute")
        self._screen = pygame.display.set_mode((WIN_W, WIN_H), pl.NOFRAME)

        # Always on top
        self._set_always_on_top()

        self._load_images()
        self._running = True
        self.animator.start()
        self._game_loop()
        pygame.quit()

    def close(self):
        self._running = False
        self.animator.stop()

    # ─── Helpers ──────────────────────────────────────────────────────────

    def _get_screen_size(self):
        try:
            import ctypes
            return (
                ctypes.windll.user32.GetSystemMetrics(0),
                ctypes.windll.user32.GetSystemMetrics(1),
            )
        except Exception:
            return 1920, 1080

    def _set_always_on_top(self):
        try:
            import ctypes
            self._hwnd = pygame.display.get_wm_info()["window"]
            ctypes.windll.user32.SetWindowPos(
                self._hwnd, -1, self._win_x, self._win_y, 0, 0,
                0x0001 | 0x0002
            )
        except Exception:
            self._hwnd = None

    def _move_window(self, x, y):
        self._win_x = x
        self._win_y = y
        try:
            import ctypes
            ctypes.windll.user32.SetWindowPos(
                self._hwnd, -1, x, y, 0, 0, 0x0001 | 0x0002
            )
        except Exception:
            pass

    # ─── Image loading ────────────────────────────────────────────────────

    def _load_images(self):
        loaded = {}
        missing = []

        for gesture, filenames in GESTURE_IMAGES.items():
            surfs = []
            for fname in filenames:
                path = os.path.join(_ASSETS_DIR, fname)
                if os.path.isfile(path):
                    try:
                        img = pygame.image.load(path).convert_alpha()
                        img = pygame.transform.smoothscale(img, IMG_SIZE)
                        surfs.append(img)
                    except Exception as e:
                        print(f"[Avatar] ⚠ Could not load {fname}: {e}")
                        missing.append(fname)
                else:
                    missing.append(fname)

            if surfs:
                loaded[gesture] = surfs

        self._images = loaded

        if missing:
            unique_missing = list(dict.fromkeys(missing))
            print(f"[Avatar] Missing images: {', '.join(unique_missing)}")
            print(f"[Avatar] Place them in: {_ASSETS_DIR}")

        # Fallback surface
        self._fallback = pygame.Surface(IMG_SIZE, pygame.SRCALPHA)
        self._fallback.fill((30, 50, 80, 200))
        if pygame.font.get_init():
            font = pygame.font.SysFont("Arial", 14)
            txt  = font.render("Add images to avatar/assets/", True, C_WHITE)
            self._fallback.blit(txt, (10, IMG_SIZE[1] // 2 - 10))

    def _get_current_frame(self) -> pygame.Surface:
        gesture = self._gesture[0]
        frames  = self._images.get(gesture)

        # Fallback chain: gesture → idle → fallback surface
        if not frames:
            frames = self._images.get("idle")
        if not frames:
            return self._fallback

        # Multi-frame: alternate at ~3Hz
        if len(frames) > 1:
            idx = (self._tick // (FPS // 3)) % len(frames)
            return frames[idx]

        return frames[0]

    # ─── Game loop ────────────────────────────────────────────────────────

    def _game_loop(self):
        clock = pygame.time.Clock()

        while self._running:
            self._tick += 1
            clock.tick(FPS)

            # ── Events ───────────────────────────────────────────────
            for event in pygame.event.get():
                if event.type == pl.QUIT:
                    self._running = False

                elif event.type == pl.MOUSEBUTTONDOWN and event.button == 1:
                    self._dragging   = True
                    self._drag_off_x = event.pos[0]
                    self._drag_off_y = event.pos[1]

                elif event.type == pl.MOUSEBUTTONUP and event.button == 1:
                    self._dragging = False

                elif event.type == pl.MOUSEMOTION and self._dragging:
                    self._move_window(
                        self._win_x + event.pos[0] - self._drag_off_x,
                        self._win_y + event.pos[1] - self._drag_off_y,
                    )

                elif event.type == pl.KEYDOWN and event.key == pl.K_ESCAPE:
                    self._running = False

            # ── Render ───────────────────────────────────────────────
            self._draw()
            pygame.display.flip()

    # ─── Drawing ──────────────────────────────────────────────────────────

    def _draw(self):
        s       = self._screen
        gesture = self._gesture[0]
        s.fill(C_BG)

        border_color = GESTURE_COLORS.get(gesture, C_BORDER)

        # Card
        self._rounded_rect(s, C_CARD, 8, 8, WIN_W - 16, WIN_H - 16, 18)
        self._rounded_rect_outline(s, border_color, 8, 8, WIN_W - 16, WIN_H - 16, 18, 2)

        # Glow
        if gesture != "idle":
            glow = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
            for r, a in [(85, 12), (65, 22), (45, 35)]:
                pygame.draw.ellipse(
                    glow, (*border_color, a),
                    (WIN_W//2 - r, WIN_H//2 - r - 20, r*2, r*2 + 20)
                )
            s.blit(glow, (0, 0))

        # Character image + breathing bob
        bob   = int(self.animator.bob_offset)
        frame = self._get_current_frame()
        s.blit(frame, (IMG_X, IMG_Y + bob))

        # Top accent line
        pygame.draw.line(s, border_color, (28, 10), (WIN_W - 28, 10), 2)

        # Status bar
        self._draw_status(s, gesture)

    def _draw_status(self, s, gesture):
        dot_count = (self._tick // 7) % 4
        base_label = GESTURE_STATUS.get(gesture, "OffTute")

        # Animated dots for thinking/speaking
        if gesture in ("thinking", "talking", "talking_1", "talking_2"):
            label = base_label + "." * dot_count
        else:
            label = base_label

        color = GESTURE_COLORS.get(gesture, C_IDLE_DOT)

        pill_w, pill_h = 170, 28
        pill_x = WIN_W // 2 - pill_w // 2
        pill_y = WIN_H - 38

        self._rounded_rect(s, (8, 8, 20), pill_x, pill_y, pill_w, pill_h, 14)
        self._rounded_rect_outline(s, color, pill_x, pill_y, pill_w, pill_h, 14, 1)

        font = pygame.font.SysFont("Consolas", 11, bold=True)
        txt  = font.render(label, True, color)
        s.blit(txt, (
            WIN_W // 2 - txt.get_width() // 2,
            pill_y + pill_h // 2 - txt.get_height() // 2
        ))

    # ─── Drawing helpers ──────────────────────────────────────────────────

    def _rounded_rect(self, surf, color, x, y, w, h, r):
        pygame.draw.rect(surf, color, (x+r, y, w-2*r, h))
        pygame.draw.rect(surf, color, (x, y+r, w, h-2*r))
        for cx, cy in [(x+r, y+r), (x+w-r, y+r), (x+r, y+h-r), (x+w-r, y+h-r)]:
            pygame.draw.circle(surf, color, (cx, cy), r)

    def _rounded_rect_outline(self, surf, color, x, y, w, h, r, lw):
        pygame.draw.arc(surf, color, (x,       y,       2*r, 2*r), math.pi/2,   math.pi,     lw)
        pygame.draw.arc(surf, color, (x+w-2*r, y,       2*r, 2*r), 0,           math.pi/2,   lw)
        pygame.draw.arc(surf, color, (x,       y+h-2*r, 2*r, 2*r), math.pi,     3*math.pi/2, lw)
        pygame.draw.arc(surf, color, (x+w-2*r, y+h-2*r, 2*r, 2*r), 3*math.pi/2, 2*math.pi,  lw)
        pygame.draw.line(surf, color, (x+r,   y),     (x+w-r, y),     lw)
        pygame.draw.line(surf, color, (x+r,   y+h),   (x+w-r, y+h),   lw)
        pygame.draw.line(surf, color, (x,     y+r),   (x,     y+h-r), lw)
        pygame.draw.line(surf, color, (x+w,   y+r),   (x+w,   y+h-r), lw)