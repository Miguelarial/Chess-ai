import pygame 

from const import *

class Dragger:

    def __init__(self):
        self.piece = None
        self.dragging = False
        self.mouseX = 0
        self.mouseY = 0
        self.initial_row = 0
        self.initial_col = 0
        self.img = None 


    # other methods

    def update_mouse(self, pos):
        self.mouseX, self.mouseY = pos # (xcor, ycor)

    def save_initial(self, pos):
        self.initial_row = pos[1] // SQSIZE
        self.initial_col = pos[0] // SQSIZE 

    def drag_piece(self, piece):
        self.piece = piece
        self.dragging = True
        # Resize the piece's texture to make it look bigger when picked up
        self.piece.set_texture(size=128)
        self.img = pygame.image.load(piece.texture).convert_alpha()  # load image once 
    
    def update_blit(self, surface):
        if self.piece:
            img_center = (self.mouseX, self.mouseY)
            self.piece.texture_rect = self.img.get_rect(center=img_center)
            surface.blit(self.img, self.piece.texture_rect)

    def undrag_piece(self):
        # Resize the piece's texture back to its original size when dropped
        if self.piece:
            self.piece.set_texture(size=80)
            self.piece = None
            self.dragging = False