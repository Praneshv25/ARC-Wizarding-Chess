import wizboard
import chess
from PythonServer import  ESPServer
import speech_movement

# ask for input
# chess bot moves?
# get path for moves
# command robots

class Game:
    def __init__(self, server=None):
        self.board = wizboard.WizBoard(server)
        self.robots_active = True

    def make_move(self, move: chess.Move):
        paths = self.board.push(move)
        if self.robots_active:
            for path in paths:
                path.piece.execute_path(path.points)
                path.piece.send_buffer()

    def check_board(self):
        if (self.board.is_checkmate()):
            return 1
        elif (self.board.is_check()):
            return 2
        elif (self.board.is_stalemate() or self.board.is_insufficient_material()):
            return 3
        else:
            return 0

    def run(self):
        while True:
            print(self.board)
            try:
                move = speech_movement.detect_moves()
                if move == "robots":
                    self.robots_active = not self.robots_active
                    print(f"robots_active: {self.robots_active}")
                    if self.robots_active:
                        self.board.assume_correct_positions()
                        print("Make sure robot positions align with board")
                else:
                    move = chess.Move.from_uci(self.board.parse_san(move).uci())
                    self.make_move(move)
            except ValueError: 
                if move == 'quit':
                    break
                print("invalid move")


            boardCheck = self.check_board()
            if boardCheck == 1:
                winner = "Black" if self.board.turn == chess.WHITE else "White"
                print(f"Checkmate! {winner} wins.")
                break
            elif boardCheck == 2:
                print("Check")
            elif boardCheck == 3:
                print("Draw")
                break
            

server = ESPServer()
game = Game(server)
game.run()