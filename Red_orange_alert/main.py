import cv2
import numpy as np
import http.client, urllib


# Open the webcam (0 = default camera)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to capture frame")
        break

    # Convert BGR frame to HSV
    HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define red color range
    lower = np.array([0, 100, 100])
    upper = np.array([10, 255, 255])

    # Create a mask
    Red_mask = cv2.inRange(HSV, lower, upper)
    result = cv2.bitwise_and(frame, frame, mask=Red_mask)

    # Find contours
    contours, _ = cv2.findContours(Red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) > 300:  # Filter small noise
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # Display the results
    cv2.imshow("Tracking Red Color", frame)
    cv2.imshow("Mask", Red_mask)

    # Exit loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

