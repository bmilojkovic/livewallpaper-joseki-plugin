
from OpenGL.GL import *
from gi.repository import LW
import cairo
import math


class Stone(object):
    """
    This class describes a stone displayed on the board.
    Each stone has it's x-y coordinate (lower-left based),
    it's color, and number

    This class does the drawing and rendering of the stone, as well.
    """

    black_tex = None
    white_tex = None
    board_size = 0
    square_size = 0
    BLACK = 1
    WHITE = 2
    EMPTY = 3  # no stone
    LIBERTY = 4  # used in stone-capture algorithm

    def __init__(self, pos_x, pos_y, stone_color, number):
        self.pos_x = pos_x  # 0-18 value indicating position of stone from left edge of board
        self.pos_y = pos_y  # 0-18 value indicating position of stone from bottom edge of board
        self.stone_color = stone_color  # commonly BLACK or WHITE
        self.number = number
        self.stone_alpha = 0
        self.removed = False

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
        to_return += ","
        to_return += str(self.number)
        to_return += "]"
        return to_return

    def get_real_x(self):
        board_start = -Stone.board_size / 2
        square_start = board_start + Stone.square_size / 2

        return square_start + Stone.square_size * self.pos_x

    def get_real_y(self):
        board_start = -Stone.board_size / 2
        square_start = board_start + Stone.square_size / 2

        return square_start + Stone.square_size * self.pos_y

    def draw(self):
        real_pos_x = self.get_real_x()
        real_pos_y = self.get_real_y()

        if self.stone_color == Stone.BLACK:
            Stone.black_tex.enable()
        else:
            Stone.white_tex.enable()

        glColor4f(1.0, 1.0, 1.0, self.stone_alpha)
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

    @staticmethod
    def init_tex(square_size):
        # White stones
        Stone.white_tex = LW.CairoTexture.new(square_size, square_size)
        cr = Stone.white_tex.cairo_create()
        pattern = cairo.RadialGradient(square_size / 3, square_size / 3, square_size / 8,
                                       square_size / 3, square_size / 3, square_size)
        pattern.add_color_stop_rgba(0, 0.9, 0.9, 0.9, 1)
        pattern.add_color_stop_rgba(1, 0.6, 0.6, 0.6, 1)
        cr.set_source(pattern)
        cr.arc(square_size / 2, square_size / 2, square_size / 2 - 2, 0, 2 * math.pi)
        cr.fill()
        cr.set_source_rgba(0.6, 0.6, 0.6, 1)
        cr.arc(square_size / 2, square_size / 2, square_size / 2 - 2, 0, 2 * math.pi)
        cr.stroke()

        Stone.white_tex.update()
        Stone.white_tex.enable()
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        Stone.white_tex.disable()

        # Black stones
        Stone.black_tex = LW.CairoTexture.new(square_size, square_size)
        cr = Stone.black_tex.cairo_create()
        pattern = cairo.RadialGradient(square_size / 3, square_size / 3, square_size / 8,
                                       square_size / 3, square_size / 3, square_size)
        pattern.add_color_stop_rgba(0, 0.3, 0.3, 0.3, 1)
        pattern.add_color_stop_rgba(1, 0, 0, 0, 1)
        cr.set_source(pattern)
        cr.arc(square_size / 2, square_size / 2, square_size / 2 - 2, 0, 2 * math.pi)
        cr.fill()
        cr.set_source_rgba(0.1, 0.1, 0.1, 1)
        cr.arc(square_size / 2, square_size / 2, square_size / 2 - 2, 0, 2 * math.pi)
        cr.stroke()

        Stone.black_tex.update()
        Stone.black_tex.enable()
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        Stone.black_tex.disable()
