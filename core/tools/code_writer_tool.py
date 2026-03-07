"""
Code Writer Tool
================
Generates code using the LLM and saves it to a file.

Input format: "filename.py | what the code should do"

Examples:
  "timer.py | countdown timer from 10 to 0"
  "sort.py | function that sorts a list of numbers"
  "hello.js | hello world in javascript"
"""

import os
import re
import subprocess
from .base_tool import BaseTool


# Supported extensions and their language names for the prompt
LANG_MAP = {
    ".py"   : "Python",
    ".js"   : "JavaScript",
    ".ts"   : "TypeScript",
    ".html" : "HTML",
    ".css"  : "CSS",
    ".java" : "Java",
    ".cpp"  : "C++",
    ".c"    : "C",
    ".sh"   : "Bash",
    ".json" : "JSON",
    ".sql"  : "SQL",
    ".md"   : "Markdown",
}

# Where to save generated files by default
DEFAULT_SAVE_DIR = os.path.join(os.path.expanduser("~"), "ili_generated")


class CodeWriterTool(BaseTool):
    name = "write_code"
    description = (
        "Generate code and save it to a file. "
        "Input format: 'filename.ext | description of what the code should do'. "
        "Example: 'timer.py | countdown timer from 10 to 0'"
    )

    # Will be injected by main.py or tutor so the tool can call the LLM
    engine = None

    def run(self, input_text: str) -> str:
        # ── Clean LLM junk ─────────────────────────────────────────────────────
        inp = re.sub(r'\s*[\(\[].*', '', input_text).strip()

        # ── Parse filename | description ───────────────────────────────────────
        if "|" not in inp:
            return (
                "Invalid input. Use: 'filename.ext | description'\n"
                "Example: 'timer.py | countdown from 10 to 0'"
            )

        parts      = inp.split("|", 1)
        filename   = parts[0].strip()
        description= parts[1].strip()

        if not filename or not description:
            return "Both filename and description are required."

        # ── Detect language ────────────────────────────────────────────────────
        ext      = os.path.splitext(filename)[1].lower()
        language = LANG_MAP.get(ext, "code")

        # ── Generate code via LLM ──────────────────────────────────────────────
        if self.engine is None:
            return "Error: CodeWriterTool has no engine attached. Set CodeWriterTool.engine in main.py."

        prompt = (
            f"Write {language} code for the following task:\n"
            f"{description}\n\n"
            f"Rules:\n"
            f"- Output ONLY the raw code, nothing else\n"
            f"- No explanation, no markdown, no backticks\n"
            f"- No comments unless they help understand the code\n"
            f"- The code must be complete and runnable\n"
            f"- Filename will be: {filename}"
        )

        try:
            raw = self.engine.generate(prompt).strip()
        except Exception as e:
            return f"Error generating code: {e}"

        # ── Strip markdown fences if model ignored instructions ────────────────
        code = self._strip_fences(raw)

        if not code:
            return "Error: LLM returned empty code."

        # ── Save to file ───────────────────────────────────────────────────────
        save_dir = DEFAULT_SAVE_DIR
        os.makedirs(save_dir, exist_ok=True)
        filepath = os.path.join(save_dir, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code)
        except Exception as e:
            return f"Code generated but failed to save: {e}\n\nGenerated code:\n{code}"

        lines = code.count("\n") + 1

        # ── Open in Notepad ────────────────────────────────────────────────────
        try:
            subprocess.Popen(["notepad.exe", filepath])
        except Exception:
            pass  # Silently skip if notepad isn't available

        return (
            f"✅ Code written and saved!\n"
            f"📄 File: {filepath}\n"
            f"📏 {lines} lines of {language}\n\n"
            f"Preview (first 20 lines):\n"
            f"{self._preview(code, 20)}"
        )

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _strip_fences(self, text: str) -> str:
        """Remove markdown code fences like ```python ... ```"""
        # Remove opening fence with optional language tag
        text = re.sub(r'^```[a-zA-Z]*\n?', '', text.strip())
        # Remove closing fence
        text = re.sub(r'\n?```$', '', text.strip())
        return text.strip()

    def _preview(self, code: str, max_lines: int) -> str:
        lines = code.splitlines()
        if len(lines) <= max_lines:
            return code
        return "\n".join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} more lines)"