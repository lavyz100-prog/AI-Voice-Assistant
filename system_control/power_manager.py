# system_control/power_manager.py

import subprocess


def shutdown(delay_seconds: int = 0) -> dict:
    """Schedule a Windows system shutdown."""
    try:
        subprocess.run(
            ["shutdown", "/s", "/t", str(delay_seconds)],
            check=True,
            shell=True,
        )
        return {
            "status": "SUCCESS",
            "message": f"System will shut down in {delay_seconds} second(s).",
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


def restart(delay_seconds: int = 0) -> dict:
    """Schedule a Windows system restart."""
    try:
        subprocess.run(
            ["shutdown", "/r", "/t", str(delay_seconds)],
            check=True,
            shell=True,
        )
        return {
            "status": "SUCCESS",
            "message": f"System will restart in {delay_seconds} second(s).",
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


def sleep() -> dict:
    """Put the Windows system to sleep immediately."""
    try:
        subprocess.run(
            ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"],
            check=True,
            shell=True,
        )
        return {"status": "SUCCESS", "message": "System is going to sleep."}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


def cancel_shutdown() -> dict:
    """Cancel a previously scheduled shutdown or restart."""
    try:
        subprocess.run(["shutdown", "/a"], check=True, shell=True)
        return {"status": "SUCCESS", "message": "Scheduled shutdown/restart cancelled."}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}
