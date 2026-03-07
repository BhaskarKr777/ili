from engines.base_engine import BaseEngine
from core.memory import Memory
from core.modes import SubjectMode, get_mode, MODES, DEFAULT_MODE
import re


GESTURE_INSTRUCTION = "Start response with one tag: [GESTURE:thinking] [GESTURE:pointing] [GESTURE:happy] [GESTURE:confused] [GESTURE:nodding] [GESTURE:talking] [GESTURE:idle]\nThen answer directly. No extra commentary."


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

    def __init__(self, engine: BaseEngine, memory: Memory = None,
                 mode: str = DEFAULT_MODE, agent=None):
        self.engine        = engine
        self.memory        = memory or Memory()
        self._last_gesture = self.DEFAULT_GESTURE
        self._mode         = get_mode(mode)
        self._agent        = agent

    # ─── Mode control ─────────────────────────────────────────────────────

    def set_mode(self, mode_name: str) -> str:
        self._mode = get_mode(mode_name)
        self.memory.clear()
        return f"{self._mode.emoji} Switched to **{self._mode.name}** mode!\n{self._mode.welcome}"

    @property
    def current_mode(self) -> SubjectMode:
        return self._mode

    # ─── Main ask ─────────────────────────────────────────────────────────

    def ask(self, user_input: str, avatar=None, confirm_fn=None) -> str:
        # ── Try agent first if available ──────────────────────────────────
        if self._agent:
            response, used_tool = self._agent.process(
                user_input, confirm_fn=confirm_fn
            )
            if used_tool:
                gesture, final = self._parse_gesture(response)
                self._last_gesture = gesture
                print(f"[DEBUG] Agent tool used | Gesture: {gesture}")
                if avatar:
                    avatar.set_gesture(gesture)
                self.memory.add("user", user_input)
                self.memory.add("tutor", final)
                return final

        # ── Normal tutor response ─────────────────────────────────────────
        history        = self.memory.get_context_text()
        prompt         = self._build_prompt(user_input, history)
        raw_response   = self.engine.generate(prompt)
        clean          = self._clean_response(raw_response)
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
        prompt  = f"{self._mode.system_prompt}\n\n"
        prompt += f"{GESTURE_INSTRUCTION}\n"

        if history:
            prompt += f"\nConversation so far:\n{history}\n"

        prompt += f"\nStudent: {user_input}\nili:"
        return prompt

    # ─── Response cleaning ────────────────────────────────────────────────

    def _clean_response(self, response: str) -> str:
        response = response.strip()

        if "ili:" in response:
            response = response.split("ili:")[-1].strip()

        bad_phrases = [
            "you are ili", "start response with",
            "gesture instruction", "rule:", "tags:", "then answer",
            "no extra commentary",
        ]
        lines = response.splitlines()
        clean_lines = [
            line for line in lines
            if not any(p in line.lower() for p in bad_phrases)
        ]
        response = "\n".join(clean_lines).strip()

        all_tags = list(re.finditer(r"\[GESTURE:\w+\]", response))
        if len(all_tags) > 1:
            response = response[all_tags[-1].start():].strip()

        return response

    def _parse_gesture(self, response: str) -> tuple[str, str]:
        response = response.strip()

        # Remove hallucinated end tags
        response = re.sub(r'\[END_TAG\]|\[END\]|\[STOP\]', '', response).strip()

        match = re.match(r"^\[GESTURE:(\w+)\]\s*", response)
        if match:
            tag     = match.group(1).lower()
            gesture = self.GESTURE_MAP.get(tag, self.DEFAULT_GESTURE)
            clean   = response[match.end():].strip()
            # Remove any remaining gesture tags from the response body
            clean   = re.sub(r'\[GESTURE:\w+\]', '', clean).strip()
            if not clean:
                clean = "I'm here! What would you like to learn or talk about?"
            return gesture, clean

        # No gesture tag — strip any stray tags from body
        response = re.sub(r'\[GESTURE:\w+\]', '', response).strip()
        return self.DEFAULT_GESTURE, response

    def reset(self):
        self.memory.clear()
        self._last_gesture = self.DEFAULT_GESTURE
        print("🔄 Memory cleared. Fresh start!")