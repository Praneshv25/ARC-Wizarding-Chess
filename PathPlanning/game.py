import wizboard
import chess
from PythonServer import  ESPServer

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

    def run(self):
        while True:
            print(self.board)
            try:
                move = input(f'Type \'robots\' to turn robots {"on" if not self.robots_active else "off"}\n{"White" if self.board.turn == chess.WHITE else "Black"} move:')
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
            

server = ESPServer()
game = Game(server)
game.run()