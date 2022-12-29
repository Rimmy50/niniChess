from piece import Piece


class Board:
    """
    Class representing a chess board. Stores white pieces as uppercase and black pieces as lowercase in an array. Empty
    squares are stored as None.
    """

    board = {}
    whiteToMove: bool
    halfMoves: int
    fullMoves: int

    def __init__(self, fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0"):
        self.fen_to_board(fen)

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
        castling_rights = [c for c in fen_fields[2]]

        if not castling_rights[0] == '-':
            for right in castling_rights:
                if right == 'K':
                    self.board[60].castle_king = True
                elif right == 'Q':
                    self.board[60].castle_queen = True
                elif right == 'k':
                    self.board[4].castle_king = True
                elif right == 'q':
                    self.board[4].castle_queen = True

        # Sets enpassant target
        if not fen_fields[3] == '-':
            file = ord(fen_fields[3][0]) - 97
            rank = fen_fields[3][1]

            if rank == '3':
                self.board[32 + file].is_enpassantable = True
            else:
                self.board[24 + file].is_enpassantable = True

        # Sets halfmove and fullmove clocks
        self.halfMoves, self.fullMoves = int(fen_fields[4]), int(fen_fields[5])

    def board_to_fen(self) -> str:
        """
        Takes current position of the board and returns the position in FEN notation.
        """

        fen = ''

        # Computes string representing board position

        # Converts self.board into a list
        placeholder = [None] * 64
        for square in self.board:
            placeholder[square] = self.board[square].piece_type

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

        fen += ' '

        # Adds active color field
        if self.whiteToMove:
            fen += 'w'
        else:
            fen += 'b'

        fen += ' '

        # Adds castling rights
        castling_rights = False

        if 60 in self.board \
            and self.board[60].piece_type == 'K':
                if self.board[60].castle_king:
                    fen += 'K'
                    castling_rights = True
                if self.board[60].castle_queen:
                    fen += 'Q'
                    castling_rights = True

        if 4 in self.board \
            and self.board[4].piece_type == 'k':
                if self.board[4].castle_king:
                    fen += 'k'
                    castling_rights = True
                if self.board[4].castle_queen:
                    fen += 'q'
                    castling_rights = True

        if not castling_rights:
            fen += '-'

        fen += ' '

        # Adds enpassant target
        enpassant_exists = False

        for square in range(24, 40):
            if square in self.board \
                    and self.board[square].is_enpassantable:
                if square < 32:
                    fen += chr(97 + square % 8) + str(9 - square // 8)
                else:
                    fen += chr(97 + square % 8) + str(7 - square // 8)
                enpassant_exists = True
                break

        if not enpassant_exists:
            fen += '-'

        fen += ' '

        # Adds halfmove and fullmove clocks
        fen += str(self.halfMoves) + ' ' + str(self.fullMoves)

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

    def in_check(self) -> bool:
        """
        Checks if legal moves include taking opposing king. Returns True is such move is included.
        """
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

        # legal = self.legal_moves()
        #
        # if move in legal:
        #     test_board = Board(self.board_to_fen(), self.whiteToMove)
        #
        #     # Currently doesn't test for enpassant
        #     test_board.board[move[1]] = test_board.board[move[0]]
        #     test_board.board.pop(move[0])
        #     test_board.whiteToMove = not test_board.whiteToMove
        #
        #     if test_board.in_check():
        #         return False
        #
        # # Implement actually making the move
        #
        # return True

        '''
        Implement this method to actually make the move regardless of legality
        '''


