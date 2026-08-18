# System Control Module Documentation

This document describes the structure of the `system_control` module, how the files are organized, how to run commands directly, and how to manage the system.

---

## 📂 Module Architecture & File Organization

The module is located in [voice_assistant/system_control/](file:///d:/AI-VOICE-ASSISTENT/voice_assistant/system_control/). It consists of a central router and multiple feature-specific managers:

*   [controller.py](file:///d:/AI-VOICE-ASSISTENT/voice_assistant/system_control/controller.py): The main router containing `SystemController`. It maps NLP intents (e.g. `GET_BATTERY`) to execute functions in managers.
*   [safety_guard.py](file:///d:/AI-VOICE-ASSISTENT/voice_assistant/system_control/safety_guard.py): Configures warnings and requires user confirmation for dangerous commands (like shutdown or clearing RAM).
*   [audio_manager.py](file:///d:/AI-VOICE-ASSISTENT/voice_assistant/system_control/audio_manager.py): Adjust, mute, unmute, or set system volume.
*   [power_manager.py](file:///d:/AI-VOICE-ASSISTENT/voice_assistant/system_control/power_manager.py): Handles shutdown, restart, sleep, and cancel.
*   [display_manager.py](file:///d:/AI-VOICE-ASSISTENT/voice_assistant/system_control/display_manager.py): Brightness and night light options.
*   [network_manager.py](file:///d:/AI-VOICE-ASSISTENT/voice_assistant/system_control/network_manager.py): Toggles Wi-Fi and Bluetooth state.
*   [app_manager.py](file:///d:/AI-VOICE-ASSISTENT/voice_assistant/system_control/app_manager.py): Opens system apps (calculator, notepad, settings).
*   [device_info_manager.py](file:///d:/AI-VOICE-ASSISTENT/voice_assistant/system_control/device_info_manager.py): Queries Battery, CPU, and Disk metrics.
*   [memory_manager.py](file:///d:/AI-VOICE-ASSISTENT/voice_assistant/system_control/memory_manager.py): Monitors and clears RAM/Virtual Memory.
*   [datetime_manager.py](file:///d:/AI-VOICE-ASSISTENT/voice_assistant/system_control/datetime_manager.py): Returns formatted dates/times.
*   [screen_manager.py](file:///d:/AI-VOICE-ASSISTENT/voice_assistant/system_control/screen_manager.py): Screenshot capturing and screen locking.

---

## 📋 Complete System Control Intents & Functions

Here is the full catalog of functionality supported by the system control module:

### 1. Audio Management
*   **`SET_VOLUME`** (Parameters: `percentage: int`): Sets the system volume to a specific percentage (0-100).
*   **`ADJUST_VOLUME`** (Parameters: `percentage_change: int`): Increases or decreases the volume by a relative amount (e.g. `+10` or `-10`).
*   **`MUTE_VOLUME`**: Mutes the system volume.
*   **`UNMUTE_VOLUME`**: Unmutes the system volume.

### 2. Power Management (Dangerous commands trigger safety gates)
*   **`SYSTEM_SHUTDOWN`** (Parameters: `delay_seconds: int`): Schedules a system shutdown.
*   **`SYSTEM_RESTART`** (Parameters: `delay_seconds: int`): Schedules a system restart.
*   **`SYSTEM_SLEEP`**: Puts the computer into sleep mode.
*   **`CANCEL_SHUTDOWN`**: Cancels any scheduled system shutdown or restart.

### 3. Display / Brightness
*   **`SET_BRIGHTNESS`** (Parameters: `level: int`): Sets the screen brightness (0-100).
*   **`ADJUST_BRIGHTNESS`** (Parameters: `change: int`): Changes screen brightness relatively.
*   **`TOGGLE_NIGHT_LIGHT`**: Toggles the Windows Night Light setting.

### 4. Network Management
*   **`WIFI_ON`**: Turns the Wi-Fi adapter on.
*   **`WIFI_OFF`**: Turns the Wi-Fi adapter off.
*   **`BLUETOOTH_ON`**: Turns Bluetooth on.
*   **`BLUETOOTH_OFF`**: Turns Bluetooth off.

### 5. Application Launcher
*   **`OPEN_APP`** (Parameters: `app_name: str`): Launches standard Windows applications (e.g., `"calculator"`, `"notepad"`, `"settings"`, `"paint"`, `"cmd"`, `"explorer"`).

### 6. Device Information
*   **`GET_BATTERY`**: Returns current battery percentage and charging status.
*   **`GET_CPU_USAGE`**: Returns CPU utilization percentage.
*   **`GET_DISK_SPACE`** (Parameters: `drive: str`): Returns total, used, and free disk space for a drive (default is `"C"`).

### 7. Memory Management
*   **`GET_RAM_USAGE`**: Gets overall RAM usage.
*   **`GET_RAM_DETAILS`**: Gets comprehensive RAM breakdown (total, used, available, cached).
*   **`GET_VIRTUAL_MEMORY`**: Returns swap space / virtual memory stats.
*   **`GET_TOP_MEMORY_PROCESSES`** (Parameters: `top_n: int`): Lists the top memory-consuming processes.
*   **`GET_MEMORY_HEALTH`**: Evaluates system RAM status and health.
*   **`CLEAR_RAM`**: Releases cached memory page lists (Dangerous).

### 8. Date & Time
*   **`GET_TIME`**: Returns current time (12-hour format).
*   **`GET_DATE`**: Returns current date.
*   **`GET_DATETIME`**: Returns full current date and time.

### 9. Screen Management
*   **`TAKE_SCREENSHOT`**: Takes a screenshot and saves it as a PNG on the Desktop.
*   **`LOCK_SCREEN`**: Locks the Windows screen immediately (Win+L equivalent).

---

## 🛠️ How to Run Every Command via `controller.py`

You can run any system control command directly from the command line using `controller.py`. First, navigate to the `system_control` directory:
```powershell
cd d:\AI-VOICE-ASSISTENT\voice_assistant\system_control
```

### 1. View Help and Usage Instructions
```powershell
python controller.py help
```

### 2. List All Registered Intents
```powershell
python controller.py list
```

### 3. Run a Command without Parameters
```powershell
python controller.py GET_BATTERY
python controller.py GET_TIME
python controller.py GET_RAM_DETAILS
python controller.py TAKE_SCREENSHOT
```

### 4. Run a Command with Key=Value Parameters
```powershell
python controller.py SET_VOLUME percentage=60
python controller.py ADJUST_VOLUME percentage_change=10
python controller.py SET_BRIGHTNESS level=80
python controller.py OPEN_APP app_name=calculator
python controller.py GET_DISK_SPACE drive=D
```

### 5. Running Sensitive/Dangerous Commands
When executing a sensitive intent, the controller safety gate prompts you to confirm before executing:
```powershell
python controller.py SYSTEM_SLEEP
python controller.py CLEAR_RAM
python controller.py LOCK_SCREEN
```
*Output Example:*
```
  [WARN]  Warning: This will lock your workstation screen immediately.
  >> Execute this dangerous command? (yes/no):
```

---

## 🖥️ Running Individual Manager Tasks Directly

Some manager files like `screen_manager.py` support running specific standalone CLI commands directly:
```powershell
# Take a screenshot to your Desktop
python screen_manager.py screenshot

# Take a screenshot to a custom location
python screen_manager.py screenshot C:\Users\JAYDIP\Desktop\test.png

# Lock your computer immediately
python screen_manager.py lock
```
