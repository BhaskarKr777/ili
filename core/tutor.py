from engines.base_engine import BaseEngine
from core.memory import Memory
from core.modes import SubjectMode, get_mode, MODES, DEFAULT_MODE
import re


GESTURE_INSTRUCTION = """
RULE: Start EVERY response with exactly one gesture tag, then your answer.
Tags: [GESTURE:happy] [GESTURE:thinking] [GESTURE:confused] [GESTURE:pointing] [GESTURE:nodding] [GESTURE:talking] [GESTURE:idle]

When to use each:
[GESTURE:thinking]  — explaining something complex or working something out
[GESTURE:pointing]  — listing steps or directing attention to something specific
[GESTURE:happy]     — student got something right, good news, encouragement
[GESTURE:confused]  — unclear question, need clarification
[GESTURE:nodding]   — agreeing, acknowledging, casual chat responses
[GESTURE:talking]   — general answers and explanations
[GESTURE:idle]      — greetings and very short one-liners

BAD: "Note that... [GESTURE:nodding] Here is my answer"
GOOD: "[GESTURE:thinking] Trigonometry studies triangles..."

Answer immediately after the tag. No disclaimers, no meta-comments."""


class Tutor:

    GESTURE_MAP = {
        "happy":    "happy",
        "thinking": "thinking",
        "confused": "confused",
        "pointing": "pointing",
        "nodding":  "nodding",
        "talking":  "talking_1",
        "idle":     "idle",
    }
    DEFAULT_GESTURE = "idle"

    def __init__(self, engine: BaseEngine, memory: Memory = None, mode: str = DEFAULT_MODE):
        self.engine        = engine
        self.memory        = memory or Memory()
        self._last_gesture = self.DEFAULT_GESTURE
        self._mode         = get_mode(mode)

    # ─── Mode control ─────────────────────────────────────────────────────

    def set_mode(self, mode_name: str) -> str:
        """Switch subject mode. Returns welcome message for new mode."""
        self._mode = get_mode(mode_name)
        self.memory.clear()
        return f"{self._mode.emoji} Switched to **{self._mode.name}** mode!\n{self._mode.welcome}"

    @property
    def current_mode(self) -> SubjectMode:
        return self._mode

    # ─── Main ask ─────────────────────────────────────────────────────────

    def ask(self, user_input: str, avatar=None) -> str:
        history  = self.memory.get_context_text()
        prompt   = self._build_prompt(user_input, history)

        raw_response = self.engine.generate(prompt)
        clean        = self._clean_response(raw_response)
        gesture, final = self._parse_gesture(clean)

        self._last_gesture = gesture
        print(f"[DEBUG] Mode: {self._mode.name} | Gesture: {gesture} | Response: {final[:60]}")

        if avatar and hasattr(avatar, "set_gesture"):
            avatar.set_gesture(gesture)

        self.memory.add("user", user_input)
        self.memory.add("tutor", final)

        return final

    # ─── Prompt building ──────────────────────────────────────────────────

    def _build_prompt(self, user_input: str, history: str) -> str:
        prompt  = self._mode.system_prompt
        prompt += f"\n\n{GESTURE_INSTRUCTION}"

        if history:
            prompt += f"\n\nConversation so far:\n{history}"

        prompt += f"\n\nStudent: {user_input}\nili:"
        return prompt

    # ─── Response cleaning ────────────────────────────────────────────────

    def _clean_response(self, response: str) -> str:
        response = response.strip()

        # If model echoed prompt, take everything after last "ili:"
        if "ili:" in response:
            parts    = response.split("ili:")
            response = parts[-1].strip()

        # Remove prompt echo lines
        bad_phrases = [
            "you are ili", "start every reply", "example reply",
            "gesture instruction", "rule:", "bad:", "good:",
            "student asks", "your response", "teaching style",
            "when to use", "tags:", "answer immediately",
        ]
        lines = response.splitlines()
        clean_lines = []
        for line in lines:
            if not any(p in line.lower() for p in bad_phrases):
                clean_lines.append(line)
        response = "\n".join(clean_lines).strip()

        # If multiple gesture tags, take from the last one
        all_tags = list(re.finditer(r"\[GESTURE:\w+\]", response))
        if len(all_tags) > 1:
            last     = all_tags[-1]
            response = response[last.start():].strip()

        return response

    def _parse_gesture(self, response: str) -> tuple[str, str]:
        response = response.strip()
        match    = re.match(r"^\[GESTURE:(\w+)\]\s*", response)

        if match:
            tag     = match.group(1).lower()
            gesture = self.GESTURE_MAP.get(tag, self.DEFAULT_GESTURE)
            clean   = response[match.end():].strip()

            if not clean:
                clean = "I'm here! What would you like to learn or talk about?"

            return gesture, clean

        return self.DEFAULT_GESTURE, response

    def reset(self):
        self.memory.clear()
        self._last_gesture = self.DEFAULT_GESTURE
        print("🔄 Memory cleared. Fresh start!")