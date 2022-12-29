from piece import Piece


class Board:
    """
    Class representing a chess board. Stores white pieces as uppercase and black pieces as lowercase in an array. Empty
    squares are stored as None.
    """

    board = {}
    whiteToMove: bool

    def __init__(self, fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0", whiteToMove=True):
        self.fen_to_board(fen)
        self.whiteToMove = whiteToMove

    def __str__(self) -> str:
        return self.board_to_fen()

    def fen_to_board(self, fen: str) -> None:
        """
        Takes a chess position stored in FEN notation and stores it in the board.
        """

        fen_fields = fen.split()

        # Sets pieces on te board
        ranks = fen_fields[0].split('/')

        r = 0
        for rank in ranks:

            f = 0
            for c in rank:

                # If the character is a number, add the corresponding number of empty squares to the board
                if c.isdecimal():
                    for _ in range(int(c)):
                        if r * 8 + f in self.board:
                            self.board.pop(r * 8 + f)
                        f += 1

                # If the character is not a number, add the piece to the board
                else:
                    self.board[r * 8 + f] = Piece(c, r * 8 + f)
                    f += 1

            r += 1

        # Sets whose turn it is to move
        if fen_fields[1] == 'w':
            self.whiteToMove = True
        else:
            self.whiteToMove = False

        # Determines castling rights
        # TODO

        # Sets enpassant targets
        if not fen_fields == '-':
            file = ord(fen_fields[3][0]) - 97
            rank = fen_fields[3][1]

            if rank == 3:
                self.board[32 + file].is_enpassantable = True
            else:
                self.board[24 + file].is_enpassantable = True

        # Sets halfmove and fullmove clocks
        # TODO

    def board_to_fen(self) -> str:
        """
        Takes current position of the board and returns the position in FEN notation.
        """

        # Converts self.board into a list
        placeholder = [None] * 64
        for square in self.board:
            placeholder[square] = self.board[square].piece_type

        fen = ''

        # Iterates through each rank
        for r in range(8):
            empty_spaces = 0

            # Iterates through each square in the rank
            for piece in placeholder[r * 8: r * 8 + 8]:
                # Keeps track of how many concurrent empty squares the iterator has encountered.
                if piece is None:
                    empty_spaces += 1
                else:
                    if empty_spaces != 0:
                        fen += str(empty_spaces)
                        empty_spaces = 0
                    fen += piece

            # Edge case where last square in rank is empty
            if empty_spaces != 0:
                fen += str(empty_spaces)

            # Adds a '/' at the end of the rank if it isn't the last rank
            if r != 7:
                fen += '/'

        return fen

    def legal_moves(self) -> list[(str, str)]:
        """
         Returns a list of legal moves as tuples, where the 0 index is the starting square and the 1 index is the final
         square.
        """

        moves = []

        if self.whiteToMove:
            for piece in self.board:
                if not self.board[piece].piece_type.islower():
                    moves += self.board[piece].legal_moves(self.board)
        else:
            for piece in self.board:
                if self.board[piece].piece_type.islower():
                    moves += self.board[piece].legal_moves(self.board)

        return moves

    # Checks if legal move includes taking opposing king. Returns True if such move is included.
    def in_check(self) -> bool:

        king_pos = -1

        # If white to move, find position of the black king
        if self.whiteToMove:
            for piece in self.board:
                if self.board[piece].piece_type == 'k':
                    king_pos = piece

        # If black to move, find position of the white king
        else:
            for piece in self.board:
                if self.board[piece].piece_type == 'K':
                    king_pos = piece

        # If the position of the king is included as a destination square in the list of legal moves, said king is
        # under check
        for move in self.legal_moves():
            if move[1] == king_pos:
                return True

        return False

    def make_move(self, move: (int, int)) -> bool:
        return True
