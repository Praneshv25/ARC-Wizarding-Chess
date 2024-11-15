import wizboard
import chess
from PythonServer import  ESPServer
import visualGUI as gui

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
        visualGUI.createVisualBoard()
        while True:
            move = visualGUI.main(self.robots_active)
            if move != None:
                print(move)
                try:
                    if move == "robots":
                        self.robots_active = not self.robots_active
                        print(f"robots_active: {self.robots_active}")
                        if self.robots_active:
                            self.board.assume_correct_positions()
                            print("Make sure robot positions align with board")
                        visualGUI.finishInvalidMove() 
                    elif move == "invalid move":
                        visualGUI.finishInvalidMove() 
                    else:
                        parsedMove = chess.Move.from_uci(self.board.parse_san(move[0:4]).uci())
                        self.make_move(parsedMove)
                        visualGUI.finishMove(move[5:6], move[7:8])
                        print("MOVE MADE")
                        print(self.board)
                except ValueError: 
                    if move == 'quit':
                        break
                    print("invalid move")       
                    visualGUI.finishInvalidMove()     
            

server = ESPServer()
game = Game(server)
visualGUI = gui.VisualGUI(1000, 800)
visualGUI.initialize()
game.run()