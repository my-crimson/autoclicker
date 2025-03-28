import time
import threading
import numpy as np
import tkinter as tk
from tkinter import ttk
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, KeyCode

# Objek mouse
mouse = Controller()

# Variabel kontrol
clicking = False
program_running = True
timer_running = False
hold_pressed = False  # Untuk mode Hold Click

# Default settings
min_delay = 0.1
max_delay = 0.5
click_button = Button.left
start_stop_key = KeyCode(char='s')  # Default shortcut
timer_seconds = 0
start_time = 0  # Untuk mencatat waktu mulai timer

# Inisialisasi Tkinter
root = tk.Tk()
root.title("Auto / Hold Clicker")
root.geometry("500x450")
root.resizable(False, False)

# Variabel Mode dan Button Click
mode = tk.StringVar(master=root, value="AutoClick")  # Default mode
click_button_var = tk.StringVar(master=root, value="Left")  

def clicker():
    """Fungsi utama untuk auto/hold click dengan timer."""
    global clicking, hold_pressed, timer_running, timer_seconds, start_time
    while program_running:
        if clicking and timer_running:
            start_time = time.time()  # Catat waktu mulai
            while clicking and (timer_seconds == 0 or (time.time() - start_time < timer_seconds)):
                if mode.get() == "AutoClick":
                    mouse.click(click_button)
                    delay = np.random.uniform(min_delay, max_delay)
                    time.sleep(delay)
                elif mode.get() == "HoldClick":
                    if not hold_pressed:
                        mouse.press(click_button)
                        hold_pressed = True
                update_timer_display()
                time.sleep(0.1)
            stop_clicking()
        time.sleep(0.1)

def start_clicking():
    """Mulai proses klik dengan timer."""
    global clicking, timer_running, timer_seconds, start_time
    clicking = True
    timer_running = True
    try:
        timer_seconds = int(timer_entry.get())
    except ValueError:
        timer_seconds = 0
    start_time = time.time()
    update_timer_display()
    countdown_timer()

def stop_clicking():
    """Hentikan proses klik."""
    global clicking, hold_pressed, timer_running
    clicking = False
    timer_running = False
    if hold_pressed:
        mouse.release(click_button)
        hold_pressed = False

def update_settings(event=None):
    """Perbarui pengaturan delay dan tombol klik."""
    global min_delay, max_delay, click_button
    try:
        min_delay = float(min_delay_entry.get())
        max_delay = float(max_delay_entry.get())
        click_button = Button.left if click_button_var.get() == "Left" else Button.right
        settings_status.config(text="Settings updated!", foreground="green")
    except ValueError:
        settings_status.config(text="Invalid input!", foreground="red")

def update_timer_display():
    """Perbarui tampilan timer di GUI."""
    if timer_running and timer_seconds > 0:
        elapsed_time = int(time.time() - start_time)
        remaining_time = max(0, timer_seconds - elapsed_time)
        timer_label.config(text=f"Timer: {remaining_time}s", foreground="blue")
        if remaining_time == 0:
            stop_clicking()
    else:
        timer_label.config(text="Timer: Not Started", foreground="black")

def countdown_timer():
    """Menampilkan countdown timer."""
    if timer_running and timer_seconds > 0:
        elapsed_time = int(time.time() - start_time)
        remaining_time = max(0, timer_seconds - elapsed_time)
        if remaining_time <= 0:
            timer_label.config(text="Timer: Finished", foreground="red")
            stop_clicking()
        else:
            timer_label.config(text=f"Timer: {remaining_time}s", foreground="blue")
            root.after(1000, countdown_timer)

def on_key_press(key):
    """Tangani shortcut keyboard untuk start/stop."""
    global clicking
    if key == start_stop_key:
        if clicking:
            stop_clicking()
        else:
            start_clicking()

def set_custom_shortcut():
    """Memulai proses pengaturan shortcut."""
    custom_status.config(text="Press any key to set as shortcut...", foreground="blue")
    root.bind("<Key>", capture_shortcut)

def capture_shortcut(event):
    """Tangani input key untuk mengatur shortcut."""
    global start_stop_key
    if event.char:
        start_stop_key = KeyCode(char=event.char)
        custom_status.config(text=f"Shortcut: '{event.char}'", foreground="green")
    else:
        custom_status.config(text="Invalid key!", foreground="red")
    root.unbind("<Key>")

def mode_changed():
    """Update UI saat mode berubah."""
    if mode.get() == "AutoClick":
        min_delay_entry.config(state="normal")
        max_delay_entry.config(state="normal")
        mode_status.config(text="Mode: Auto Click", foreground="blue")
    else:
        min_delay_entry.config(state="disabled")
        max_delay_entry.config(state="disabled")
        mode_status.config(text="Mode: Hold Click", foreground="blue")

# Mulai thread untuk auto clicker
click_thread = threading.Thread(target=clicker, daemon=True)
click_thread.start()

# Layout Utama menggunakan grid
main_frame = ttk.Frame(root)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Row 0: Mode Frame (Paling Atas, ditengahkan)
mode_frame_top = ttk.LabelFrame(main_frame, text="Mode")
mode_frame_top.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)
mode_frame_top.columnconfigure(0, weight=1)
mode_frame_top.columnconfigure(1, weight=1)
ttk.Radiobutton(mode_frame_top, text="Auto Click", variable=mode, value="AutoClick", command=mode_changed).grid(row=0, column=0, padx=10, pady=5, sticky="e")
ttk.Radiobutton(mode_frame_top, text="Hold Click", variable=mode, value="HoldClick", command=mode_changed).grid(row=0, column=1, padx=10, pady=5, sticky="w")
mode_status = ttk.Label(mode_frame_top, text="Mode: Auto Click", foreground="blue")
mode_status.grid(row=1, column=0, columnspan=2, pady=5)

# Row 1: Top Settings Frame (Delay Settings di kiri, Timer Settings di kanan)
settings_frame = ttk.Frame(main_frame)
settings_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=10)

# Delay Settings (kiri)
delay_frame = ttk.LabelFrame(settings_frame, text="Delay Settings")
delay_frame.grid(row=0, column=0, sticky="w", padx=10)
ttk.Label(delay_frame, text="Min Delay (sec):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
min_delay_entry = ttk.Entry(delay_frame, width=10)
min_delay_entry.insert(0, str(min_delay))
min_delay_entry.grid(row=0, column=1, padx=5, pady=2)
min_delay_entry.bind("<Return>", update_settings)
ttk.Label(delay_frame, text="Max Delay (sec):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
max_delay_entry = ttk.Entry(delay_frame, width=10)
max_delay_entry.insert(0, str(max_delay))
max_delay_entry.grid(row=1, column=1, padx=5, pady=2)
max_delay_entry.bind("<Return>", update_settings)
ttk.Label(delay_frame, text="Click Button:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
click_button_option = ttk.OptionMenu(delay_frame, click_button_var, "Left", "Left", "Right")
click_button_option.grid(row=2, column=1, padx=5, pady=2)
click_button_var.trace_add("write", update_settings)
settings_status = ttk.Label(delay_frame, text="", foreground="black")
settings_status.grid(row=3, column=0, columnspan=2, sticky="w", padx=5, pady=2)

# Timer Settings (kanan)
timer_settings_frame = ttk.LabelFrame(settings_frame, text="Timer Settings")
timer_settings_frame.grid(row=0, column=1, sticky="e", padx=10)
ttk.Label(timer_settings_frame, text="Set Timer (sec, 0 for unlimited):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
timer_entry = ttk.Entry(timer_settings_frame, width=10)
timer_entry.insert(0, "0")
timer_entry.grid(row=0, column=1, padx=5, pady=2)
timer_label = ttk.Label(timer_settings_frame, text="Timer: Not Started", foreground="black")
timer_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=2)

# Row 2: Control Frame (Tengah, tombol Start/Stop)
control_frame = ttk.LabelFrame(main_frame, text="Control")
control_frame.grid(row=2, column=0, columnspan=2, pady=20)
start_button = ttk.Button(control_frame, text="Start Clicking", command=start_clicking)
start_button.grid(row=0, column=0, padx=20, pady=10)
stop_button = ttk.Button(control_frame, text="Stop Clicking", command=stop_clicking)
stop_button.grid(row=0, column=1, padx=20, pady=10)

# Row 3: Shortcut Settings (Bawah, ditengahkan; tombol di atas dan label di bawah)
shortcut_frame = ttk.LabelFrame(main_frame, text="Shortcut Settings")
shortcut_frame.grid(row=3, column=0, columnspan=2, pady=10)
ttk.Button(shortcut_frame, text="Set Custom Shortcut", command=set_custom_shortcut).grid(row=0, column=0, padx=10, pady=5)
custom_status = ttk.Label(shortcut_frame, text="Shortcut: 's'", foreground="black")
custom_status.grid(row=1, column=0, padx=10, pady=5)

# Keyboard Listener (dijalankan di thread terpisah)
listener_thread = threading.Thread(target=lambda: Listener(on_press=on_key_press).start(), daemon=True)
listener_thread.start()

mode_changed()
root.mainloop()
