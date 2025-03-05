import cv2
from pyapriltags import Detector

detector = Detector(families='tag36h11')

    # Open a connection to the camera (camera index 0 usually refers to the default built-in camera)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    # Image tuning to recognize tags more accurately
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # grayscale (Necessary)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)  # Removes Gaussian Noise
    adaptive_thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 11, 2)  # Accounts for variation in lighting

    # Detect all April tags in the frame
    detections = detector.detect(adaptive_thresh)
    for detection in detections:
        cv2.putText(frame, str(detection.tag_id), (int(detection.center[0]), int(detection.center[1])),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow('Frame', frame)
