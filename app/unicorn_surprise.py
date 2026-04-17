#!/usr/bin/env python3
"""
Unicorn Surprise - A fun cross-platform app that shows a dancing unicorn
and oiia cat animation when you launch applications.

At each startup/unlock, the user is asked to Activate or Deactivate.
If activated: detects new app launches and shows a 7-second animation.
If deactivated: does nothing until next startup/unlock.
"""

import sys
import os
import platform
import threading
import time
import math
import queue
import tkinter as tk

try:
    import psutil
except ImportError:
    print("Installing psutil...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
    import psutil


SYSTEM = platform.system()
OWN_PID = os.getpid()


def _own_process_tree():
    """Return the set of PIDs in our own process tree (self + ancestors + children)."""
    pids = {OWN_PID}
    try:
        me = psutil.Process(OWN_PID)
        for anc in me.parents():
            pids.add(anc.pid)
        for ch in me.children(recursive=True):
            pids.add(ch.pid)
    except Exception:
        pass
    return pids


# ─── Animation Overlay ───────────────────────────────────────────────────────

class AnimationOverlay:
    """Fullscreen-ish popup overlay. Must be driven from the main Tk thread."""

    def __init__(self, root):
        self.root = root
        self.running = False
        self.win = None

    def show(self):
        if self.running:
            return
        self.running = True

        win = tk.Toplevel(self.root)
        win.title("Unicorn Surprise")
        win.attributes("-topmost", True)
        win.configure(bg="black")
        win.overrideredirect(True)

        win_w, win_h = 500, 400
        screen_w = win.winfo_screenwidth()
        screen_h = win.winfo_screenheight()
        x = (screen_w - win_w) // 2
        y = (screen_h - win_h) // 2
        win.geometry(f"{win_w}x{win_h}+{x}+{y}")
        win.resizable(False, False)

        canvas = tk.Canvas(win, width=win_w, height=win_h, bg="#1a1a2e", highlightthickness=0)
        canvas.pack()

        self.win = win
        self.canvas = canvas
        self.win_w = win_w
        self.win_h = win_h
        self.start_time = time.time()
        self.phase = "unicorn"

        self._animate()

    def _animate(self):
        if not self.running or self.win is None:
            return
        elapsed = time.time() - self.start_time
        self.canvas.delete("all")

        if elapsed < 4.0:
            self.phase = "unicorn"
            self._draw_unicorn(elapsed)
        elif elapsed < 7.0:
            self.phase = "oiia_cat"
            self._draw_oiia_cat(elapsed - 4.0)
        else:
            self.running = False
            try:
                self.win.destroy()
            except Exception:
                pass
            self.win = None
            return

        progress = elapsed / 7.0
        bar_y = self.win_h - 8
        self.canvas.create_rectangle(0, bar_y, self.win_w * progress, self.win_h,
                                     fill="#ff6b9d", outline="")

        self.win.after(33, self._animate)

    def _draw_unicorn(self, t):
        """Draw a dancing unicorn with rainbow effects."""
        w, h = self.win_w, self.win_h
        cx, cy = w // 2, h // 2

        colors = ["#ff0000", "#ff7700", "#ffff00", "#00ff00", "#0077ff", "#8800ff"]
        for i, color in enumerate(colors):
            wave_y = 50 + i * 45 + math.sin(t * 3 + i * 0.8) * 20
            self.canvas.create_line(0, wave_y, w, wave_y + math.sin(t * 2 + i) * 30,
                                    fill=color, width=3)

        for i in range(12):
            sx = (i * 97 + int(t * 150)) % w
            sy = (i * 73 + int(t * 80)) % (h - 80) + 20
            size = 2 + math.sin(t * 5 + i) * 2
            sparkle_color = colors[i % len(colors)]
            self.canvas.create_text(sx, sy, text="*", fill=sparkle_color,
                                    font=("Arial", int(8 + size)))

        bounce = math.sin(t * 6) * 15
        body_x = cx + math.sin(t * 2) * 30
        body_y = cy + bounce

        self.canvas.create_oval(body_x - 50, body_y - 20, body_x + 50, body_y + 30,
                                fill="white", outline="#ddd", width=2)

        head_x = body_x + 45
        head_y = body_y - 25 + math.sin(t * 4) * 5
        self.canvas.create_oval(head_x - 15, head_y - 15, head_x + 20, head_y + 15,
                                fill="white", outline="#ddd", width=2)

        horn_colors = ["#ff6b9d", "#ffb347", "#fff44f"]
        horn_x = head_x + 10
        horn_y = head_y - 15
        for i, hc in enumerate(horn_colors):
            self.canvas.create_line(horn_x - 3 + i * 3, horn_y,
                                    horn_x + 5, horn_y - 30 - math.sin(t * 3) * 5,
                                    fill=hc, width=2)

        self.canvas.create_oval(head_x + 5, head_y - 5, head_x + 12, head_y + 2,
                                fill="black")

        for i, lx_off in enumerate([-30, -10, 10, 30]):
            leg_phase = t * 8 + i * math.pi / 2
            leg_kick = math.sin(leg_phase) * 15
            lx = body_x + lx_off
            ly = body_y + 30
            self.canvas.create_line(lx, ly, lx + leg_kick, ly + 35,
                                    fill="#ddd", width=4)

        for i in range(5):
            mx = body_x + 30 - i * 8
            my = body_y - 20 + i * 3
            mane_flow = math.sin(t * 4 + i * 0.5) * 10
            self.canvas.create_line(mx, my, mx - 15 + mane_flow, my - 15,
                                    fill=colors[i % len(colors)], width=3)

        tail_x = body_x - 50
        tail_y = body_y
        for i in range(4):
            tx = tail_x - 10 - i * 8 + math.sin(t * 3 + i) * 8
            ty = tail_y - 5 + i * 5
            self.canvas.create_line(tail_x - i * 5, tail_y + i * 3,
                                    tx, ty, fill=colors[(i + 2) % len(colors)], width=3)

        text_y = h - 50
        rainbow_idx = int(t * 8) % len(colors)
        self.canvas.create_text(w // 2, text_y,
                                text="~ UNICORN DANCE ~",
                                fill=colors[rainbow_idx],
                                font=("Arial", 20, "bold"))

    def _draw_oiia_cat(self, t):
        """Draw oiia cat going backwards."""
        w, h = self.win_w, self.win_h

        self.canvas.create_rectangle(0, 0, w, h, fill="#0d1117", outline="")

        cat_x = w - 80 - (t / 3.0) * (w - 100)
        cat_y = h // 2 + 20

        self.canvas.create_oval(cat_x - 35, cat_y - 20, cat_x + 35, cat_y + 25,
                                fill="#ff8c00", outline="#cc7000", width=2)

        head_x = cat_x + 40
        head_y = cat_y - 15

        head_y += math.sin(t * 6) * 8
        head_x += math.cos(t * 6) * 3

        self.canvas.create_oval(head_x - 18, head_y - 16, head_x + 18, head_y + 16,
                                fill="#ff8c00", outline="#cc7000", width=2)

        for ear_off in [-10, 10]:
            ex = head_x + ear_off
            ey = head_y - 16
            self.canvas.create_polygon(ex - 6, ey + 5, ex, ey - 12, ex + 6, ey + 5,
                                       fill="#ff8c00", outline="#cc7000", width=1)
            self.canvas.create_polygon(ex - 3, ey + 3, ex, ey - 7, ex + 3, ey + 3,
                                       fill="#ffb060", outline="")

        for eye_off in [-7, 7]:
            ex = head_x + eye_off
            ey = head_y - 3
            self.canvas.create_oval(ex - 5, ey - 5, ex + 5, ey + 5, fill="white")
            px = ex + math.sin(t * 15) * 2
            py = ey + math.cos(t * 12) * 1
            self.canvas.create_oval(px - 3, py - 3, px + 3, py + 3, fill="black")

        mouth_open = abs(math.sin(t * 6)) * 8 + 3
        self.canvas.create_oval(head_x - 5, head_y + 4,
                                head_x + 5, head_y + 4 + mouth_open,
                                fill="#ff4444", outline="#cc0000")

        for i, lx_off in enumerate([-20, -8, 8, 20]):
            leg_phase = t * 10 + i * math.pi / 2
            leg_move = math.sin(leg_phase) * 12
            lx = cat_x + lx_off
            ly = cat_y + 25
            self.canvas.create_line(lx, ly, lx - leg_move, ly + 25,
                                    fill="#cc7000", width=3)

        tail_x = cat_x - 35
        tail_y = cat_y - 5
        tail_swing = math.sin(t * 5) * 25
        self.canvas.create_line(tail_x, tail_y,
                                tail_x - 20, tail_y - 20 + tail_swing,
                                tail_x - 35, tail_y - 10 + tail_swing * 0.5,
                                fill="#cc7000", width=3, smooth=True)

        oiia_texts = ["O", "I", "I", "A"]
        pulse = abs(math.sin(t * 4))
        text_size = int(28 + pulse * 12)
        oiia_colors = ["#ff4444", "#ff8844", "#ffcc44", "#ff4444"]

        letter_idx = int(t * 4) % 4

        for i, (letter, color) in enumerate(zip(oiia_texts, oiia_colors)):
            lx = w // 2 - 60 + i * 40
            ly = 60 + math.sin(t * 6 + i * 0.8) * 10
            size = text_size if i == letter_idx else 24
            self.canvas.create_text(lx, ly, text=letter, fill=color,
                                    font=("Arial", size, "bold"))

        self.canvas.create_text(w // 2, h - 40,
                                text="~ oiia oiia oiia ~",
                                fill="#ff8c00",
                                font=("Arial", 16, "bold"))

        for i in range(5):
            line_x = cat_x + 50 + i * 15
            line_y = cat_y - 10 + (i * 17) % 40
            line_len = 10 + math.sin(t * 3 + i) * 5
            self.canvas.create_line(line_x, line_y, line_x + line_len, line_y,
                                    fill="#555", width=2)


# ─── Process Monitor ─────────────────────────────────────────────────────────

class ProcessMonitor:
    """Monitors for new process launches and pushes events to a queue."""

    IGNORED_PROCESSES = {
        "svchost.exe", "conhost.exe", "RuntimeBroker.exe", "dllhost.exe",
        "WmiPrvSE.exe", "SearchProtocolHost.exe", "SearchFilterHost.exe",
        "backgroundTaskHost.exe", "sihost.exe", "taskhostw.exe",
        "ShellExperienceHost.exe", "StartMenuExperienceHost.exe",
        "SystemSettings.exe", "SettingSyncHost.exe", "CompPkgSrv.exe",
        "TextInputHost.exe", "SecurityHealthService.exe", "MsMpEng.exe",
        "NisSrv.exe", "SgrmBroker.exe", "spoolsv.exe", "lsass.exe",
        "csrss.exe", "smss.exe", "wininit.exe", "services.exe",
        "winlogon.exe", "dwm.exe", "fontdrvhost.exe", "LogonUI.exe",
        "kworker", "ksoftirqd", "migration", "rcu_", "kthread",
        "systemd", "journald", "udevd", "dbus-daemon", "polkitd",
        "gdm", "Xorg", "Xwayland", "gnome-shell", "pulseaudio",
        "pipewire", "wireplumber", "gvfsd", "gvfs-", "at-spi",
        "ibus-daemon", "xdg-", "gsd-", "evolution-",
        "kernel_task", "launchd", "WindowServer", "loginwindow",
        "mds", "mds_stores", "fseventsd", "coreaudiod",
        "python", "python3", "pip", "unicorn_surprise",
        "sh", "bash", "zsh", "dash", "tmux", "cron", "crond",
        "sleep", "sudo", "su", "whoami", "which", "grep", "sed", "awk",
        "tracker-", "goa-", "packagekit", "fwupd", "colord",
        "rtkit-daemon", "upowerd", "accounts-daemon", "NetworkManager",
        "wpa_supplicant", "ModemManager", "avahi-daemon",
        "dconf-service", "xdg-desktop-portal",
    }

    COOLDOWN_SECONDS = 10.0

    def __init__(self, event_queue):
        self.queue = event_queue
        self.active = False
        self._stop_event = threading.Event()
        self._known_pids = set()
        self._own_tree = _own_process_tree()

    def start(self):
        if self.active:
            return
        self.active = True
        self._stop_event.clear()
        self._own_tree = _own_process_tree()
        self._known_pids = {p.pid for p in psutil.process_iter()}
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.active = False
        self._stop_event.set()

    def _monitor_loop(self):
        while not self._stop_event.is_set():
            try:
                current_pids = set()
                trigger = None
                for proc in psutil.process_iter(['pid', 'name', 'ppid', 'cmdline']):
                    pid = proc.info.get('pid')
                    current_pids.add(pid)
                    if pid in self._known_pids:
                        continue
                    name = proc.info.get('name') or ''
                    ppid = proc.info.get('ppid') or 0
                    cmdline = proc.info.get('cmdline') or []
                    if not name:
                        continue
                    if not cmdline:
                        # kernel thread / empty cmdline — skip
                        continue
                    if ppid in self._own_tree or pid in self._own_tree:
                        continue
                    if self._is_ignored(name):
                        continue
                    trigger = name
                    break

                self._known_pids = current_pids

                if trigger:
                    print(f"[unicorn] detected launch: {trigger}")
                    self.queue.put(('launch', trigger))
                    # cooldown: let the animation play and avoid re-triggering
                    # on subprocess spawns from the same app launch
                    if self._stop_event.wait(self.COOLDOWN_SECONDS):
                        break
                    # refresh known PIDs so cooldown-spawned children aren't flagged
                    self._known_pids = {p.pid for p in psutil.process_iter()}
                    continue
            except Exception as e:
                print(f"[unicorn] monitor error: {e}", file=sys.stderr)
            if self._stop_event.wait(1.5):
                break

    def _is_ignored(self, name):
        name_lower = name.lower()
        for ignored in self.IGNORED_PROCESSES:
            if ignored.lower() in name_lower:
                return True
        return False


# ─── Screen Lock/Unlock Detection ────────────────────────────────────────────

class ScreenMonitor:
    """Detects screen unlock events (platform-specific) and pushes to queue."""

    def __init__(self, event_queue):
        self.queue = event_queue
        self._stop = threading.Event()

    def start(self):
        t = threading.Thread(target=self._monitor, daemon=True)
        t.start()

    def stop(self):
        self._stop.set()

    def _notify(self):
        self.queue.put(('unlock', None))

    def _monitor(self):
        if SYSTEM == "Linux":
            self._monitor_linux()
        elif SYSTEM == "Darwin":
            self._monitor_macos()
        elif SYSTEM == "Windows":
            self._monitor_windows()

    def _monitor_linux(self):
        try:
            import subprocess
            proc = subprocess.Popen(
                ["dbus-monitor", "--session",
                 "type='signal',interface='org.gnome.ScreenSaver'",
                 "type='signal',interface='org.freedesktop.ScreenSaver'"],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
            )
            locked = False
            for line in proc.stdout:
                if self._stop.is_set():
                    proc.kill()
                    break
                if "boolean true" in line:
                    locked = True
                elif "boolean false" in line and locked:
                    locked = False
                    self._notify()
        except Exception:
            pass

    def _monitor_macos(self):
        try:
            import subprocess
            was_locked = False
            while not self._stop.is_set():
                result = subprocess.run(
                    ["python3", "-c",
                     "import Quartz; d=Quartz.CGSessionCopyCurrentDictionary(); "
                     "print(d.get('CGSSessionScreenIsLocked', 0))"],
                    capture_output=True, text=True, timeout=5
                )
                is_locked = result.stdout.strip() == "1"
                if was_locked and not is_locked:
                    self._notify()
                was_locked = is_locked
                self._stop.wait(3)
        except Exception:
            pass

    def _monitor_windows(self):
        try:
            import ctypes
            was_locked = False
            while not self._stop.is_set():
                user32 = ctypes.windll.user32
                desk = user32.OpenInputDesktop(0, False, 0x0100)
                is_locked = desk == 0
                if desk:
                    user32.CloseDesktop(desk)
                if was_locked and not is_locked:
                    self._notify()
                was_locked = is_locked
                self._stop.wait(3)
        except Exception:
            pass


# ─── Choice Dialog ────────────────────────────────────────────────────────────

def show_choice_dialog(root):
    """Show Activer/Desactiver dialog as a Toplevel of root. Blocks until closed."""
    result = [None]

    win = tk.Toplevel(root)
    win.title("Unicorn Surprise")
    win.attributes("-topmost", True)
    win.resizable(False, False)

    win_w, win_h = 420, 280
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    x = (screen_w - win_w) // 2
    y = (screen_h - win_h) // 2
    win.geometry(f"{win_w}x{win_h}+{x}+{y}")
    win.configure(bg="#1a1a2e")

    title_frame = tk.Frame(win, bg="#1a1a2e")
    title_frame.pack(pady=(25, 5))

    tk.Label(title_frame, text="Unicorn Surprise",
             font=("Arial", 22, "bold"), fg="#ff6b9d", bg="#1a1a2e").pack()

    tk.Label(title_frame, text="~",
             font=("Arial", 14), fg="#ffb347", bg="#1a1a2e").pack()

    desc_frame = tk.Frame(win, bg="#1a1a2e")
    desc_frame.pack(pady=(5, 20))

    tk.Label(desc_frame,
             text="Activer les animations licorne & oiia cat\nlors du lancement d'applications ?",
             font=("Arial", 12), fg="#e0e0e0", bg="#1a1a2e",
             justify="center").pack()

    tk.Label(desc_frame,
             text="(Ce choix dure jusqu'au prochain\nd\u00e9marrage ou d\u00e9verrouillage)",
             font=("Arial", 9), fg="#888", bg="#1a1a2e",
             justify="center").pack(pady=(8, 0))

    btn_frame = tk.Frame(win, bg="#1a1a2e")
    btn_frame.pack(pady=(5, 20))

    def on_activate():
        result[0] = True
        win.destroy()

    def on_deactivate():
        result[0] = False
        win.destroy()

    tk.Button(btn_frame, text="Activer",
              font=("Arial", 13, "bold"),
              fg="white", bg="#28a745",
              activebackground="#218838", activeforeground="white",
              relief="flat", padx=25, pady=8,
              cursor="hand2", command=on_activate).pack(side="left", padx=10)

    tk.Button(btn_frame, text="D\u00e9sactiver",
              font=("Arial", 13, "bold"),
              fg="white", bg="#dc3545",
              activebackground="#c82333", activeforeground="white",
              relief="flat", padx=25, pady=8,
              cursor="hand2", command=on_deactivate).pack(side="left", padx=10)

    win.protocol("WM_DELETE_WINDOW", on_deactivate)
    try:
        win.grab_set()
    except Exception:
        pass
    win.wait_window()
    return bool(result[0])


# ─── Main App ────────────────────────────────────────────────────────────────

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.events = queue.Queue()
        self.overlay = AnimationOverlay(self.root)
        self.process_monitor = ProcessMonitor(self.events)
        self.screen_monitor = ScreenMonitor(self.events)

    def run(self):
        activated = show_choice_dialog(self.root)
        if activated:
            print("Unicorn Surprise activ\u00e9 ! Les licornes arrivent...")
            self.process_monitor.start()
        else:
            print("Unicorn Surprise d\u00e9sactiv\u00e9. \u00c0 la prochaine fois !")

        self.screen_monitor.start()
        self.root.after(100, self._poll_events)

        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass
        finally:
            self.process_monitor.stop()
            self.screen_monitor.stop()

    def _poll_events(self):
        try:
            while True:
                ev = self.events.get_nowait()
                self._handle_event(ev)
        except queue.Empty:
            pass
        self.root.after(100, self._poll_events)

    def _handle_event(self, ev):
        kind = ev[0]
        if kind == 'launch':
            if not self.overlay.running:
                self.overlay.show()
        elif kind == 'unlock':
            self.process_monitor.stop()
            activated = show_choice_dialog(self.root)
            if activated:
                self.process_monitor.start()


def main():
    App().run()


if __name__ == "__main__":
    main()
