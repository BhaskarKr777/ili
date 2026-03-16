"""
ili Chat UI
============
PyQt5-based chat window that replaces the terminal UI.
Features: avatar display, chat history, text input, voice toggle,
document upload, mode switcher.
"""

import os
import sys
import threading
import time

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLineEdit, QLabel, QComboBox,
    QFileDialog, QScrollArea, QFrame, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation,
    QEasingCurve, QSize, pyqtProperty, QRect
)
from PyQt5.QtGui import (
    QFont, QColor, QPalette, QPixmap, QPainter, QBrush,
    QLinearGradient, QPen, QFontDatabase, QIcon, QTextCursor
)

from core.modes import MODES, get_mode, list_modes

# ─── Theme ────────────────────────────────────────────────────────────────────
BG          = "#0A0A14"
BG2         = "#0F1020"
CARD        = "#12152A"
CARD2       = "#161B35"
BORDER      = "#1E2845"
ACCENT      = "#7C6FFF"
ACCENT2     = "#FF6B9D"
TEXT        = "#E2E8FF"
TEXT_DIM    = "#6B7599"
TEXT_MUTED  = "#3A4268"
USER_BG     = "#1A1F3D"
BOT_BG      = "#111428"
SUCCESS     = "#4EFFA0"
WARNING     = "#FFB547"

FONT_MONO   = "Consolas"
FONT_UI     = "Segoe UI"


# ─── Worker thread for LLM responses ─────────────────────────────────────────
class ResponseWorker(QThread):
    response_ready = pyqtSignal(str, bool)
    thinking_start = pyqtSignal()
    thinking_stop  = pyqtSignal()

    def __init__(self, tutor, user_input, confirm_fn=None, doc_content=None):
        super().__init__()
        self.tutor       = tutor
        self.user_input  = user_input
        self.confirm_fn  = confirm_fn
        self.doc_content = doc_content

    def run(self):
        self.thinking_start.emit()
        try:
            prompt = self.user_input
            if self.doc_content:
                prompt = f"{self.user_input}\n\n[Document content]:\n{self.doc_content}"

            if hasattr(self.tutor, '_agent') and self.tutor._agent and self.confirm_fn:
                response, used_tool = self.tutor._agent.process(prompt, self.confirm_fn)
            else:
                response  = self.tutor.ask(prompt)
                used_tool = False

            import re
            response = re.sub(r'\[GESTURE:[^\]]+\]', '', response).strip()

        except Exception as e:
            response  = f"Something went wrong: {e}"
            used_tool = False
        finally:
            self.thinking_stop.emit()

        self.response_ready.emit(response, used_tool)


# ─── Bubble widget ────────────────────────────────────────────────────────────
class MessageBubble(QFrame):
    def __init__(self, text: str, is_user: bool, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self._setup(text)

    def _setup(self, text: str):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(10)

        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setFont(QFont(FONT_UI, 10))
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        if self.is_user:
            label.setStyleSheet(f"""
                color: {TEXT};
                background: {USER_BG};
                border: 1px solid {ACCENT}44;
                border-radius: 14px;
                padding: 10px 14px;
            """)
            layout.addStretch()
            layout.addWidget(label)
        else:
            label.setStyleSheet(f"""
                color: {TEXT};
                background: {BOT_BG};
                border: 1px solid {BORDER};
                border-radius: 14px;
                padding: 10px 14px;
            """)
            layout.addWidget(label)
            layout.addStretch()

        self.setStyleSheet("background: transparent; border: none;")


# ─── Typing indicator ─────────────────────────────────────────────────────────
class TypingIndicator(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._dots = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update)
        self.setFont(QFont(FONT_MONO, 9))
        self.setStyleSheet(f"color: {ACCENT}; padding: 6px 16px;")
        self.hide()

    def start(self):
        self._dots = 0
        self._timer.start(400)
        self.show()

    def stop(self):
        self._timer.stop()
        self.hide()

    def _update(self):
        self._dots = (self._dots + 1) % 4
        self.setText("ili is thinking" + "." * self._dots)


# ─── Avatar panel ─────────────────────────────────────────────────────────────
class AvatarPanel(QLabel):
    def __init__(self, assets_dir: str, parent=None):
        super().__init__(parent)
        self.assets_dir = assets_dir
        self._state     = "idle"
        self.setFixedSize(200, 220)
        self.setAlignment(Qt.AlignCenter)
        self._load_pixmap()
        self.setStyleSheet(f"""
            background: {CARD};
            border: 1px solid {BORDER};
            border-radius: 16px;
        """)

    def _load_pixmap(self):
        names = {
            "idle":     "idle.png",
            "thinking": "thinking.png",
            "talking":  "talking_1.png",
            "happy":    "happy.png",
        }
        fname = names.get(self._state, "idle.png")
        path  = os.path.join(self.assets_dir, fname)
        if os.path.isfile(path):
            pix = QPixmap(path).scaled(
                180, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.setPixmap(pix)
        else:
            self.setText("ili")
            self.setFont(QFont(FONT_MONO, 28, QFont.Bold))
            self.setStyleSheet(f"""
                color: {ACCENT};
                background: {CARD};
                border: 1px solid {BORDER};
                border-radius: 16px;
            """)

    def set_state(self, state: str):
        self._state = state
        self._load_pixmap()


# ─── Main window ──────────────────────────────────────────────────────────────
class IliChatWindow(QMainWindow):

    confirm_signal = pyqtSignal(str, object)
    append_signal  = pyqtSignal(str, bool)

    def __init__(self, tutor, engine_name: str, initial_mode: str = "general",
                 voice_output: bool = False, agent_enabled: bool = False):
        super().__init__()
        self.tutor          = tutor
        self.engine_name    = engine_name
        self.current_mode   = initial_mode
        self.voice_output   = voice_output
        self.agent_enabled  = agent_enabled
        self.voice_mode     = False
        self._doc_content   = None
        self._doc_name      = None
        self._worker        = None

        self._setup_window()
        self._build_ui()
        self._apply_styles()

        self.append_signal.connect(self._append_message)
        self.confirm_signal.connect(self._show_confirm_dialog)

        mode = get_mode(initial_mode)
        self._append_system(f"{mode.welcome}")

    # ─── Window setup ─────────────────────────────────────────────────────

    def _setup_window(self):
        self.setWindowTitle("ili")
        self.setMinimumSize(560, 780)
        self.resize(600, 860)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)

        screen = QApplication.primaryScreen().geometry()
        self.move(
            screen.width()  - self.width()  - 20,
            screen.height() - self.height() - 60,
        )

    # ─── UI construction ──────────────────────────────────────────────────

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        main = QVBoxLayout(root)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        main.addWidget(self._build_header())
        main.addWidget(self._build_chat_area(), stretch=1)
        main.addWidget(self._build_input_bar())

    def _build_header(self):
        header = QFrame()
        header.setFixedHeight(240)
        header.setObjectName("header")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)

        # Avatar
        assets_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "avatar", "assets"
        )
        self.avatar_panel = AvatarPanel(os.path.normpath(assets_dir))
        layout.addWidget(self.avatar_panel)

        # Info panel
        info = QVBoxLayout()
        info.setSpacing(8)

        title = QLabel("ili")
        title.setFont(QFont(FONT_MONO, 26, QFont.Bold))
        title.setStyleSheet(f"color: {ACCENT}; letter-spacing: 3px;")
        info.addWidget(title)

        sub = QLabel("Interactive Learning Intelligence")
        sub.setFont(QFont(FONT_UI, 9))
        sub.setStyleSheet(f"color: {TEXT_DIM};")
        info.addWidget(sub)

        info.addSpacing(8)

        # Mode switcher
        mode_row = QHBoxLayout()
        mode_label = QLabel("Mode")
        mode_label.setFont(QFont(FONT_UI, 9))
        mode_label.setStyleSheet(f"color: {TEXT_DIM};")
        mode_row.addWidget(mode_label)

        self.mode_combo = QComboBox()
        for key, mode in MODES.items():
            self.mode_combo.addItem(f"{mode.emoji}  {mode.name}", key)
        for i in range(self.mode_combo.count()):
            if self.mode_combo.itemData(i) == self.current_mode:
                self.mode_combo.setCurrentIndex(i)
                break
        self.mode_combo.currentIndexChanged.connect(self._on_mode_change)
        mode_row.addWidget(self.mode_combo)
        info.addLayout(mode_row)

        info.addSpacing(4)

        # Status
        status_row = QHBoxLayout()
        self.status_dot = QLabel("●")
        self.status_dot.setFont(QFont(FONT_MONO, 8))
        self.status_dot.setStyleSheet(f"color: {SUCCESS};")
        status_row.addWidget(self.status_dot)

        self.status_label = QLabel(f"{self.engine_name.upper()} · Ready")
        self.status_label.setFont(QFont(FONT_UI, 8))
        self.status_label.setStyleSheet(f"color: {TEXT_DIM};")
        status_row.addWidget(self.status_label)
        status_row.addStretch()
        info.addLayout(status_row)

        info.addStretch()
        layout.addLayout(info)
        layout.addStretch()

        return header

    def _build_chat_area(self):
        container = QFrame()
        container.setObjectName("chatContainer")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setObjectName("chatScroll")

        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setContentsMargins(8, 12, 8, 12)
        self.chat_layout.setSpacing(4)
        self.chat_layout.addStretch()

        self.scroll.setWidget(self.chat_widget)
        layout.addWidget(self.scroll)

        self.typing = TypingIndicator()
        layout.addWidget(self.typing)

        return container

    def _build_input_bar(self):
        bar = QFrame()
        bar.setObjectName("inputBar")
        bar.setFixedHeight(110)

        outer = QVBoxLayout(bar)
        outer.setContentsMargins(12, 8, 12, 10)
        outer.setSpacing(8)

        # Doc indicator
        self.doc_bar = QFrame()
        self.doc_bar.setObjectName("docBar")
        doc_row = QHBoxLayout(self.doc_bar)
        doc_row.setContentsMargins(8, 4, 8, 4)
        self.doc_label = QLabel()
        self.doc_label.setFont(QFont(FONT_UI, 8))
        self.doc_label.setStyleSheet(f"color: {WARNING};")
        doc_row.addWidget(self.doc_label)
        doc_row.addStretch()
        clear_doc = QPushButton("x")
        clear_doc.setFixedSize(18, 18)
        clear_doc.setObjectName("clearDoc")
        clear_doc.clicked.connect(self._clear_doc)
        doc_row.addWidget(clear_doc)
        self.doc_bar.hide()
        outer.addWidget(self.doc_bar)

        # Input row
        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask anything...")
        self.input_field.setFont(QFont(FONT_UI, 10))
        self.input_field.setObjectName("inputField")
        self.input_field.returnPressed.connect(self._send)
        input_row.addWidget(self.input_field)

        self.send_btn = QPushButton("Send")
        self.send_btn.setObjectName("sendBtn")
        self.send_btn.setFixedSize(70, 38)
        self.send_btn.setFont(QFont(FONT_UI, 9, QFont.Bold))
        self.send_btn.clicked.connect(self._send)
        input_row.addWidget(self.send_btn)

        outer.addLayout(input_row)

        # Controls row
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(8)

        self.voice_btn = QPushButton("Voice: OFF")
        self.voice_btn.setObjectName("voiceBtn")
        self.voice_btn.setCheckable(True)
        self.voice_btn.setFixedHeight(30)
        self.voice_btn.setFont(QFont(FONT_UI, 8))
        self.voice_btn.clicked.connect(self._toggle_voice)
        ctrl_row.addWidget(self.voice_btn)

        self.upload_btn = QPushButton("Upload Doc")
        self.upload_btn.setObjectName("uploadBtn")
        self.upload_btn.setFixedHeight(30)
        self.upload_btn.setFont(QFont(FONT_UI, 8))
        self.upload_btn.clicked.connect(self._upload_doc)
        ctrl_row.addWidget(self.upload_btn)

        ctrl_row.addStretch()

        clear_btn = QPushButton("Clear Chat")
        clear_btn.setObjectName("clearBtn")
        clear_btn.setFixedHeight(30)
        clear_btn.setFont(QFont(FONT_UI, 8))
        clear_btn.clicked.connect(self._clear_chat)
        ctrl_row.addWidget(clear_btn)

        outer.addLayout(ctrl_row)

        return bar

    # ─── Styles ───────────────────────────────────────────────────────────

    def _apply_styles(self):
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background: {BG};
                color: {TEXT};
            }}
            #header {{
                background: {BG2};
                border-bottom: 1px solid {BORDER};
            }}
            #chatContainer {{
                background: {BG};
            }}
            #chatScroll {{
                background: {BG};
                border: none;
            }}
            #chatScroll QScrollBar:vertical {{
                background: {BG2};
                width: 6px;
                border-radius: 3px;
            }}
            #chatScroll QScrollBar::handle:vertical {{
                background: {BORDER};
                border-radius: 3px;
                min-height: 30px;
            }}
            #chatScroll QScrollBar::add-line:vertical,
            #chatScroll QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            #inputBar {{
                background: {BG2};
                border-top: 1px solid {BORDER};
            }}
            #inputField {{
                background: {CARD};
                color: {TEXT};
                border: 1px solid {BORDER};
                border-radius: 10px;
                padding: 8px 14px;
                font-size: 10pt;
                selection-background-color: {ACCENT}66;
            }}
            #inputField:focus {{
                border: 1px solid {ACCENT}88;
            }}
            #sendBtn {{
                background: {ACCENT};
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }}
            #sendBtn:hover {{ background: #9D92FF; }}
            #sendBtn:pressed {{ background: #6358DD; }}
            #sendBtn:disabled {{
                background: {BORDER};
                color: {TEXT_MUTED};
            }}
            #voiceBtn {{
                background: {CARD};
                color: {TEXT_DIM};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 0 12px;
            }}
            #voiceBtn:checked {{
                background: {ACCENT2}22;
                color: {ACCENT2};
                border: 1px solid {ACCENT2}88;
            }}
            #voiceBtn:hover {{ border-color: {ACCENT}88; }}
            #uploadBtn {{
                background: {CARD};
                color: {TEXT_DIM};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 0 12px;
            }}
            #uploadBtn:hover {{
                border-color: {WARNING}88;
                color: {WARNING};
            }}
            #clearBtn {{
                background: transparent;
                color: {TEXT_MUTED};
                border: 1px solid {TEXT_MUTED}44;
                border-radius: 8px;
                padding: 0 12px;
            }}
            #clearBtn:hover {{
                color: {ACCENT2};
                border-color: {ACCENT2}66;
            }}
            #docBar {{
                background: {WARNING}11;
                border: 1px solid {WARNING}44;
                border-radius: 6px;
            }}
            #clearDoc {{
                background: transparent;
                color: {TEXT_DIM};
                border: none;
                font-size: 8pt;
            }}
            QComboBox {{
                background: {CARD};
                color: {TEXT};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 4px 10px;
                font-size: 9pt;
                min-width: 160px;
            }}
            QComboBox:hover {{ border-color: {ACCENT}88; }}
            QComboBox QAbstractItemView {{
                background: {CARD2};
                color: {TEXT};
                border: 1px solid {BORDER};
                selection-background-color: {ACCENT}44;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
        """)

    # ─── Chat actions ──────────────────────────────────────────────────────

    def _send(self):
        text = self.input_field.text().strip()
        if not text or self._worker is not None:
            return

        self.input_field.clear()
        self._append_message(text, True)
        self.send_btn.setEnabled(False)
        self.status_label.setText(f"{self.engine_name.upper()} · Thinking...")
        self.status_dot.setStyleSheet(f"color: {WARNING};")
        self.avatar_panel.set_state("thinking")

        self._worker = ResponseWorker(
            tutor       = self.tutor,
            user_input  = text,
            confirm_fn  = self._confirm_action if self.agent_enabled else None,
            doc_content = self._doc_content,
        )
        self._worker.response_ready.connect(self._on_response)
        self._worker.thinking_start.connect(self.typing.start)
        self._worker.thinking_stop.connect(self.typing.stop)
        self._worker.start()

        if self._doc_content:
            self._clear_doc()

    def _on_response(self, text: str, used_tool: bool):
        self._worker = None
        self._append_message(text, False)
        self.send_btn.setEnabled(True)
        self.status_label.setText(f"{self.engine_name.upper()} · Ready")
        self.status_dot.setStyleSheet(f"color: {SUCCESS};")
        self.avatar_panel.set_state("idle")

        if self.voice_output or self.voice_mode:
            threading.Thread(target=self._speak, args=(text,), daemon=True).start()

    def _speak(self, text: str):
      try:
        from voice.text_to_speech import speak
        speak(
            text,
            on_start = lambda: self.avatar_panel.set_state("talking"),
            on_stop  = lambda: self.avatar_panel.set_state("idle"),
            blocking = True,
        )
      except Exception as e:
        print(f"[TTS] {e}")

    def _append_message(self, text: str, is_user: bool):
        bubble = MessageBubble(text, is_user)
        count  = self.chat_layout.count()
        self.chat_layout.insertWidget(count - 1, bubble)
        QTimer.singleShot(50, self._scroll_to_bottom)

    def _append_system(self, text: str):
        label = QLabel(text)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont(FONT_UI, 8))
        label.setStyleSheet(f"color: {TEXT_DIM}; padding: 6px;")
        count = self.chat_layout.count()
        self.chat_layout.insertWidget(count - 1, label)

    def _scroll_to_bottom(self):
        sb = self.scroll.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _clear_chat(self):
        while self.chat_layout.count() > 1:
            item = self.chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        mode = get_mode(self.current_mode)
        self._append_system(f"{mode.welcome}")

    # ─── Mode switcher ────────────────────────────────────────────────────

    def _on_mode_change(self, index: int):
        key = self.mode_combo.itemData(index)
        if key and key != self.current_mode:
            self.current_mode = key
            self.tutor.set_mode(key)
            mode = get_mode(key)
            self._append_system(f"Switched to {mode.name} mode")

    # ─── Voice toggle ─────────────────────────────────────────────────────

    def _toggle_voice(self, checked: bool):
        self.voice_mode = checked
        self.voice_btn.setText("Voice: ON" if checked else "Voice: OFF")
        if checked:
            self._start_voice_input()

    def _start_voice_input(self):
        def _listen():
            try:
                from voice.speech_to_text import listen
                self._append_system("Listening...")
                text = listen()
                if text:
                    self.append_signal.emit(text, True)
                    self.input_field.setText(text)
                    QTimer.singleShot(100, self._send)
            except Exception as e:
                self._append_system(f"Voice error: {e}")
            finally:
                self.voice_btn.setChecked(False)
                self.voice_mode = False
                self.voice_btn.setText("Voice: OFF")

        threading.Thread(target=_listen, daemon=True).start()

    # ─── Document upload ──────────────────────────────────────────────────

    def _upload_doc(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Upload Document", "",
            "Documents (*.pdf *.txt *.md *.py *.js *.csv);;All Files (*)"
        )
        if not path:
            return

        ext = os.path.splitext(path)[1].lower()

        try:
            if ext == ".pdf":
                try:
                    import pypdf
                    reader  = pypdf.PdfReader(path)
                    content = "\n".join(p.extract_text() or "" for p in reader.pages)
                except ImportError:
                    content = "[pypdf not installed — cannot read PDF]"
            else:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

            if len(content) > 8000:
                content = content[:8000] + "\n... (truncated)"

            self._doc_content = content
            self._doc_name    = os.path.basename(path)
            self.doc_label.setText(f"Attached: {self._doc_name}")
            self.doc_bar.show()
            self.input_field.setPlaceholderText(f"Ask about {self._doc_name}...")

        except Exception as e:
            self._append_system(f"Could not read file: {e}")

    def _clear_doc(self):
        self._doc_content = None
        self._doc_name    = None
        self.doc_bar.hide()
        self.input_field.setPlaceholderText("Ask anything...")

    # ─── Agent confirm ────────────────────────────────────────────────────

    def _confirm_action(self, action_desc: str) -> bool:
        import queue
        result_q = queue.Queue()
        self.confirm_signal.emit(action_desc, result_q)
        return result_q.get()

    def _show_confirm_dialog(self, action_desc: str, result_q):
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("ili wants to act")
        msg.setText(f"ili wants to:\n\n{action_desc}")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background: {CARD2};
                color: {TEXT};
            }}
            QPushButton {{
                background: {ACCENT};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 18px;
                min-width: 60px;
            }}
            QPushButton:hover {{ background: #9D92FF; }}
        """)
        result = msg.exec_() == QMessageBox.Yes
        result_q.put(result)

    # ─── Public API ───────────────────────────────────────────────────────

    def set_gesture(self, gesture: str):
        state_map = {
            "thinking": "thinking", "talking": "talking",
            "talking_1": "talking", "talking_2": "talking",
            "happy": "happy", "idle": "idle",
        }
        self.avatar_panel.set_state(state_map.get(gesture, "idle"))

    def start_talking(self):  self.avatar_panel.set_state("talking")
    def stop_talking(self):   self.avatar_panel.set_state("idle")
    def start_thinking(self): self.avatar_panel.set_state("thinking")
    def stop_thinking(self):  self.avatar_panel.set_state("idle")


# ─── Entry point ──────────────────────────────────────────────────────────────

def run_gui(tutor, engine_name: str, initial_mode: str = "general",
            voice_output: bool = False, agent_enabled: bool = False):
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyle("Fusion")

    window = IliChatWindow(
        tutor         = tutor,
        engine_name   = engine_name,
        initial_mode  = initial_mode,
        voice_output  = voice_output,
        agent_enabled = agent_enabled,
    )
    window.show()
    sys.exit(app.exec_())