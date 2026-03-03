"""
OffTute Persistent Memory
=========================
- Saves conversations to JSON files in memory/sessions/
- Keeps last 7 days of sessions
- Each session stores: messages, timestamp, engine, summary, student name
- On startup: shows session list and lets user pick one to load
"""

import os
import json
import datetime
from typing import List, Dict, Optional


# ─── Storage location ─────────────────────────────────────────────────────────
_ROOT_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MEMORY_DIR   = os.path.join(_ROOT_DIR, "memory", "sessions")
_PROFILE_FILE = os.path.join(_ROOT_DIR, "memory", "profile.json")

# Keep sessions for 7 days
MAX_AGE_DAYS  = 7
# Max turns kept in active context window
MAX_TURNS     = 10


class Memory:
    """
    Persistent conversation memory.
    Saves to disk after every message.
    Loads previous sessions on startup.
    """

    def __init__(self, max_turns: int = MAX_TURNS):
        self.max_turns       = max_turns
        self._history        : List[Dict[str, str]] = []
        self._session_id     : Optional[str] = None
        self._session_file   : Optional[str] = None
        self._engine_name    : str = "local"
        self._student_name   : str = "Student"
        self._topics_covered : List[str] = []
        self._started_at     : str = ""

        # Ensure directories exist
        os.makedirs(_MEMORY_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(_PROFILE_FILE), exist_ok=True)

    # ─── Session management ───────────────────────────────────────────────

    def startup(self, engine_name: str = "local") -> bool:
        """
        Called on startup. Cleans old sessions, loads student profile,
        shows session picker. Returns True if a session was loaded.
        """
        self._engine_name = engine_name
        self._clean_old_sessions()
        self._load_profile()

        print(f"\n👋 Welcome back, {self._student_name}!")

        sessions = self._list_sessions()

        if not sessions:
            print("📭 No previous sessions found. Starting fresh!\n")
            self._new_session()
            return False

        # Show session picker
        print("\n📚 Previous sessions:\n")
        print(f"  [0] Start a new session")
        for i, s in enumerate(sessions, 1):
            date    = s.get("started_at", "Unknown date")[:16].replace("T", " ")
            engine  = s.get("engine", "local")
            topics  = s.get("topics", [])
            name    = s.get("student_name", "Student")
            summary = ", ".join(topics[:3]) if topics else "No topics recorded"
            turns   = len(s.get("messages", [])) // 2
            print(f"  [{i}] {date}  |  {engine}  |  {turns} exchanges  |  {summary}")

        print()
        choice = self._get_choice(len(sessions))

        if choice == 0:
            print("✨ Starting fresh session!\n")
            self._new_session()
            return False
        else:
            chosen = sessions[choice - 1]
            self._load_session(chosen)
            print(f"✅ Loaded session from {chosen.get('started_at', '')[:16].replace('T', ' ')}\n")
            return True

    def set_student_name(self, name: str):
        """Save student name to profile."""
        self._student_name = name
        self._save_profile()

    # ─── Message operations ───────────────────────────────────────────────

    def add(self, role: str, content: str):
        """Add a message and immediately save to disk."""
        self._history.append({"role": role, "content": content})

        # Trim to max turns
        max_entries = self.max_turns * 2
        if len(self._history) > max_entries:
            self._history = self._history[-max_entries:]

        # Auto-detect topics from tutor responses
        if role == "tutor":
            self._detect_topic(content)

        # Save after every message
        self._save_session()

    def get_context_text(self) -> str:
        """Format history as text for prompt injection."""
        if not self._history:
            return ""
        lines = []
        for msg in self._history:
            label = "Student" if msg["role"] == "user" else "Tutor"
            lines.append(f"{label}: {msg['content']}")
        return "\n".join(lines)

    def clear(self):
        """Clear in-memory history and start a new session file."""
        self._history = []
        self._topics_covered = []
        self._new_session()

    def __len__(self):
        return len(self._history)

    def is_empty(self):
        return len(self._history) == 0

    # ─── Internal: session file operations ───────────────────────────────

    def _new_session(self):
        """Create a new session file."""
        now = datetime.datetime.now()
        self._session_id   = now.strftime("%Y%m%d_%H%M%S")
        self._session_file = os.path.join(_MEMORY_DIR, f"session_{self._session_id}.json")
        self._started_at   = now.isoformat()
        self._history      = []
        self._topics_covered = []
        self._save_session()

    def _save_session(self):
        """Write current session to disk."""
        if not self._session_file:
            self._new_session()
            return

        data = {
            "session_id":   self._session_id,
            "started_at":   self._started_at,
            "saved_at":     datetime.datetime.now().isoformat(),
            "engine":       self._engine_name,
            "student_name": self._student_name,
            "topics":       self._topics_covered,
            "messages":     self._history,
        }

        try:
            with open(self._session_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Memory] ⚠ Could not save session: {e}")

    def _load_session(self, session_data: dict):
        """Load a previous session into memory."""
        self._session_id     = session_data.get("session_id", "")
        self._session_file   = os.path.join(
            _MEMORY_DIR, f"session_{self._session_id}.json"
        )
        self._started_at     = session_data.get("started_at", "")
        self._engine_name    = session_data.get("engine", "local")
        self._student_name   = session_data.get("student_name", "Student")
        self._topics_covered = session_data.get("topics", [])
        self._history        = session_data.get("messages", [])

        # Trim to max turns on load
        max_entries = self.max_turns * 2
        if len(self._history) > max_entries:
            self._history = self._history[-max_entries:]

    def _list_sessions(self) -> List[dict]:
        """Return all valid sessions sorted newest first."""
        sessions = []
        try:
            for fname in os.listdir(_MEMORY_DIR):
                if not fname.endswith(".json"):
                    continue
                path = os.path.join(_MEMORY_DIR, fname)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    # Only include sessions with actual messages
                    if data.get("messages"):
                        sessions.append(data)
                except Exception:
                    continue
        except Exception:
            pass

        # Sort newest first
        sessions.sort(key=lambda s: s.get("started_at", ""), reverse=True)
        return sessions

    def _clean_old_sessions(self):
        """Delete session files older than MAX_AGE_DAYS."""
        cutoff = datetime.datetime.now() - datetime.timedelta(days=MAX_AGE_DAYS)
        try:
            for fname in os.listdir(_MEMORY_DIR):
                if not fname.endswith(".json"):
                    continue
                path = os.path.join(_MEMORY_DIR, fname)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    started = datetime.datetime.fromisoformat(
                        data.get("started_at", "2000-01-01")
                    )
                    if started < cutoff:
                        os.unlink(path)
                except Exception:
                    pass
        except Exception:
            pass

    # ─── Internal: profile ────────────────────────────────────────────────

    def _save_profile(self):
        try:
            with open(_PROFILE_FILE, "w", encoding="utf-8") as f:
                json.dump({"student_name": self._student_name}, f)
        except Exception:
            pass

    def _load_profile(self):
        try:
            if os.path.isfile(_PROFILE_FILE):
                with open(_PROFILE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._student_name = data.get("student_name", "Student")
        except Exception:
            pass

    # ─── Internal: topic detection ────────────────────────────────────────

    def _detect_topic(self, text: str):
        """
        Simple keyword-based topic detection from tutor responses.
        Adds new topics to the session's topic list.
        """
        keywords = {
            "math": ["equation", "algebra", "calculus", "geometry", "trigonometry",
                     "arithmetic", "fraction", "derivative", "integral"],
            "science": ["physics", "chemistry", "biology", "quantum", "atom",
                        "molecule", "energy", "force", "gravity"],
            "history": ["war", "revolution", "empire", "ancient", "century",
                        "civilization", "historical", "dynasty"],
            "programming": ["code", "function", "variable", "algorithm", "python",
                            "javascript", "loop", "class", "object"],
            "language": ["grammar", "vocabulary", "sentence", "verb", "noun",
                         "spelling", "pronunciation", "language"],
            "economics": ["supply", "demand", "market", "inflation", "gdp",
                          "economy", "trade", "currency"],
        }

        text_lower = text.lower()
        for topic, words in keywords.items():
            if topic not in self._topics_covered:
                if any(word in text_lower for word in words):
                    self._topics_covered.append(topic)

    # ─── Internal: input helper ───────────────────────────────────────────

    def _get_choice(self, max_val: int) -> int:
        while True:
            try:
                raw = input(f"  Choose [0-{max_val}]: ").strip()
                val = int(raw)
                if 0 <= val <= max_val:
                    return val
                print(f"  Please enter a number between 0 and {max_val}")
            except (ValueError, EOFError):
                return 0