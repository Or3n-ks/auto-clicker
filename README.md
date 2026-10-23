# Kingshot Autoclicker

A small desktop app that repeatedly clicks the mouse at a chosen location. It is designed for Kingshot, but it can click in any app. The app has a simple Tkinter window and runs the clicking loop in a background thread.

## Requirements

- macOS
- Python with Tkinter available
- `pyautogui` and `pynput` installed in a Python environment

The project instructions require using that centralized environment rather than installing packages globally or creating a project-specific virtual environment. If either dependency is missing, install it there:

```bash
python -m pip install pyautogui pynput
```

macOS may require granting your terminal app permission under **System Settings → Privacy & Security → Accessibility** for mouse control and the global F6 hotkey. If the hotkey does not work, check that permission and relaunch the app.

## Start

Run the launcher from any directory:

```bash
run.sh
```

The launcher uses the centralized environment and opens an always-on-top window.

## Use

1. Choose a click mode:
   - **Current mouse position** clicks wherever the cursor is when each click happens. It does not move the cursor.
   - **Fixed X,Y** clicks at the entered screen coordinates. The cursor moves to those coordinates for each click.
2. To set fixed coordinates from the cursor's current location, hover over the target and press **Capture**. This fills in X and Y and selects Fixed mode.
3. Set the click **Interval (sec)**. It must be greater than zero; the default is `0.5`.
4. Set **Click count**. Enter `0` to continue until stopped, or a positive integer to stop after that many clicks.
5. Set **Start countdown (sec)** to give yourself time to return focus to the target app. The default is `3`; `0` starts immediately.
6. Press **Start**.

### Optional jitter

- **Interval jitter ±10%** varies each wait interval randomly between 90% and 110% of the selected interval.
- **Position jitter ±3 px** adds a random offset of up to 3 pixels on each axis when using Fixed X,Y mode. It has no effect in Current mouse position mode.

## Stop safely

- Press **F6** anywhere to stop the click loop.
- Close the app window to stop the loop and exit.
- PyAutoGUI's failsafe is enabled: moving the cursor to a screen corner triggers its emergency stop.

Use the autoclicker only when repeated clicking is appropriate for the app and activity. Keep the window visible and confirm the selected mode, coordinates, interval, and click count before starting.

## Troubleshooting

- **F6 does not stop clicking:** Check macOS Accessibility permission for the terminal app that launched the script, then relaunch.
- **The app does not start:** Confirm the centralized Python environment exists and has `pyautogui` and `pynput` installed. Python must also have Tkinter available.
- **Clicks go to the wrong place:** Stop with F6. Use Current mouse position if you intend to control the cursor yourself, or use Capture to set a fresh fixed target.

## Files

- `autoclicker.py` — app and click-loop implementation.
- `run.sh` — launcher for the centralized Python environment.
