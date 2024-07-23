import cv2
import numpy as np
import time
import os
import requests

def detect_significant_change(frame1, frame2, min_area=500, threshold=30):
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, threshold, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour) > min_area:
            return True
    return False

def play_sound():
    os.system("aplay /usr/share/sounds/alsa/Front_Center.wav")

def send_pushover_notification(title, message, image_path=None):
    url = "https://api.pushover.net/1/messages.json"
    data = {
        "token": "--------------------",
        "user": "---------------------",
        "title": title,
        "message": message
    }
    files = None
    if image_path:
        files = {
            "attachment": ("image.jpg", open(image_path, "rb"), "image/jpeg")
        }
    response = requests.post(url, data=data, files=files)
    if response.status_code != 200:
        print(f"Failed to send notification: {response.text}")

cap = cv2.VideoCapture(0)
time.sleep(2)  # Allow the camera to warm up

ret, frame1 = cap.read()
frame1_display = cv2.flip(frame1, 1)

last_alert_time = time.time()
last_alive_time = time.time()
alert_cooldown = 5  # Minimum time between alerts in seconds
alive_interval = 900  # 15 minutes in seconds

while True:
    ret, frame2 = cap.read()
    frame2_display = cv2.flip(frame2, 1)

    current_time = time.time()

    if detect_significant_change(frame1_display, frame2_display):
        if current_time - last_alert_time > alert_cooldown:
            print("Significant change detected!")
            play_sound()
            image_path = "/home/pi/captured_frame.jpg"
            cv2.imwrite(image_path, frame2)  # Save the original frame, not the flipped one
            send_pushover_notification("Bell Outlook", "New email detected!", image_path)
            last_alert_time = current_time

    # Check if it's time to send an "I am alive" notification
    if current_time - last_alive_time > alive_interval:
        print("Sending 'I am alive' notification")
        send_pushover_notification("System Status", "I am alive and monitoring")
        last_alive_time = current_time

    frame1_display = frame2_display.copy()
    frame1 = frame2.copy()  # Keep an unflipped copy for the next comparison

    # Remove the cv2.imshow and cv2.waitKey lines as they're not needed for headless operation

cap.release()
