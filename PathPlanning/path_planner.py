import chess
from robot_control import Robot

class Path:
    def __init__(self, piece: Robot, points: list) -> None:
        self.piece = piece
        self.points = points
   
    def __repr__(self):
        return f'{self.piece}: {self.points}'

def get_rank(square):
    if square <= 63:
        rank = chess.square_rank(square)
    elif square <= 79:
        # Black pieces (white side)
        rank = (square - 64) // 4
    else:
        # White Pieces (black side)
        rank = 7 - (square - 80) // 4
    return rank

def get_file(square):
    if square <= 63:
        file = chess.square_file(square)
    elif square <= 79:
        # Black pieces (white side)
        file = 11 - (square - 64) % 4
    else:
        # White Pieces (black side)
        file = 11 - (square - 80) % 4
    return file

class PathPlanner():
    def __init__(self, board:chess.Board) -> None:
        self.board = board

    def turn_paths(self, move:chess.Move) -> list[Path]:
        '''
        Given move, generate Paths for in the order that they should be traveled
            - Paths contain active piece code (ex. 'p1') and list of points
            - ex. Capturing piece moves next to captured piece, captured piece
                  moves away, capturing piece moves to captured piece's spot 
        
        Returns list of tuples that contain (piece, [list of points])
        '''
        
        paths = []

        if not self.board.is_legal(move):
            return False
        
        piece_id = self.board.piece_list[move.from_square]

        # Handle Capture
        if self.board.is_capture(move):
            
            captured_position = self.board.get_capture_position()
            
            if self.board.is_en_passant(move):
                captured_piece_square = move.to_square + (8 * self.board.turn)
                captured_piece_id = self.board.piece_list[captured_piece_square]

                paths.append(Path(piece_id, self.single_path(move.from_square, move.to_square)))
                paths.append(Path(captured_piece_id, self.single_path(captured_piece_square, captured_position, move_type="LEAVE")))
                return paths
            else:
                captured_piece_id = self.board.piece_list[move.to_square]
                capture_path = self.single_path(move.from_square, move.to_square, move_type="CAPTURE")
                obstructed_edge = -1
                if type(capture_path[0]) == int:
                    obstructed_edge = capture_path[0]
                    capture_path = capture_path[1:]
                paths.append(Path(piece_id, capture_path))
                paths.append(Path(captured_piece_id, self.single_path(move.to_square, captured_position, move_type="LEAVE", obstructed_edge = obstructed_edge)))
                paths.append(Path(piece_id, self.single_path(move.to_square, move.to_square)))
                return paths

        # Handle Castle
        if self.board.is_castling(move):
            paths.append(Path(piece_id, self.single_path(move.from_square, move.to_square)))
            if self.board.is_kingside_castling(move):
                rook_id = self.board.piece_list[chess.square(7, chess.square_rank(move.from_square))]
                paths.append(Path(rook_id, self.single_path(move.from_square + 3, move.from_square + 1, move_type="CASTLE")))
            else:
                rook_id = self.board.piece_list[chess.square(0, chess.square_rank(move.from_square))]
                paths.append(Path(piece_id, self.single_path(move.from_square - 4, move.from_square - 1, move_type="CASTLE")))
            return paths
                
        
        # Handle Standard moves
        paths.append(Path(piece_id, self.single_path(move.from_square, move.to_square)))

        return paths
    
    def single_path(self, start:chess.Square, target:chess.Square, move_type="NORMAL", obstructed_edge = -1) -> list[tuple]:
        '''
        Given starting/target locations and a piece type, generate list of points
        a single piece needs to travel to
        
        Path should generally reflect how a player would move the piece
           - ex. diagonal vs straight and then right for a bishop
        
        Use self.board data to avoid other pieces on the board if necessary

        move_type: "NORMAL", "CASTLE", "CAPTURE", or "LEAVE"
        '''
        #Variables used for Knight movement
        startRank = get_rank(start) 
        startFile = get_file(start)
        endRank = get_rank(target)
        endFile = get_file(target)
        changeInRank = endRank - startRank
        changeInFile = endFile - startFile
        rankDirection = 1 if changeInRank > 0 else -1
        fileDirection = 1 if changeInFile > 0 else -1
        moveInbetween = False

        #Normal movement (includes knight move)
        if (move_type in ["NORMAL", "CAPTURE"]):

        #Knight movement: path planning 1 path, not both paths.
            if ((abs(changeInRank) == 2 and abs(changeInFile) == 1) or (abs(changeInFile) == 2 and abs(changeInRank) == 1)):
                currentRank = startRank + rankDirection
                currentFile = startFile + fileDirection
                #go through each square and see if there is a piece on the square
                while ((currentRank != endRank) or (currentFile != endFile)):
                    currentSquare = chess.square(currentFile, currentRank)
                    #if at any point there is a piece on the path, move inbetween squares, end loop
                    if self.board.piece_at(currentSquare) is not None:
                        moveInbetween = True
                        break
                    #should be one at a time, not both at once, fix this to check both paths
                    if (currentRank != endRank):
                        currentRank += rankDirection
                    if (currentFile != endFile):
                        currentFile += fileDirection
                #Locates the 'change square' of the L movement from the knight
                if (abs(changeInRank) == 2):
                    changeRank = startRank + (1.5 + 1 * (rankDirection == 1)) * rankDirection
                    changeFile = startFile + 1 * (fileDirection == 1) if moveInbetween else startFile + .5
                    #changeFile = startFile + fileDirection
                    startPosition = (changeFile, startRank + .5)
                    changePosition = (changeFile, changeRank)
                    if move_type == "CAPTURE":
                        endPosition = (endFile + 1 * (fileDirection == -1), endRank + .5)
                    else:
                        endPosition = (endFile + .5, endRank + .5)
                else:
                    #changeRank = startRank + rankDirection
                    changeFile = startFile + (1.5 + 1 * (fileDirection == 1)) * fileDirection
                    changeRank = startRank + 1 * (rankDirection == 1) if moveInbetween else startRank + .5
                    startPosition = (startFile + .5, changeRank)
                    changePosition = (changeFile, changeRank)
                    if move_type == "CAPTURE":
                        endPosition = (endFile + .5, endRank + 1 * (rankDirection == -1))
                        # when function is called with "CAPTURE", calling function expects output
                        # to sometimes begin with an integer representing what edge will be covered.
                        # 1 = top edge, 0 = bottom edge
                        # Side edges will not affect movement of pieces leaving the board
                        return [0 + 1 * (rankDirection == -1), startPosition, changePosition, endPosition]
                    else:
                        endPosition = (endFile + .5, endRank + .5)
                return [startPosition, changePosition, endPosition] if moveInbetween else [changePosition, endPosition]

                #move in between squares and end up back in middle of square
        #Normal Movement: Movement for any piece not fitting the criteria of a special move
            elif move_type == "CAPTURE":
                if (changeInFile and changeInRank):
                    beforeEndPosition = (endFile + 1 * (fileDirection == -1), endRank + 1 * (rankDirection == -1))
                    endPosition = (endFile + .5, endRank + 1 * (rankDirection == -1))
                    # Piece ends at top or bottom, need to include obstructed edge at beginning
                    return [0 + 1 * (rankDirection == -1), beforeEndPosition, endPosition]
                elif changeInFile:
                    endPosition = (endFile + 1 * (fileDirection == -1), endRank + .5)
                    return [endPosition]
                elif changeInRank:
                    endPosition = (endFile + .5, endRank + 1 * (rankDirection == -1))
                    # Piece ends at top or bottom, need to include obstructed edge at beginning
                    return [0 + 1 * (rankDirection == -1), endPosition]
            else:
                return [(get_file(target) + 0.5, get_rank(target) + 0.5)]
    
    #Castle: Means that the rook is moving, need to move the rook inbetween squares
        elif move_type == "CASTLE":
            castleRank = startRank + 1 * (startRank == 0)
            t = [(startFile + .5, castleRank), (endFile + .5, castleRank), (endFile + .5, endRank + .5)]
            return t
        
    #Piece is leaving the board: Moves inbetween squares and then back to center of square
        elif(move_type == "LEAVE"):
            leaveRank = startRank + 1 * ((rankDirection == 1 and obstructed_edge != 1) or obstructed_edge == 0)
            t = [(startFile + .5, leaveRank), (endFile, leaveRank), (endFile, endRank + .5), (endFile + .5, endRank + .5)]
            return t
        
