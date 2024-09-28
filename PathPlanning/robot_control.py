import math

COUNTS_PER_SQUARE = 10500
PASSWORD = bytearray([ord('W'), ord('I'), ord('Z')])

class Robot():

    def __init__(self, id, position, angle, server, device_id):
        self.id = id
        self.position = position
        self.server = server
        self.device_id = device_id

        # Angle is measured counterclockwise from horizontal
        self.angle = angle
        self.initial_angle = angle

        self.buffer = bytearray()

    def __repr__(self):
        return self.id
    
    # ALL COMMANDS ONLY ADD MOVEMENT TO BUFFER, BUT STILL AFFECT ROBOT POSITION VALUES BEFORE BUFFER IS SENT / MOVEMENT IS MADE. 
    # send_buffer() MUST BE USED FOR COMMAND TO BE SENT TO ROBOT
    # THIS MEANS Robot.position DOES NOT REFLECT ACTUAL POSITION OF ROBOT, THIS NEEDS TO BE DERIVED FROM COMPUTER VISION.
    
    # Robot.position is the hypothetical position of the robot after all buffered moves are executed

    # BYTE ARRAY FORMAT
    # First byte -> command (1 = move, 2 = turn)
    # 
    # Moving
    # - Second/third byte -> distance 
    #    (float distance in terms of squares or integer # of encoder counts?)
    #
    # Turning
    # - Second/third byte -> angle (in degrees) (signed int)
    # - need 2 bytes because 180 > 128 and negative values being used

    def send_buffer(self):
        if self.server:
            self.server.send_command(self.device_id, PASSWORD + self.buffer + bytearray([3]))
        self.buffer = bytearray()
        
    def move(self, distance):
        encoder_counts = distance * COUNTS_PER_SQUARE / 100
        command = bytearray([1, 0]) + bytearray(int(encoder_counts).to_bytes(2, byteorder="big"))
        print(command)
        self.buffer += command
    
    def turn(self, angle):
        # 1 = clockwise, 0 = counterclockwise
        # positive angle is counterclockwise, negative is clockwise
        # Negative numbers are represented with two's complement, to be interpreted by arduino
        if angle == 0:
            return
        
        command_angle = int(angle if angle > 0 else -angle)
        command = bytearray([2, 0 if angle > 0 else 1]) + bytearray(command_angle.to_bytes(1, byteorder="big")) + bytearray([0])
        print(command)
        self.buffer += command
        self.angle += angle
        self.angle = self.angle % 360

    def turn_to(self, angle):
        angle = angle % 360
        turn_angle = angle - self.angle
        if turn_angle > 180:
            turn_angle = -360 + turn_angle
        elif turn_angle < -180:
            turn_angle = 360 + turn_angle
        
        self.turn(turn_angle)

    def move_to(self, position):
        if self.position[0] == position[0]:
            angle = 90 if position[1] > self.position[1] else -90
        else:
            angle = math.degrees(math.atan((position[1] - self.position[1]) / (position[0] - self.position[0])))

        if position[0] < self.position[0]:
            angle += 180
        self.turn_to(angle)
        self.move(math.dist(self.position, position))
        self.position = position

    def face_forward(self):
        self.turn_to(self.initial_angle)

    def execute_path(self, path_points):
        print(f'Moving: {self.id} from {self.position} to {path_points[-1]}')
        for point in path_points:
            self.move_to(point)
            print(self.position)
            print(self.angle)
            print(f"Moved to {point}")
        self.face_forward()
        print(self.position)
        print(self.angle)
        print("Finished Path")