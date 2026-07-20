"""
live_demo.py
============
Interactive live demo - commands ACTUALLY execute on your PC.

  - Shutdown / Restart  -> 30-second delay so you can cancel
  - Sleep               -> immediate
  - Cancel Shutdown     -> aborts any pending countdown
  - Volume Up/Down/Mute -> real audio changes
"""

import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from system_control import SystemController

# ─── Simple coloured print (ASCII only, no special chars) ────────────────────
def banner(text):
    line = "=" * 50
    print(f"\n{line}")
    print(f"  {text}")
    print(f"{line}")

def info(text):  print(f"  [INFO]  {text}")
def warn(text):  print(f"  [WARN]  {text}")
def ok(text):    print(f"  [ OK ]  {text}")
def err(text):   print(f"  [FAIL]  {text}")

# ─── Confirmation helper ──────────────────────────────────────────────────────
YES = {"yes", "y", "yeah", "yep", "ok", "okay", "confirm", "sure", "do it"}
NO  = {"no", "n", "nope", "cancel", "stop", "abort", "never mind"}

def confirm(prompt="Are you sure? (yes/no): ") -> bool:
    while True:
        reply = input(f"\n  >> {prompt}").strip().lower()
        if reply in YES: return True
        if reply in NO:  return False
        print("  Please type yes or no.")

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    sc = SystemController()

    banner("Voice Assistant - Live System Demo")
    print("""
  Commands you can type:
  -----------------------------------------------
  shutdown        -> Shut down PC (30s delay)
  restart         -> Restart PC   (30s delay)
  sleep           -> Sleep PC immediately
  cancel          -> Cancel a pending shutdown/restart
  volume up       -> Increase volume by 10%
  volume down     -> Decrease volume by 10%
  mute            -> Mute audio
  unmute          -> Unmute audio
  exit            -> Quit this demo
  -----------------------------------------------
""")

    while True:
        try:
            cmd = input("  You: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n  Exiting.")
            break

        if not cmd:
            continue

        # ── Exit ─────────────────────────────────────────────────────────────
        if cmd in ("exit", "quit", "bye"):
            ok("Goodbye!")
            break

        # ── Map command to intent + params ────────────────────────────────────
        if cmd == "shutdown":
            intent, params = "SYSTEM_SHUTDOWN", {"delay_seconds": 30}
        elif cmd == "restart":
            intent, params = "SYSTEM_RESTART",  {"delay_seconds": 30}
        elif cmd == "sleep":
            intent, params = "SYSTEM_SLEEP",    {}
        elif cmd in ("cancel", "cancel shutdown"):
            intent, params = "CANCEL_SHUTDOWN", {}
        elif cmd == "volume up":
            intent, params = "ADJUST_VOLUME",   {"percentage_change": 10}
        elif cmd == "volume down":
            intent, params = "ADJUST_VOLUME",   {"percentage_change": -10}
        elif cmd == "mute":
            intent, params = "MUTE_VOLUME",     {}
        elif cmd == "unmute":
            intent, params = "UNMUTE_VOLUME",   {}
        else:
            warn(f"Unknown command: '{cmd}'")
            continue

        # ── Step 1: First pass (may hit safety gate) ──────────────────────────
        result = sc.execute_task(intent, params, is_confirmed=False)

        if result["status"] == "REQUIRES_CONFIRMATION":
            # Print the warning and ask for real confirmation in the terminal
            print(f"\n  [!] {result['message']}")
            agreed = confirm()

            if agreed:
                if intent in ("SYSTEM_SHUTDOWN", "SYSTEM_RESTART"):
                    info("Starting 30-second countdown. Type 'cancel' then Enter to abort!")
                result = sc.execute_task(
                    result["pending_intent"],
                    result["pending_parameters"],
                    is_confirmed=True,
                )
            else:
                ok("Cancelled. Nothing happened.")
                continue

        # ── Step 2: Show result ───────────────────────────────────────────────
        if result["status"] == "SUCCESS":
            ok(result["message"])
        elif result["status"] == "ERROR":
            err(result["message"])
        elif result["status"] == "UNKNOWN_INTENT":
            warn(result["message"])

if __name__ == "__main__":
    main()
