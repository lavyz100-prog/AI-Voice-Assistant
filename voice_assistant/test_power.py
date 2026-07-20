"""
test_power.py
=============
Tests SYSTEM_SHUTDOWN, SYSTEM_RESTART, SYSTEM_SLEEP safely:

  Phase 1 - Safety Gate  : Confirms every power command is blocked without is_confirmed=True.
  Phase 2 - Warning Text : Confirms the spoken warning message is correct.
  Phase 3 - Dry Run      : Calls the real cancel_shutdown (harmless if no shutdown is pending).

  ** The actual shutdown / restart / sleep functions are NEVER called. **
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from system_control import SystemController
from system_control.safety_guard import is_dangerous, get_warning_message

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

results = []

def check(name, condition, note=""):
    icon = f"{GREEN}PASS{RESET}" if condition else f"{RED}FAIL{RESET}"
    print(f"  [{icon}] {name}" + (f"\n         {note}" if note else ""))
    results.append((name, condition))

sc = SystemController()

print(f"\n{BOLD}{CYAN}=============================={RESET}")
print(f"{BOLD}{CYAN}  Power Commands - Test Suite{RESET}")
print(f"{BOLD}{CYAN}=============================={RESET}\n")

# ─── Phase 1: Safety Gate ────────────────────────────────────────────────────
print(f"{BOLD}[Phase 1]  Safety Gate (no confirmation){RESET}")

for intent, params in [
    ("SYSTEM_SHUTDOWN", {"delay_seconds": 0}),
    ("SYSTEM_RESTART",  {"delay_seconds": 0}),
    ("SYSTEM_SLEEP",    {}),
]:
    result = sc.execute_task(intent, params, is_confirmed=False)
    check(
        f"{intent} blocked without confirmation",
        result["status"] == "REQUIRES_CONFIRMATION",
        f"status={result['status']}"
    )
    check(
        f"{intent} returns pending_intent",
        result.get("pending_intent") == intent,
    )
    check(
        f"{intent} returns pending_parameters",
        result.get("pending_parameters") == params,
    )

# ─── Phase 2: Warning Text ───────────────────────────────────────────────────
print(f"\n{BOLD}[Phase 2]  Warning Messages{RESET}")

cases = {
    "SYSTEM_SHUTDOWN": "shut down",
    "SYSTEM_RESTART":  "restart",
    "SYSTEM_SLEEP":    "sleep",
}
for intent, keyword in cases.items():
    msg = get_warning_message(intent, {}).lower()
    check(
        f"{intent} warning contains '{keyword}'",
        keyword in msg,
        f"Message: {msg.strip()}"
    )

check("is_dangerous(SYSTEM_SHUTDOWN) = True",  is_dangerous("SYSTEM_SHUTDOWN"))
check("is_dangerous(SYSTEM_RESTART)  = True",  is_dangerous("SYSTEM_RESTART"))
check("is_dangerous(SYSTEM_SLEEP)    = True",  is_dangerous("SYSTEM_SLEEP"))
check("is_dangerous(ADJUST_VOLUME)   = False", not is_dangerous("ADJUST_VOLUME"))

# ─── Phase 3: cancel_shutdown (real, but harmless) ───────────────────────────
print(f"\n{BOLD}[Phase 3]  cancel_shutdown (real call — safe if no shutdown pending){RESET}")

from system_control import power_manager
result = power_manager.cancel_shutdown()

# Windows returns an error if there's nothing to cancel — that's expected & fine
harmless = result["status"] in ("SUCCESS", "ERROR")
check(
    "cancel_shutdown runs without crashing",
    harmless,
    f"status={result['status']}  msg={result['message']}"
)

# ─── Summary ─────────────────────────────────────────────────────────────────
total  = len(results)
passed = sum(1 for _, ok in results if ok)
failed = total - passed

print(f"\n{BOLD}{CYAN}=============================={RESET}")
print(f"{BOLD}  {GREEN}{passed} passed{RESET}  |  "
      f"{(RED if failed else GREEN)}{failed} failed{RESET}  |  {total} total")
print(f"{BOLD}{CYAN}=============================={RESET}\n")

if failed:
    print(f"{RED}Some tests failed - see details above.{RESET}\n")
    sys.exit(1)
else:
    print(f"{GREEN}All power-command tests passed! Your machine is safe. [OK]{RESET}\n")
