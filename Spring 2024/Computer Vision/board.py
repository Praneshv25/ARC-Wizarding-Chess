# Horizontal: A to H
# Vertical: 8 to 1
chessboard = {}

ranks = ['1', '2', '3', '4', '5', '6', '7', '8']
files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

# Populate the dictionary with keys representing squares on the chessboard
for rank in ranks:
    for file in files:
        # Generate the key for each square (e.g., 'a1', 'b1', ..., 'h8')
        square = file + rank
        # Assign a placeholder value to each square
        chessboard[square] = None


def populate_position(square_in, coordinate):
    chessboard[square_in] = coordinate


def get_position(square_in):
    return chessboard[square_in]