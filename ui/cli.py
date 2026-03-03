import sys
import threading
import time
from core.modes import list_modes, MODES, get_mode


BANNER = """
╔══════════════════════════════════════════════╗
║         ili — Interactive Learning           ║
║              Intelligence                    ║
╚══════════════════════════════════════════════╝
"""

HELP_TEXT = """
Commands:
  /mode <name>  → Switch subject mode (e.g. /mode math)
  /modes        → List all available modes
  /reset        → Clear conversation memory
  /engine       → Show current engine
  /avatar       → Show avatar status
  /help         → Show this help
  /quit         → Exit ili
"""


def print_banner(engine_name: str, mode_name: str, voice_output: bool = False):
    print(BANNER)
    mode = get_mode(mode_name)
    print(f"  Engine : {engine_name.upper()}")
    print(f"  Mode   : {mode.emoji} {mode.name}")
    print(f"  Voice  : {'ON' if voice_output else 'OFF'}")
    print(f"  Type /help for commands\n")
    print("─" * 50)


def pick_mode_on_startup() -> str:
    """Show mode menu and let user pick on startup."""
    print("\n🎓 What would you like to do today?\n")

    mode_list = list(MODES.items())
    for i, (key, mode) in enumerate(mode_list, 1):
        print(f"  [{i}] {mode.emoji}  {mode.name:<12} — {mode.description}")

    print()
    while True:
        try:
            raw = input("  Choose a mode [1-7] or press Enter for General: ").strip()
            if not raw:
                return "general"
            val = int(raw)
            if 1 <= val <= len(mode_list):
                chosen_key = mode_list[val - 1][0]
                return chosen_key
            print(f"  Please enter a number between 1 and {len(mode_list)}")
        except (ValueError, EOFError):
            return "general"


def get_user_input(voice_mode: bool = False) -> str:
    if voice_mode:
        from voice.speech_to_text import listen
        return listen()
    try:
        return input("\nYou: ").strip()
    except (EOFError, KeyboardInterrupt):
        return "/quit"


def speak_response(response: str, avatar=None):
    from voice.text_to_speech import speak
    speak(
        response,
        on_start=avatar.start_talking if avatar else None,
        on_stop=avatar.stop_talking  if avatar else None,
        blocking=True,
    )


def animate_text_mode(response: str, avatar):
    def _fake():
        avatar.start_talking()
        duration = max(len(response.split()) * 0.05, 1.0)
        time.sleep(min(duration, 6.0))
        avatar.stop_talking()
    threading.Thread(target=_fake, daemon=True).start()


def run_cli(
    tutor,
    engine_name:  str,
    voice_mode:   bool = False,
    voice_output: bool = False,
    avatar=None,
    initial_mode: str  = "general",
):
    # ── Show welcome message for chosen mode ──────────────────────────────
    mode      = get_mode(initial_mode)
    print_banner(engine_name, initial_mode, voice_output)
    print(f"\n{mode.emoji} {mode.welcome}\n")

    while True:
        user_input = get_user_input(voice_mode)

        if not user_input:
            continue

        cmd = user_input.lower().strip()

        # ── Commands ──────────────────────────────────────────────────────

        if cmd == "/quit":
            print("\n👋 See you next time! Keep learning! 🌟\n")
            sys.exit(0)

        elif cmd == "/reset":
            tutor.reset()
            print("🔄 Memory cleared. Fresh start!\n")
            continue

        elif cmd == "/modes":
            print(list_modes())
            continue

        elif cmd.startswith("/mode"):
            parts = cmd.split()
            if len(parts) < 2:
                print(list_modes())
            else:
                mode_name = parts[1].lower()
                if mode_name in MODES:
                    msg = tutor.set_mode(mode_name)
                    new_mode = get_mode(mode_name)
                    print(f"\n{msg}\n")
                    print("─" * 50)
                else:
                    print(f"\n  Unknown mode '{mode_name}'.{list_modes()}")
            continue

        elif cmd == "/engine":
            print(f"\n  Active engine : {engine_name.upper()}")
            print(f"  Active mode   : {tutor.current_mode.emoji} {tutor.current_mode.name}\n")
            continue

        elif cmd == "/help":
            print(HELP_TEXT)
            print(list_modes())
            continue

        elif cmd == "/avatar":
            if avatar:
                print("  Avatar is running. Drag to move, ESC to close.\n")
            else:
                print("  Avatar not running. Restart with --avatar flag.\n")
            continue

        # ── Normal conversation ───────────────────────────────────────────

        if avatar:
            avatar.start_thinking()

        print(f"\n{tutor.current_mode.emoji} ili: ", end="", flush=True)

        response = tutor.ask(user_input, avatar=avatar)

        if avatar:
            avatar.stop_thinking()

        print(response)

        if voice_mode or voice_output:
            speak_response(response, avatar)
        elif avatar:
            animate_text_mode(response, avatar)

        print()