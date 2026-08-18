# system_control/network_manager.py
"""
Network Manager
===============
Controls Wi-Fi and Bluetooth adapters on Windows.

Wi-Fi   : Uses `netsh wlan` commands (built-in Windows tool).
Bluetooth: Uses PowerShell + Windows.Devices.Radios WinRT API
           (available on Windows 10 1607+ and Windows 11).
"""

import subprocess


# ─── Wi-Fi ────────────────────────────────────────────────────────────────────

def _run_ps(command: str) -> subprocess.CompletedProcess:
    """Run a PowerShell command and return the result."""
    return subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
        capture_output=True, text=True
    )


def wifi_on() -> dict:
    """Enable the Wi-Fi adapter."""
    try:
        result = subprocess.run(
            ["netsh", "interface", "set", "interface",
             "name=Wi-Fi", "admin=ENABLED"],
            capture_output=True, text=True, shell=False
        )
        if result.returncode == 0:
            return {"status": "SUCCESS", "message": "Wi-Fi has been turned on."}
        # Fallback: try with PowerShell Enable-NetAdapter
        ps = "Enable-NetAdapter -Name 'Wi-Fi' -Confirm:$false"
        r2 = _run_ps(ps)
        if r2.returncode == 0:
            return {"status": "SUCCESS", "message": "Wi-Fi has been turned on."}
        return {
            "status": "ERROR",
            "message": f"Failed to enable Wi-Fi: {result.stderr.strip() or r2.stderr.strip()}",
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


def wifi_off() -> dict:
    """Disable the Wi-Fi adapter."""
    try:
        result = subprocess.run(
            ["netsh", "interface", "set", "interface",
             "name=Wi-Fi", "admin=DISABLED"],
            capture_output=True, text=True, shell=False
        )
        if result.returncode == 0:
            return {"status": "SUCCESS", "message": "Wi-Fi has been turned off."}
        ps = "Disable-NetAdapter -Name 'Wi-Fi' -Confirm:$false"
        r2 = _run_ps(ps)
        if r2.returncode == 0:
            return {"status": "SUCCESS", "message": "Wi-Fi has been turned off."}
        return {
            "status": "ERROR",
            "message": f"Failed to disable Wi-Fi: {result.stderr.strip() or r2.stderr.strip()}",
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


# ─── Bluetooth ────────────────────────────────────────────────────────────────

_BT_PS_TEMPLATE = """\
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() |
    Where-Object {{ $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and
    $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' }})[0]
Function Await($WinRtTask, $ResultType) {{
    $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
    $netTask = $asTask.Invoke($null, @($WinRtTask))
    $netTask.Wait(-1) | Out-Null
    $netTask.Result
}}
[Windows.Devices.Radios.Radio,Windows.System.Devices,ContentType=WindowsRuntime] | Out-Null
[Windows.Devices.Radios.RadioAccessStatus,Windows.System.Devices,ContentType=WindowsRuntime] | Out-Null
$radios = Await ([Windows.Devices.Radios.Radio]::GetRadiosAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Devices.Radios.Radio]])
$bluetooth = $radios | Where-Object {{ $_.Kind -eq 'Bluetooth' }}
if ($bluetooth) {{
    Await ($bluetooth.SetStateAsync([Windows.Devices.Radios.RadioState]::{state})) ([Windows.Devices.Radios.RadioAccessStatus]) | Out-Null
    Write-Output "OK"
}} else {{
    Write-Output "NO_BT"
}}
"""


def _toggle_bluetooth(state: str, label: str) -> dict:
    """Internal: set Bluetooth radio to 'On' or 'Off'."""
    try:
        ps_script = _BT_PS_TEMPLATE.format(state=state)
        result = _run_ps(ps_script)
        output = result.stdout.strip()
        if "OK" in output:
            return {
                "status": "SUCCESS",
                "message": f"Bluetooth has been turned {label}.",
            }
        if "NO_BT" in output:
            return {
                "status": "ERROR",
                "message": "No Bluetooth adapter found on this device.",
            }
        return {
            "status": "ERROR",
            "message": f"Bluetooth toggle failed: {result.stderr.strip()}",
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


def bluetooth_on() -> dict:
    """Enable the Bluetooth radio."""
    return _toggle_bluetooth("On", "on")


def bluetooth_off() -> dict:
    """Disable the Bluetooth radio."""
    return _toggle_bluetooth("Off", "off")
