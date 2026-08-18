# system_control/device_info_manager.py
"""
Device Info Manager
===================
Reads hardware status: battery, CPU usage, and disk space.
Memory/RAM queries are handled separately by memory_manager.py.

Requires: pip install psutil
"""

import psutil
import platform


def get_battery() -> dict:
    """
    Read the current battery level and charging status.
    Returns an error message on desktop PCs that have no battery.
    """
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            return {
                "status": "ERROR",
                "message": "No battery detected. This device may be a desktop PC.",
            }
        percent = int(battery.percent)
        plugged = battery.power_plugged

        if plugged:
            status_str = "plugged in and charging" if percent < 100 else "fully charged"
        else:
            # Estimate time remaining
            secs = battery.secsleft
            if secs == psutil.POWER_TIME_UNKNOWN or secs < 0:
                time_str = "remaining time unknown"
            else:
                hours, rem = divmod(secs, 3600)
                mins = rem // 60
                time_str = (
                    f"about {hours}h {mins}m remaining"
                    if hours else f"about {mins} minutes remaining"
                )
            status_str = f"on battery — {time_str}"

        return {
            "status": "SUCCESS",
            "message": f"Battery is at {percent}%, {status_str}.",
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


def get_cpu_usage() -> dict:
    """
    Read current CPU utilisation (1-second sample across all cores).
    """
    try:
        # interval=1 gives a 1-second measurement window (more accurate)
        usage = psutil.cpu_percent(interval=1)
        core_count = psutil.cpu_count(logical=True)
        freq = psutil.cpu_freq()

        freq_str = ""
        if freq:
            freq_str = f" running at {freq.current:.0f} MHz"

        msg = (
            f"CPU usage is {usage:.1f}% "
            f"across {core_count} logical core{'s' if core_count != 1 else ''}"
            f"{freq_str}."
        )
        return {"status": "SUCCESS", "message": msg}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


def get_disk_space(drive: str = "C") -> dict:
    """
    Read free and total disk space for the specified drive.

    Parameters
    ----------
    drive : str  Drive letter (default 'C'). Case-insensitive.
    """
    try:
        drive = drive.upper().rstrip(":\\") + ":\\"
        usage = psutil.disk_usage(drive)

        total_gb = usage.total / (1024 ** 3)
        used_gb  = usage.used  / (1024 ** 3)
        free_gb  = usage.free  / (1024 ** 3)
        pct_used = usage.percent

        msg = (
            f"Drive {drive[0]}: has {free_gb:.1f} GB free out of "
            f"{total_gb:.1f} GB total ({pct_used:.0f}% used)."
        )
        return {"status": "SUCCESS", "message": msg}
    except FileNotFoundError:
        return {
            "status": "ERROR",
            "message": f"Drive {drive[0]}: was not found on this system.",
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}
