# system_control/display_manager.py
"""
Display Manager
===============
Controls screen brightness and Night Light on Windows.

Brightness:
  - Uses WMI (Win32_MonitorBrightnessMethods) — works on laptops / built-in displays.
  - Falls back to a clear error message for external monitors unsupported by WMI.

Night Light:
  - Toggles via Windows registry (HKCU CloudStore key) + broadcasts WM_SETTINGCHANGE.
"""

import subprocess
import struct
import winreg
import ctypes


# ─── Brightness helpers ────────────────────────────────────────────────────────

def _get_current_brightness() -> int | None:
    """Return current brightness 0-100 via WMI, or None if unsupported."""
    try:
        ps = (
            "Get-WmiObject -Namespace root/WMI "
            "-Class WmiMonitorBrightness | "
            "Select-Object -ExpandProperty CurrentBrightness"
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps],
            capture_output=True, text=True
        )
        value = result.stdout.strip()
        return int(value) if value.isdigit() else None
    except Exception:
        return None


def _set_brightness_wmi(level: int) -> bool:
    """Set brightness via WMI. Returns True on success."""
    try:
        ps = (
            f"(Get-WmiObject -Namespace root/WMI "
            f"-Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})"
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps],
            capture_output=True, text=True
        )
        return result.returncode == 0
    except Exception:
        return False


# ─── Public Functions ──────────────────────────────────────────────────────────

def set_brightness(level: int) -> dict:
    """
    Set screen brightness to an absolute level (0–100).

    Parameters
    ----------
    level : int  Target brightness percentage (0–100).
    """
    level = max(0, min(100, level))
    ok = _set_brightness_wmi(level)
    if ok:
        return {
            "status": "SUCCESS",
            "message": f"Screen brightness set to {level}%.",
        }
    return {
        "status": "ERROR",
        "message": (
            "Could not change brightness. This feature works on laptops and "
            "built-in displays. External monitors may not be supported."
        ),
    }


def adjust_brightness(change: int) -> dict:
    """
    Increase or decrease brightness by a relative amount.

    Parameters
    ----------
    change : int  Positive to increase, negative to decrease (percent).
    """
    current = _get_current_brightness()
    if current is None:
        return {
            "status": "ERROR",
            "message": (
                "Cannot read current brightness. "
                "WMI brightness may not be supported on this display."
            ),
        }
    new_level = max(0, min(100, current + change))
    return set_brightness(new_level)


def toggle_night_light() -> dict:
    """
    Toggle Windows Night Light on/off via the registry.
    Works on Windows 10 build 1703+ and Windows 11.
    """
    # Registry path used by the Night Light CloudStore entry
    REG_PATH = (
        r"Software\Microsoft\Windows\CurrentVersion\CloudStore\Store"
        r"\DefaultAccount\Current\default$windows.data.bluelightreduction.bluelightreductionstate"
        r"\windows.data.bluelightreduction.bluelightreductionstate"
    )
    VALUE_NAME = "Data"

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, REG_PATH,
            0, winreg.KEY_READ | winreg.KEY_WRITE
        )
        data, _ = winreg.QueryValueEx(key, VALUE_NAME)

        # Byte 18 is the on/off toggle byte: 0x13 = ON, 0x10 = OFF
        # Convert bytes to bytearray for mutability
        ba = bytearray(data)
        if len(ba) > 18:
            if ba[18] == 0x13:
                ba[18] = 0x10  # Turn OFF
                state = "off"
            else:
                ba[18] = 0x13  # Turn ON
                state = "on"
            winreg.SetValueEx(key, VALUE_NAME, 0, winreg.REG_BINARY, bytes(ba))
            winreg.CloseKey(key)

            # Signal Windows to pick up the change
            ctypes.windll.user32.SendMessageTimeoutW(
                0xFFFF, 0x001A, 0, "ImmersiveColorSet", 0, 100, None
            )
            return {
                "status": "SUCCESS",
                "message": f"Night Light turned {state}.",
            }
        winreg.CloseKey(key)
        return {
            "status": "ERROR",
            "message": "Night Light registry data has unexpected format.",
        }
    except FileNotFoundError:
        return {
            "status": "ERROR",
            "message": (
                "Night Light registry key not found. "
                "Make sure Night Light has been opened at least once in Windows Settings."
            ),
        }
    except Exception as e:
        return {"status": "ERROR", "message": f"Night Light toggle failed: {e}"}
