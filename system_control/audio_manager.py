# system_control/audio_manager.py

try:
    from pycaw.pycaw import AudioUtilities
    PYCAW_AVAILABLE = True
except ImportError:
    PYCAW_AVAILABLE = False


def _get_volume_interface():
    """Internal helper: returns the Windows IAudioEndpointVolume interface.

    Compatible with pycaw >= 20230407 which exposes EndpointVolume directly
    on the AudioDevice object returned by GetSpeakers().
    """
    if not PYCAW_AVAILABLE:
        raise RuntimeError("pycaw is not installed. Run: pip install pycaw")
    device = AudioUtilities.GetSpeakers()
    return device.EndpointVolume


def adjust_volume(percentage_change: int) -> dict:
    """
    Increase or decrease system volume by a relative percentage.
    percentage_change: positive to increase, negative to decrease.
    """
    try:
        volume = _get_volume_interface()
        current_vol = volume.GetMasterVolumeLevelScalar()
        new_vol = max(0.0, min(1.0, current_vol + (percentage_change / 100.0)))
        volume.SetMasterVolumeLevelScalar(new_vol, None)
        action = "increased" if percentage_change > 0 else "decreased"
        return {
            "status": "SUCCESS",
            "message": f"Volume {action} by {abs(percentage_change)}%. "
                       f"New level: {round(new_vol * 100)}%.",
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


def set_volume(percentage: int) -> dict:
    """
    Set system volume to an absolute level (0–100).
    """
    try:
        volume = _get_volume_interface()
        level = max(0.0, min(1.0, percentage / 100.0))
        volume.SetMasterVolumeLevelScalar(level, None)
        return {
            "status": "SUCCESS",
            "message": f"Volume set to {percentage}%.",
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


def mute_volume() -> dict:
    """Mute the system audio."""
    try:
        volume = _get_volume_interface()
        volume.SetMute(1, None)
        return {"status": "SUCCESS", "message": "System audio muted."}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


def unmute_volume() -> dict:
    """Unmute the system audio."""
    try:
        volume = _get_volume_interface()
        volume.SetMute(0, None)
        return {"status": "SUCCESS", "message": "System audio unmuted."}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}
