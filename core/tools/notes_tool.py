"""
Notes Tool
==========
Save, list, search and delete persistent study notes.

Input formats:
  "save | Newton's first law says objects in motion stay in motion"
  "save | title: Physics | Newton's first law..."
  "list"                  — show all notes
  "search | newton"       — search notes by keyword
  "delete | 3"            — delete note number 3
  "clear"                 — delete all notes (asks confirmation)
"""

import os
import re
import json
from datetime import datetime
from .base_tool import BaseTool


NOTES_FILE = os.path.join(os.path.expanduser("~"), "ili_notes", "notes.json")


class NotesTool(BaseTool):
    name = "notes"
    description = (
        "Save, list, search or delete study notes. "
        "Input: 'save | your note text' to save, "
        "'list' to see all notes, "
        "'search | keyword' to find notes, "
        "'delete | number' to delete a note."
    )

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _load(self) -> list:
        if not os.path.exists(NOTES_FILE):
            return []
        try:
            with open(NOTES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save_all(self, notes: list):
        os.makedirs(os.path.dirname(NOTES_FILE), exist_ok=True)
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(notes, f, indent=2, ensure_ascii=False)

    # ── Main ──────────────────────────────────────────────────────────────────

    def run(self, input_text: str) -> str:
        # Clean LLM junk
        inp = re.sub(r'\s*[\(\[].*', '', input_text).strip()
        cmd = inp.lower().split("|")[0].strip()

        # ── SAVE ──────────────────────────────────────────────────────────────
        if cmd == "save":
            parts = inp.split("|", 1)
            if len(parts) < 2 or not parts[1].strip():
                return "Nothing to save. Use: 'save | your note text'"

            content = parts[1].strip()

            # Optional title: "save | title: Physics | content..."
            title = None
            title_match = re.match(r'title:\s*(.+?)\s*\|(.+)', content, re.IGNORECASE)
            if title_match:
                title   = title_match.group(1).strip()
                content = title_match.group(2).strip()

            notes = self._load()
            note  = {
                "id"     : len(notes) + 1,
                "title"  : title or f"Note {len(notes) + 1}",
                "content": content,
                "saved"  : datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            notes.append(note)
            self._save_all(notes)

            return (
                f"📝 Note saved!\n"
                f"  #{note['id']} — {note['title']}\n"
                f"  \"{content[:80]}{'…' if len(content) > 80 else ''}\""
            )

        # ── LIST ──────────────────────────────────────────────────────────────
        if cmd == "list":
            notes = self._load()
            if not notes:
                return "📭 No notes saved yet. Use 'save | your note' to add one."

            lines = [f"📓 You have {len(notes)} note(s):\n"]
            for n in notes:
                preview = n['content'][:60] + ("…" if len(n['content']) > 60 else "")
                lines.append(f"  #{n['id']} [{n['saved']}] {n['title']}: {preview}")
            return "\n".join(lines)

        # ── SEARCH ────────────────────────────────────────────────────────────
        if cmd == "search":
            parts = inp.split("|", 1)
            if len(parts) < 2 or not parts[1].strip():
                return "What to search? Use: 'search | keyword'"

            keyword = parts[1].strip().lower()
            notes   = self._load()
            matches = [
                n for n in notes
                if keyword in n['content'].lower() or keyword in n['title'].lower()
            ]

            if not matches:
                return f"🔍 No notes found matching '{keyword}'."

            lines = [f"🔍 Found {len(matches)} note(s) matching '{keyword}':\n"]
            for n in matches:
                preview = n['content'][:80] + ("…" if len(n['content']) > 80 else "")
                lines.append(f"  #{n['id']} [{n['saved']}] {n['title']}: {preview}")
            return "\n".join(lines)

        # ── DELETE ────────────────────────────────────────────────────────────
        if cmd == "delete":
            parts = inp.split("|", 1)
            if len(parts) < 2 or not parts[1].strip():
                return "Which note? Use: 'delete | number'"

            try:
                note_id = int(parts[1].strip())
            except ValueError:
                return f"Invalid note number '{parts[1].strip()}'. Use a number."

            notes   = self._load()
            updated = [n for n in notes if n['id'] != note_id]

            if len(updated) == len(notes):
                return f"Note #{note_id} not found."

            self._save_all(updated)
            return f"🗑️ Note #{note_id} deleted."

        # ── CLEAR ─────────────────────────────────────────────────────────────
        if cmd == "clear":
            self._save_all([])
            return "🗑️ All notes cleared."

        return (
            f"Didn't understand '{cmd}'. "
            "Try: 'save | text', 'list', 'search | keyword', 'delete | number'."
        )