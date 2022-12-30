class Piece:
    """
    Superclass representing chess pieces.
    """

    piece_type: str
    valid_directions: list[int]
    position: int
    is_enpassantable = False
    castle_king: bool
    castle_queen: bool

    def __init__(self, piece_type: str, position: int, castle_king=False, castle_queen=False) -> None:
        self.piece_type = piece_type
        self.position = position

        new_type = piece_type.lower()

        if new_type == 'q' or new_type == 'k':
            self.valid_directions = [1, -1, 8, -8, 7, -7, 9, -9]
            # if new_type == 'k':
            #     self.castle_king = castle_king
            #     self.castle_queen = castle_queen
        elif new_type == 'r':
            self.valid_directions = [1, -1, 8, -8]
        elif new_type == 'b':
            self.valid_directions = [7, -7, 9, -9]
        elif new_type == 'n':
            self.valid_directions = [17, -17, 15, -15, 10, -10, 6, -6]
        elif new_type == 'p' and self.piece_type.islower():
            self.valid_directions = [8]
        else:
            self.valid_directions = [-8]

        self.castle_king = castle_king
        self.castle_queen = castle_queen

    def legal_moves(self, board: dict) -> list[(int, int)]:

        new_type = self.piece_type.lower()

        moves = []

        # If the piece is a queen, rook, or bishop, iterate through their respective legal directions until they hit
        # the edge of the board or another piece.
        if new_type == 'q' or new_type == 'r' or new_type == 'b':
            for direction in self.valid_directions:
                iter_pos = self.position + direction

                # Checks if the iterator has reached the edge of the board
                while 0 <= iter_pos <= 63 \
                        and (abs(direction) != 1 or iter_pos % 8 - (iter_pos - direction) % 8 == direction) \
                        and (abs(direction) != 7 or iter_pos % 8 - (iter_pos - direction) % 8 == direction // -7) \
                        and (abs(direction) != 9 or iter_pos % 8 - (iter_pos - direction) % 8 == direction // 9):

                    # Checks if piece exists on the square and if so, whether the piece is the same color
                    if iter_pos in board:
                        if board[iter_pos].piece_type.islower() != self.piece_type.islower():
                            moves.append(iter_pos)
                        break

                    moves.append(iter_pos)
                    iter_pos += direction

        # If the piece is a king or knight, check whether a piece of the same color is the respective legal directions
        # or whether the piece is at the edge of the board.
        if new_type == 'k' or new_type == 'n':
            for direction in self.valid_directions:
                new_pos = self.position + direction

                # Checks if the direction is on the board and if so, if a piece of the same color is not in the
                # direction
                if 0 <= new_pos <= 63 \
                    and 0 <= abs(new_pos % 8 - self.position % 8) <= 2 \
                    and (new_pos not in board or board[new_pos].piece_type.islower() != self.piece_type.islower()):

                    moves.append(new_pos)

            # If king still has castling rights, add it to list of legal moves
            if self.castle_king and self.position + 1 not in board and self.position + 2 not in board:
                moves.append(self.position + 2)
            if self.castle_queen and all({square not in board for square in range(self.position - 3, self.position)}):
                moves.append((self.position - 2))

        # If the piece is a pawn, check whether forward square is unoccupied or diagonal squares are occupied by enemy
        # pieces. Also checks for enpassant.
        if new_type == 'p':

            forward_square = self.position + self.valid_directions[0]

            # Checks if forward square is occupied
            if 0 <= forward_square <= 63 and forward_square not in board:
                moves.append(forward_square)

            # Checks if right diagonal square is on the board and opposing piece is on it
            if 0 <= forward_square + 1 <= 63 \
                    and (forward_square + 1) % 8 - forward_square % 8 == 1 \
                    and forward_square + 1 in board \
                    and board[forward_square + 1].piece_type.islower() != self.piece_type.islower():

                moves.append(forward_square + 1)

            # Checks if left diagonal square is on the board and opposing piece is on it
            if 0 <= forward_square - 1 <= 63 \
                    and forward_square % 8 - (forward_square - 1) % 8 == 1 \
                    and forward_square - 1 in board \
                    and board[forward_square - 1].piece_type.islower() != self.piece_type.islower():

                moves.append(forward_square - 1)

            # Checks if pawn is black and is on the 7th rank
            if self.piece_type.islower() \
                    and 8 <= self.position <= 15 \
                    and self.position + 16 not in board:

                moves.append(self.position + 16)

            # Checks if pawn is white and is on the 2nd rank
            if not self.piece_type.islower() \
                    and 48 <= self.position <= 55 \
                    and self.position - 16 not in board:

                moves.append(self.position - 16)

            # Checks enpassant for right diagonal
            if self.position + 1 in board \
                and 0 <= self.position + 1 <= 63 \
                and board[self.position + 1].is_enpassantable:

                moves.append(self.position + self.valid_directions[0] + 1)

            # Checks enpassant for left diagonal
            if self.position - 1 in board \
                    and 0 <= self.position - 1 <= 63 \
                    and board[self.position - 1].is_enpassantable:
                moves.append(self.position + self.valid_directions[0] - 1)

        return [(self.position, move) for move in moves]
