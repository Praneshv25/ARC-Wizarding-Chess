import cv2
import numpy as np
from pupil_apriltags import Detector
import linear_equations as le
import board as bd


def main():
    # Create an AprilTag detector
    detector = Detector(families='tag36h11')

    # Open a connection to the camera (camera index 0 usually refers to the default built-in camera)
    cap = cv2.VideoCapture(0)

    # List of corner tag IDs to detect
    target_tag_ids = [12, 13, 7, 6]  # [Top Left, Bottom Left, Bottom Right, Top Right]

    while True:
        # Capture a frame from the camera
        ret, frame = cap.read()

        # Image tuning to recognize tags more accurately
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

                # Calculate midpoints
                mid1_x = int((top_left[0] + top_right[0]) / 2)
                mid1_y = int((top_left[1] + top_right[1]) / 2)
                mid2_x = int((bottom_left[0] + bottom_right[0]) / 2)
                mid2_y = int((bottom_left[1] + bottom_right[1]) / 2)

                # Draw lines to create rectangle
                if all(point is not None for point in [top_left, bottom_left, bottom_right, top_right]):
                    draw_bounding_box(frame, top_left, bottom_left, bottom_right, top_right)
                    draw_vertical_lines(frame, top_left, bottom_left, bottom_right, top_right, mid1_x, mid1_y,
                                        mid2_x, mid2_y)
                    identify_apriltag_area(detections, target_tag_ids, frame, top_left, bottom_left, bottom_right,
                                           top_right, mid1_x, mid1_y, mid2_x, mid2_y)

        else:
            cv2.putText(frame, "Not all tags detected!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Display the frame with lines forming rectangle and tag IDs
        cv2.imshow('Chess Board Boundaries', frame)

        # Break the loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close all windows
    cap.release()
    cv2.destroyAllWindows()


def draw_bounding_box(frame, top_left, bottom_left, bottom_right, top_right):
    """
    Function draws bounding rectangle around 4 designated april tags
    :param frame: Camera feed
    :param top_left: top-left coordinate of rectangle
    :param bottom_left: bottom-left coordinate of rectangle
    :param bottom_right: bottom-right coordinate of rectangle
    :param top_right: top-right coordinate of rectangle
    """
    cv2.line(frame, tuple(map(int, top_left)), tuple(map(int, bottom_left)), (255, 0, 0), 2)
    cv2.line(frame, tuple(map(int, bottom_left)), tuple(map(int, bottom_right)), (255, 0, 0), 2)
    cv2.line(frame, tuple(map(int, bottom_right)), tuple(map(int, top_right)), (255, 0, 0), 2)
    cv2.line(frame, tuple(map(int, top_right)), tuple(map(int, top_left)), (255, 0, 0), 2)


def draw_vertical_lines(frame, top_left, bottom_left, bottom_right, top_right, mid1_x, mid1_y, mid2_x, mid2_y):
    """
    Draw vertical lines for chessboard
    :param frame: Camera feed
    :param top_left: top-left coordinate of rectangle
    :param bottom_left: bottom-left coordinate of rectangle
    :param bottom_right: bottom-right coordinate of rectangle
    :param top_right: top-right coordinate of rectangle
    :param mid1_x:
    :param mid1_y:
    :param mid2_x:
    :param mid2_y:
    :return:
    """
    # Draw midpoint line
    cv2.line(frame, (mid1_x, mid1_y), (mid2_x, mid2_y), (200, 0, 0), 2)

    # Calculate the delta x and delta y
    delta_x_bottom = bottom_right[0] - bottom_left[0]
    delta_y_bottom = bottom_right[1] - bottom_left[1]

    delta_x_top = top_right[0] - top_left[0]
    delta_y_top = top_right[1] - top_left[1]

    # Calculating angle of rotation for bottom line
    # Convert Cartesian coordinates to polar coordinates
    magnitude, angle_deg_bottom = cv2.cartToPolar(delta_x_bottom, delta_y_bottom)

    # Calculating angle of rotation for top line
    mag, angle_deg_top = cv2.cartToPolar(delta_x_top, delta_y_top)

    # Convert angle to degrees
    angle_deg_bottom = np.degrees(angle_deg_bottom)[0][0]
    angle_deg_top = np.degrees(angle_deg_top)[0][0]

    left_bound = [0, 0, 0, 0]
    right_bound = [0, 0, 0, 0]
    ranks = ['1', '2', '3', '4', '5', '6', '7', '8', '.']
    for i in range(-4, 5):
        distance_const = 45
        distance = i * distance_const
        bottom_point = [mid2_x, mid2_y]
        top_point = [mid1_x, mid1_y]

        new_bottom = le.get_new_point(distance, angle_deg_bottom, bottom_point)
        new_top = le.get_new_point(distance, angle_deg_top, top_point)

        if i == -4:
            left_bound = [new_top[0], new_top[1], new_bottom[0], new_bottom[1]]

        if i == 4:
            right_bound = [new_top[0], new_top[1], new_bottom[0], new_bottom[1]]

        cv2.line(frame, (int(new_bottom[0]), int(new_bottom[1])), (int(new_top[0]), int(new_top[1])),
                 (200, 0, 0), 2)
        if i != 4:
            cv2.putText(frame, str(ranks[i+4]), (int(new_top[0] + (distance_const / 2)), int(new_top[1] + (distance_const / 2))),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    draw_horizontal_lines(frame, left_bound, right_bound)


def draw_horizontal_lines(frame, left_bound, right_bound):
    """
    Draw horizontal lines for chess board
    :param frame: Camera feed
    :param left_bound: A tuple of (x1, y1, x2, y2) that represents coordinates for a line
    :param right_bound: A tuple of (x1, y1, x2, y2) that represents coordinates for a line
    """
    mid1_x = int((left_bound[0] + left_bound[2]) / 2)
    mid1_y = int((left_bound[1] + left_bound[3]) / 2)
    mid2_x = int((right_bound[0] + right_bound[2]) / 2)
    mid2_y = int((right_bound[1] + right_bound[3]) / 2)

    cv2.line(frame, (mid1_x, mid1_y), (mid2_x, mid2_y), (200, 0, 0), 2)

    delta_x_left = left_bound[0] - left_bound[2]
    delta_y_left = left_bound[1] - left_bound[3]

    delta_x_right = right_bound[0] - right_bound[2]
    delta_y_right = right_bound[1] - right_bound[3]

    magnitude, angle_deg_left = cv2.cartToPolar(delta_x_left, delta_y_left)
    magnitude, angle_deg_right = cv2.cartToPolar(delta_x_right, delta_y_right)

    angle_deg_left = np.degrees(angle_deg_left)[0][0]
    angle_deg_right = np.degrees(angle_deg_right)[0][0]

    files = [None, 'h', 'g', 'f', 'e', 'd', 'c', 'b', 'a']
    for i in range(-4, 5):
        distance_const = 45
        distance = i * distance_const
        left_point = [mid1_x, mid1_y]
        right_point = [mid2_x, mid2_y]

        new_left = le.get_new_point(distance, angle_deg_left, left_point)
        new_right = le.get_new_point(distance, angle_deg_right, right_point)

        cv2.line(frame, (int(new_left[0]), int(new_left[1])), (int(new_right[0]), int(new_right[1])),
                 (200, 200, 0), 2)
        if i != -4:
            cv2.putText(frame, str(files[i + 4]),
                    (int(new_left[0] - (distance_const / 2)), int(new_left[1] + (distance_const / 2))),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)


def identify_apriltag_area(detections, target_tag_ids, frame, top_left, bottom_left, bottom_right, top_right, mid1_x,
                           mid1_y, mid2_x, mid2_y):
    """
    Identifies if the unspecified april tags are in a designated area
    :param detections:
    :param target_tag_ids:
    :param frame:
    :param top_left:
    :param bottom_left:
    :param bottom_right:
    :param top_right:
    :param mid1_x:
    :param mid1_y:
    :param mid2_x:
    :param mid2_y:
    :return:
    """
    # Draw the IDs of tags not in target_tag_ids if they fall within the bounding box
    for detection in detections:
        if detection.tag_id not in target_tag_ids:
            cv2.putText(frame, str(detection.tag_id), (int(detection.center[0]), int(detection.center[1])),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            # Detection in area 1 (left)
            line_top = [top_left[0], top_left[1], mid1_x, mid1_y]
            line_bottom = [bottom_left[0], bottom_left[1], mid2_x, mid2_y]
            line_left = [bottom_left[0], bottom_left[1], top_left[0], top_left[1]]
            line_right = [mid2_x, mid2_y, mid1_x, mid1_y]
            if le.in_boundary(detection.center, line_top, line_bottom, line_right, line_left):
                cv2.putText(frame, "Area 1", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # Detection in area 2 right
            line_top = [mid1_x, mid1_y, top_right[0], top_right[1]]
            line_bottom = [mid2_x, mid2_y, bottom_right[0], bottom_right[1]]
            line_left = [mid2_x, mid2_y, mid1_x, mid1_y]
            line_right = [top_right[0], top_right[1], bottom_right[0], bottom_right[1]]

            if le.in_boundary(detection.center, line_top, line_bottom, line_right, line_left):
                cv2.putText(frame, "Area 2", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)


if __name__ == "__main__":
    main()
