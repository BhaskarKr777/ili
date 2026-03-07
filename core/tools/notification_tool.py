"""
Notification Tool
=================
Send immediate or scheduled desktop notifications.

Input formats:
  Immediate:  "title | message"
  Scheduled:  "title | message | HH:MM"  or  "title | message | in X minutes"
"""

import re
import threading
import time
from datetime import datetime, timedelta
from .base_tool import BaseTool


class NotificationTool(BaseTool):
    name = "notification"
    description = (
        "Send a desktop notification immediately or at a scheduled time. "
        "Input format: 'title | message' for immediate, "
        "or 'title | message | HH:MM' to schedule at a specific time, "
        "or 'title | message | in X minutes' to schedule after a delay."
    )

    # Track pending scheduled notifications
    _scheduled: list = []

    def run(self, input_text: str) -> str:
        # ── Clean LLM junk (parenthetical editorializing etc.) ─────────────────
        inp = re.sub(r'\s*[\(\[].*', '', input_text).strip()

        if not inp:
            return "Error: notification message cannot be empty."

        # ── Parse parts ────────────────────────────────────────────────────────
        parts = [p.strip() for p in inp.split("|")]

        title   = parts[0] if len(parts) >= 1 else "ili"
        message = parts[1] if len(parts) >= 2 else parts[0]
        schedule= parts[2] if len(parts) >= 3 else None

        # If only one part given, treat it as message with default title
        if len(parts) == 1:
            title   = "ili"
            message = parts[0]

        if not message:
            return "Error: notification message cannot be empty."

        # ── Scheduled? ────────────────────────────────────────────────────────
        if schedule:
            return self._schedule(title, message, schedule)

        # ── Immediate ─────────────────────────────────────────────────────────
        return self._send(title, message)

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _send(self, title: str, message: str) -> str:
        """Fire the notification right now."""
        try:
            from plyer import notification
            notification.notify(
                title    = title,
                message  = message,
                app_name = "ili",
                timeout  = 8,
            )
            return f"✅ Notification sent — \"{title}: {message}\""

        except ImportError:
            return "plyer is not installed. Run: pip install plyer"

        except Exception as e:
            # Fallback to winotify
            try:
                from winotify import Notification, audio
                toast = Notification(app_id="ili", title=title, msg=message, duration="short")
                toast.set_audio(audio.Default, loop=False)
                toast.show()
                return f"✅ Notification sent — \"{title}: {message}\""
            except Exception as e2:
                return f"Error sending notification: plyer={e} | winotify={e2}"

    def _schedule(self, title: str, message: str, schedule_str: str) -> str:
        """Parse schedule string and fire in a background thread."""
        schedule_str = schedule_str.strip().lower()
        delay_seconds = None
        fire_at_str   = None

        # ── "in X minutes" / "in X hours" ─────────────────────────────────────
        match = re.match(r'in\s+(\d+)\s*(minute|minutes|min|hour|hours|hr|second|seconds|sec)', schedule_str)
        if match:
            amount = int(match.group(1))
            unit   = match.group(2)
            if "hour" in unit or unit == "hr":
                delay_seconds = amount * 3600
            elif "second" in unit or unit == "sec":
                delay_seconds = amount
            else:
                delay_seconds = amount * 60
            fire_at_str = f"in {amount} {unit}(s)"

        # ── HH:MM or H:MM (12h or 24h) ────────────────────────────────────────
        if delay_seconds is None:
            match = re.match(r'(\d{1,2}):(\d{2})\s*(am|pm)?', schedule_str)
            if match:
                hour   = int(match.group(1))
                minute = int(match.group(2))
                ampm   = match.group(3)

                if ampm == "pm" and hour != 12:
                    hour += 12
                elif ampm == "am" and hour == 12:
                    hour = 0

                now        = datetime.now()
                fire_time  = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

                # If time already passed today, schedule for tomorrow
                if fire_time <= now:
                    fire_time += timedelta(days=1)

                delay_seconds = (fire_time - now).total_seconds()
                fire_at_str   = fire_time.strftime("%I:%M %p")

        if delay_seconds is None:
            return (
                f"Couldn't parse schedule '{schedule_str}'. "
                "Use 'HH:MM' (e.g. 14:30 or 2:30 pm) or 'in X minutes'."
            )

        # ── Launch background thread ───────────────────────────────────────────
        def _fire():
            time.sleep(delay_seconds)
            self._send(title, message)

        t = threading.Thread(target=_fire, daemon=True)
        t.start()
        NotificationTool._scheduled.append({
            "title"  : title,
            "message": message,
            "fire_at": fire_at_str,
            "thread" : t,
        })

        return (
            f"⏰ Notification scheduled for {fire_at_str} — "
            f"\"{title}: {message}\""
        )