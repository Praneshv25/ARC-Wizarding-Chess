import pygame
import sys
import math
import chess


# Constants for board colors and square size
LIGHT_BOARD = (238,238,210)
DARK_BOARD = (118,150,86)
PARKING_BOARD = (1, 50, 32)
SQUARE_SIZE = 100


# Constants for board
RANK = "abcdefgh"

# ---------------- Draw methods ----------------------
def draw_board(screen):
    """Draws an 8x8 chessboard on the screen."""
    for row in range(8):
        for col in range(8):
            # Alternate colors for each square
            color = LIGHT_BOARD if (row + col) % 2 == 0 else DARK_BOARD
            pygame.draw.rect(screen, color, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    # Draws parking and text for who's turn it is
    pygame.draw.rect(screen, PARKING_BOARD, pygame.Rect(8 * SQUARE_SIZE, 0, 2 * SQUARE_SIZE, 8 * SQUARE_SIZE))


def draw_piece(screen, pieceName, row, column, alternatePosition):
    """Draws a piece at a specified location."""
    # Load the image
    try:
        fileName = "./images/" + pieceName + ".png"
        image = pygame.image.load(fileName).convert_alpha()
    except FileNotFoundError:
        image = pygame.image.load("./images/missingPiece.png").convert_alpha()

    # Scale image
    defaultPieceImageSize = (80, 80)
    image = pygame.transform.scale(image, defaultPieceImageSize)

    # Get the image's rectangle
    image_rect = image.get_rect()

    # Position the image
    if alternatePosition == (-1, -1):
        image_rect.center = (SQUARE_SIZE * column + SQUARE_SIZE // 2, SQUARE_SIZE * row + SQUARE_SIZE // 2)
    else:
        image_rect.center = alternatePosition

    # Draw to screen
    screen.blit(image, image_rect)

# ----------------- Piece class --------------------
class Piece:
    def __init__(self, name, row, column, captured=False):
        self.name = name
        self.row = row
        self.column = column
        self.captured = captured
        self.isSelected = False
        self.alternatePosition = (-1, -1)

# ----------------- VisualGUI class --------------------
class VisualGUI():  
    def __init__(self, width, height, turn=True):
        self.turn = turn
        self.width = width
        self.height = height
        self.turn = turn
        self.board = [[0 for _ in range(8)] for _ in range(8)]
        self.selected_piece = None  # Track the currently selected piece

    def initialize(self):
        pygame.init()
        # Create window
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("White's Turn" if self.turn else "Black's" + "'s Turn")

    def createVisualBoard(self):
        # Get list of pieces

        # Create black pieces
        self.board[0][0] = Piece("black_rook", 0, 0)
        self.board[0][1] = Piece("black_knight", 0, 1)
        self.board[0][2] = Piece("black_bishop", 0, 2)
        self.board[0][3] = Piece("black_queen", 0, 3)
        self.board[0][4] = Piece("black_king", 0, 4)
        self.board[0][5] = Piece("black_bishop", 0, 5)
        self.board[0][6] = Piece("black_knight", 0, 6)
        self.board[0][7] = Piece("black_rook", 0, 7)

        for i in range(0, 8):
            self.board[1][i] = Piece("black_pawn", 1, i)

        # Create white pieces
        self.board[7][0] = Piece("white_rook", 7, 0)
        self.board[7][1] = Piece("white_knight", 7, 1)
        self.board[7][2] = Piece("white_bishop", 7, 2)
        self.board[7][3] = Piece("white_queen", 7, 3)
        self.board[7][4] = Piece("white_king", 7, 4)
        self.board[7][5] = Piece("white_bishop", 7, 5)
        self.board[7][6] = Piece("white_knight", 7, 6)
        self.board[7][7] = Piece("white_rook", 7, 7)

        for i in range(0, 8):
            self.board[6][i] = Piece("white_pawn", 6, i)

    def finishMove(self, new_row, new_col):
        # Change who's turn it in
        self.turn = not self.turn
        # Cast back to integer
        new_row = int(new_row)
        new_col = int(new_col)
        if 0 <= new_row < 8 and 0 <= new_col < 8:
            self.board[self.selected_piece.row][self.selected_piece.column] = 0
            self.board[new_row][new_col] = self.selected_piece
            self.selected_piece.row, self.selected_piece.column = new_row, new_col # set the new positions

        # Reset selection
        self.selected_piece.isSelected = False
        self.selected_piece.alternatePosition = (-1, -1)
        self.selected_piece = None

    def finishInvalidMove(self):
        # Reset selection
        self.selected_piece.isSelected = False
        self.selected_piece.alternatePosition = (-1, -1)
        self.selected_piece = None

    def main(self) -> str:
        # Update text
        pygame.display.set_caption("White's Turn" if self.turn else "Black's" + "'s Turn")

        # Handle events ------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Start dragging a piece if clicked on it
                mouse_x, mouse_y = pygame.mouse.get_pos()
                row, col = mouse_y // SQUARE_SIZE, mouse_x // SQUARE_SIZE
                if 0 <= row < 8 and 0 <= col < 8 and self.board[row][col] != 0:
                    self.selected_piece = self.board[row][col]
                    self.selected_piece.isSelected = True
            elif event.type == pygame.MOUSEBUTTONUP:
                # Drop the selected piece
                if self.selected_piece:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    new_row, new_col = mouse_y // SQUARE_SIZE, mouse_x // SQUARE_SIZE
                    # Get move
                    print("Moving piece from (" + str(self.selected_piece.row) + ", " + str(self.selected_piece.column) + ") to (" + str(new_row) + ", " + str(new_col) + ")")
                    # Both positions
                    move = RANK[self.selected_piece.column] + str(8 - self.selected_piece.row) + RANK[new_col] + str(8 - new_row)

                    # just final position
                    # move = RANK[new_col] + str(8 - new_row)

                    # Add board postion to move
                    move = move + "|" + str(new_row) + "|" + str(new_col)
                    return move
                    

        # Move selected piece with mouse if dragging
        if self.selected_piece and pygame.mouse.get_pressed()[0]:
            self.selected_piece.alternatePosition = pygame.mouse.get_pos()

        # Draw chessboard background
        draw_board(self.screen)

        # Draw pieces
        for row in self.board:
            for piece in row:
                if piece:
                    draw_piece(self.screen, piece.name, piece.row, piece.column, piece.alternatePosition)

        # Update the display
        pygame.display.flip()
        return None
