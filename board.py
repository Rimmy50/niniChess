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

    def __init__(self, fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        self.fen_to_board(fen)

    def __str__(self) -> str:
        return self.board_to_fen()

    def fen_to_board(self, fen: str) -> None:
        """
        Takes a chess position stored in FEN notation and stores it in the board.
        """

        fen_fields = fen.split()

        # Sets pieces on the board
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

    def pseudolegal_moves(self) -> list[(int, int)]:
        """
         Returns a list of pseudolegal moves as tuples, where the 0 index is the starting square and the 1 index is the
         final square.
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

    def in_check(self, pseudo_moves: list[(int, int)]) -> bool:
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
        for move in pseudo_moves:
            if move[1] == king_pos:
                return True

        return False

    def make_move(self, move: (int, int), pseudo_moves: list[(int, int)]) -> bool:
        """
        Returns True if move is pseudolegal and move is made. Returns False otherwise.
        """

        if move in pseudo_moves:

            # If move is a castling move, castle
            if self.board[move[0]].piece_type.lower() == 'k':

                # Check kingside castling
                if self.board[move[0]].castle_king and abs(move[1] - move[0]) == 2:

                    # Check if castling moves through check and return False if so
                    test_board = Board(self.board_to_fen())
                    test_board.whiteToMove = not test_board.whiteToMove
                    test_board_pseudo_moves = {pseudo_move[1] for pseudo_move in test_board.pseudolegal_moves()}
                    if any({move[0] + i in test_board_pseudo_moves for i in range(3)}):
                        return False

                    # Remove castling rights
                    self.board[move[0]].castle_king, self.board[move[0]].castle_queen = False, False

                    self.board[move[1]], self.board[move[1] - 1] = self.board[move[0]], self.board[move[1] + 1]
                    self.board.pop(move[0])
                    self.board.pop(move[1] + 1)

                # Check queenside castling
                elif self.board[move[0]].castle_queen and abs(move[1] - move[0]) == 2:

                    # Check if castling moves through check and return False if so
                    test_board = Board(self.board_to_fen())
                    test_board.whiteToMove = not test_board.whiteToMove
                    test_board_pseudo_moves = {pseudo_move[1] for pseudo_move in test_board.pseudolegal_moves()}
                    if any({move[0] - i in test_board_pseudo_moves for i in range(3)}):
                        return False

                    # Remove castling rights
                    self.board[move[0]].castle_king, self.board[move[0]].castle_queen = False, False

                    self.board[move[1]], self.board[move[1] + 1] = self.board[move[0]], self.board[move[1] - 2]
                    self.board.pop(move[0])
                    self.board.pop(move[1] - 2)

            # If move is enpassant, do enpassant
            elif self.board[move[0]].piece_type.lower() == 'p' \
                    and move[1] not in self.board \
                    and abs(move[1] % 8 - move[0] % 8) == 1:
                self.board[move[1]] = self.board[move[0]]
                self.board.pop(move[1] - self.board[move[0]].valid_directions[0])
                self.board.pop(move[0])

            # Make normal move otherwise
            else:

                # Remove respective castle rights if piece is rook
                rook = self.board[move[0]]

                if rook.piece_type.lower() == 'r':

                    # If piece moved is kingside rook, remove castling rights
                    if move[0] == 7 or move[0] == 63:
                        for piece in self.board:
                            if self.board[piece].piece_type.lower() == 'k' \
                                    and self.board[piece].piece_type.islower() == rook.piece_type.islower():
                                self.board[piece].castle_king = False

                    # If piece move is queenside rook, remove castling rights
                    if move[0] == 0 or move[0] == 56:
                        for piece in self.board:
                            if self.board[piece].piece_type.lower() == 'k' \
                                    and self.board[piece].piece_type.islower() == rook.piece_type.islower():
                                self.board[piece].castle_queen = False

                self.board[move[1]] = self.board[move[0]]
                self.board.pop(move[0])

            # Reset enpassant boolean
            for i in range(24, 40):
                if i != move[1] \
                        and i in self.board \
                        and self.board[i].piece_type.lower() == 'p' \
                        and self.board[i].is_enpassantable:
                    self.board[i].is_enpassantable = False
                    break

            # Increments fullmove clock
            if not self.whiteToMove:
                self.fullMoves += 1

            # Switches active color
            self.whiteToMove = not self.whiteToMove

            # Increments/resets halfmove clock
            if abs(move[1] - move[0]) == 16 and self.board[move[1]].piece_type.lower() == 'p':
                self.halfMoves = 0
            else:
                self.halfMoves += 1

            return True

        else:

            return False

    def check_move_legality(self, move: (int, int), make_move=False) -> bool:
        """
        Checks if move is legal and returns True if so. If make_move is True and move is legal, move is also made.
        """

        # Create a test board
        test_board = Board(self.board_to_fen())

        # If move is pseudolegal, move is made on test_board
        is_move_pseudolegal = test_board.make_move(move, test_board.pseudolegal_moves())

        # If move is pseudolegal, check if test_board is in check. If in check, pseudolegal move is not legal move
        if is_move_pseudolegal:
            in_check = test_board.in_check(test_board.pseudolegal_moves())

            # If make_move is true and move is legal, make the move on self
            if not in_check and make_move:
                self.board = test_board.board
                self.whiteToMove = test_board.whiteToMove
                self.halfMoves = test_board.halfMoves
                self.fullMoves = test_board.fullMoves
                return True
            else:
                return not in_check
        else:
            return False
