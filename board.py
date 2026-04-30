from __future__ import annotations

from typing import List, Optional, Tuple

from pieces import (
    Bishop,
    King,
    Knight,
    Move,
    Pawn,
    Piece,
    Queen,
    Rook,
    in_bounds,
    parse_square,
    piece_from_symbol,
    symbol_from_piece,
)
"""
ECE 122: Project 3
Sean Graziano
Spire ID: 35297651
Constanin Knab
Spire ID: 35452627
"""

#Stores board, applies move, undo moves, check legal, serializez board state



Square = Tuple[int, int]


class Board:
    def __init__(self, setup: bool = True):
        self.grid: List[List[Optional[Piece]]] = [[None for _ in range(8)] for _ in range(8)]
        #create grid
        self.turn: str = "w" #White moves first
        self.history: List[Move] = []#Stores moves for undo and logging
        if setup:
            self.setup_start() #Initialize board

    @staticmethod
    def opposite(color: str) -> str:
        #Returns opposite side
        return "b" if color == "w" else "w"

    def setup_start(self) -> None:
        # Initialize an empty 8x8 board (all squares set to None)
        self.grid = [[None for _ in range(8)] for _ in range(8)]

        # Define the order of major pieces on the back rank
        back_rank = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]

        # Place back rank pieces for both white and black
        for c, cls in enumerate(back_rank):   # c = column index, cls = piece class
            self.grid[7][c] = cls("w")        # place white pieces on row 7 (bottom)
            self.grid[0][c] = cls("b")        # place black pieces on row 0 (top)
          
        # Place pawns for both sides
        for c in range(8):
            self.grid[6][c] = Pawn("w")       # white pawns on row 6
            self.grid[1][c] = Pawn("b")       # black pawns on row 1
        self.turn = "w"                       # Set the starting turn to white
        self.history.clear()                  # Clear move history

    def clone(self) -> "Board":
        # Creates a deep copy of the board so changes to the copy do not affect the original
        b = Board(setup=False)  # create a new Board without running the initial setup
        b.turn = self.turn      # copy whose turn it is

        # create a new grid by copying each piece (if present), otherwise keep None
        b.grid = [[p.copy() if p is not None else None for p in row] for row in self.grid]
        return b  # return the independent board copy

    def piece_at(self, r: int, c: int) -> Optional[Piece]:
        #Returns piece at square
        if not in_bounds(r, c): #Check bounds to avoid index errors
            return None
        return self.grid[r][c]  #Return the piece at the specified row and column, or None if the square is empty

    def king_pos(self, color: str) -> Optional[Square]:
        #Finds king for color
        for r in range(8):          # loop through rows
            for c in range(8):      # loop through columns
                p = self.grid[r][c] # get the piece at (r, c)
                if p is not None and p.color == color and isinstance(p, King): # check if it's the king of the specified color
                    return (r, c)   # return the position of the king as a tuple (row, column)    
        return None

    def square_attacked(self, r: int, c: int, by_color: str) -> bool:
        #Checkif square is attacked by color,
        #Loops through all pieces of color and checks whether any attached square matches
        for rr in range(8):              # loop through rows 
            for cc in range(8):          # loop through columns
                p = self.grid[rr][cc]    # get the piece at (rr, cc)
                if p is None or p.color != by_color:    # skip if there's no piece or it's not the attacking color
                    continue
                for ar, ac in p.attacks(self, rr, cc):  # loop through squares attacked by this piece
                    if (ar, ac) == (r, c):              # check if the attacked square matches the target square
                        return True
        return False

    def in_check(self, color: Optional[str] = None) -> bool:
        #Determine if color isin chechk
        if color is None:
            color = self.turn       # default to current player's turn if no color specified
        kpos = self.king_pos(color) # get the position of the king for the specified color
        if kpos is None:
            return False
        return self.square_attacked(kpos[0], kpos[1], self.opposite(color))  # check if the king's position is attacked by the opposite color

    def apply_move(self, move: Move) -> None:    #Apply move to board, update history, store info for undo
        """
        Apply a move to the board.

        Parameters:
            move: a Move object containing start and end positions

        Output:
            None (the board is modified directly)

        Rules:
            - Move the piece from its start position to its end position
            - If a piece exists at the destination -> it is captured
            - The starting square must become empty
            - Update the board state correctly
            - Do not create a new board
            ● must store moved_piece, captured_piece, and previous turn in move
            ● must append move to history

        Hint:
            Access the piece using its starting position, then update both squares.
        """
        # TODO: Implement board update logic
        sr, sc = move.src
        dr, dc = move.dst
        
        # Store move information for undo
        move.moved_piece = self.grid[sr][sc]        # Store the piece being moved
        move.captured_piece = self.grid[dr][dc]     # Store the piece being captured (if any)
        move.prev_turn = self.turn                  # Store the current turn before changing it
        
        # Move the piece
        self.grid[dr][dc] = self.grid[sr][sc]       # Place the piece at the destination
        self.grid[sr][sc] = None                    # Clear the starting square
        
        # Handle promotion
        if move.promotion:
            if move.promotion == 'q':                   # Promote to queen
                self.grid[dr][dc] = Queen(self.turn)    # Create a new Queen piece of the current color and place it at the destination
            elif move.promotion == 'r':                 # Promote to rook
                self.grid[dr][dc] = Rook(self.turn)     # Create a new Rook piece of the current color and place it at the destination
            elif move.promotion == 'b':                 # Promote to bishop
                self.grid[dr][dc] = Bishop(self.turn)   # Create a new Bishop piece of the current color and place it at the destination
            elif move.promotion == 'n':                 # Promote to knight
                self.grid[dr][dc] = Knight(self.turn)   # Create a new Knight piece of the current color and place it at the destination
            # Note: The original piece is replaced by the promoted piece, so we don't need to store the original piece separately
        
        # Switch turn
        self.turn = self.opposite(self.turn)
        
        # Add to history
        self.history.append(move)

    def undo_move(self, move: Move) -> None:
        #Restores moving piece to source, capture piece to dest, previous turn
        sr, sc = move.src           
        dr, dc = move.dst
        if move.prev_turn is None:
            raise ValueError("Move does not contain undo information")
        self.turn = move.prev_turn
        self.grid[sr][sc] = move.moved_piece            # Restore the piece to its original position
        self.grid[dr][dc] = move.captured_piece         # Restore the captured piece to its original position (or None if there was no capture)
        if self.history and self.history[-1] == move:   # get the piece at (r, c)
            self.history.pop()                          # Remove the move from history if it's the last move

    def undo_last(self) -> Move:
        #Undo recent
        if not self.history:
            raise ValueError("No moves to undo")         # Check if there are moves to undo
        move = self.history[-1]                          # Get the last move from history    
        self.undo_move(move)                            
        return move                                      # Return the move that was undone, in case the caller wants to know what move was undone

    def generate_pseudo_legal_moves(self) -> List[Move]:
        """
        Generate all pseudo-legal moves for the current player.

        Parameters:
            None (uses the current board state)

        Output:
            A list of Move objects representing all possible moves.

        Rules:
            - Loop through all squares on the board
            - For each piece belonging to the current player:
                 Call its pseudo_legal_moves() function
            - Combine all moves into one list
            - Do not modify the board

        Hint:
            Check piece color before generating moves.
        """
        # TODO: Collect moves from all pieces
        moves: List[Move] = []      # Loop through all squares on the board
        for r in range(8):          
            for c in range(8):     
                piece = self.grid[r][c]     
                if piece is not None and piece.color == self.turn:      # Check if the piece belongs to the current player
                    moves.extend(piece.pseudo_legal_moves(self, r, c))  # Call the piece's pseudo_legal_moves() function and add the moves to the list
        return moves            # Return the combined list of pseudo-legal moves

    def generate_legal_moves(self) -> List[Move]:           
        """
        Generate all legal moves for the current player.

        Parameters:
            None

        Output:
            A list of Move objects representing legal moves.

        Rules:
            - Start with pseudo-legal moves
            - For each move:
                 Apply the move temporarily
                 Check if the player is in check
                 If still in check → discard move
                 Otherwise → keep move
            - Undo the move after checking
            - Do not permanently modify the board

        Hint:
            Use apply_move() and undo functionality if available.
        """
        # TODO: Filter pseudo-legal moves into legal moves
        pseudo_legal = self.generate_pseudo_legal_moves()   # Generate all pseudo-legal moves for the current player
        legal_moves = []                                    # List to store legal moves
        for move in pseudo_legal:                           # Loop through each pseudo-legal move
            self.apply_move(move)                           # Apply the move temporarily to the board                            
            if not self.in_check(self.opposite(self.turn)): # Check if the player is still in check after the move
                legal_moves.append(move)                    # If the player is not in check, the move is legal, so we add it to the legal_moves list
            self.undo_move(move)                            # Undo the move to restore the original board state for the next iteration  
        return legal_moves


    def is_game_over(self) -> bool:
        """
        Determine whether the game has ended.

        Parameters:
            None

        Output:
            True if the game is over, False otherwise.

        Rules:
            - Game is over if:
                 The current player has no legal moves
                
            - Do not modify the board

        Hint:
            Check if there are no legal moves
        """
        # TODO: Implement game-ending condition
        legal_moves = self.generate_legal_moves()       # Generate legal moves for the current player
        return len(legal_moves) == 0                    # The game is over if there are no legal moves available for the current player


    def result(self) -> str:

        """
        Return the result of the game.

        Parameters:
            None

        Output:
            ● "ongoing"
            ● "<opposite side> wins by checkmate"
            ● "draw by stalemate"

        Rules:
            
        - If no legal moves exist:
            If in check → opponent wins
            Otherwise → draw (stalemate)

        Hint:
            Use is_game_over() and in_check() to decide.
        """
        # TODO: Determine game result
        if not self.is_game_over():
            return "ongoing"
        if self.in_check(self.turn):
            return f"{'Black' if self.turn == 'w' else 'White'} wins by checkmate"
        return "draw by stalemate"

    def position_key(self) -> str:
        #Builds a string representation of the board plus side to move.
        rows = []
        for r in range(8):
            rows.append("".join(symbol_from_piece(p) for p in self.grid[r]))    # Create a string for each row by concatenating the symbols of the pieces in that row
        return f"{self.turn}|" + "/".join(rows)                                 # Combine the turn and the row strings into a single position key string

    def to_text(self) -> str:           
        #Serialize board to plain text
        lines = [f"turn {self.turn}"]       # First line indicates whose turn it is
        for r in range(8):                  # Loop through each row of the board
            lines.append("".join(symbol_from_piece(p) for p in self.grid[r]))   # Create a string for each row by concatenating the symbols of the pieces in that row and add it to the lines list
        return "\n".join(lines) + "\n"      # Join all lines into a single string with newline characters and return it

    @classmethod
    def from_text(cls, text: str) -> "Board":
        #Loads board from text
        lines = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")]   # Split the input text into lines, strip whitespace, and ignore empty lines and comments (lines starting with '#')
        if len(lines) < 9:
            raise ValueError("Position file must contain one turn line and 8 board lines")  # Check if there are at least 9 lines (1 for turn and 8 for the board)
        first = lines[0].split()        # Split the first line to extract the turn information
        if len(first) != 2 or first[0].lower() != "turn" or first[1] not in ("w", "b"):     # Validate the format of the first line to ensure it specifies the turn correctly
            raise ValueError("First line must be 'turn w' or 'turn b'")                     # If the first line is not in the correct format, raise an error
        board = cls(setup=False)
        board.turn = first[1]
        if len(lines[1:9]) != 8:                           # Check if there are exactly 8 lines for the board representation
            raise ValueError("Board must have 8 rows")     # If there are not exactly 8 lines for the board, raise an error        
        for r in range(8):                                 # Loop through each of the 8 lines representing the rows of the board
            row = lines[1 + r]                             # Get the line corresponding to the current row of the board
            if len(row) != 8:                              # Check if the line has exactly 8 characters (one for each column)
                raise ValueError(f"Row {r+1} must have exactly 8 characters")   # If the line does not have exactly 8 characters, raise an error indicating which row is incorrect
            for c, ch in enumerate(row):                   # Loop through each character in the line, where c is the column index and ch is the character representing the piece
                board.grid[r][c] = piece_from_symbol(ch)   # Convert the character to a Piece object using piece_from_symbol and place it in the corresponding position on the board grid
        return board

    def __str__(self) -> str:
        #Create display
        out = []
        out.append("    a   b   c   d   e   f   g   h")
        out.append("  +---+---+---+---+---+---+---+---+")
        for r in range(8):
            rank = 8 - r
            cells = []
            for c in range(8):
                p = self.grid[r][c]
                cells.append(f" {symbol_from_piece(p)} ")
            out.append(f"{rank} |" + "|".join(cells) + f"| {rank}") # Add the rank number on both sides of the row for better readability
            out.append("  +---+---+---+---+---+---+---+---+")       # Add a separator line after each row for better readability
        out.append("    a   b   c   d   e   f   g   h")             # Add the file letters at the bottom for better readability
        out.append(f"Turn: {'White' if self.turn == 'w' else 'Black'}") # Add a line indicating whose turn it is
        if self.in_check(self.turn):            # If the current player is in check, add a line to indicate that
            out.append("Check!")                # Add a line to indicate that the current player is in check
        return "\n".join(out)                   # Join all the lines into a single string with newline characters and return it for display

    def try_parse_move(self, text: str) -> Move:
        """
        Convert a user input string into a Move object.

        Parameters:
            text: a string representing a move (e.g., "e2e4")

        Output:
            A Move object if valid, Raises an error if the input is invalid

        Rules:
            - Extract starting and ending positions from the string
            - Convert letters to columns (a=0, b=1, etc.)
            - Convert numbers to rows
            - Raise an error if input is invalid

        Hint:
            Carefully map chess notation to array indices.
        """
        starting_pos = text[:2]
        ending_pos = text[2:4]
        promotion = text[4].lower() if len(text) > 4 else None
        src = parse_square(starting_pos)    # Convert the starting position from chess notation (e.g., "e2") to array indices (e.g., (6, 4))
        dst = parse_square(ending_pos)      # Convert the starting and ending positions from chess notation (e.g., "e2") to array indices (e.g., (6, 4))
        move = Move(src=src, dst=dst, promotion=promotion)
        return move

    def play_move_text(self, text: str) -> Move:
        #Parse move, apply, return move
        move = self.try_parse_move(text)            # Parse the input text to create a Move object
        legal_moves = self.generate_legal_moves()   # Generate the list of legal moves for the current board state
        # Check if the move is in legal moves
        for legal_move in legal_moves:              # Loop through each legal move to see if it matches the parsed move
            if legal_move.src == move.src and legal_move.dst == move.dst and legal_move.promotion == move.promotion:
                self.apply_move(legal_move)         # If a matching legal move is found, apply it to the board and return that move
                return legal_move         
        raise ValueError(f"Illegal move: {move.uci()}") # If no matching legal move is found, raise an error indicating that the move is illegal
