import chess
from path_planner import PathPlanner, get_rank, get_file
from robot_control import Robot

class WizBoard(chess.Board):
    def __init__(self, server=None) -> None:
        super().__init__()
        self.path_planner = PathPlanner(self)
        initial_board = ['R1', 'N1', 'B1', 'Q', 'K', 'B2', 'N2', 'R2',
                         'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8'] + \
                         [''] * 32 + \
                        ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8',
                         'r1', 'n1', 'b1', 'q', 'k', 'b2', 'n2', 'r2'] + \
                         [''] * 32
            # - this is to keep track of which specific knight/bishop/rook is where, chess module only tracks kind of piece.
            # - this is important because there is more than one black knight robot for example
        
        self.piece_list = []
        device_id = 0
        for i, piece_id in enumerate(initial_board):
            if piece_id != '':
                position = (get_file(i) + .5, get_rank(i) + .5)
                robot = Robot(piece_id, position, (-90 if get_rank(i) > 3 else 90), server, device_id)
                device_id += 1
            else:
                robot = None
            self.piece_list.append(robot)

        self.capture_counts = [0, 0]
    
    def assume_correct_positions(self):
        # set every robot's position data to the center of the square it should be on 
        for i, piece in enumerate(self.piece_list):
            if piece:
                piece.position = (get_file(i) + .5, get_rank(i) + .5)

    def get_capture_position(self):
        return chess.H8 + 1 + ((self.turn == chess.BLACK) * 16) + self.capture_counts[not self.turn]         
 
    def push(self, move: chess.Move) -> None:
        paths = self.path_planner.turn_paths(move)

        if self.is_capture(move):
            captured_position = self.get_capture_position()

            # need to fix en passant
            self.piece_list[captured_position] = self.piece_list[move.to_square]

            self.capture_counts[not self.turn] += 1

        # Handle Castle  (extra swaps)
        if self.is_castling(move):
            castle_rank = chess.square_rank(move.to_square)
            
            if chess.square_file(move.to_square) == 2:
                rook_start = chess.square(0, castle_rank)
                rook_end   = chess.square(3, castle_rank)
            else:
                rook_start = chess.square(7, castle_rank)
                rook_end   = chess.square(5, castle_rank)
            
            self.piece_list[rook_end] = self.piece_list[rook_start]
            self.piece_list[rook_start] = None
        
        # Standard Moves
        self.piece_list[move.to_square] = self.piece_list[move.from_square]
        self.piece_list[move.from_square] = None

        super().push(move)
        return paths

    # Undo move (won't be needed in gameplay, can be implemented for debugging)
    # def pop(self) -> None:
    #     super().pop()
        # update wizboard's data about specific pieces (pieces_list)