from const import *
from square import Square
from piece import *
from move import Move
from sound import Sound
import copy
import os

class Board:
    def __init__(self):
        self.squares = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.move_history = []
        self.last_move = None 
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')

    def evaluate(self):
        piece_value = {
            Pawn: 1, Knight: 3, Bishop: 3,
            Rook: 5, Queen: 9, King: 1000
        }
        score = 0
        for row in self.squares:
            for square in row:
                piece = square.piece
                if piece:
                    value = piece_value[type(piece)]
                    if piece.color == 'black':  # Assuming AI is black
                        score += value
                    else:
                        score -= value
        return score
    
    def minimax(self, depth, maximizingPlayer):
        if depth == 0 or self.is_game_over():
            return self.evaluate()

        if maximizingPlayer:
            maxEval = float('-inf')
            for move in self.get_all_possible_moves('black'):  # Assuming AI is black
                self.move_piece(move)
                evaluation = self.minimax(depth - 1, False)
                self.undo_move(move)
                maxEval = max(maxEval, evaluation)
            return maxEval
        else:
            minEval = float('inf')
            for move in self.get_all_possible_moves('white'):
                self.move_piece(move)
                evaluation = self.minimax(depth - 1, True)
                self.undo_move(move)
                minEval = min(minEval, evaluation)
            return minEval
    
    def move(self, piece, move, testing=False):
        if move not in piece.moves:
            raise ValueError("Invalid move")       
        initial = move.initial
        final = move.final

        # Ensure that the move is valid for the piece
        if move not in piece.moves:
            raise ValueError("Invalid move")
        
        en_passant_empty = self.squares[final.row][final.col].isempty()


        if isinstance(piece, Pawn):
            # en passant capture
            diff = final.col - initial.col
            if diff != 0 and en_passant_empty:
                # console board move update
                self.squares[initial.row][initial.col + diff].piece = None
                self.squares[final.row][final.col].piece = piece
                if not testing:
                    sound = Sound(os.path.join(
                        'assets/sounds/capture.wav'
                    ))
                    sound.play()

            # pawn promotion
            else:
                self.check_promotion(piece, final)

        # king castling
        if isinstance(piece, King):
            if self.castling(initial, final) and not testing:
                diff = final.col - initial.col
                rook = piece.left_rook if (diff < 0) else piece.right_rook
                self.move(rook, rook.moves[-1])

        # move
        piece.moved = True

        # console board move update
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece
        self.last_move = move


    def move_piece(self, move):
        initial_square = move.initial
        final_square = move.final

        # Check for valid squares
        if not initial_square or not final_square:
            print("Invalid move: Missing initial or final square")
            return

        piece = self.squares[initial_square.row][initial_square.col].piece

        # Check if there's a piece at the initial square
        if not piece:
            print("Invalid move: No piece found at initial square")
            return

        # Check if the move is valid for the piece
        if move not in piece.moves:
            print("Invalid move: Move not in piece's move list")
            return

        # Capturing a piece, if there's one at the final square
        captured_piece = self.squares[final_square.row][final_square.col].piece

        # Update pawn's moved property if it's a pawn
        if isinstance(piece, Pawn):
            piece.moved = True

        # Now that the move is validated, update the board state
        # Remove the piece from its initial position
        self.squares[initial_square.row][initial_square.col].piece = None

        # Place the piece in its final position
        self.squares[final_square.row][final_square.col].piece = piece

        # Update the piece's position
        piece.row, piece.col = final_square.row, final_square.col

        # Record the move and the captured piece in move history
        self.move_history.append((move, captured_piece))

        # Update last_move
        self.last_move = move

    def undo_move(self):
        if not self.move_history:
            return  # No move to undo

        # Retrieve the last move and the captured piece from the history
        last_move, captured_piece = self.move_history.pop()

        # Revert the move
        initial_square = last_move.initial
        final_square = last_move.final

        # Move the piece back to its original square
        piece = self.squares[final_square.row][final_square.col].piece
        self.squares[initial_square.row][initial_square.col].piece = piece
        self.squares[final_square.row][final_square.col].piece = captured_piece

        # Update the piece's position back (if your implementation requires it)
        piece.row, piece.col = initial_square.row, initial_square.col

    def is_in_check(self, player_color):
        # Find the king's position
        king_pos = None
        for row in self.squares:
            for square in row:
                piece = square.piece
                if piece and piece.color == player_color and isinstance(piece, King):
                    king_pos = (square.row, square.col)
                    break
            if king_pos:
                break

        # Check if any opponent's pieces can attack the king
        opponent_color = 'black' if player_color == 'white' else 'white'
        for row in self.squares:
            for square in row:
                piece = square.piece
                if piece and piece.color == opponent_color:
                    self.calc_moves(piece, square.row, square.col, bool=True)
                    for move in piece.moves:
                        if move.final.row == king_pos[0] and move.final.col == king_pos[1]:
                            return True
        return False

    def is_checkmate(self, player_color):
        if not self.is_in_check(player_color):
            return False

        for row in self.squares:
            for square in row:
                piece = square.piece
                if piece and piece.color == player_color:
                    self.calc_moves(piece, square.row, square.col, bool=True)
                    for move in piece.moves:
                        self.move_piece(move)
                        if not self.is_in_check(player_color):
                            self.undo_move()
                            return False
                        self.undo_move()
        return True
    
    def is_stalemate(self, player_color):
        if self.is_in_check(player_color):
            return False

        for row in self.squares:
            for square in row:
                piece = square.piece
                if piece and piece.color == player_color:
                    self.calc_moves(piece, square.row, square.col, bool=True)
                    if piece.moves:
                        return False
        return True

    def is_game_over(self):
        return self.is_checkmate('white') or self.is_checkmate('black') or self.is_stalemate('white') or self.is_stalemate('black')
     

    def valid_move(self, piece, move):
        return move in piece.moves 
    
    def check_promotion(self, piece, final):
        if final.row == 0 or final.row == 7:
            self.squares[final.row][final.col].piece = Queen(piece.color)

    def castling(self, initial, final):
        return abs(initial.col - final.col) == 2 
    
    def set_true_en_passant(self, piece):
        
        if not isinstance(piece, Pawn):
            return

        for row in range(ROWS):
            for col in range(COLS):
                if isinstance(self.squares[row][col].piece, Pawn):
                    self.squares[row][col].piece.en_passant = False
        
        piece.en_passant = True
    
    def in_check(self, piece, move):
        temp_piece = copy.deepcopy(piece)
        temp_board = copy.deepcopy(self)

        # Update temp_piece's position to match the initial position of the move
        temp_piece.row = move.initial.row
        temp_piece.col = move.initial.col

        # Recalculate moves for temp_piece on temp_board
        temp_board.calc_moves(temp_piece, temp_piece.row, temp_piece.col, bool=False)

        # Simulate the move
        temp_board.move(temp_piece, move, testing=True)

        # Check if this simulated move puts the king in check
        for row in range(ROWS):
            for col in range(COLS):
                if temp_board.squares[row][col].has_enemy_piece(piece.color):
                    p = temp_board.squares[row][col].piece
                    temp_board.calc_moves(p, row, col, bool=False)
                    for m in p.moves:
                        if isinstance(m.final.piece, King):
                            return True

        return False
    
    def get_all_possible_moves(self, player_color):
        all_moves = []
        for row in self.squares:
            for square in row:
                piece = square.piece
                if piece and piece.color == player_color:
                    self.calc_moves(piece, square.row, square.col, bool=True)
                    all_moves.extend(piece.moves)
        return all_moves


    def calc_moves(self, piece, row, col, bool=True):
        '''
            Calculate all the possible (valid) moves of a specifc piece on a specific position 
        '''
        # Clear existing moves before calculating new ones
        piece.clear_moves()

        def pawn_moves():
    
            move = None  # Initialize move to None at the beginning
            # Steps
            steps = 1 if piece.moved else 2

            # vertical moves
            start = row + piece.dir
            end = row + (piece.dir * (1 + steps))
            for possible_move_row in range(start, end, piece.dir):
                if Square.in_range(possible_move_row):
                    if self.squares[possible_move_row][col].isempty():
                        # create initial and final move squares
                        initial = Square(row, col)
                        final = Square(possible_move_row, col)
                        # create a new move
                        move = Move(initial, final)

                        # check potencial checks
                        if bool:
                            if not self.in_check(piece, move):
                                # append new move
                                piece.add_move(move)
                        else:
                            # append new move
                            piece.add_move(move)
                    # blocked
                    else: break
                # not in range
                else: break

            # diagonal moves
            possible_move_row = row + piece.dir
            possible_move_cols = [col-1, col+1]
            for possible_move_col in possible_move_cols:
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                        # create initial and final move squares
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        # create a new move
                        move = Move(initial, final)
                        
                        # check potencial checks
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)

            # en passant moves
            r = 3 if piece.color == 'white' else 4
            fr = 2 if piece.color == 'white' else 5
            # left en pessant
            if Square.in_range(col-1) and row == r:
                if self.squares[row][col-1].has_enemy_piece(piece.color):
                    p = self.squares[row][col-1].piece
                    if isinstance(p, Pawn):
                        if p.en_passant:
                            # create initial and final move squares
                            initial = Square(row, col)
                            final = Square(fr, col-1, p)
                            # create a new move
                            move = Move(initial, final)
                        
                        # check potencial checks
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)

            # right en passant
            if Square.in_range(col+1) and row == r:
                if self.squares[row][col+1].has_enemy_piece(piece.color):
                    p = self.squares[row][col+1].piece
                    if isinstance(p, Pawn):
                        if p.en_passant:
                            # create initial and final move squares
                            initial = Square(row, col)
                            final = Square(fr, col+1, p)
                            # create a new move
                            move = Move(initial, final)
                        
                            # check potencial checks
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)
                        
                            
        def knight_moves():
            possible_moves = [
                (row-2, col+1),
                (row-1, col+2),
                (row+1, col+2),
                (row+2, col+1),
                (row+2, col-1),
                (row+1, col-2),
                (row-1, col-2),
                (row-2, col-1),
            ]

            for possible_move in possible_moves:
                possible_move_row, possible_move_col = possible_move 
                
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.color):
                        # create squares of the new move
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece) 
                        # create a new move
                        move = Move(initial, final)
                        
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                            else: break
                        else:
                            piece.add_move(move)
        
        def straightline_moves(incrs):
            for incr in incrs:
                row_incr, col_incr = incr
                possible_move_row = row + row_incr 
                possible_move_col = col + col_incr

                while True:
                    if Square.in_range(possible_move_row, possible_move_col):
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        # create a possible new move
                        move = Move(initial, final)
                        
                        # empty
                        if self.squares[possible_move_row][possible_move_col].isempty():
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)

                        # has enemy piece
                        elif self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)
                            break

                        # has a team piece
                        elif self.squares[possible_move_row][possible_move_col].has_team_piece(piece.color):
                            break

                    # not in range 
                    else: break

                    
                    # incrementing incr
                    possible_move_row = possible_move_row + row_incr
                    possible_move_col = possible_move_col + col_incr

        def king_moves():
            adjs = [
                (row-1, col+0), # up
                (row-1, col+1), # up-right
                (row+0, col+1), # right
                (row+1, col+1), # down-right
                (row+1, col+0), # down
                (row+1, col-1), # down-left
                (row+0, col-1), #left
                (row-1, col-1), # up-left
            ]

            for possible_move in adjs:
                possible_move_row, possible_move_col = possible_move

                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.color):
                        # create squares of the new move
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col) 
                        # create a new move
                        move = Move(initial, final)
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                            else: break
                        else:
                            piece.add_move(move)

            # castling moves
            if not piece.moved:
                # queen castling
                left_rook = self.squares[row][0].piece
                if isinstance(left_rook, Rook):
                    if not left_rook.moved:
                        for c in range(1, 4):
                            if self.squares[row][c].has_piece(): 
                                break

                            if c == 3:
                                # adds left rook to king
                                piece.left_rook = left_rook 

                                # rook move
                                initial = Square(row, 0)
                                final = Square(row, 3)
                                moveR = Move(initial, final)

                                # king move
                                initial = Square(row, col)
                                final = Square(row, 2)
                                moveK = Move(initial, final)

                                if bool:
                                    if not self.in_check(piece, moveK) and not self.in_check(left_rook, moveR):
                                        # append new move to rook 
                                        left_rook.add_move(moveR)                                       
                                        # append new move to king 
                                        piece.add_move(moveK)
                                else:
                                    # append new move to rook 
                                    left_rook.add_move(moveR) 
                                    # append new move to king 
                                    piece.add_move(moveK)
                        
                # king castling
                right_rook = self.squares[row][7].piece
                if isinstance(right_rook, Rook):
                    if not right_rook.moved:
                        for c in range(5, 7):
                            if self.squares[row][c].has_piece(): 
                                break

                            if c == 6:
                                # adds right rook to king
                                piece.right_rook = right_rook 

                                # rook move
                                initial = Square(row, 7)
                                final = Square(row, 5)
                                moveR = Move(initial, final)

                                # king move
                                initial = Square(row, col)
                                final = Square(row, 6)
                                moveK = Move(initial, final)

                                if bool:
                                    if not self.in_check(piece, moveK) and not self.in_check(right_rook, moveR):
                                        # append new move to rook 
                                        right_rook.add_move(moveR)                                       
                                        # append new move to king 
                                        piece.add_move(moveK)
                                else:
                                    # append new move to rook 
                                    right_rook.add_move(moveR) 
                                    # append new move to king 
                                    piece.add_move(moveK)
       
        if isinstance(piece, Pawn): 
            pawn_moves() 
        
        elif isinstance(piece, Knight): 
            knight_moves()

        elif isinstance(piece, Bishop): 
            straightline_moves([
                (-1, 1), # up-right
                (-1, -1), # up-left
                (1, 1), # down-right
                (1, -1), # down-left
            ])

        elif isinstance(piece, Rook): 
            straightline_moves([
                (-1, 0), # up
                (0, 1), # right
                (1, 0), # down
                (0, -1), # left
            ])

        elif isinstance(piece, Queen): 
            straightline_moves([
                (-1, 1), # up-right
                (-1, -1), # up-left
                (1, 1), # down-right
                (1, -1), # down-left
                (-1, 0), # up
                (0, 1), # right
                (1, 0), # down
                (0, -1) # left 
            ])

        elif isinstance(piece, King): 
            king_moves()
            
          
    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col, None)

    def _add_pieces(self, color):
        row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)

        # pawns
        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))

        # knights 
        self.squares[row_other][1] = Square(row_other, 1, Knight(color))
        self.squares[row_other][6] = Square(row_other, 6, Knight(color))

        # bishops 
        self.squares[row_other][2] = Square(row_other, 2, Bishop(color))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(color))

        # rooks 
        self.squares[row_other][0] = Square(row_other, 0, Rook(color))
        self.squares[row_other][7] = Square(row_other, 7, Rook(color))

        # Queen and King
        queen_col, king_col = (3, 4) if color == 'white' else (3, 4)
        self.squares[row_other][queen_col] = Square(row_other, queen_col, Queen(color))
        self.squares[row_other][king_col] = Square(row_other, king_col, King(color))
        
