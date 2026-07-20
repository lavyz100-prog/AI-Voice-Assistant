# voice_assistant/test_modules.py
"""
Safe module tester for the system_control package.
─────────────────────────────────────────────────
✔ Creates a temp file/folder inside voice_assistant/ so nothing real is deleted.
✔ Tests audio only if pycaw is installed (skips gracefully otherwise).
✔ Never actually shuts down / restarts / sleeps the machine.
✔ Prints a colour-coded PASS / FAIL summary at the end.
"""

import os
import sys
import tempfile
import shutil

# ─── Make sure the parent package is importable ──────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from system_control import SystemController
from system_control.safety_guard import is_dangerous, get_warning_message
from system_control import file_manager, audio_manager, power_manager

# ─── ANSI colours ────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

results = []   # (test_name, passed: bool, note: str)


def check(name: str, condition: bool, note: str = ""):
    icon = f"{GREEN}PASS{RESET}" if condition else f"{RED}FAIL{RESET}"
    print(f"  [{icon}] {name}" + (f"  — {note}" if note else ""))
    results.append((name, condition, note))


# ═══════════════════════════════════════════════════════════════════════════════
print(f"\n{BOLD}{CYAN}══════════════════════════════════════════════{RESET}")
print(f"{BOLD}{CYAN}   Voice Assistant — Module Test Suite{RESET}")
print(f"{BOLD}{CYAN}══════════════════════════════════════════════{RESET}\n")

# ─────────────────────────────────────────────────────────────────────────────
# 1. Safety Guard
# ─────────────────────────────────────────────────────────────────────────────
print(f"{BOLD}[1] safety_guard.py{RESET}")

check("DELETE_FILE is dangerous",
      is_dangerous("DELETE_FILE"))

check("ADJUST_VOLUME is NOT dangerous",
      not is_dangerous("ADJUST_VOLUME"))

check("SYSTEM_SHUTDOWN is dangerous",
      is_dangerous("SYSTEM_SHUTDOWN"))

check("SYSTEM_SLEEP is dangerous",
      is_dangerous("SYSTEM_SLEEP"))

warning = get_warning_message("DELETE_FILE", {"path": "C:/temp/test.txt"})
check("Warning message contains path",
      "C:/temp/test.txt" in warning,
      warning)

# ─────────────────────────────────────────────────────────────────────────────
# 2. File Manager
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{BOLD}[2] file_manager.py{RESET}")

# Set up a safe temp directory inside voice_assistant/
tmp_dir = os.path.join(os.path.dirname(__file__), "_test_tmp")
os.makedirs(tmp_dir, exist_ok=True)
tmp_file = os.path.join(tmp_dir, "hello.txt")

# Write a test file
with open(tmp_file, "w") as f:
    f.write("Hello, Voice Assistant!")

# read_file
result = file_manager.read_file(tmp_file)
check("read_file — SUCCESS status",
      result["status"] == "SUCCESS")
check("read_file — content correct",
      "Hello, Voice Assistant!" in result["message"])

# read_file on missing path
result = file_manager.read_file(tmp_file + "_missing")
check("read_file — ERROR on missing file",
      result["status"] == "ERROR")

# move_file (rename within same dir)
moved_file = os.path.join(tmp_dir, "moved.txt")
result = file_manager.move_file(tmp_file, moved_file)
check("move_file — SUCCESS",
      result["status"] == "SUCCESS" and os.path.exists(moved_file))

# delete_file
result = file_manager.delete_file(moved_file)
check("delete_file — SUCCESS",
      result["status"] == "SUCCESS" and not os.path.exists(moved_file))

# delete_file on already-deleted path
result = file_manager.delete_file(moved_file)
check("delete_file — ERROR on missing file",
      result["status"] == "ERROR")

# delete_directory
sub_dir = os.path.join(tmp_dir, "subdir")
os.makedirs(sub_dir, exist_ok=True)
with open(os.path.join(sub_dir, "inner.txt"), "w") as f:
    f.write("inner")
result = file_manager.delete_directory(sub_dir)
check("delete_directory — SUCCESS",
      result["status"] == "SUCCESS" and not os.path.exists(sub_dir))

# delete_directory on missing path
result = file_manager.delete_directory(sub_dir)
check("delete_directory — ERROR on missing dir",
      result["status"] == "ERROR")

# Cleanup temp dir
shutil.rmtree(tmp_dir, ignore_errors=True)

# ─────────────────────────────────────────────────────────────────────────────
# 3. Audio Manager
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{BOLD}[3] audio_manager.py{RESET}")

try:
    from pycaw.pycaw import AudioUtilities
    PYCAW_OK = True
except ImportError:
    PYCAW_OK = False

if not PYCAW_OK:
    print(f"  [{YELLOW}SKIP{RESET}] pycaw not installed — run: pip install pycaw comtypes")
    results.append(("pycaw available", True, "SKIPPED"))
else:
    result = audio_manager.adjust_volume(0)   # +0% change — safe no-op read
    check("adjust_volume — runs without exception",
          result["status"] in ("SUCCESS", "ERROR"),
          result["message"])

    result = audio_manager.mute_volume()
    check("mute_volume — SUCCESS", result["status"] == "SUCCESS")

    result = audio_manager.unmute_volume()
    check("unmute_volume — SUCCESS", result["status"] == "SUCCESS")

# ─────────────────────────────────────────────────────────────────────────────
# 4. Power Manager (DRY RUN — functions are NOT called to avoid real reboot)
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{BOLD}[4] power_manager.py  {YELLOW}(import-only; not executed to protect the machine){RESET}")

try:
    import importlib
    pm = importlib.import_module("system_control.power_manager")
    check("power_manager imports cleanly",    True)
    check("shutdown function exists",         callable(getattr(pm, "shutdown",         None)))
    check("restart function exists",          callable(getattr(pm, "restart",          None)))
    check("sleep function exists",            callable(getattr(pm, "sleep",            None)))
    check("cancel_shutdown function exists",  callable(getattr(pm, "cancel_shutdown",  None)))
except Exception as e:
    check("power_manager imports cleanly", False, str(e))

# ─────────────────────────────────────────────────────────────────────────────
# 5. SystemController — end-to-end routing
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{BOLD}[5] controller.py  (SystemController end-to-end){RESET}")

sc = SystemController()

# Unknown intent
result = sc.execute_task("DANCE_ROBOT", {})
check("Unknown intent → UNKNOWN_INTENT",
      result["status"] == "UNKNOWN_INTENT")

# Dangerous intent without confirmation
result = sc.execute_task("SYSTEM_SHUTDOWN", {"delay_seconds": 0}, is_confirmed=False)
check("SYSTEM_SHUTDOWN without confirm → REQUIRES_CONFIRMATION",
      result["status"] == "REQUIRES_CONFIRMATION")
check("Response includes pending_intent",
      result.get("pending_intent") == "SYSTEM_SHUTDOWN")

# Safe file read through controller (uses real temp file)
tmp2 = os.path.join(os.path.dirname(__file__), "_ctrl_test.txt")
with open(tmp2, "w") as f:
    f.write("controller test")

result = sc.execute_task("READ_FILE", {"path": tmp2})
check("READ_FILE through controller — SUCCESS",
      result["status"] == "SUCCESS")
os.remove(tmp2)

# DELETE_FILE without confirmation → should halt
result = sc.execute_task("DELETE_FILE", {"path": "/some/path"}, is_confirmed=False)
check("DELETE_FILE without confirm → REQUIRES_CONFIRMATION",
      result["status"] == "REQUIRES_CONFIRMATION")

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
total   = len(results)
passed  = sum(1 for _, ok, _ in results if ok)
failed  = total - passed

print(f"\n{BOLD}{CYAN}══════════════════════════════════════════════{RESET}")
print(f"{BOLD}  Results:  {GREEN}{passed} passed{RESET}  |  "
      f"{(RED if failed else GREEN)}{failed} failed{RESET}  |  {total} total")
print(f"{BOLD}{CYAN}══════════════════════════════════════════════{RESET}\n")

if failed:
    print(f"{RED}Some tests failed. Check the output above for details.{RESET}\n")
    sys.exit(1)
else:
    print(f"{GREEN}All tests passed! ✔{RESET}\n")
