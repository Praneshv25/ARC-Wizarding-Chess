class Quadrant:
    """
    Creates the visualization for its quadrant of its board
    """
    def __init__(self, camera_index, quadrant_num, tags_corner):
        """

        @param camera_index:
        @param quadrant_num: 0, 1, 2, or 3
        @param tags_list: {top_left: specified corner, top_right: specified corner,
        bottom_left: specified corner, bottom_right: specified corner}
        """
        self.camera_index = camera_index
        self.quadrant_num = quadrant_num
        self.tags_corner = tags_corner

    # create function that
