# ECE122-Project-3: Chess Engine

A fully functional chess game implementation with an AI engine that uses negamax search with alpha-beta pruning.

## Overview

This project implements a complete chess game in Python featuring:
- **Full chess rules implementation** including move validation, check detection, and checkmate/stalemate recognition
- **AI engine** using negamax search algorithm with alpha-beta pruning for intelligent move selection
- **Interactive CLI** for playing against the engine or analyzing positions
- **Position evaluation** using piece-value tables and positional assessment
- **Game logging and replay** with move history and save/load functionality

## Project Structure

The implementation is divided into three main components (which were the assignment focus):

### 1. **pieces.py** - Chess Piece Definitions and Movement Rules
Defines all six piece types (Pawn, Knight, Bishop, Rook, Queen, King) with their unique movement patterns.

**Key Features:**
- `_slide_moves()`: Helper for sliding pieces (Bishop, Rook, Queen) that move in straight lines until blocked
- `_step_moves()`: Helper for pieces with fixed move patterns (King, Knight)
- Each piece class implements `pseudo_legal_moves()` to generate candidate moves based on piece-specific rules
- Movement rules handle:
  - Pawn: forward movement (with double-move from start), diagonal captures, and promotion
  - Knight: L-shaped moves that can jump over pieces
  - Bishop: diagonal sliding movement
  - Rook: orthogonal (straight-line) sliding movement
  - Queen: combination of bishop and rook (8-direction sliding)
  - King: single square in any direction

### 2. **board.py** - Board State Management and Legal Move Generation
Manages the 8×8 chess board, applies moves, tracks game state, and enforces chess rules.

**Key Methods:**
- `apply_move()`: Updates board state, handles captures and promotions, maintains move history for undo
- `generate_pseudo_legal_moves()`: Generates all possible moves for the current player (ignoring check)
- `generate_legal_moves()`: Filters pseudo-legal moves by testing each one to ensure the king isn't left in check
- `is_game_over()`: Returns True if the current player has no legal moves
- `result()`: Determines game outcome (ongoing, checkmate, or stalemate)
- `in_check()`: Detects if a player's king is under attack
- Supports move undo, position cloning, and game serialization

**Core Logic:**
- Legal move generation works by testing pseudo-legal moves: apply each, check if king is safe, undo if not
- Maintains full move history for replay and analysis
- Implements move validation to reject illegal moves in `play_move_text()`

### 3. **eval.py** - Position Evaluation for Search Algorithm
Evaluates board positions numerically so the AI engine can rank different moves.

**Evaluation Components:**
- **Material Count**: Values each piece type (Pawn=100, Knight=320, Bishop=330, Rook=500, Queen=900)
- **Piece-Square Tables**: Positional bonuses/penalties based on piece location (e.g., central squares are better)
- **Mobility Bonus**: Rewards positions with more legal moves available
- **Check Penalty**: Penalizes positions where the king is in check
- `evaluate()`: Returns position score from current player's perspective (for use in negamax search)

## Supporting Files

### main.py - Interactive CLI Interface
Provides a command-line interface for playing chess:
- `board`: Display current board position
- `move e2e4`: Make a move (algebraic notation)
- `hint`: Get best move suggestion from engine
- `ai`: Let engine make one move
- `depth N`: Set search depth for engine
- `auto N`: Let engine play N moves
- `undo`: Undo last move
- `save/load`: Save and load game positions

### search.py - Game Tree Search Engine
Implements the AI using negamax algorithm with:
- Alpha-beta pruning for efficiency
- Transposition table to cache already-analyzed positions
- Configurable search depth
- Time limit support (optional)
- Move ordering to improve pruning effectiveness

### movegen.py - Move Ordering
Optimizes search by examining promising moves first:
- Capture moves scored highest (especially if they win material)
- Promotions scored very high
- Central moves slightly favored
- King moves given slight preference

### io_utils.py - File I/O Utilities
- `save_position()`: Serialize board to text file
- `load_position()`: Deserialize board from text file
- `save_moves()`: Save move list for game replay
- `load_moves()`: Load move list from file

### tests.py - Test Suite
Validates core functionality:
- Starting position has 20 legal moves
- Make/undo functionality works correctly
- Illegal moves are properly rejected
- Save/load preserves board state

## How It Works

### Move Generation Flow
1. For each piece of the current player, generate all possible moves based on piece type
2. Filter these "pseudo-legal" moves by testing each: does it leave our king in check?
3. Only keep moves where the king is safe after the move

### Search Algorithm (AI Engine)
1. Uses negamax search (simplified minimax) with alpha-beta pruning
2. Evaluates positions at maximum depth using piece values and positional assessment
3. Prunes branches where one side is clearly winning (alpha-beta cutoff)
4. Uses transposition table to avoid re-evaluating identical positions
5. Returns best move found within specified search depth

### Game State Representation
- 8×8 grid of pieces (or None for empty squares)
- Current player's turn ("w" for white, "b" for black)
- Move history for undo and game logging
- Piece positions encoded as (row, column) with row 0 = rank 8, row 7 = rank 1

## Running the Program

```bash
python3 main.py
```

Then use commands like:
```
> move e2e4      # Play move (white pawn e2→e4)
> hint           # Get AI recommendation
> ai             # Let AI make a move
> depth 5        # Set search depth to 5 plies (2.5 full moves)
> auto 10        # Let AI play 10 half-moves
> undo           # Take back last move
```

## Key Implementation Details

### Chess Rules Implemented
✓ Piece movement rules for all 6 piece types  
✓ Capture mechanics (including en passant setup, though not implemented)  
✓ Pawn promotion (to Q, R, B, or N)  
✓ Check and checkmate detection  
✓ Stalemate detection  
✓ Move validation (can't move into/stay in check)  
✓ Move history and undo functionality  

### Limitations
- En passant capture not implemented
- Castling not implemented
- 50-move rule not implemented
- Threefold repetition not implemented
- No time controls, only depth controls

## Original Assignment

The instructor provided most of the code; students were responsible for implementing:
1. **pieces.py**: Movement rules for all piece types
2. **board.py**: Board state management and move validation
3. **eval.py**: Position evaluation for the search engine

All three files now include comprehensive comments explaining the reasoning behind each function.
