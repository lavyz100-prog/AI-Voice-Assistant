# system_control/memory_manager.py
"""
Memory Manager
==============
All RAM / memory related voice commands.

Intents handled:
  GET_RAM_USAGE             — basic used / free / total / percent
  GET_RAM_DETAILS           — full breakdown (used, free, cached, available)
  GET_VIRTUAL_MEMORY        — Windows Page File (swap) statistics
  GET_TOP_MEMORY_PROCESSES  — top N processes sorted by RAM usage
  GET_MEMORY_HEALTH         — categorised health: Normal / Warning / Critical
  CLEAR_RAM                 — trim working sets via Windows API (safe, no kills)

Requires: pip install psutil
"""

import ctypes
import sys
import psutil


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _bytes_to_gb(b: int) -> float:
    return b / (1024 ** 3)

def _bytes_to_mb(b: int) -> float:
    return b / (1024 ** 2)


# ─── Public Functions ──────────────────────────────────────────────────────────

def get_ram_usage() -> dict:
    """
    Basic RAM status: total, used, available, and usage percent.
    Voice: "How much RAM is available?" / "Show RAM usage"
    """
    try:
        vm = psutil.virtual_memory()
        total     = _bytes_to_gb(vm.total)
        used      = _bytes_to_gb(vm.used)
        available = _bytes_to_gb(vm.available)
        pct       = vm.percent

        msg = (
            f"You have {available:.1f} GB free out of {total:.1f} GB RAM. "
            f"Current usage is {pct:.0f}%."
        )
        return {"status": "SUCCESS", "message": msg}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


def get_ram_details() -> dict:
    """
    Full RAM breakdown including cached pages.
    Voice: "Show RAM details" / "Memory breakdown" / "Detailed memory info"
    """
    try:
        vm = psutil.virtual_memory()
        total     = _bytes_to_gb(vm.total)
        used      = _bytes_to_gb(vm.used)
        free      = _bytes_to_gb(vm.free)
        available = _bytes_to_gb(vm.available)
        pct       = vm.percent

        # 'cached' is available on Linux; on Windows use available - free ≈ cached
        cached_bytes = max(0, vm.available - vm.free)
        cached = _bytes_to_gb(cached_bytes)

        lines = [
            f"RAM Details:",
            f"  Total     : {total:.2f} GB",
            f"  Used      : {used:.2f} GB  ({pct:.0f}%)",
            f"  Available : {available:.2f} GB",
            f"  Free      : {free:.2f} GB",
            f"  Cached    : {cached:.2f} GB",
        ]
        msg = " | ".join([
            f"Total {total:.1f} GB",
            f"Used {used:.1f} GB ({pct:.0f}%)",
            f"Available {available:.1f} GB",
            f"Cached {cached:.1f} GB",
        ])
        return {
            "status": "SUCCESS",
            "message": msg,
            "details": "\n".join(lines),
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


def get_virtual_memory() -> dict:
    """
    Windows Page File (virtual / swap) statistics.
    Voice: "What is my virtual memory?" / "Show swap usage" / "Page file usage"
    """
    try:
        swap = psutil.swap_memory()
        total = _bytes_to_gb(swap.total)
        used  = _bytes_to_gb(swap.used)
        free  = _bytes_to_gb(swap.free)
        pct   = swap.percent

        if total < 0.1:
            return {
                "status": "SUCCESS",
                "message": "Virtual memory (Page File) is not configured or is disabled.",
            }

        msg = (
            f"Virtual memory (Page File): {used:.1f} GB used out of "
            f"{total:.1f} GB ({pct:.0f}% used, {free:.1f} GB free)."
        )
        return {"status": "SUCCESS", "message": msg}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


def get_top_memory_processes(top_n: int = 5) -> dict:
    """
    List the top N processes sorted by RAM consumption (RSS).
    Voice: "Which apps are using the most memory?" / "Top memory processes"

    Parameters
    ----------
    top_n : int  Number of processes to return (default 5).
    """
    try:
        procs = []
        for proc in psutil.process_iter(["pid", "name", "memory_info"]):
            try:
                rss = proc.info["memory_info"].rss
                name = proc.info["name"] or "Unknown"
                procs.append((name, rss))
            except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                continue

        if not procs:
            return {
                "status": "ERROR",
                "message": "Could not retrieve process memory information.",
            }

        procs.sort(key=lambda x: x[1], reverse=True)
        top = procs[:top_n]

        parts = []
        for rank, (name, rss) in enumerate(top, 1):
            if rss >= 1024 ** 3:
                size_str = f"{_bytes_to_gb(rss):.2f} GB"
            else:
                size_str = f"{_bytes_to_mb(rss):.0f} MB"
            parts.append(f"{rank}. {name} ({size_str})")

        msg = f"Top {top_n} memory-consuming processes: " + ", ".join(parts) + "."
        return {"status": "SUCCESS", "message": msg}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


def get_memory_health() -> dict:
    """
    Categorise memory health: Normal (<70%), Warning (70-85%), Critical (>85%).
    Voice: "Is my memory okay?" / "Memory health check" / "Check RAM health"
    """
    try:
        vm = psutil.virtual_memory()
        pct = vm.percent
        available_gb = _bytes_to_gb(vm.available)

        if pct < 70:
            tier = "healthy"
            icon = "[OK]"
            tip  = "well within normal range."
        elif pct < 85:
            tier = "moderately loaded"
            icon = "[WARN]"
            tip  = "consider closing unused applications."
        else:
            tier = "critically high"
            icon = "[CRITICAL]"
            tip  = "you may experience slowdowns. Close apps or run 'clear ram'."

        msg = (
            f"{icon} Memory is {tier} at {pct:.0f}% usage "
            f"({available_gb:.1f} GB available) — {tip}"
        )
        return {
            "status": "SUCCESS",
            "message": msg,
            "health_tier": tier,        # 'healthy' | 'moderately loaded' | 'critically high'
            "usage_percent": pct,
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


def clear_ram() -> dict:
    """
    Trim working sets of all accessible processes via the Windows API.
    Uses SetProcessWorkingSetSize(-1, -1) — does NOT kill any process.
    Signals Windows to move idle pages out of RAM into the page file.
    Voice: "Free up RAM" / "Clear memory" / "Release memory"
    """
    if sys.platform != "win32":
        return {
            "status": "ERROR",
            "message": "RAM clearing via working set trim is only supported on Windows.",
        }
    try:
        before_pct = psutil.virtual_memory().percent

        freed_count = 0
        PROCESS_ALL_ACCESS = 0x1F0FFF
        k32 = ctypes.windll.kernel32

        for proc in psutil.process_iter(["pid"]):
            try:
                pid = proc.info["pid"]
                handle = k32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
                if handle:
                    k32.SetProcessWorkingSetSize(handle, ctypes.c_size_t(-1), ctypes.c_size_t(-1))
                    k32.CloseHandle(handle)
                    freed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, Exception):
                continue

        after_pct = psutil.virtual_memory().percent
        delta = before_pct - after_pct

        msg = (
            f"RAM cleanup complete. Trimmed working sets of {freed_count} processes. "
            f"Usage changed from {before_pct:.0f}% to {after_pct:.0f}%"
        )
        if delta > 0:
            msg += f" (freed ~{delta:.1f}%)."
        else:
            msg += ". Windows may defer page release — check Task Manager in a few seconds."

        return {"status": "SUCCESS", "message": msg}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}
