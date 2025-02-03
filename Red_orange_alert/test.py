import cv2
import numpy as np
import http.client, urllib
import time

# Open the webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

last_sent_time = 0  # Track last sent message time
delay = 5  # Wait 5 seconds before sending another message

def send_pushover_message():
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
      urllib.parse.urlencode({
        "token": "asfnkakm2iucmi3a629k4svv6tmvfv",  # Replace with your actual token
        "user": "uevbaowm1c5dfqmgva6ai7tv4q5mot",  # Replace with your actual user key
        "message": "Red Color Detected!",
      }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()
    print("Notification sent!")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame")
        break

    # Convert frame to HSV
    HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define red color range
    lower = np.array([0, 100, 100])
    upper = np.array([10, 255, 255])

    # Create a mask
    Red_mask = cv2.inRange(HSV, lower, upper)

    # Find contours
    contours, _ = cv2.findContours(Red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    detected = False

    for contour in contours:
        if cv2.contourArea(contour) > 300:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            detected = True

    current_time = time.time()
    if detected and (current_time - last_sent_time > delay):
        # send_pushover_message()
        last_sent_time = current_time

    if detected:
        cv2.rectangle(frame, (50, 50), (400, 150), (0, 0, 255), -1)  # Red box
        cv2.putText(frame, "Red Color Detected!", (60, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.imshow("Tracking Red Color", frame)
    cv2.imshow("Mask", Red_mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
