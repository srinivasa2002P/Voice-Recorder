import tkinter as tk
from tkinter import messagebox, Listbox
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import simpleaudio as sa

# ---------------- GLOBAL VARIABLES ----------------
recording = False
fs = 44100
audio_data = []
recordings = []
play_obj = None

# ---------------- RECORDING FUNCTIONS ----------------
def start_recording():
    global recording, audio_data
    recording = True
    audio_data = []
    threading.Thread(target=record, daemon=True).start()
    messagebox.showinfo("Recording", "Recording Started")

def record():
    with sd.InputStream(samplerate=fs, channels=1, callback=callback):
        while recording:
            sd.sleep(100)

def callback(indata, frames, time, status):
    audio_data.append(indata.copy())
    update_waveform(indata)

def stop_recording():
    global recording
    recording = False

    if not audio_data:
        return

    audio_np = np.concatenate(audio_data, axis=0)

    # ✅ CONVERT FLOAT → INT16 (IMPORTANT FIX)
    audio_int16 = np.int16(audio_np / np.max(np.abs(audio_np)) * 32767)

    filename = f"recording_{len(recordings)+1}.wav"
    write(filename, fs, audio_int16)

    recordings.append(filename)
    listbox.insert(tk.END, filename)

    messagebox.showinfo("Saved", f"Saved as {filename}")

# ---------------- PLAYBACK ----------------
def play_audio(event=None):
    global play_obj
    selected = listbox.curselection()
    if not selected:
        return

    filename = listbox.get(selected[0])
    try:
        wave_obj = sa.WaveObject.from_wave_file(filename)
        play_obj = wave_obj.play()
    except Exception as e:
        messagebox.showerror("Error", str(e))

# ---------------- WAVEFORM ----------------
def update_waveform(data):
    ax.clear()
    ax.plot(data, color="black")
    ax.set_ylim(-1, 1)
    ax.set_title("Live Audio Waveform")
    canvas.draw_idle()

# ---------------- GUI ----------------
window = tk.Tk()
window.title("Voice Recorder")
window.geometry("650x520")

title = tk.Label(window, text="Python Voice Recorder",
                 font=("Arial", 16, "bold"))
title.pack(pady=10)

# Waveform
fig, ax = plt.subplots(figsize=(6.5, 2))
canvas = FigureCanvasTkAgg(fig, master=window)
canvas.get_tk_widget().pack()

# Buttons
btn_frame = tk.Frame(window)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Start Recording",
          bg="green", fg="white",
          font=("Arial", 11),
          width=15,
          command=start_recording).grid(row=0, column=0, padx=10)

tk.Button(btn_frame, text="Stop Recording",
          bg="red", fg="white",
          font=("Arial", 11),
          width=15,
          command=stop_recording).grid(row=0, column=1, padx=10)

# Saved Recordings
tk.Label(window, text="Saved Recordings",
         font=("Arial", 12)).pack(pady=5)

listbox = Listbox(window, width=55, height=8)
listbox.pack()
listbox.bind("<Double-Button-1>", play_audio)

tk.Label(window,
         text="Double-click a recording to play",
         font=("Arial", 9)).pack(pady=5)

window.mainloop()
