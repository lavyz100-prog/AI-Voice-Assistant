# system_control/screen_manager.py
"""
Screen Manager
==============
Handles screenshot capture and screen locking on Windows.

Screenshot : Uses Pillow (PIL) to capture the full screen and save to Desktop.
Lock Screen: Uses rundll32.exe user32.dll,LockWorkStation — no elevation needed.

Requires: pip install Pillow
"""

import os
import subprocess
import datetime

try:
    from PIL import ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# ─── Screenshot ───────────────────────────────────────────────────────────────

def _default_screenshot_path() -> str:
    """Build a timestamped filename on the user's Desktop."""
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    os.makedirs(desktop, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(desktop, f"screenshot_{ts}.png")


def take_screenshot(save_path: str = None) -> dict:
    """
    Capture the full screen and save it as a PNG file.

    Parameters
    ----------
    save_path : str | None
        Where to save the image. Defaults to Desktop with a timestamp filename.
    Voice: "Take a screenshot" / "Capture the screen" / "Screenshot"
    """
    if not PIL_AVAILABLE:
        return {
            "status": "ERROR",
            "message": "Pillow is not installed. Run: pip install Pillow",
        }
    try:
        path = save_path or _default_screenshot_path()
        screenshot = ImageGrab.grab()
        screenshot.save(path)

        filename = os.path.basename(path)
        return {
            "status": "SUCCESS",
            "message": f"Screenshot saved as '{filename}' on your Desktop.",
            "file_path": path,
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


# ─── Lock Screen ──────────────────────────────────────────────────────────────

def lock_screen() -> dict:
    """
    Lock the Windows workstation immediately.
    Equivalent to pressing Win + L.
    Voice: "Lock my computer" / "Lock the screen" / "Lock the PC"
    """
    try:
        result = subprocess.run(
            ["rundll32.exe", "user32.dll,LockWorkStation"],
            check=True, shell=False
        )
        return {
            "status": "SUCCESS",
            "message": "Screen locked. Goodbye!",
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


# ─── CLI Runner ───────────────────────────────────────────────────────────────
# Run individual functions directly from the terminal.
#
# Usage:
#   python screen_manager.py help
#   python screen_manager.py screenshot
#   python screen_manager.py screenshot C:\Users\JAYDIP\Desktop\my_shot.png
#   python screen_manager.py lock

if __name__ == "__main__":
    import sys

    TASKS = {
        "screenshot": "Capture the full screen and save to Desktop (or a custom path).",
        "lock":       "Lock the Windows screen immediately (Win+L equivalent).",
    }

    def _print_help():
        print("\n  screen_manager.py  -- Available tasks:")
        print("  " + "-" * 45)
        for name, desc in TASKS.items():
            print(f"  {name:<14} {desc}")
        print()
        print("  Examples:")
        print("    python screen_manager.py screenshot")
        print(r"    python screen_manager.py screenshot C:\Users\JAYDIP\Desktop\test.png")
        print("    python screen_manager.py lock")
        print()

    def _show(result: dict):
        status = result.get("status", "?")
        msg    = result.get("message", "")
        extra  = result.get("file_path", "")
        tag    = "[ OK ]" if status == "SUCCESS" else "[FAIL]"
        print(f"\n  {tag}  {msg}")
        if extra:
            print(f"  [PATH]  {extra}")
        print()

    args = sys.argv[1:]

    if not args or args[0].lower() in ("help", "--help", "-h"):
        _print_help()
        sys.exit(0)

    task = args[0].lower()

    if task == "screenshot":
        custom_path = args[1] if len(args) > 1 else None
        print(f"\n  [INFO]  Taking screenshot"
              f"{' -> ' + custom_path if custom_path else ' (saving to Desktop)'}...")
        _show(take_screenshot(save_path=custom_path))

    elif task == "lock":
        confirm = input(
            "\n  [WARN]  This will lock your screen immediately. "
            "Confirm? (yes/no): "
        ).strip().lower()
        if confirm in {"yes", "y", "ok", "confirm"}:
            _show(lock_screen())
        else:
            print("\n  [INFO]  Lock cancelled.\n")

    else:
        print(f"\n  [FAIL]  Unknown task: '{task}'")
        _print_help()
        sys.exit(1)
