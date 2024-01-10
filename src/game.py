import pygame
from const import ROWS, COLS, SQSIZE, HEIGHT
from typing import Any
from board import Board
from dragger import Dragger 
from config import Config
from square import Square

class Game:

    def __init__(self):
        self.next_player = 'white'
        self.hovered_sqr = None
        self.board = Board()
        self.dragger = Dragger()
        self.config = Config()

    # Show methods

    def show_bg(self, surface):      
        theme = self.config.theme

        for row in range(ROWS):
            for col in range(COLS):
                # color
                color = theme.bg.light if (row + col) % 2 == 0 else theme.bg.dark
                # rect
                rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
                # blit
                pygame.draw.rect(surface, color, rect)

                # row coordinates
                if col == 0:
                    #color
                    color = theme.bg.dark if row % 2 == 0 else theme.bg.light 
                    # label
                    lbl = self.config.font.render(str(ROWS-row), 1, color)
                    lbl_pos = (5, 5 + row * SQSIZE)
                    # blit
                    surface.blit(lbl, lbl_pos)

                # col coordinates
                if row == 7:
                    #color
                    color = theme.bg.dark if (row + col) % 2 == 0 else theme.bg.light 
                    # label
                    lbl = self.config.font.render(Square.get_alphacol(col), 1, color)
                    lbl_pos = (col * SQSIZE + SQSIZE - 17, HEIGHT - 17)
                    # blit
                    surface.blit(lbl, lbl_pos)

    def show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board.squares[row][col].piece
                if piece and piece is not self.dragger.piece:
                    img = pygame.image.load(piece.texture).convert_alpha()
                    img_rect = img.get_rect()
                    img_rect.center = (col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2)
                    surface.blit(img, img_rect)

    def show_moves(self, surface):
        theme = self.config.theme

        if self.dragger.dragging: 
            piece = self.dragger.piece

            # loop all valid moves 
            for move in piece.moves:
                # color 
                color = theme.moves.light if (move.final.row + move.final.col) % 2 == 0 else theme.moves.dark
                # rect
                rect = (move.final.col * SQSIZE, move.final.row * SQSIZE, SQSIZE, SQSIZE)
                # blit
                blit = pygame.draw.rect(surface, color, rect)

    def show_last_move(self, surface):
        theme = self.config.theme

        if self.board.last_move:
            initial = self.board.last_move.initial 
            final = self.board.last_move.final

            for pos in [initial, final]:
                # color 
                color = theme.trace.light if (pos.row + pos.col) % 2 == 0 else theme.trace.dark 
                # rect
                rect = (pos.col * SQSIZE, pos.row * SQSIZE, SQSIZE, SQSIZE)
                # blit
                pygame.draw.rect(surface, color, rect)

    def show_hover(self, surface):
        if self.hovered_sqr:
            # color
            color = (180, 180, 180)
            # rect
            rect = (self.hovered_sqr.col * SQSIZE, self.hovered_sqr.row * SQSIZE, SQSIZE, SQSIZE)
            # blit
            pygame.draw.rect(surface, color, rect, width=3)

    # other methods
    def next_turn(self):
        self.next_player = 'white' if self.next_player == 'black' else 'black'

    def set_hover(self, row, col):
        if 0 <= row < 8 and 0 <= col < 8:
            self.hovered_sqr = self.board.squares[row][col]
        else:
            self.hovered_sqr = None  # Or any other suitable default action

    def change_theme(self):
        self.config.change_theme()

    def play_sound(self, captured=False):
        if captured:
            self.config.capture_sound.play()
        else:
            self.config.move_sound.play()

    def reset(self):
        self.__init__()
