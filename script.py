import tkinter as tk
from tkinter import messagebox
import cv2
import numpy as np
import pygame
from PIL import Image, ImageTk

VIDEO = "badapple.mp4"
AUDIO = "badapple_audio.mp3"

W, H = 120, 66
SCALE = 5
TARGET_FPS = 30
FRAME_TIME = 1 / TARGET_FPS
THRESHOLD = 140

root = tk.Tk()
root.withdraw()

# frame caching
frames = []
cap = cv2.VideoCapture(VIDEO)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    small = cv2.resize(gray, (W, H), interpolation=cv2.INTER_AREA)
    bw = ((small > THRESHOLD) * 255).astype(np.uint8)
    frames.append(bw)

cap.release()
TOTAL_FRAMES = len(frames)

# msgbox
messagebox.showinfo(
    "Bad Apple",
    "Bad Apple is fully loaded in RAM!\nClick OK to play."
)

# audio
pygame.mixer.init()
pygame.mixer.music.load(AUDIO)

# window
root.deiconify()
root.title("Bad Apple")

canvas = tk.Canvas(
    root,
    width=W * SCALE,
    height=H * SCALE,
    bg="black",
    highlightthickness=0
)
canvas.pack()

img = Image.fromarray(frames[0], "L")
photo = ImageTk.PhotoImage(
    img.resize((W * SCALE, H * SCALE), Image.NEAREST)
)
img_id = canvas.create_image(0, 0, anchor="nw", image=photo)
canvas.image = photo

speed_text = canvas.create_text(
    5,
    H * SCALE - 5,
    anchor="sw",
    text="1.00x",
    fill="lime",
    font=("Consolas", 18, "bold")
)

started = False

# render loop
def update():
    global started

    if not started:
        pygame.mixer.music.play()
        started = True

    # if audio ended -> close
    if not pygame.mixer.music.get_busy():
        root.destroy()
        return

    audio_time = pygame.mixer.music.get_pos() / 1000.0
    if audio_time < 0:
        root.after(1, update)
        return

    target_frame = int(audio_time * TARGET_FPS)
    if target_frame >= TOTAL_FRAMES:
        root.destroy()
        return

    img = Image.fromarray(frames[target_frame], "L")
    photo = ImageTk.PhotoImage(
        img.resize((W * SCALE, H * SCALE), Image.NEAREST)
    )
    canvas.itemconfig(img_id, image=photo)
    canvas.image = photo

    expected_time = target_frame * FRAME_TIME
    speed = audio_time / expected_time if expected_time > 0 else 1.0

    canvas.itemconfig(
        speed_text,
        text=f"{speed:.2f}x",
        fill="lime" if speed >= 0.95 else "red"
    )

    root.after(1, update)

update()
root.mainloop()
