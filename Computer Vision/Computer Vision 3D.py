import cv2
import numpy as np
from pupil_apriltags import Detector
import computer_vision_2d as cv2d

cap = cv2.VideoCapture(0)
detector = Detector(families='tag36h11')


def transform_points():
    coords_to_transform = [top_left, top_right, bottom_left, bottom_right]

    coords_transformed = []

    for coord in coords_to_transform:
        # Create a homogeneous coordinates matrix for the point
        homogeneous_point = np.array([[int(coord[0])], [int(coord[1])], [1]])

        # Transform the point using the perspective transformation matrix
        transformed_homogeneous_point = np.dot(matrix, homogeneous_point)

        # Convert the transformed point back to 2D coordinates
        transformed_x = int(transformed_homogeneous_point[0, 0] / transformed_homogeneous_point[2, 0])
        transformed_y = int(transformed_homogeneous_point[1, 0] / transformed_homogeneous_point[2, 0])
        coords_transformed.append([transformed_x, transformed_y])

    return coords_transformed


# List of corner tag IDs to detect
target_tag_ids = [12, 13, 7, 6]  # [Top Left, Bottom Left, Bottom Right, Top Right]

while True:
    ret, frame = cap.read()

    top_left = (100, 100)
    top_right = (400, 100)
    bottom_left = (100, 500)
    bottom_right = (400, 500)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # grayscale (Necessary)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)  # Removes Gaussian Noise
    adaptive_thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 11, 2)  # Accounts for variation in lighting

    # Detect all April tags in the frame
    detections = detector.detect(adaptive_thresh)

    # Filter detections for specific tag IDs
    filtered_detections = [detection for detection in detections if detection.tag_id in target_tag_ids]

    # Draw lines based on corner coordinates
    if len(filtered_detections) == len(target_tag_ids):
        # Initialize points of the rectangle
        tag_corners_dict = {}

        for detection in filtered_detections:
            cv2.putText(frame, str(detection.tag_id), (int(detection.center[0]), int(detection.center[1])),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            tag_id = detection.tag_id
            tag_corners = detection.corners

            # Store corners in the dictionary
            tag_corners_dict[tag_id] = tag_corners

        if len(tag_corners_dict) == len(target_tag_ids):
            # Initialize points of the rectangle
            top_left = bottom_left = bottom_right = top_right = None

            for tag_id, tag_corners in tag_corners_dict.items():
                for i, corner in enumerate(tag_corners):
                    x, y = corner.ravel()
                    if tag_id == target_tag_ids[0] and i == 0:
                        top_left = (x, y)
                    elif tag_id == target_tag_ids[1] and i == 0:
                        bottom_left = (x, y)
                    elif tag_id == target_tag_ids[2] and i == 3:
                        bottom_right = (x, y)
                    elif tag_id == target_tag_ids[3] and i == 0:
                        top_right = (x, y)

                    # Draws the corner points:
                    cv2.circle(frame, (int(x), int(y)), 3, (0, 255, 0), -1)

        pts1 = np.float32([top_left, top_right, bottom_left, bottom_right])

        max_x = max(pts1[:, 0])
        max_y = max(pts1[:, 1])

        pts2 = np.float32([[0, 0], [max_x, 0], [0, max_y], [max_x, max_y]])
        matrix = cv2.getPerspectiveTransform(pts1, pts2)

        result = cv2.warpPerspective(frame, matrix, (int(max_x), int(max_y)))

        top_left, top_right, bottom_left, bottom_right = transform_points()


        gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)  # grayscale (Necessary)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)  # Removes Gaussian Noise
        adaptive_thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                cv2.THRESH_BINARY, 11, 2)  # Accounts for variation in lighting

        #Calculate midpoints
        mid1_x = int((top_left[0] + top_right[0]) / 2)
        mid1_y = int((top_left[1] + top_right[1]) / 2)
        mid2_x = int((bottom_left[0] + bottom_right[0]) / 2)
        mid2_y = int((bottom_left[1] + bottom_right[1]) / 2)

        # Draw lines to create rectangle
        if all(point is not None for point in [top_left, bottom_left, bottom_right, top_right]):
            cv2d.draw_bounding_box(result, top_left, bottom_left, bottom_right, top_right)
            cv2d.draw_vertical_lines(result, top_left, bottom_left, bottom_right, top_right, mid1_x, mid1_y,
                                     mid2_x, mid2_y)
            #cv2d.identify_apriltag_area(detection_2d, target_tag_ids, result, top_left, bottom_left, bottom_right,
                                #        top_right, mid1_x, mid1_y, mid2_x, mid2_y)

        cv2.imshow("Perspective transform", result)

    cv2.imshow('Frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()

