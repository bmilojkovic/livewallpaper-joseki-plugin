
from OpenGL.GL import *


class Stone(object):
    black_tex = 0
    white_tex = 0
    board_size = 0
    square_size = 0
    BLACK = 1
    WHITE = 2
    EMPTY = 3
    LIBERTY = 4

    def __init__(self, pos_x, pos_y, stone_color, number):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.stone_color = stone_color
        self.number = number

    def __str__(self):
        to_return = "["
        to_return += str(self.pos_x)
        to_return += ","
        to_return += str(self.pos_y)
        to_return += ","
        if self.stone_color == Stone.BLACK:
            to_return += "B"
        elif self.stone_color == Stone.WHITE:
            to_return += "W"
        elif self.stone_color == Stone.EMPTY:
            to_return += " "
        elif self.stone_color == Stone.LIBERTY:
            to_return += "L"
        else:
            to_return += "#"
        to_return += "]"
        return to_return

    def draw(self):
        board_start = -Stone.board_size / 2
        square_start = board_start + Stone.square_size / 2

        real_pos_x = square_start + Stone.square_size * self.pos_x
        real_pos_y = square_start + Stone.square_size * self.pos_y

        if self.stone_color == Stone.BLACK:
            Stone.black_tex.enable()
        else:
            Stone.white_tex.enable()

        glBegin(GL_QUADS)
        glTexCoord2d(1.0, 0.0)
        glVertex2f(real_pos_x + Stone.square_size / 2, real_pos_y + Stone.square_size / 2)
        glTexCoord2d(0.0, 0.0)
        glVertex2f(real_pos_x - Stone.square_size / 2, real_pos_y + Stone.square_size / 2)
        glTexCoord2d(0.0, 1.0)
        glVertex2f(real_pos_x - Stone.square_size / 2, real_pos_y - Stone.square_size / 2)
        glTexCoord2d(1.0, 1.0)
        glVertex2f(real_pos_x + Stone.square_size / 2, real_pos_y - Stone.square_size / 2)
        glEnd()

        if self.stone_color == Stone.BLACK:
            Stone.black_tex.disable()
        else:
            Stone.white_tex.disable()


