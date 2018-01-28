#
#
# Livewallpaper
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2013-2016 Maximilian Schnarr <Maximilian.Schnarr@googlemail.com>
#
#

from gi.repository import GObject, Gdk, GdkPixbuf, LW, Gio
from gi.repository import cairo, Pango, PangoCairo
from OpenGL.GL import *
import cairo, math, sgf


class Stone(object):
    black_tex = 0
    white_tex = 0
    board_size = 0
    square_size = 0
    BLACK = 1
    WHITE = 2

    def __init__(self, pos_x, pos_y, stone_color, number):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.stone_color = stone_color
        self.number = number

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


class JosekiPlugin(GObject.Object, LW.Wallpaper):
    __gproperties__ = {
        "main-alpha": (
        float, "Transparency", "Transparency of the main circle", 0.0, 1.0, 0.85, GObject.PARAM_READWRITE)
    }

    def __init__(self):
        color1 = Gdk.Color(255 * 148, 255 * 77, 255 * 85)
        color2 = Gdk.Color(255 * 47, 255 * 9, 255 * 22)
        self.background = LW.Background.new_from_colors(color1, color2, LW.BackgroundShadingType.BACKGROUNDVERTICAL)

        Stone.board_size = self.board_size = (Gdk.Screen.get_default().get_height() / 4.0) * 3.0
        Stone.square_size = self.square_size = self.board_size / 20.0
        Stone.stone_size = Stone.square_size - 1
        self.board_tex = LW.CairoTexture.new(self.board_size, self.board_size)

        # White stones
        self.white_tex = LW.CairoTexture.new(self.square_size, self.square_size)
        cr = self.white_tex.cairo_create()
        pattern = cairo.RadialGradient(self.square_size / 3, self.square_size / 3, self.square_size / 8,
                                       self.square_size / 3, self.square_size / 3, self.square_size)
        pattern.add_color_stop_rgba(0, 0.9, 0.9, 0.9, 1)
        pattern.add_color_stop_rgba(1, 0.6, 0.6, 0.6, 1)
        cr.set_source(pattern)
        cr.arc(self.square_size / 2, self.square_size / 2, self.square_size / 2 - 2, 0, 2 * math.pi)
        cr.fill()
        cr.set_source_rgba(0.6, 0.6, 0.6, 1)
        cr.arc(self.square_size / 2, self.square_size / 2, self.square_size / 2 - 2, 0, 2 * math.pi)
        cr.stroke()

        self.white_tex.update()
        Stone.white_tex = self.white_tex

        # Black stones
        self.black_tex = LW.CairoTexture.new(self.square_size, self.square_size)
        cr = self.black_tex.cairo_create()
        pattern = cairo.RadialGradient(self.square_size / 3, self.square_size / 3, self.square_size / 8,
                                       self.square_size / 3, self.square_size / 3, self.square_size)
        pattern.add_color_stop_rgba(0, 0.3, 0.3, 0.3, 1)
        pattern.add_color_stop_rgba(1, 0, 0, 0, 1)
        cr.set_source(pattern)
        cr.arc(self.square_size / 2, self.square_size / 2, self.square_size / 2 - 2, 0, 2 * math.pi)
        cr.fill()
        cr.set_source_rgba(0.1, 0.1, 0.1, 1)
        cr.arc(self.square_size / 2, self.square_size / 2, self.square_size / 2 - 2, 0, 2 * math.pi)
        cr.stroke()

        self.black_tex.update()
        Stone.black_tex = self.black_tex

        self.main_alpha = 0.85
        self.update_tex = 0
        self.kaya_img = None
        self.joseki_collection = None
        self.current_node = None
        self.stones = []

    def do_init_plugin(self):
        datadir = self.plugin_info.get_data_dir()

        self.kaya_img = cairo.ImageSurface.create_from_png(datadir + "/kaya.png")

        with open (datadir+"/example.sgf") as f:
            self.joseki_collection = sgf.parse(f.read())

        self.current_node = self.joseki_collection[0].nodes[0]

        # Bind settings
        settings = Gio.Settings.new("net.launchpad.livewallpaper.plugins.joseki")
        settings.bind("main-alpha", self, "main-alpha", Gio.SettingsBindFlags.GET)

    def do_get_property(self, prop):
        if prop.name == "main-alpha":
            return self.main_alpha
        else:
            raise AttributeError("unknown property %s" % prop.name)

    def do_set_property(self, prop, value):
        if prop.name == "main-alpha":
            self.main_alpha = value
        else:
            raise AttributeError("unknown property %s" % prop.name)

    def do_adjust_viewport(self, output):
        glPushAttrib(GL_TEXTURE_BIT)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

        glEnable(GL_BLEND)

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()

        x = output.get_width() / 2
        y = output.get_height() / 2
        glOrtho(-x, x, -y, y, 0.0, 1.0)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

    def do_paint_board(self):
        cr = self.board_tex.cairo_create()

        for i in range(int(self.board_size / self.kaya_img.get_width()) + 1):
            for j in range(int(self.board_size / self.kaya_img.get_height()) + 1):
                cr.set_source_surface(self.kaya_img, i * self.kaya_img.get_width(), j * self.kaya_img.get_height())
                cr.paint()

        cr.set_source_rgba(0.0, 0.0, 0.0, 1.0)

        cr.set_line_width(1.0)

        cr.rectangle(self.square_size / 2.0, self.square_size / 2.0, self.board_size - self.square_size, self.board_size - self.square_size)
        cr.stroke()

        for i in range(20):
            cr.move_to(self.square_size / 2.0, self.square_size / 2.0 + i * self.square_size)
            cr.line_to(self.board_size - self.square_size / 2.0, self.square_size / 2.0 + i * self.square_size)
            cr.move_to(self.square_size / 2.0 + i * self.square_size, self.square_size / 2.0)
            cr.line_to(self.square_size / 2.0 + i * self.square_size, self.board_size - self.square_size / 2.0)
            cr.stroke()

        self.board_tex.update()

    def make_stone(self, node):
        if "B" in node.properties.keys():
            node_string = node.properties["B"]
            stone_color = Stone.BLACK
        elif "W" in node.properties.keys():
            node_string = node.properties["W"]
            stone_color = Stone.WHITE
        else:
            return None

        stone_x = ord(node_string[0][0]) - ord('a')
        stone_y = ord(node_string[0][1]) - ord('a')

        return Stone(stone_x, stone_y, stone_color)

    def do_prepare_paint(self, ms_since_last_paint):
        self.update_tex -= ms_since_last_paint

        # Update main texture
        if self.update_tex <= 0:
            self.do_paint_board()

            self.current_node = self.current_node.next

            if self.current_node is None:
                self.current_node = self.joseki_collection[0].nodes[0]
                self.stones = []

            while self.make_stone(self.current_node) is None:
                self.current_node = self.current_node.next

            self.stones.append(self.make_stone(self.current_node))

            self.update_tex = 1000

    def draw_board(self):
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glTexCoord2d(1.0, 0.0)
        glVertex2f(self.board_size / 2, -self.board_size / 2)
        glTexCoord2d(0.0, 0.0)
        glVertex2f(-self.board_size / 2, -self.board_size / 2)
        glTexCoord2d(0.0, 1.0)
        glVertex2f(-self.board_size / 2, self.board_size / 2)
        glTexCoord2d(1.0, 1.0)
        glVertex2f(self.board_size / 2, self.board_size / 2)
        glEnd()

    def do_paint(self, output):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        self.background.draw(output)

        self.board_tex.enable()
        self.draw_board()
        self.board_tex.disable()

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glColor4f(1.0, 1.0, 1.0, 1.0)

        for stone in self.stones:
            stone.draw()

    def do_restore_viewport(self):
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()

        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

        glDisable(GL_BLEND)

        glPopAttrib(GL_TEXTURE_BIT)
