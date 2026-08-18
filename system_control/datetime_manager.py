# system_control/datetime_manager.py
"""
Date & Time Manager
===================
Reads and speaks the current system date and time.
Zero external dependencies — pure Python stdlib only.
"""

import datetime


def get_time() -> dict:
    """
    Return the current system time in a natural spoken format.
    Voice: "What time is it?" / "Tell me the time" / "What's the current time?"
    """
    try:
        now = datetime.datetime.now()
        # Format: "10:31 AM" (12-hour with AM/PM, no leading zero)
        time_str = now.strftime("%I:%M %p").lstrip("0")
        msg = f"The current time is {time_str}."
        return {
            "status": "SUCCESS",
            "message": msg,
            "time_24h": now.strftime("%H:%M"),
            "time_12h": time_str,
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


def get_date() -> dict:
    """
    Return today's date in a natural spoken format.
    Voice: "What's today's date?" / "What day is it?" / "Tell me the date"
    """
    try:
        now = datetime.datetime.now()

        # Ordinal suffix: 1st, 2nd, 3rd, 4th…
        day = now.day
        if 11 <= day <= 13:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

        weekday   = now.strftime("%A")          # e.g. "Sunday"
        month     = now.strftime("%B")          # e.g. "August"
        year      = now.strftime("%Y")          # e.g. "2026"
        date_str  = f"{weekday}, {month} {day}{suffix}, {year}"

        return {
            "status": "SUCCESS",
            "message": f"Today is {date_str}.",
            "date_iso": now.strftime("%Y-%m-%d"),
            "date_spoken": date_str,
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


def get_datetime() -> dict:
    """
    Return both date and time in one response.
    Voice: "What's the date and time?" / "Tell me the date and time"
    """
    try:
        time_result = get_time()
        date_result = get_date()

        if time_result["status"] != "SUCCESS" or date_result["status"] != "SUCCESS":
            return {
                "status": "ERROR",
                "message": "Could not read system date or time.",
            }

        msg = (
            f"It is {time_result['time_12h']} on {date_result['date_spoken']}."
        )
        return {"status": "SUCCESS", "message": msg}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}
