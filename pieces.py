"""This file is used to define the basic chess concepts, squares, 
moves, the piece base class, the individual piece types.
"""

from __future__ import annotations

import board
"""This delays evaluation of type hints until runtime is finished. 
It is useful because later in the file, Move refers to Piece, and 
Piece refers to Board, if you don't have this, it'd create forward-reference issues.
"""
from dataclasses import dataclass#dataclass lets us define Move with minimal boilerplate.

from typing import List, Optional, Tuple, TYPE_CHECKING
#List, Optional, Tuple are type annotations.
#TYPE_CHECKING is being used to avoid circular imports at runtime.

if TYPE_CHECKING:
    from board import Board
#This import is only used by static type checkers. prevents circular import problem 
# between pieces.py and board.py.

Square = Tuple[int, int]#Defines a square as a pair of integers (row, col).



def in_bounds(r: int, c: int) -> bool:
    #Checks whether a coordinate is on the 8×8 board.
    return 0 <= r < 8 and 0 <= c < 8


def square_name(r: int, c: int) -> str:
    #Converts internal board coordinates like (6, 4) into chess notation like e2.
    return f"{chr(ord('a') + c)}{8 - r}"


def parse_square(text: str) -> Square:
    #Converts notation like "e2" into internal coordinates

    text = text.strip().lower()
    if len(text) != 2:
        raise ValueError(f"Invalid square: {text}")
    file_ch, rank_ch = text[0], text[1]
    if file_ch < "a" or file_ch > "h" or rank_ch < "1" or rank_ch > "8":
        raise ValueError(f"Invalid square: {text}")
    c = ord(file_ch) - ord("a")
    r = 8 - int(rank_ch)
    return r, c


@dataclass
class Move:
    src: Square#Starting square
    dst: Square#Ending square
    promotion: Optional[str] = None#Promotion
    moved_piece: Optional["Piece"] = None#Moved piece
    captured_piece: Optional["Piece"] = None#Captured piece
    prev_turn: Optional[str] = None#Turn before the move, for undo

    def uci(self) -> str:
        #Returns the move in coordinate format like e2e4 or e7e8q.

        text = square_name(*self.src) + square_name(*self.dst)
        if self.promotion:
            text += self.promotion.lower()
        return text

    def __str__(self) -> str:
        return self.uci()


class Piece:
    #Default piece type and value. Subclasses override these.
    kind = "?"
    value = 0

    def __init__(self, color: str):
        #Creates a piece with color "w" or "b".
        if color not in ("w", "b"):
            raise ValueError("color must be 'w' or 'b'")
        self.color = color

    @property
    def symbol(self) -> str:
        #Returns the printed character for this piece. white=uppercase, black=lower
        return self.kind.upper() if self.color == "w" else self.kind.lower()

    def copy(self) -> "Piece":
        #Creates a new piece of the same type and color,used when cloning boards.
        return type(self)(self.color)

    def _slide_moves(self, board: "Board", r: int, c: int, dirs: List[Tuple[int, int]]) -> List[Move]:
        """
        Generate moves for pieces that move continuously in a direction (sliding pieces).
        Helper method used by Bishop, Rook, and Queen.

        Parameters:
            board: the current board object
            r: current row of the piece
            c: current column of the piece
            directions: list of (row_change, col_change) pairs representing directions

        Output:
            A list of Move objects representing valid moves.

        Rules:
            - For each direction, keep moving until:
                • You go out of bounds
                • You hit another piece
            - If a square is empty -> add move and continue
            - If it has an enemy piece -> add move and STOP in that direction
            - If it has your own piece -> STOP immediately (do not add move)
            - Do not modify the board

        Reasoning:
            Sliding pieces (Bishop, Rook, Queen) move in straight lines along their allowed
            directions. We iterate through each direction and keep stepping until we hit a
            boundary or a piece. Captures are recorded but terminate the slide in that direction.

        Hint:
            Use a loop to continue stepping in each direction.
        """
        moves = []
        # For each direction the piece can move (e.g., diagonals for bishops, straight lines for rooks)
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            # Keep sliding in this direction until we go out of bounds or hit a piece
            while in_bounds(nr, nc):
                target_piece = board.grid[nr][nc]
                if target_piece is None:
                    # Empty square: add move and continue sliding in this direction
                    moves.append(Move(src=(r, c), dst=(nr, nc)))
                elif target_piece.color != self.color:
                    # Enemy piece: add capture move and stop sliding (cannot go past capture)
                    moves.append(Move(src=(r, c), dst=(nr, nc), captured_piece=target_piece))
                    break
                else:
                    # Own piece: cannot capture friendly piece, stop immediately without adding
                    break
                # Move one step further in the current direction
                nr += dr
                nc += dc
        return moves

    def _step_moves(self, board: "Board", r: int, c: int, deltas: List[Tuple[int, int]]) -> List[Move]:

        """
        Generate moves for pieces that move a fixed distance (one step per direction).
        Helper method used by King and Knight (though Knight uses different logic).

        Parameters:
            board: the current board object (used to check positions and pieces)
            r: current row of the piece
            c: current column of the piece
            steps: list of (row_change, col_change) pairs representing possible moves

        Output:
            A list of Move objects representing valid moves for this piece.

        Rules:
            - Each step represents a single possible move (no looping).
            - The move must stay inside the board.
            - If the destination square is empty -> add the move.
            - If the destination has an enemy piece -> add the move.
            - If the destination has your own piece -> do NOT add the move.
            - Do not modify the board.

        Reasoning:
            Unlike sliding pieces, kings and knights have fixed move patterns. A king can move
            one square in any direction (8 possible moves), and knights move in L-shapes.
            We simply check each possible destination without continuing in any direction.
            This differs from sliding moves which continue until blocked.

        Hint:
            Loop through each (dr, dc) in steps and check the resulting square.
        """
        moves = []
        # For each possible destination (fixed set of moves, not sliding)
        for dr, dc in deltas:
            nr, nc = r + dr, c + dc
            # Check if destination is within board bounds
            if in_bounds(nr, nc):
                target_piece = board.grid[nr][nc]
                # Can move to empty squares or capture enemy pieces
                if target_piece is None or target_piece.color != self.color:
                    moves.append(Move(src=(r, c), dst=(nr, nc)))
        return moves
       

    def pseudo_legal_moves(self, board: "Board", r: int, c: int) -> List[Move]:
        #Abstract method implemented by subclasses
        raise NotImplementedError

    def attacks(self, board: "Board", r: int, c: int) -> List[Square]:
        #Returns all attacked squares on p-l moves, used for check detection
        return [mv.dst for mv in self.pseudo_legal_moves(board, r, c)]


class Pawn(Piece):
    """Pawn piece: the most numerous but least powerful piece. Moves forward, captures diagonally."""
    kind = "P"
    value = 100 #Worth 100 in evaluation function

    def pseudo_legal_moves(self, board: "Board", r: int, c: int) -> List[Move]:
        """
        Generate all pseudo-legal moves for a pawn.
        Pawns have special movement rules: they move forward but capture diagonally.

        Parameters:
            board: the current board object
            r: current row of the pawn
            c: current column of the pawn

        Output:
            A list of Move objects for this pawn.

        Rules:
            - Pawn moves depend on color:
                • White moves up (row decreases)
                • Black moves down (row increases)
            - Forward move:
                • Can move 1 square forward if empty
            - Capture move:
                • Can move diagonally forward if an enemy piece is present

            ● pawn may move 2 squares from starting position
            ● promotion must include q, r, b, n
            - Do NOT allow moving off the board
            - Do NOT modify the board

        Reasoning:
            Pawns are unique: they move forward one square (or two from start) but capture
            diagonally. We handle color-specific direction, check for promotion (when reaching
            the opposite end), and generate all possible moves including promotion variants.
            Pawns are pseudo-legal here because we don't check if moving would expose the king.

        Hint:
            Check forward square and diagonal squares separately.
        """
        # Determine direction and starting position based on pawn color
        if self.color == "w":
            # White pawns move upward (decreasing row index)
            forward = (r - 1, c)
            double_forward = (r - 2, c)
            captures = [(r - 1, c - 1), (r - 1, c + 1)]
            start_row = 6  # White pawns start on row 6
            promo_row = 0  # Promote when reaching row 0 (rank 8)
        else:
            # Black pawns move downward (increasing row index)
            forward = (r + 1, c)
            double_forward = (r + 2, c)
            captures = [(r + 1, c - 1), (r + 1, c + 1)]
            start_row = 1  # Black pawns start on row 1
            promo_row = 7  # Promote when reaching row 7 (rank 1)
        
        moves = []
        
        # Forward pawn move: one square ahead if empty
        if in_bounds(*forward) and board.grid[forward[0]][forward[1]] is None:
            if forward[0] == promo_row:
                # Pawn reaching promotion rank: generate 4 moves (promote to q, r, b, n)
                for promo in "qrbn":
                    moves.append(Move(src=(r, c), dst=forward, promotion=promo))
            else:
                # Regular forward move
                moves.append(Move(src=(r, c), dst=forward))
            
            # Double forward move: two squares from starting position if both squares empty
            if r == start_row and in_bounds(*double_forward) and board.grid[double_forward[0]][double_forward[1]] is None:
                moves.append(Move(src=(r, c), dst=double_forward))

        # Diagonal pawn captures: can capture diagonally forward if enemy piece present
        for cap in captures:
            if in_bounds(*cap):
                target_piece = board.grid[cap[0]][cap[1]]
                # Can only capture if there's an enemy piece on the diagonal
                if target_piece is not None and target_piece.color != self.color:
                    if cap[0] == promo_row:
                        # Capture with promotion: 4 variants
                        for promo in "qrbn":
                            moves.append(Move(src=(r, c), dst=cap, promotion=promo))
                    else:
                        # Regular capture
                        moves.append(Move(src=(r, c), dst=cap))

        return moves

#Same template now for rest
class Knight(Piece):
    """Knight piece: moves in L-shaped patterns (2 squares + 1 square perpendicular)."""
    kind = "N"
    value = 320

    def pseudo_legal_moves(self, board: "Board", r: int, c: int) -> List[Move]:
        """
        Generate all pseudo-legal moves for a knight.
        Knights have a unique movement pattern compared to other pieces.

        Parameters:
            board: the current board object
            r: current row of the knight
            c: current column of the knight

        Output:
            A list of Move objects.

        Rules:
            - Knight moves in L-shapes:
                (±2, ±1) and (±1, ±2)
            - Knight can jump over pieces
            - If destination is empty → add move
            - If destination has enemy piece → add move
            - If destination has own piece → do NOT add
            - Must stay within board bounds

        Reasoning:
            Knights move in a fixed L-shaped pattern (2 squares in one direction, 1 in
            perpendicular) and can jump over other pieces. There are exactly 8 possible
            destination squares from any given position. We check each without sliding.
            This unique jumping ability makes knights very useful for tactics.

        Hint:
            Use a predefined list of 8 possible moves.
        """
        # All 8 possible L-shaped moves a knight can make
        knight_moves = [
            (r - 2, c - 1), (r - 2, c + 1),  # 2 up, 1 left/right
            (r - 1, c - 2), (r - 1, c + 2),  # 1 up, 2 left/right
            (r + 1, c - 2), (r + 1, c + 2),  # 1 down, 2 left/right
            (r + 2, c - 1), (r + 2, c + 1),  # 2 down, 1 left/right
        ]
        
        moves = []
        # Check each possible knight move
        for move in knight_moves:
            if in_bounds(*move):
                target_piece = board.grid[move[0]][move[1]]
                # Can move to empty squares or capture enemy pieces
                if target_piece is None or target_piece.color != self.color:
                    moves.append(Move(src=(r, c), dst=move))
        
        return moves 


class Bishop(Piece):
    """Bishop piece: moves diagonally any number of squares."""
    kind = "B"
    value = 330

    def pseudo_legal_moves(self, board: "Board", r: int, c: int) -> List[Move]:
        """Generate all pseudo-legal moves for a bishop using diagonal sliding."""
        # Use the sliding move helper with the 4 diagonal directions
        # (-1, -1) = up-left, (-1, 1) = up-right, (1, -1) = down-left, (1, 1) = down-right
        return self._slide_moves(board, r, c, [(-1, -1), (-1, 1), (1, -1), (1, 1)])


class Rook(Piece):
    """Rook piece: moves horizontally or vertically any number of squares."""
    kind = "R"
    value = 500

    def pseudo_legal_moves(self, board: "Board", r: int, c: int) -> List[Move]:
        """
        Generate all pseudo-legal moves for a rook.
        Rooks move in straight lines (orthogonally) and are among the most mobile pieces.

        Parameters:
            board: the current board object
            r: current row of the rook
            c: current column of the rook

        Output:
            A list of Move objects.

        Rules:
            - Rook moves in straight lines:
                 Up, Down, Left, Right
            - Must continue moving until blocked
            - Use sliding movement logic
            - Do not modify the board

        Reasoning:
            Rooks are sliding pieces that move orthogonally (4 directions: up, down, left, right).
            We delegate to the _slide_moves helper with the four orthogonal directions.
            The helper handles sliding until blocked and capture logic. Rooks are very powerful
            pieces and are worth about 5 pawns in material value.

        Hint:
            Call the sliding move helper with the correct directions.
        """
        # Use the sliding move helper with the 4 orthogonal directions
        # (-1, 0) = up, (1, 0) = down, (0, -1) = left, (0, 1) = right
        pseudo_moves = self._slide_moves(board, r, c, [(-1, 0), (1, 0), (0, -1), (0, 1)])
        return pseudo_moves



class Queen(Piece):
    """Queen piece: combines rook and bishop, moving horizontally, vertically, or diagonally."""
    kind = "Q"
    value = 900

    def pseudo_legal_moves(self, board: "Board", r: int, c: int) -> List[Move]:
        """
        Generate all pseudo-legal moves for a queen using both diagonal and orthogonal sliding.
        The queen is the most powerful piece, combining rook and bishop movement.
        """
        # Use the sliding move helper with all 8 directions (4 diagonals + 4 orthogonal)
        # This makes the queen one of the most powerful pieces on the board
        return self._slide_moves(board, r, c, [
            (-1, -1), (-1, 1), (1, -1), (1, 1),  # Diagonals (like bishop)
            (-1, 0), (1, 0), (0, -1), (0, 1),    # Orthogonal (like rook)
        ])


class King(Piece):
    """King piece: moves one square in any direction. Most important piece in chess."""
    kind = "K"
    value = 20000

    def pseudo_legal_moves(self, board: "Board", r: int, c: int) -> List[Move]:
        """
        Generate all pseudo-legal moves for a king (one square in any direction).
        The king is the most important piece - if it's checkmated, you lose.
        """
        # Use the step move helper with all 8 surrounding squares
        # Kings move one square per turn but can attack in all directions
        return self._step_moves(board, r, c, [
            (-1, -1), (-1, 0), (-1, 1),  # Up row (left, center, right)
            (0, -1),           (0, 1),   # Same row (left, right)
            (1, -1),  (1, 0),  (1, 1),   # Down row (left, center, right)
        ])

#Maps piece symbol to class
PIECE_MAP = {
    "p": Pawn,
    "n": Knight,
    "b": Bishop,
    "r": Rook,
    "q": Queen,
    "k": King,
}

#Converts char from text board file into a piece object/None
def piece_from_symbol(ch: str) -> Optional[Piece]:
    if ch == ".":
        return None
    if len(ch) != 1 or ch.lower() not in PIECE_MAP:
        raise ValueError(f"Unknown piece symbol: {ch}")
    cls = PIECE_MAP[ch.lower()]
    color = "w" if ch.isupper() else "b"
    return cls(color)

#Other way round.
def symbol_from_piece(piece: Optional[Piece]) -> str:
    return "." if piece is None else piece.symbol
