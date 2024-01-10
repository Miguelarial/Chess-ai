import pygame
import sys

from const import *
from game import Game
from square import Square 
from move import Move 


def minimax(board, depth, maximizingPlayer):
    if depth == 0 or board.is_game_over():
        return board.evaluate()

    if maximizingPlayer:
        maxEval = float('-inf')
        for move in board.get_all_possible_moves('black'):
            # Get the piece associated with the move
            piece = board.squares[move.initial.row][move.initial.col].piece
            # Check if the move is valid
            if piece and board.valid_move(piece, move):
                board.move_piece(move)
                evaluation = minimax(board, depth - 1, False)
                board.undo_move()
                maxEval = max(maxEval, evaluation)
        return maxEval
    else:
        minEval = float('inf')
        for move in board.get_all_possible_moves('white'):
            # Get the piece associated with the move
            piece = board.squares[move.initial.row][move.initial.col].piece
            # Check if the move is valid
            if piece and board.valid_move(piece, move):
                board.move_piece(move)
                evaluation = minimax(board, depth - 1, True)
                board.undo_move()
                minEval = min(minEval, evaluation)
        return minEval

class Main:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((680, 680))
        pygame.display.set_caption('Chess')
        self.game = Game()


    def mainloop(self):
        board = self.game.board
        dragger = self.game.dragger 

        while True:
            # Render the game state
            self.render(dragger)

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    dragger.update_mouse(event.pos)
                    clicked_row = dragger.mouseY // SQSIZE
                    clicked_col = dragger.mouseX // SQSIZE
                    if board.squares[clicked_row][clicked_col].has_piece():
                        piece = board.squares[clicked_row][clicked_col].piece
                        # valid piece (color) ?
                        if piece.color == self.game.next_player:
                            board.calc_moves(piece, clicked_row, clicked_col, bool=True)
                            dragger.save_initial(event.pos)
                            dragger.drag_piece(piece)
                            # show methods 
                            self.game.show_bg(self.screen)
                            self.game.show_last_move(self.screen)
                            self.game.show_moves(self.screen)
                            self.game.show_pieces(self.screen)

                        if self.game.next_player == 'black':
                            best_move = None
                            best_score = float('-inf')
                            for move in board.get_all_possible_moves('black'):
                                board.move_piece(move)
                                score = minimax(board, 0, False) # where you can change the depth of the minimax algorithm 
                                board.undo_move(move)

                                if score > best_score:
                                    best_score = score
                                    best_move = move

                            if best_move:
                                board.move_piece(best_move)
                                board.last_move = best_move  # Update last move
                                # Switch to the next player
                                self.game.next_turn()

                elif event.type == pygame.MOUSEMOTION:
                    motion_row = event.pos[1] // SQSIZE
                    motion_col = event.pos[0] // SQSIZE

                    self.game.set_hover(motion_row, motion_col)

                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        # show methods
                        self.game.show_bg(self.screen)
                        self.game.show_last_move(self.screen)
                        self.game.show_moves(self.screen)
                        self.game.show_pieces(self.screen)
                        self.game.show_hover(self.screen)
                        dragger.update_blit(self.screen)

                elif event.type == pygame.MOUSEBUTTONUP:                   
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)

                        released_row = dragger.mouseY // SQSIZE
                        released_col = dragger.mouseX // SQSIZE

                        # create possible move
                        initial = Square(dragger.initial_row, dragger.initial_col)
                        final = Square(released_row, released_col)
                        move = Move(initial, final)

                        # valid move ?
                        if board.valid_move(dragger.piece, move):
                            # normal capture
                            captured = board.squares[released_row][released_col].has_piece()
                            board.move(dragger.piece, move)

                            board.set_true_en_passant(dragger.piece)

                            # sounds
                            self.game.play_sound(captured)
                            # show methods 
                            self.game.show_bg(self.screen)
                            self.game.show_last_move(self.screen) 
                            self.game.show_pieces(self.screen)
                            # next turn
                            self.game.next_turn()
                                       
                    dragger.undrag_piece()

                # key press 
                elif event.type == pygame.KEYDOWN:
                    
                    # changing themes
                    if event.key == pygame.K_t:
                        self.game.change_theme()

                    # restart
                    if event.key == pygame.K_r:
                        self.game.reset()
                        game = self.game
                        board = self.game.board
                        dragger = self.game.dragger 

                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # AI's turn to move
            self.execute_ai_turn()

    def execute_ai_turn(self):
        if self.game.next_player == 'black':
            best_move = None
            best_score = float('-inf')
            for move in self.game.board.get_all_possible_moves('black'):
                # Get the piece associated with the move
                piece = self.game.board.squares[move.initial.row][move.initial.col].piece

                # Check if the move is valid
                if piece and self.game.board.valid_move(piece, move):
                    self.game.board.move_piece(move)
                    score = minimax(self.game.board, 0, False)  # Adjust depth as needed
                    self.game.board.undo_move()

                    if score > best_score:
                        best_score = score
                        best_move = move

            if best_move:
                self.game.board.move_piece(best_move)
                self.game.board.last_move = best_move
                self.game.next_turn()

    def render(self, dragger):
        self.game.show_bg(self.screen)
        self.game.show_last_move(self.screen)
        self.game.show_moves(self.screen)
        self.game.show_pieces(self.screen)
        self.game.show_hover(self.screen)

        if dragger.dragging: 
                dragger.update_blit(self.screen)


        pygame.display.update()

if __name__ == "__main__":
    main = Main()
    main.mainloop()
