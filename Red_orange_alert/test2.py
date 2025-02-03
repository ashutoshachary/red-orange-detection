import cv2
import numpy as np
import http.client, urllib
import time

# Open the webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

last_sent_time = 0
delay = 5


def send_pushover_message(color):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
                 urllib.parse.urlencode({
                     "token": "asfnkakm2iucmi3a629k4svv6tmvfv",
                     "user": "uevbaowm1c5dfqmgva6ai7tv4q5mot",
                     "message": f"{color} Color Detected!",
                 }), {"Content-type": "application/x-www-form-urlencoded"})
    conn.getresponse()
    print(f"{color} notification sent!")


def detect_color(frame, HSV, lower, upper, color_name, color_bgr):
    # Create a mask
    mask = cv2.inRange(HSV, lower, upper)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    detected = False

    for contour in contours:
        if cv2.contourArea(contour) > 300:
            x, y, w, h = cv2.boundingRect(contour)
            # Draw rectangle around the detected color
            cv2.rectangle(frame, (x, y), (x + w, y + h), color_bgr, 2)
            # Add label above the rectangle
            cv2.putText(frame, color_name, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_bgr, 2, cv2.LINE_AA)
            detected = True

    return detected, mask


while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame")
        break

    # Convert frame to HSV
    HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define color ranges
    # Red color range (using two ranges due to how red wraps around in HSV)
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])

    # Orange color range
    lower_orange = np.array([11, 100, 100])
    upper_orange = np.array([25, 255, 255])

    # Detect red (combining two ranges)
    red_detected1, red_mask1 = detect_color(frame, HSV, lower_red1, upper_red1, "Red", (0, 0, 255))
    red_detected2, red_mask2 = detect_color(frame, HSV, lower_red2, upper_red2, "Red", (0, 0, 255))
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)
    red_detected = red_detected1 or red_detected2

    # Detect orange
    orange_detected, orange_mask = detect_color(frame, HSV, lower_orange, upper_orange, "Orange", (0, 165, 255))

    # Combine masks for display
    combined_mask = cv2.bitwise_or(red_mask, orange_mask)

    current_time = time.time()
    if (red_detected or orange_detected) and (current_time - last_sent_time > delay):
        # Uncomment to enable notifications
        if red_detected:
            send_pushover_message("Red")
        if orange_detected:
            send_pushover_message("Orange")
        last_sent_time = current_time

    # Show detection message
    if red_detected or orange_detected:
        messages = []
        if red_detected:
            messages.append("Red")
        if orange_detected:
            messages.append("Orange")
        message = " and ".join(messages) + " Color Detected!"

        cv2.rectangle(frame, (50, 50), (400, 150), (0, 0, 255), -1)
        cv2.putText(frame, message, (60, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.imshow("Color Tracking", frame)
    cv2.imshow("Mask", combined_mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()