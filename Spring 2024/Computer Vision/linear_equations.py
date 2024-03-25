import numpy as np


def get_slope(x1, y1, x2, y2):
    """
    Calculates slope
    :param x1: x coordinate of point 1
    :param y1: y coordinate of point 1
    :param x2: x coordinate of point 2
    :param y2: y coordinate of point 2
    :return: slope of line (m)
    """

    if (x2 - x1) == 0:
        return 0
    return (y2 - y1) / (x2 - x1)


def get_y_intercept(x1, y1, m):
    """
    Calculates y_intercept
    :param x1: x coordinate
    :param y1: y coordinate
    :param m: slope
    :return: y-intercept (b)
    """
    return y1 - (m * x1)


def get_new_point(distance, angle, point):
    """
    Gets the new point relative to the old point for the given distance
    :param distance:
    :param angle: in degrees of rotation of the bounding box
    :param point: list of x and y coordinate
    :return: point in the form of x and y coordinate
    """
    x1 = point[0] + distance * np.cos(np.deg2rad(angle))
    y1 = point[1] + distance * np.sin(np.deg2rad(angle))
    return [x1, y1]


def get_x(line, y_coordinate):
    """
    Returns the x coordinate for a given y_coordinate in a line
    :param line: list of (x1, y1, x2, y2)
    :param y_coordinate:
    :return: x coordinate
    """
    slope = get_slope(line[0], line[1], line[2], line[3])
    y_intercept = get_y_intercept(line[0], line[1], slope)

    if slope == 0:
        return 1
    return (y_coordinate - y_intercept) / slope


def get_y(line, x_coordinate):
    """
    Returns the y coordinate for a given x_coordinate in a line
    :param line: list of (x1, y1, x2, y2)
    :param x_coordinate:
    :return: y coordinate
    """
    slope = get_slope(line[0], line[1], line[2], line[3])
    y_intercept = get_y_intercept(line[0], line[1], slope)

    return (slope * x_coordinate) + y_intercept


def in_boundary(tag_center, line_top, line_bottom, line_right, line_left):
    """
    This function calculates whether a tag is within a boundary
    :param tag_center: List of center coordinates of tag (x,y)
    :param line_top: List of coordinates needed to make line (x1,y1,x2,y2)
    :param line_bottom: List of coordinates needed to make line (x1,y1,x2,y2)
    :param line_right: List of coordinates needed to make line (x1,y1,x2,y2)
    :param line_left: List of coordinates needed to make line (x1,y1,x2,y2)
    :return: Whether the tag is in the boundary
    """
    within_boundary = False

    tag_x = tag_center[0]
    tag_y = tag_center[1]

    # Upper Limit
    if ((tag_y >= get_y(line_top, tag_x)) and (tag_y <= get_y(line_bottom, tag_x)) and
        (tag_x >= get_x(line_left, tag_y)) and (tag_x <= get_x(line_right, tag_y))):
        within_boundary = True

    return within_boundary
