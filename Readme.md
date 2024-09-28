## Path Planning
- This code handles chess game management, path planning, and sending instructions to robots
- All chess logic is done using the python chess library: https://python-chess.readthedocs.io/en/latest/

## Control Code
- This is the code running on the raspberry pi picos and ESP01 wireless module
- "UDPSocketESP.ino" is uploaded to the ESP01 wireless transceiver
    - Opens a UDP connection to the "wizardschess" wifi network (password is same as network name)
        - you must set up the router and connect to this network to connect to the ESP from a computer
    - Communicates with pico using UART (TX and RX pins)
- "casePicoWirelessControl.ino" is uploaded to the raspberry pi pico on the robot
    - Listens for communication from serial port (connected to ESP)
    - 1st byte of data received from port = command executed (move, turn, stop)
    - Other bytes of data received from port = parameters (direction/distance, angle, duration of stop)

## Computer Vision
- This code detects positions of pieces using computer vision and april tags
- It defines a boundary rectangle by finding the april tags with specific IDs; this identifies the chess board
- Lines are then drawn using the 4 tags as reference to create every individual square on the board
- Other April Tags (which represent chess pieces) are then assigned to a region

## How it works:
1. game.py from path planning runs the chess game. It takes a move as input and sends it to a Wizboard object from wizboard.py.
2. Wizboard updates position of each piece and the chess game's state, and sends the move to PathPlanner object from path_planner.py
3. PathPlanner object determines how each robot must move to reflect the piece's new position on the chess board. These paths are returned to game.py
3. For each path, game.py calls:
    - path.piece.execute_path(path.points), which stores all of the instructions to send to the robot as an array of bytes
    - path.piece.send_buffer(), which uses code from PythonServer.py to send UDP packets over the "wizardschess" wifi network
4. Each piece's ESP recieves the UDP packet, then sends the data to the piece's Raspberry pi using UART.
5. The Raspberry pi interprets the packet as an instruction, and executes the moves using the control code

## To do:
1. Computer vision integration: 
    - the server should compare the robot's position (from computer vision) and ideal position (center of square or current position on path), and correct. For most accuracy, this should probably happen multiple times for each path. This could require some refactoring of robot_control.py. 
2. Accurate movement commands:
    - During gameplay, the amount the robots move / turn given a certain number of motor encoder counts is inconsistent, especially between different robots. Feedback from computer vision will help with this, but more solutions in the robot's control code is probably necessary.
    - the move_profile() function in the control code was a test at an idea of something to help this, implemented during last semester's last meeting. It is not finished. I do not remember if it worked, and if it did, I do not remember if it helped the problem at all.
3. Improved interface:
    - Right now, the game interface is just a python script running in the terminal. If somebody wanted to work on a better interface (display chess board, drag chess pieces, etc.), that would make the final product look a lot better.
          - to make moves in the current interface, write them in standard algebraic notation (https://en.wikipedia.org/wiki/Algebraic_notation_(chess))
    - Voice recognition and voice commands. This was part of original project description.
    - Play against chess bot. Right now, both players type moves.
          - The python chess library supports generating moves from an engine given the current board state. This would be very helpful for implementing this.
