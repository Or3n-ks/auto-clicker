#!/usr/bin/env python3
"""Kingshot autoclicker. Tk GUI, F6 stops globally."""

import random
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

import pyautogui
from pynput import keyboard

pyautogui.FAILSAFE = True  # slam mouse to a corner = emergency stop


class Autoclicker:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.stop_event = threading.Event()
        self.worker: threading.Thread | None = None

        root.title("Kingshot Autoclicker")
        root.attributes("-topmost", True)
        root.resizable(False, False)

        frm = ttk.Frame(root, padding=12)
        frm.grid()

        ttk.Label(frm, text="Mode:").grid(row=0, column=0, sticky="w")
        self.mode = tk.StringVar(value="current")
        ttk.Radiobutton(
            frm, text="Current mouse position", variable=self.mode, value="current",
            command=self._sync_mode,
        ).grid(row=0, column=1, columnspan=3, sticky="w")
        ttk.Radiobutton(
            frm, text="Fixed X,Y", variable=self.mode, value="fixed",
            command=self._sync_mode,
        ).grid(row=1, column=1, columnspan=3, sticky="w")

        ttk.Label(frm, text="X:").grid(row=2, column=0, sticky="e", pady=(8, 0))
        self.x_var = tk.StringVar()
        self.x_entry = ttk.Entry(frm, textvariable=self.x_var, width=8)
        self.x_entry.grid(row=2, column=1, sticky="w", pady=(8, 0))

        ttk.Label(frm, text="Y:").grid(row=2, column=2, sticky="e", pady=(8, 0))
        self.y_var = tk.StringVar()
        self.y_entry = ttk.Entry(frm, textvariable=self.y_var, width=8)
        self.y_entry.grid(row=2, column=3, sticky="w", pady=(8, 0))

        self.capture_btn = ttk.Button(frm, text="Capture", command=self._capture)
        self.capture_btn.grid(row=2, column=4, padx=(8, 0), pady=(8, 0))

        ttk.Label(frm, text="Interval (sec):").grid(row=3, column=0, columnspan=2, sticky="w", pady=(8, 0))
        self.interval_var = tk.StringVar(value="0.5")
        ttk.Entry(frm, textvariable=self.interval_var, width=8).grid(row=3, column=2, sticky="w", pady=(8, 0))

        ttk.Label(frm, text="Click count (0 = ∞):").grid(row=4, column=0, columnspan=2, sticky="w")
        self.count_var = tk.StringVar(value="0")
        ttk.Entry(frm, textvariable=self.count_var, width=8).grid(row=4, column=2, sticky="w")

        ttk.Label(frm, text="Start countdown (sec):").grid(row=5, column=0, columnspan=2, sticky="w")
        self.countdown_var = tk.StringVar(value="3")
        ttk.Entry(frm, textvariable=self.countdown_var, width=8).grid(row=5, column=2, sticky="w")

        ttk.Separator(frm, orient="horizontal").grid(
            row=6, column=0, columnspan=5, sticky="ew", pady=(10, 6)
        )

        self.jitter_interval_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            frm, text="Interval jitter ±10%", variable=self.jitter_interval_var,
        ).grid(row=7, column=0, columnspan=5, sticky="w")

        self.jitter_pos_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            frm, text="Position jitter ±3 px", variable=self.jitter_pos_var,
        ).grid(row=8, column=0, columnspan=5, sticky="w")

        self.start_btn = ttk.Button(frm, text="Start  (F6 to stop)", command=self._start)
        self.start_btn.grid(row=9, column=0, columnspan=5, pady=(10, 4), sticky="ew")

        self.status_var = tk.StringVar(value="idle")
        ttk.Label(frm, textvariable=self.status_var, foreground="#555").grid(
            row=10, column=0, columnspan=5, sticky="w"
        )

        self._sync_mode()
        self._start_hotkey_listener()
        root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _sync_mode(self) -> None:
        fixed = self.mode.get() == "fixed"
        state = "normal" if fixed else "disabled"
        self.x_entry.configure(state=state)
        self.y_entry.configure(state=state)

    def _capture(self) -> None:
        x, y = pyautogui.position()
        self.x_var.set(str(x))
        self.y_var.set(str(y))
        self.mode.set("fixed")
        self._sync_mode()

    def _set_status(self, text: str) -> None:
        self.root.after(0, self.status_var.set, text)

    def _start(self) -> None:
        if self.worker and self.worker.is_alive():
            return
        try:
            interval = float(self.interval_var.get())
            if interval <= 0:
                raise ValueError("interval must be > 0")
            count = int(self.count_var.get())
            if count < 0:
                raise ValueError("count must be >= 0")
            countdown = int(self.countdown_var.get())
            if countdown < 0:
                raise ValueError("countdown must be >= 0")
            target: tuple[int, int] | None = None
            if self.mode.get() == "fixed":
                target = (int(self.x_var.get()), int(self.y_var.get()))
        except (ValueError, TypeError) as exc:
            messagebox.showerror("Invalid input", str(exc))
            return

        jitter_interval = self.jitter_interval_var.get()
        jitter_pos = self.jitter_pos_var.get()

        self.stop_event.clear()
        self.worker = threading.Thread(
            target=self._click_loop,
            args=(interval, count, countdown, target, jitter_interval, jitter_pos),
            daemon=True,
        )
        self.worker.start()

    def _click_loop(
        self,
        interval: float,
        count: int,
        countdown: int,
        target: tuple[int, int] | None,
        jitter_interval: bool,
        jitter_pos: bool,
    ) -> None:
        for remaining in range(countdown, 0, -1):
            if self.stop_event.is_set():
                self._set_status("stopped")
                return
            self._set_status(f"starting in {remaining}…")
            time.sleep(1)

        clicks = 0
        while not self.stop_event.is_set():
            if target is None:
                pyautogui.click()
            else:
                x = target[0] + (random.randint(-3, 3) if jitter_pos else 0)
                y = target[1] + (random.randint(-3, 3) if jitter_pos else 0)
                pyautogui.click(x, y)
            clicks += 1
            self._set_status(f"clicking… ({clicks})")
            if count and clicks >= count:
                break
            wait = interval * random.uniform(0.9, 1.1) if jitter_interval else interval
            if self.stop_event.wait(wait):
                break

        self._set_status(f"stopped after {clicks} click(s)")

    def _start_hotkey_listener(self) -> None:
        def on_press(key: object) -> None:
            if key == keyboard.Key.f6:
                self.stop_event.set()

        try:
            self.listener = keyboard.Listener(on_press=on_press)
            self.listener.start()
        except Exception as exc:  # pynput raises if Accessibility is missing
            messagebox.showwarning(
                "Hotkey unavailable",
                "F6 stop hotkey could not start. Grant Accessibility to your "
                "terminal in System Settings → Privacy & Security → Accessibility, "
                f"then relaunch.\n\nDetail: {exc}",
            )
            self.listener = None

    def _on_close(self) -> None:
        self.stop_event.set()
        if getattr(self, "listener", None):
            self.listener.stop()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    Autoclicker(root)
    root.mainloop()


if __name__ == "__main__":
    main()
