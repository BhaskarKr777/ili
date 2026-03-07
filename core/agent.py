"""
ili Agent
==========
The agent layer sits between the tutor and the tools.
It decides whether a question needs a tool, asks permission,
runs the tool, and feeds the result back to the LLM for a final answer.
"""

import re
from core.tools.base_tool import BaseTool


# ─── Tool decision prompt ─────────────────────────────────────────────────────

AGENT_PROMPT = """You are ili, an AI tutor that can also use tools to help students.

Available tools:
{tool_list}

Given the student's message, decide if you need a tool or can answer directly.

If you need a tool, respond EXACTLY in this format:
USE_TOOL: <tool_name>
INPUT: <tool_input>

If you can answer directly without a tool, respond EXACTLY in this format:
DIRECT: <your answer starting with a gesture tag>

Examples:
Student: what is the weather today
USE_TOOL: web_search
INPUT: weather today

Student: search for python tutorials
USE_TOOL: web_search
INPUT: python tutorials

Student: open calculator for me
USE_TOOL: open_app
INPUT: calculator

Student: open youtube
USE_TOOL: open_app
INPUT: youtube

Student: take a screenshot
USE_TOOL: screenshot
INPUT:

Student: run this python code: print(2+2)
USE_TOOL: run_code
INPUT: python:print(2+2)

Student: copy 'hello world' to my clipboard
USE_TOOL: clipboard
INPUT: write: hello world

Student: copy 'ili is awesome' to clipboard
USE_TOOL: clipboard
INPUT: write: ili is awesome

Student: what is in my clipboard
USE_TOOL: clipboard
INPUT: read

Student: what's in my clipboard
USE_TOOL: clipboard
INPUT: read

Student: read text on my screen
USE_TOOL: ocr
INPUT: full

Student: what does my screen say
USE_TOOL: ocr
INPUT: full

Student: read the text on screen
USE_TOOL: ocr
INPUT: full

Student: send me a notification saying take a break
USE_TOOL: notification
INPUT: ili | take a break

Student: remind me to drink water
USE_TOOL: notification
INPUT: ili | drink water

Student: send a desktop notification that study time is over
USE_TOOL: notification
INPUT: ili | study time is over

Student: remind me at 2:30 pm to stop studying
USE_TOOL: notification
INPUT: ili | stop studying | 2:30 pm

Student: notify me at 14:00 to take a break
USE_TOOL: notification
INPUT: ili | take a break | 14:00

Student: remind me in 10 minutes to drink water
USE_TOOL: notification
INPUT: ili | drink water | in 10 minutes

Student: set a reminder in 1 hour to eat lunch
USE_TOOL: notification
INPUT: ili | eat lunch | in 1 hour

Student: write a python file called timer.py that counts down from 10
USE_TOOL: write_code
INPUT: timer.py | countdown timer from 10 to 0

Student: create a javascript file hello.js that prints hello world
USE_TOOL: write_code
INPUT: hello.js | print hello world to console

Student: write a python script to sort a list and save it as sort.py
USE_TOOL: write_code
INPUT: sort.py | function that sorts a list of numbers

Student: make a python file called calculator.py with add subtract multiply divide
USE_TOOL: write_code
INPUT: calculator.py | calculator with add subtract multiply divide functions

Student: set volume to 50
USE_TOOL: volume
INPUT: set 50

Student: turn volume up by 10
USE_TOOL: volume
INPUT: up 10

Student: mute the volume
USE_TOOL: volume
INPUT: mute

Student: unmute
USE_TOOL: volume
INPUT: unmute

Student: what is the current volume
USE_TOOL: volume
INPUT: get

Student: save a note that newton's first law is about inertia
USE_TOOL: notes
INPUT: save | Newton's first law is about inertia

Student: show me all my notes
USE_TOOL: notes
INPUT: list

Student: search my notes for physics
USE_TOOL: notes
INPUT: search | physics

Student: delete note number 2
USE_TOOL: notes
INPUT: delete | 2

Student: read this pdf C:/Users/Asus/Documents/notes.pdf
USE_TOOL: read_pdf
INPUT: C:/Users/Asus/Documents/notes.pdf

Student: read page 3 of C:/Users/Asus/Documents/notes.pdf
USE_TOOL: read_pdf
INPUT: C:/Users/Asus/Documents/notes.pdf | page 3

Student: open a youtube video on bubble sort
USE_TOOL: youtube
INPUT: bubble sort tutorial

Student: search youtube for python for beginners
USE_TOOL: youtube
INPUT: python for beginners

Student: play a video on newton's laws
USE_TOOL: youtube
INPUT: newton's laws explained

Student: what is photosynthesis
DIRECT: [GESTURE:thinking] Photosynthesis is the process by which plants...

Student: explain newton's laws
DIRECT: [GESTURE:thinking] Newton's three laws of motion describe...

Student: {user_input}"""


ANSWER_PROMPT = """You are ili, a friendly AI tutor.

The student asked: {user_input}

You used the tool '{tool_name}' and got this result:
{tool_result}

Now give a helpful, friendly answer to the student based on this result.
Start with a gesture tag: [GESTURE:thinking] [GESTURE:talking] [GESTURE:happy] [GESTURE:pointing]
Be concise and helpful."""


class Agent:

    def __init__(self, engine, tools: list):
        self.engine = engine
        self.tools  = {t.name: t for t in tools}

    def _tool_list_str(self) -> str:
        lines = []
        for name, tool in self.tools.items():
            lines.append(f"- {name}: {tool.description}")
        return "\n".join(lines)

    def process(self, user_input: str, confirm_fn=None) -> tuple[str, bool]:
        """
        Process a user message through the agent.

        Args:
            user_input:  The student's message
            confirm_fn:  Function to ask user permission — confirm_fn(action_desc) -> bool

        Returns:
            (response_text, used_tool: bool)
        """
        # Ask LLM whether to use a tool
        decision_prompt = AGENT_PROMPT.format(
            tool_list  = self._tool_list_str(),
            user_input = user_input,
        )

        decision = self.engine.generate(decision_prompt).strip()

        # ── Parse decision ────────────────────────────────────────────────
        tool_name, tool_input = self._parse_decision(decision)

        if not tool_name:
            # Direct answer — extract from decision
            direct = self._extract_direct(decision)
            return direct, False

        # ── Tool selected — ask permission ────────────────────────────────
        tool = self.tools.get(tool_name)
        if not tool:
            return f"[GESTURE:confused] I tried to use '{tool_name}' but it's not available.", False

        action_desc = f"Use tool '{tool_name}' with input: {tool_input or '(none)'}"

        if confirm_fn:
            allowed = confirm_fn(action_desc)
            if not allowed:
                return "[GESTURE:nodding] No problem, I won't do that. Ask me anything else!", False

        # ── Run tool ──────────────────────────────────────────────────────
        print(f"[Agent] Running tool: {tool_name} | Input: {tool_input}")
        tool_result = tool.safe_run(tool_input or "")

        print(f"[Agent] Tool result: {tool_result[:100]}")

        # ── Feed result back to LLM for final answer ──────────────────────
        answer_prompt = ANSWER_PROMPT.format(
            user_input  = user_input,
            tool_name   = tool_name,
            tool_result = tool_result,
        )

        final_answer = self.engine.generate(answer_prompt).strip()

        # Clean up if model echoed prompt
        if "ili:" in final_answer:
            final_answer = final_answer.split("ili:")[-1].strip()

        return final_answer, True

    def _parse_decision(self, decision: str) -> tuple[str, str]:
        """Extract tool_name and input from LLM decision."""
        tool_name  = None
        tool_input = ""

        lines = decision.strip().splitlines()
        for line in lines:
            line = line.strip()
            if line.upper().startswith("USE_TOOL:"):
                tool_name = line.split(":", 1)[1].strip().lower()
            elif line.upper().startswith("INPUT:"):
                tool_input = line.split(":", 1)[1].strip()

        return tool_name, tool_input

    def _extract_direct(self, decision: str) -> str:
        """Extract direct answer from LLM decision."""
        for line in decision.strip().splitlines():
            line = line.strip()
            if line.upper().startswith("DIRECT:"):
                return line.split(":", 1)[1].strip()

        # If format not followed, return the whole response
        # (clean up tool decision artifacts first)
        clean = re.sub(r"(USE_TOOL|INPUT|DIRECT):.*", "", decision, flags=re.IGNORECASE)
        return clean.strip() or "[GESTURE:talking] Let me help you with that!"