"""
ili Avatar — Free Drag Edition
================================
- Click and drag to move anywhere on screen
- Stays exactly where you drop it
- Right click menu: hide/show, close
- Double click to hide
- Always on top
"""

import pygame
import pygame.locals as pl
import os
import math
import ctypes

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
C_MENU_BG  = (20,  25,  45)
C_MENU_HOV = (40,  50,  80)
C_MENU_TXT = (200, 210, 240)

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

GESTURE_STATUS = {
    "idle":      "ili  ◆",
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
        self.animator       = Animator()
        self._running       = False
        self._screen        = None
        self._hwnd          = None
        self._tick          = 0

        # Window position (screen coords)
        self._win_x         = 0
        self._win_y         = 0

        # Drag state — tracked in SCREEN coordinates
        self._dragging      = False
        self._drag_start_wx = 0   # window x when drag started
        self._drag_start_wy = 0   # window y when drag started
        self._drag_start_mx = 0   # mouse x (screen) when drag started
        self._drag_start_my = 0   # mouse y (screen) when drag started

        # Double click
        self._last_click_time = 0

        # Visibility
        self._visible       = True

        # Right click menu
        self._menu_open     = False
        self._menu_x        = 0
        self._menu_y        = 0
        self._menu_hovered  = -1

        # Gesture
        self._gesture       = ["idle"]

        # Images
        self._images        = {}
        self._fallback      = None

    # ─── Public API ───────────────────────────────────────────────────────

    def start_talking(self):
        self._gesture[0] = "talking"
        self.animator.set_talking()

    def stop_talking(self):
        self._gesture[0] = "idle"
        self.animator.set_idle()

    def start_thinking(self):
        self._gesture[0] = "thinking"
        self.animator.set_thinking()

    def stop_thinking(self):
        self.animator.set_idle()

    def set_gesture(self, gesture: str):
        self._gesture[0] = gesture if gesture in GESTURE_IMAGES else "idle"

    # ─── Launch ───────────────────────────────────────────────────────────

    def launch(self):
        sw = ctypes.windll.user32.GetSystemMetrics(0)
        sh = ctypes.windll.user32.GetSystemMetrics(1)
        self._screen_w = sw
        self._screen_h = sh
        self._win_x    = sw - WIN_W - 20
        self._win_y    = sh - WIN_H - 60

        os.environ["SDL_VIDEO_WINDOW_POS"] = f"{self._win_x},{self._win_y}"

        pygame.init()
        pygame.display.set_caption("ili")
        self._screen = pygame.display.set_mode((WIN_W, WIN_H), pl.NOFRAME)

        # Get window handle and set always on top
        try:
            self._hwnd = pygame.display.get_wm_info()["window"]
            self._apply_always_on_top()
        except Exception:
            self._hwnd = None

        self._load_images()
        self._running = True
        self.animator.start()
        self._game_loop()
        pygame.quit()

    def close(self):
        self._running = False
        self.animator.stop()

    # ─── Window positioning ───────────────────────────────────────────────

    def _apply_always_on_top(self):
        """Set window always on top using Windows API."""
        try:
            HWND_TOPMOST = -1
            SWP_NOMOVE   = 0x0002
            SWP_NOSIZE   = 0x0001
            ctypes.windll.user32.SetWindowPos(
                self._hwnd, HWND_TOPMOST,
                0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE
            )
        except Exception:
            pass

    def _set_window_pos(self, x, y):
        """Move window to exact screen position using Windows API."""
        self._win_x = x
        self._win_y = y
        try:
            # HWND_TOPMOST=-1, SWP_NOSIZE=0x0001, SWP_NOACTIVATE=0x0010
            ctypes.windll.user32.SetWindowPos(
                self._hwnd, -1,
                int(x), int(y), 0, 0,
                0x0001 | 0x0010
            )
        except Exception as e:
            print(f"[Avatar] move error: {e}")

    def _get_cursor_screen_pos(self):
        """Get mouse position in SCREEN coordinates using Windows API."""
        try:
            import ctypes.wintypes
            pt = ctypes.wintypes.POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
            return pt.x, pt.y
        except Exception:
            # Fallback: use pygame mouse + window offset
            mx, my = pygame.mouse.get_pos()
            return self._win_x + mx, self._win_y + my

    # ─── Image loading ────────────────────────────────────────────────────

    def _load_images(self):
        loaded  = {}
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
            print(f"[Avatar] Missing: {', '.join(dict.fromkeys(missing))}")

        self._fallback = pygame.Surface(IMG_SIZE, pygame.SRCALPHA)
        self._fallback.fill((30, 50, 80, 200))
        font = pygame.font.SysFont("Arial", 13)
        txt  = font.render("Place images in avatar/assets/", True, C_WHITE)
        self._fallback.blit(txt, (8, IMG_SIZE[1] // 2))

    def _get_current_frame(self):
        gesture = self._gesture[0]
        frames  = self._images.get(gesture) or self._images.get("idle")
        if not frames:
            return self._fallback
        if len(frames) > 1:
            return frames[(self._tick // (FPS // 3)) % len(frames)]
        return frames[0]

    # ─── Game loop ────────────────────────────────────────────────────────

    def _game_loop(self):
        clock = pygame.time.Clock()

        while self._running:
            self._tick += 1
            clock.tick(FPS)

            # ── Events ───────────────────────────────────────────────────
            for event in pygame.event.get():
                if event.type == pl.QUIT:
                    self._running = False

                elif event.type == pl.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self._on_left_down(event)
                    elif event.button == 3:
                        self._on_right_click(event)

                elif event.type == pl.MOUSEBUTTONUP:
                    pass  # drag handled by Windows natively

                elif event.type == pl.MOUSEMOTION:
                    if self._menu_open:
                        self._update_menu_hover(event.pos)

                elif event.type == pl.KEYDOWN:
                    if event.key == pl.K_ESCAPE:
                        self._menu_open = False

            self._draw()
            pygame.display.flip()

    # ─── Event handlers ───────────────────────────────────────────────────

    def _on_left_down(self, event):
        # If menu is open, handle menu click and stop
        if self._menu_open:
            self._handle_menu_click(event.pos)
            return

        # Use Windows native drag — smooth, works everywhere
        try:
            ctypes.windll.user32.ReleaseCapture()
            ctypes.windll.user32.SendMessageW(self._hwnd, 0x00A1, 2, 0)
        except Exception:
            pass

    def _on_right_click(self, event):
        # Open menu — do NOT close avatar
        self._menu_open    = True
        self._menu_x       = event.pos[0]
        self._menu_y       = event.pos[1]
        self._menu_hovered = -1
        self._dragging     = False  # stop any drag

    def _update_menu_hover(self, pos):
        if not self._menu_open:
            return
        mx, my = pos
        item_h = 36
        menu_w = 180
        self._menu_hovered = -1
        for i in range(3):
            iy = self._menu_y + i * item_h
            if self._menu_x <= mx <= self._menu_x + menu_w:
                if iy <= my <= iy + item_h:
                    self._menu_hovered = i

    def _handle_menu_click(self, pos):
        mx, my = pos
        item_h = 36
        menu_w = 180
        clicked_item = -1

        for i in range(3):
            iy = self._menu_y + i * item_h
            if self._menu_x <= mx <= self._menu_x + menu_w:
                if iy <= my <= iy + item_h:
                    clicked_item = i
                    break

        # Always close menu first
        self._menu_open = False

        # Then execute action
        if clicked_item == 0:
            self._visible = not self._visible
        elif clicked_item == 1:
            self._set_window_pos(
                self._screen_w - WIN_W - 20,
                self._screen_h - WIN_H - 60
            )
        elif clicked_item == 2:
            self._running = False
        # If clicked_item == -1 (clicked outside menu), just close menu — do nothing else

    # ─── Drawing ──────────────────────────────────────────────────────────

    def _draw(self):
        s       = self._screen
        gesture = self._gesture[0]
        s.fill(C_BG)

        if not self._visible:
            self._draw_hidden_pill(s)
            return

        border = GESTURE_COLORS.get(gesture, C_BORDER)

        # Card
        self._rrect(s, C_CARD, 8, 8, WIN_W-16, WIN_H-16, 18)
        self._rrect_outline(s, border, 8, 8, WIN_W-16, WIN_H-16, 18, 2)

        # Glow
        if gesture != "idle":
            glow = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
            for r, a in [(85,12),(65,22),(45,35)]:
                pygame.draw.ellipse(glow, (*border, a),
                    (WIN_W//2-r, WIN_H//2-r-20, r*2, r*2+20))
            s.blit(glow, (0,0))

        # Image
        bob = int(self.animator.bob_offset)
        s.blit(self._get_current_frame(), (IMG_X, IMG_Y + bob))

        # Top line
        pygame.draw.line(s, border, (28,10), (WIN_W-28,10), 2)

        # Drag dots
        for i in range(5):
            pygame.draw.circle(s, C_BORDER, (WIN_W//2 - 16 + i*8, 20), 2)

        # Status
        self._draw_status(s, gesture)

        # Menu
        if self._menu_open:
            self._draw_menu(s)

    def _draw_hidden_pill(self, s):
        pw, ph = 120, 32
        px = WIN_W//2 - pw//2
        py = WIN_H//2 - ph//2
        self._rrect(s, C_MENU_BG, px, py, pw, ph, 16)
        self._rrect_outline(s, C_IDLE_DOT, px, py, pw, ph, 16, 1)
        font = pygame.font.SysFont("Consolas", 10, bold=True)
        txt  = font.render("ili  (hidden)", True, C_IDLE_DOT)
        s.blit(txt, (WIN_W//2 - txt.get_width()//2,
                     WIN_H//2 - txt.get_height()//2))

    def _draw_menu(self, s):
        labels  = [
            "👁  Hide" if self._visible else "👁  Show",
            "🏠  Reset position",
            "❌  Close",
        ]
        item_h  = 36
        menu_w  = 180
        total_h = len(labels) * item_h + 8
        mx      = min(self._menu_x, WIN_W - menu_w - 4)
        my      = min(self._menu_y, WIN_H - total_h - 4)

        self._rrect(s, C_MENU_BG, mx, my, menu_w, total_h, 8)
        self._rrect_outline(s, C_BORDER, mx, my, menu_w, total_h, 8, 1)

        font = pygame.font.SysFont("Segoe UI", 12)
        for i, label in enumerate(labels):
            iy = my + 4 + i * item_h
            if i == self._menu_hovered:
                self._rrect(s, C_MENU_HOV, mx+4, iy+2, menu_w-8, item_h-4, 6)
            txt = font.render(label, True, C_MENU_TXT)
            s.blit(txt, (mx+14, iy + item_h//2 - txt.get_height()//2))
            if i < len(labels)-1:
                pygame.draw.line(s, C_BORDER,
                    (mx+10, iy+item_h), (mx+menu_w-10, iy+item_h), 1)

    def _draw_status(self, s, gesture):
        dots  = (self._tick // 7) % 4
        base  = GESTURE_STATUS.get(gesture, "ili")
        label = base + "." * dots if gesture in (
            "thinking","talking","talking_1","talking_2") else base
        color = GESTURE_COLORS.get(gesture, C_IDLE_DOT)

        pw, ph = 170, 28
        px = WIN_W//2 - pw//2
        py = WIN_H - 38
        self._rrect(s, (8,8,20), px, py, pw, ph, 14)
        self._rrect_outline(s, color, px, py, pw, ph, 14, 1)
        font = pygame.font.SysFont("Consolas", 11, bold=True)
        txt  = font.render(label, True, color)
        s.blit(txt, (WIN_W//2 - txt.get_width()//2,
                     py + ph//2 - txt.get_height()//2))

    # ─── Drawing helpers ──────────────────────────────────────────────────

    def _rrect(self, s, c, x, y, w, h, r):
        pygame.draw.rect(s, c, (x+r, y, w-2*r, h))
        pygame.draw.rect(s, c, (x, y+r, w, h-2*r))
        for cx, cy in [(x+r,y+r),(x+w-r,y+r),(x+r,y+h-r),(x+w-r,y+h-r)]:
            pygame.draw.circle(s, c, (cx,cy), r)

    def _rrect_outline(self, s, c, x, y, w, h, r, lw):
        pygame.draw.arc(s,c,(x,y,2*r,2*r),          math.pi/2,   math.pi,     lw)
        pygame.draw.arc(s,c,(x+w-2*r,y,2*r,2*r),    0,           math.pi/2,   lw)
        pygame.draw.arc(s,c,(x,y+h-2*r,2*r,2*r),    math.pi,     3*math.pi/2, lw)
        pygame.draw.arc(s,c,(x+w-2*r,y+h-2*r,2*r,2*r),3*math.pi/2,2*math.pi, lw)
        pygame.draw.line(s,c,(x+r,y),    (x+w-r,y),   lw)
        pygame.draw.line(s,c,(x+r,y+h),  (x+w-r,y+h), lw)
        pygame.draw.line(s,c,(x,y+r),    (x,y+h-r),   lw)
        pygame.draw.line(s,c,(x+w,y+r),  (x+w,y+h-r), lw)