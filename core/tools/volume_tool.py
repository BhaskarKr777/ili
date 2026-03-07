"""
Volume Tool
===========
Control system volume on Windows using pycaw 20251023+

Input formats:
  "set 50"    — set volume to 50%
  "up 10"     — increase by 10%
  "down 20"   — decrease by 20%
  "mute"      — mute
  "unmute"    — unmute
  "get"       — get current volume
"""

import re
from .base_tool import BaseTool


class VolumeTool(BaseTool):
    name = "volume"
    description = (
        "Control the system volume. "
        "Input: 'set 50' to set to 50%, 'up 10' to increase, "
        "'down 20' to decrease, 'mute', 'unmute', or 'get' to check volume."
    )

    def _get_volume(self):
        """Get pycaw EndpointVolume object using the new 20251023 API."""
        from pycaw.pycaw import AudioUtilities
        device = AudioUtilities.GetSpeakers()
        return device.EndpointVolume

    def _scalar_to_percent(self, vol) -> int:
        """Convert current dB level to 0-100 percent."""
        db_min, db_max, _ = vol.GetVolumeRange()
        db_current = vol.GetMasterVolumeLevel()
        # Clamp and scale
        if db_max == db_min:
            return 0
        percent = (db_current - db_min) / (db_max - db_min) * 100
        return max(0, min(100, round(percent)))

    def _percent_to_db(self, vol, percent: int) -> float:
        """Convert 0-100 percent to dB value."""
        db_min, db_max, _ = vol.GetVolumeRange()
        return db_min + (db_max - db_min) * (percent / 100)

    def run(self, input_text: str) -> str:
        # Clean LLM junk
        inp = re.sub(r'\s*[\(\[].*', '', input_text).strip().lower()
        inp = re.sub(r'%', '', inp).strip()

        try:
            vol = self._get_volume()
        except ImportError:
            return "pycaw is not installed. Run: pip install pycaw"
        except Exception as e:
            return f"Error accessing audio device: {e}"

        # ── GET ───────────────────────────────────────────────────────────────
        if inp in ("get", ""):
            level = self._scalar_to_percent(vol)
            muted = bool(vol.GetMute())
            return f"{'🔇 Muted —' if muted else '🔊'} Volume: {level}%"

        # ── MUTE ──────────────────────────────────────────────────────────────
        if inp == "mute":
            vol.SetMute(1, None)
            return "🔇 Muted."

        # ── UNMUTE ────────────────────────────────────────────────────────────
        if inp == "unmute":
            vol.SetMute(0, None)
            level = self._scalar_to_percent(vol)
            return f"🔊 Unmuted — volume at {level}%."

        # ── SET X ─────────────────────────────────────────────────────────────
        m = re.match(r'set\s+(\d+)', inp)
        if m:
            percent = max(0, min(100, int(m.group(1))))
            db      = self._percent_to_db(vol, percent)
            vol.SetMasterVolumeLevel(db, None)
            vol.SetMute(0, None)
            return f"🔊 Volume set to {percent}%."

        # ── UP X ──────────────────────────────────────────────────────────────
        m = re.match(r'up\s+(\d+)', inp)
        if m:
            delta   = int(m.group(1))
            current = self._scalar_to_percent(vol)
            new     = max(0, min(100, current + delta))
            db      = self._percent_to_db(vol, new)
            vol.SetMasterVolumeLevel(db, None)
            vol.SetMute(0, None)
            return f"🔊 Volume increased from {current}% to {new}%."

        # ── DOWN X ────────────────────────────────────────────────────────────
        m = re.match(r'down\s+(\d+)', inp)
        if m:
            delta   = int(m.group(1))
            current = self._scalar_to_percent(vol)
            new     = max(0, min(100, current - delta))
            db      = self._percent_to_db(vol, new)
            vol.SetMasterVolumeLevel(db, None)
            return f"🔊 Volume decreased from {current}% to {new}%."

        return (
            f"Didn't understand '{inp}'. "
            "Try: 'set 50', 'up 10', 'down 20', 'mute', 'unmute', or 'get'."
        )