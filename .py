import cv2
import winsound
import time
import tkinter as tk
from tkinter import Label, Frame, font
from PIL import Image, ImageTk

class DrowsinessDetectorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Driver Drowsiness Detection - Engineer Muslim")

        
        self.title_font = font.Font(family="Arial", size=18, weight="bold")
        self.status_font = font.Font(family="Segoe UI", size=12)
        self.alert_font = font.Font(family="Segoe UI", size=14, weight="bold")
        self.primary_color = "#e0f7fa"  
        self.secondary_color = "#ffffff" 
        self.alert_color = "#f44336"    
        self.warning_color = "#ff9800"  
        self.ok_color = "#4caf50"       
        self.closed_eyes_color = "#ffeb3b" 

        master.config(bg=self.primary_color)

        main_frame = Frame(master, bg=self.primary_color, padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")

        title_label = Label(main_frame, text="Driver Drowsiness Detection", font=self.title_font, bg=self.primary_color, fg="#1976d2") 
        title_label.pack(pady=(0, 10))
        name_label = Label(main_frame, text="- Engineer Muslim -", font=self.status_font, bg=self.primary_color, fg="#757575") 
        name_label.pack(pady=(0, 15))

        self.video_frame = Frame(main_frame, bg=self.secondary_color, bd=2, relief="groove")
        self.video_frame.pack(pady=(0, 15), fill="x", expand=True)
        self.video_label = Label(self.video_frame)
        self.video_label.pack(padx=10, pady=10)

        status_frame = Frame(main_frame, bg=self.secondary_color, bd=2, relief="groove")
        status_frame.pack(pady=(0, 15), fill="x")
        self.status_label = Label(status_frame, text="Camera is running...", font=self.status_font, bg=self.secondary_color, padx=15, pady=15, anchor="w") 
        self.status_label.pack(fill="x")

        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.cap = cv2.VideoCapture(0)
        self.sleep_counter = 0
        self.threshold = 10  
        self.alarm_active = False
        self.beeping = False  

        self.update_frame()

    def play_alarm_sound(self):
        if self.alarm_active and not self.beeping:
            try:
                winsound.Beep(1200, 500)  # Frequency 1200 Hz, Duration 0.5 seconds (adjust as needed)
                self.beeping = True
                self.master.after(1000, self.reset_beep_flag) # Reset beep flag after a short delay
            except Exception as e:
                print(f"Error playing sound: {e}")
        if self.alarm_active:
            self.master.after(2000, self.play_alarm_sound) # Repeat alarm every 2 seconds

    def reset_beep_flag(self):
        self.beeping = False

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.status_label.config(text="Failed to read frame from camera.", fg=self.alert_color)
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        eyes_detected = False
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = frame[y:y + h, x:x + w]
            eyes = self.eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=3, minSize=(20, 20)) 
            if len(eyes) > 0:
                eyes_detected = True
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (255, 0, 0), 2)
                break

        if len(faces) == 0:
            self.status_label.config(text="❌ Face not clear, not checking for sleep.", fg=self.warning_color, font=self.status_font)
            self.alarm_active = False # Stop alarm if face is not clear
            self.sleep_counter = 0
        elif eyes_detected:
            self.sleep_counter = 0
            self.alarm_active = False 
            self.status_label.config(text="👀 Eyes are open.", fg=self.ok_color, font=self.status_font)
        else:
            self.sleep_counter += 1
            self.status_label.config(text=f"😴 Eyes closed for {self.sleep_counter} frames.", fg=self.closed_eyes_color, font=self.status_font)

        if self.sleep_counter >= self.threshold and not self.alarm_active:
            self.status_label.config(text="🚨 ALERT: Driver might be drowsy! 🚨", fg=self.alert_color, font=self.alert_font)
            self.alarm_active = True
            self.play_alarm_sound() 
        elif self.sleep_counter < self.threshold:
            self.alarm_active = False 

        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.config(image=imgtk)
        self.video_label.after(10, self.update_frame)

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()

root = tk.Tk()
gui = DrowsinessDetectorGUI(root)
root.mainloop()
