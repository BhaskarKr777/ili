"""
ili — Interactive Learning Intelligence
========================================

Usage:
    python main.py                              # pick mode on startup
    python main.py --mode math                  # start directly in math mode
    python main.py --mode friend                # just chat
    python main.py --voice-out                  # text input + spoken output
    python main.py --avatar                     # show floating avatar
    python main.py --engine local --voice-out --avatar --mode coding
"""

import argparse
import sys
import os
import threading

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.engine_router import get_engine, SUPPORTED_ENGINES
from core.tutor import Tutor
from core.memory import Memory
from core.modes import MODE_KEYS
from ui.cli import run_cli, pick_mode_on_startup


def parse_args():
    parser = argparse.ArgumentParser(description="ili — Interactive Learning Intelligence")
    parser.add_argument("--engine",    type=str, default="local", choices=SUPPORTED_ENGINES)
    parser.add_argument("--mode",      type=str, default=None,    choices=MODE_KEYS,
                        help="Subject mode: general, math, science, coding, language, history, friend")
    parser.add_argument("--voice",     action="store_true", help="Mic input + voice output")
    parser.add_argument("--voice-in",  action="store_true", help="Mic input only")
    parser.add_argument("--voice-out", action="store_true", help="Voice output only")
    parser.add_argument("--avatar",    action="store_true", help="Show avatar window")
    parser.add_argument("--name",      type=str, default=None,    help="Your name")
    parser.add_argument("--model",     type=str, default=None,    help="Override LLM model")
    return parser.parse_args()


def check_engine(engine, engine_name: str):
    if engine.is_available():
        return
    print(f"\n⚠  {engine_name.upper()} engine may not be ready:")
    if engine_name == "local":
        print("   • ollama serve")
        print("   • ollama pull phi3.5")
    else:
        print(f"   • Set {engine_name.upper()}_API_KEY in .env")
    print()


def main():
    args = parse_args()

    voice_mode   = args.voice or args.voice_in
    voice_output = args.voice or args.voice_out

    # ── Engine ───────────────────────────────────────────────────────────
    try:
        engine = get_engine(args.engine)
    except ValueError as e:
        print(f"\n❌ {e}\n")
        sys.exit(1)

    check_engine(engine, args.engine)

    # ── Memory ───────────────────────────────────────────────────────────
    memory = Memory(max_turns=10)
    if args.name:
        memory.set_student_name(args.name)
    memory.startup(engine_name=args.engine)

    # ── Mode selection ────────────────────────────────────────────────────
    # If --mode flag given, skip menu. Otherwise show startup picker.
    if args.mode:
        initial_mode = args.mode
    else:
        initial_mode = pick_mode_on_startup()

    # ── Tutor ────────────────────────────────────────────────────────────
    tutor = Tutor(engine=engine, memory=memory, mode=initial_mode)

    # ── Avatar ───────────────────────────────────────────────────────────
    if args.avatar:
        from avatar.avatar_window import AvatarWindow
        avatar = AvatarWindow()

        cli_thread = threading.Thread(
            target=run_cli,
            kwargs={
                "tutor":        tutor,
                "engine_name":  args.engine,
                "voice_mode":   voice_mode,
                "voice_output": voice_output,
                "avatar":       avatar,
                "initial_mode": initial_mode,
            },
            daemon=True,
        )
        cli_thread.start()
        avatar.launch()

    else:
        run_cli(
            tutor=tutor,
            engine_name=args.engine,
            voice_mode=voice_mode,
            voice_output=voice_output,
            avatar=None,
            initial_mode=initial_mode,
        )


if __name__ == "__main__":
    main()