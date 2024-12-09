# Author: Kolton Evans
# GitHub user: k0leslaw
# Date: 12/08/2024
# Desc: Portfolio Project - Fog of War Chess

class Piece:
    """
    represents a chess piece in a ChessVar object's game of fog of war chess.
    has a piece_type, letter_abbreviation and color
    """
    def __init__(self, letter_abbreviation):
        self._letter_abbreviation = letter_abbreviation
        self._piece_type = self.translate_letter_to_piece(self._letter_abbreviation)

        if self._letter_abbreviation.upper() == letter_abbreviation:
            self._color = "white"
        else:
            self._color = "black"

    def get_letter_abbreviation(self):
        """returns letter abbreviation of piece"""
        return self._letter_abbreviation

    def get_piece_type(self):
        """returns piece type"""
        return self._piece_type

    def get_color(self):
        """return color of piece"""
        return self._color

    @staticmethod
    def translate_letter_to_piece(letter):
        """
        takes the abbreviated letter and returns the full piece name.
        used only when initializing a Piece
        """
        letter = letter.lower()
        letter_to_piece_dict = {"p": "pawn", "r": "rook", "n": "knight", "b": "bishop", "q": "queen", "k": "king"}
        if letter in letter_to_piece_dict:
            return letter_to_piece_dict[letter]
        return


class InvalidPositionError(Exception):
    """user-defined exception for invalid board position"""
    pass


class InvalidPlayerError(Exception):
    """user-defined error for invalid player input"""
    pass


class ChessVar:
    """
    represents a game of the fog of war variation of chess.
    has a board, current_turn tracker, and game_state
    """
    def __init__(self):
        # initialize board with strings
        self._board = [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],  # 8
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],  # 7
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],  # 6
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],  # 5
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],  # 4
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],  # 3
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],  # 2
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']   # 1
        ]   # a    b    c    d    e    f    g    h

        # for each square, change its value to a Piece
        for row in range(len(self._board)):
            board = self._board
            for col in range(len(self._board[row])):
                if board[row][col] == " ":
                    board[row][col] = None
                else:
                    board[row][col] = Piece(board[row][col])

        self._current_turn = 0  # even is white's turn, odd is black's turn
        self._game_state = "UNFINISHED"

    def get_game_state(self):
        """returns state of the game: UNFINISHED, WHITE_WON, BLACK_WON"""
        return self._game_state

    def get_board(self, player="audience"):
        """returns the board as a list of lists oriented for the given player: audience, white, black"""
        player = player.lower()
        if player == "audience" or player == "white" or player == "black":
            board = []

            # find all possible moves for the player
            if player != "audience":
                possible_moves = set()
                for row in self._board:
                    for piece in row:
                        cur_pos = self.convert_position([self._board.index(row), row.index(piece)])
                        if piece is not None and piece.get_color() == player:
                            for move in self.determine_possible_moves(cur_pos, piece):
                                possible_moves.add(move)

            # generate the board
            count = 8
            for row in self._board:
                new_row = []
                for piece in row:
                    pos_as_list = [8 - count, row.index(piece)]
                    pos_as_coordinates = self.convert_position(pos_as_list)

                    if piece is None:  # empty spaces
                        new_row.append(' ')
                    elif player == "audience" or piece.get_color() == player: # either belongs to player or player is audience
                        new_row.append(piece.get_letter_abbreviation())
                    elif pos_as_coordinates in possible_moves:  # able to be captured
                        new_row.append(piece.get_letter_abbreviation())
                    else:
                        new_row.append("*")
                count -= 1
                board.append(new_row)
            return board
        print(f"Error: {player} is not a valid player.")
        raise InvalidPlayerError

    def display_board(self, player="audience"):
        """returns the board as a formatted string oriented for the given player: audience, white, black"""
        count = 8
        for row in self.get_board(player):
            print(f"{row} {count}")
            count -= 1
        print("  a    b    c    d    e    f    g    h")

    def update_game_state(self):
        """
        if both kings are found, sets the game_state to UNFINISHED.
        if only the white king is found, sets the game_state to WHITE_WON, and vice versa
        """
        white_king_found = False
        black_king_found = False

        for row in self._board:
            for piece in row:
                if piece is not None:
                    if piece.get_letter_abbreviation() == "k":
                        black_king_found = True
                        break
                    elif piece.get_letter_abbreviation() == "K":
                        white_king_found = True
                        break
        if white_king_found and black_king_found:
            self._game_state = "UNFINISHED"
        elif white_king_found and not black_king_found:
            self._game_state = "WHITE_WON"
        elif black_king_found and not white_king_found:
            self._game_state = "BLACK_WON"

    def make_move(self, move_from, move_to):
        """
        takes a square to move from and a square to move to, both strings of form "a1".
        returns False if the move is not possible, otherwise makes the move and implements its consequences
        """
        # validate input positions
        try:
            self.validate_position(move_from)
        except InvalidPositionError:
            print(f"Error: {move_from} is an invalid position.")
            return False

        try:
            self.validate_position(move_to)
        except InvalidPositionError:
            print(f"Error: {move_to} is an invalid position.")
            return False

        piece = self.get_piece_from_square(move_from)

        # if the game is over, move_from has no piece, or the piece belongs to the other player
        if self.get_game_state() != "UNFINISHED":
            return False
        elif piece is None or piece.get_color() != self.get_current_player():
            return False

        possible_moves = self.determine_possible_moves(move_from, piece)
        if move_to not in possible_moves:
            return False

        # move piece from move_from to move_to
        move_to = self.convert_position(move_to)
        self._board[move_to[0]][move_to[1]] = self.get_piece_from_square(move_from)
        move_from = self.convert_position(move_from)
        self._board[move_from[0]][move_from[1]] = None

        self._current_turn += 1
        self.update_game_state()
        return True

    def determine_possible_moves(self, move_from, piece):
        """
        takes a square to move from as a string of form "a1".
        returns a list of strings representing possible squares to move to, of form "a1"
        """

        def unbounded_movement(coordinates_list):
            """
            takes a list of lists [[y, x], [y, x]...] where y is number of squares to move up and x is number of squares
            to move right. returns a list of valid moves for pieces that don't move a fixed number of spaces
            """
            moves = []
            for coordinates in coordinates_list:
                up = coordinates[0]
                right = coordinates[1]

                cur_pos = move_from
                found_piece_or_off_board = False

                while found_piece_or_off_board is False:
                    potential_move = self.get_position_from_movement(cur_pos, up, right)
                    if potential_move is None:  # move would leave the board bounds
                        found_piece_or_off_board = True
                    elif self.get_piece_from_square(potential_move) is None:  # no piece in square
                        moves.append(potential_move)
                        cur_pos = potential_move
                    elif self.get_piece_from_square(potential_move).get_color() != self.get_current_player():  # the piece on the square belongs to the other player
                        moves.append(potential_move)
                        found_piece_or_off_board = True
                    else:  # the square has a piece that belongs to the current player
                        found_piece_or_off_board = True
            return moves

        def bounded_movement(coordinates_list):
            """
            takes a list of lists [[y, x], [y, x]...] where y is number of squares to move up and x is number of squares
            to move right. returns a list of valid moves for pieces that move a fixed number of spaces
            """
            moves = []
            pawn_exceptions = [[1, 0], [-1, 0], [2, 0], [-2, 0]]
            for coordinates in coordinates_list:
                up = coordinates[0]
                right = coordinates[1]
                potential_move = self.get_position_from_movement(move_from, up, right)
                if potential_move is not None:
                    if self.get_piece_from_square(potential_move) is None:  # the square is empty
                        if piece_type != "pawn" or coordinates in pawn_exceptions:
                            moves.append(potential_move)
                    elif self.get_piece_from_square(potential_move).get_color() != self.get_current_player():  # the piece on the square belongs to the other player
                        moves.append(potential_move)
            return moves

        piece_type = piece.get_piece_type()
        moves_list = []

        # add all legal moves based on piece type
        if piece_type == "pawn":
            coordinates = []
            if self.get_current_player() == "white":
                coordinates = [[1, 1], [1, -1]]
                if move_from[1] == "2":
                    coordinates.append([2, 0])

                piece_ahead = self.get_position_from_movement(move_from, 1, 0)
                if self.get_piece_from_square(piece_ahead) is None:
                    coordinates.append([1, 0])
            else:
                coordinates = [[-1, 1], [-1, -1]]
                if move_from[1] == "7":
                    coordinates.append([-2, 0])

                piece_ahead = self.get_position_from_movement(move_from, -1, 0)
                if self.get_piece_from_square(piece_ahead) is None:
                    coordinates.append([-1, 0])

            for move in bounded_movement(coordinates):
                moves_list.append(move)
        elif piece_type == "king":
            for move in bounded_movement([[1, 0], [-1, 0], [0, -1], [0, 1], [1, -1], [1, 1], [-1, -1], [-1, 1]]):
                moves_list.append(move)
        elif piece_type == "knight":
            for move in bounded_movement([[2, 1], [2, -1], [-2, -1], [-2, 1], [1, -2], [-1, -2], [1, 2], [-1, 2]]):
                moves_list.append(move)
        elif piece_type == "queen":
            for move in unbounded_movement([[1, 0], [-1, 0], [0, 1], [0, -1], [1, -1], [1, 1], [-1, -1], [-1, 1]]):
                moves_list.append(move)
        elif piece_type == "bishop":
            for move in unbounded_movement([[1, -1], [1, 1], [-1, -1], [-1, 1]]):
                moves_list.append(move)
        elif piece_type == "rook":
            for move in unbounded_movement([[1, 0], [-1, 0], [0, 1], [0, -1]]):
                moves_list.append(move)
        return moves_list

    def get_piece_from_square(self, square):
        """
        takes a square to check as a string of form "a1".
        returns the piece object on that square
        """
        # set row to the board's row index
        row = 8 - int(square[1])
        col = square[0]
        letter_to_index_dict = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
        col = letter_to_index_dict[col]
        return self._board[row][col]

    def convert_position(self, pos):
        """
        takes a position as 1: a string of form "a1", returning the equivalent position as a list [row, column].
                            2: a list of form [row, column], returning the equivalent position as a string of form "a1"
        returns False if the position is invalid
        """
        try:
            self.validate_position(pos)
        except InvalidPositionError:
            print(f"Error: {pos} is an invalid position.")
            return False

        if type(pos[0]) is str:  # if pos begins with a letter
            letter_to_col_dict = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
            row = 8 - int(pos[1])
            col = letter_to_col_dict[pos[0]]
            return [row, col]
        # else, pos is a list [row, col]
        col_to_letter_dict = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
        num = str(8 - pos[0])
        let = col_to_letter_dict[pos[1]]
        return let + num

    @staticmethod
    def validate_position(pos):
        """
        takes a position in form "a1"
        returns True if the position is between a1 and h8, otherwise raises InvalidPositionError
        """
        accepted_letters = ["a", "b", "c", "d", "e", "f", "g", "h"]
        accepted_numbers = ["1", "2", "3", "4", "5", "6", "7", "8"]
        if len(pos) == 2:
            # if string
            if type(pos) is str:
                if pos[0] in accepted_letters and pos[1] in accepted_numbers:
                    return True
            # if list
            elif type(pos) is list and type(pos[0]) is int and type(pos[1]) is int:
                if 0 <= pos[0] <= 7 and 0 <= pos[1] <= 7:
                    return True
        raise InvalidPositionError(f"Error: {pos} is an invalid position.")

    def get_position_from_movement(self, starting_pos, up, right):
        """
        takes a starting position as a string of form "a1", an int for how many squares to move up, and an int for how
        many squares to move right.
        returns a string of form "a1" representing the new position after the designated movement
        """
        starting_pos = self.convert_position(starting_pos)
        if (0 <= starting_pos[0] - up <= 7) and (0 <= starting_pos[1] + right <= 7):
            starting_pos[0] -= up
            starting_pos[1] += right
            new_pos = self.convert_position(starting_pos)

            try:
                self.validate_position(new_pos)
            except InvalidPositionError:
                return

            return new_pos
        return None

    def get_current_player(self):
        """returns white if current_turn is even, black if it is odd"""
        if self._current_turn % 2 == 0:
            return "white"
        return "black"


def start_user_input_game():
    """
    starts a chess game in the console
    """
    game = ChessVar()

    while game.get_game_state() == "UNFINISHED":
        # get the current player's color
        current_player = game.get_current_player()
        print(f"\nCurrent player: {current_player.capitalize()}")

        # display the board
        game.display_board(current_player)

        # prompt the player for a move
        move = input("\nEnter your move: ").strip()
        if move.lower() == "exit":
            break

        move_from, move_to = move.split()
        if game.make_move(move_from, move_to):
            print(f"Move successful: {move_from} to {move_to}")
        else:
            print("Invalid move. Try again.")

    # The game is finished, so print the game state
    print(f"\nGame Over\nResult: {game.get_game_state()}")


def main():
    start_user_input_game()


if __name__ == "__main__":
    main()