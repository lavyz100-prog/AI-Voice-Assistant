# system_control/app_manager.py
"""
Application Manager
===================
Launches common Windows applications by a friendly name.
The NLP layer normalises the app name before calling open_app().
"""

import subprocess
import shutil


# ─── App name → launch command map ────────────────────────────────────────────
# Each value is a list passed to subprocess.Popen / subprocess.run.
# We use 'start' shell built-in for UWP / ms-settings apps.

_APP_MAP: dict[str, list[str]] = {
    # System tools
    "task manager":      ["taskmgr"],
    "taskmgr":           ["taskmgr"],
    "settings":          ["ms-settings:"],          # UWP — needs shell=True
    "control panel":     ["control"],
    "control":           ["control"],
    "file explorer":     ["explorer"],
    "explorer":          ["explorer"],
    "device manager":    ["devmgmt.msc"],
    "disk management":   ["diskmgmt.msc"],
    "event viewer":      ["eventvwr.msc"],
    "registry editor":   ["regedit"],
    "command prompt":    ["cmd"],
    "cmd":               ["cmd"],
    "powershell":        ["powershell"],
    "run":               ["cmd", "/c", "start", "run"],

    # Accessories
    "notepad":           ["notepad"],
    "calculator":        ["calc"],
    "calc":              ["calc"],
    "paint":             ["mspaint"],
    "snipping tool":     ["SnippingTool"],
    "wordpad":           ["wordpad"],
    "character map":     ["charmap"],
    "magnifier":         ["magnify"],
    "on-screen keyboard":["osk"],
    "narrator":          ["narrator"],

    # Browsers (launched only if installed)
    "chrome":            ["chrome"],
    "google chrome":     ["chrome"],
    "edge":              ["msedge"],
    "microsoft edge":    ["msedge"],
    "firefox":           ["firefox"],
    "brave":             ["brave"],

    # Communication / productivity
    "notepad++":         ["notepad++"],
    "vs code":           ["code"],
    "visual studio code":["code"],
}

# Apps that need `shell=True` to resolve (ms-settings:, etc.)
_SHELL_REQUIRED = {"ms-settings:"}


def open_app(app_name: str) -> dict:
    """
    Launch an application by friendly name.

    Parameters
    ----------
    app_name : str
        Normalised app name (e.g. 'task manager', 'settings', 'chrome').
    """
    key = app_name.strip().lower()
    cmd = _APP_MAP.get(key)

    if cmd is None:
        # Last-resort: try launching the raw name directly
        cmd = [app_name]

    exe = cmd[0]
    use_shell = exe in _SHELL_REQUIRED

    try:
        if use_shell:
            subprocess.Popen(f"start {exe}", shell=True)
        else:
            # Check if the executable is findable (for installed third-party apps)
            if not shutil.which(exe) and not _is_system_command(exe):
                return {
                    "status": "ERROR",
                    "message": (
                        f"'{app_name}' does not appear to be installed "
                        f"or accessible on this system."
                    ),
                }
            subprocess.Popen(cmd, shell=False)

        return {
            "status": "SUCCESS",
            "message": f"Opening {app_name.title()}.",
        }
    except FileNotFoundError:
        return {
            "status": "ERROR",
            "message": f"Could not find '{app_name}'. Is it installed?",
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


def _is_system_command(name: str) -> bool:
    """Return True for well-known Windows built-in executables."""
    _BUILTINS = {
        "taskmgr", "control", "explorer", "notepad", "calc", "mspaint",
        "cmd", "powershell", "regedit", "devmgmt.msc", "diskmgmt.msc",
        "eventvwr.msc", "SnippingTool", "wordpad", "charmap", "magnify",
        "osk", "narrator", "msedge", "mspaint",
    }
    return name in _BUILTINS
