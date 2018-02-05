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
from go_stone import Stone
from go_algorithm import GoAlgorithm
import cairo
import math
import sgf
import random


class JosekiPlugin(GObject.Object, LW.Wallpaper):
    __gproperties__ = {
        "move-speed": (
            int, "Move speed (ms)", "Move speed in milliseconds", 500, 10000, 1000, GObject.PARAM_READWRITE),
        "joseki-file": (
            str, "Joseki dictionary", "The SGF file with variations that should be displayed", "", GObject.PARAM_READWRITE),
        "joseki-corner": (
            GObject.TYPE_UINT, "Joseki corner", "The corner in which to display the joseki.", 1, 5, 2,
            GObject.PARAM_READWRITE)
    }

    def __init__(self):
        color1 = Gdk.Color(255 * 148, 255 * 77, 255 * 85)
        color2 = Gdk.Color(255 * 47, 255 * 9, 255 * 22)
        self.background = LW.Background.new_from_colors(color1, color2, LW.BackgroundShadingType.BACKGROUNDVERTICAL)

        Stone.board_size = self.board_size = (Gdk.Screen.get_default().get_height() / 4.0) * 3.0
        Stone.square_size = self.square_size = self.board_size / 19.0
        Stone.stone_size = Stone.square_size - 1
        self.board_tex = LW.CairoTexture.new(self.board_size, self.board_size)
        self.board_tex.enable()
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        self.board_tex.disable()

        self.number_tex = LW.CairoTexture.new(self.board_size, self.board_size)
        self.number_tex.enable()
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        self.number_tex.disable()

        self.move_speed = 1000
        self.joseki_file = None
        self.joseki_corner = 2
        self.new_joseki_corner = 2
        self.update_tex = 0
        self.kaya_img = None
        self.joseki_collection = None
        self.current_variation = None
        self.node_ind = 0
        self.stones = []
        self.current_number = 1

    def do_init_plugin(self):
        datadir = self.plugin_info.get_data_dir()

        self.kaya_img = cairo.ImageSurface.create_from_png(datadir + "/kaya.png")
        self.joseki_file = datadir + "/kjd.sgf"

        self.init_collection()

        glClearColor(0.0, 0.0, 0.0, 1.0)

        self.do_paint_board()
        Stone.init_tex(self.square_size)

        # Bind settings
        settings = Gio.Settings.new("net.launchpad.livewallpaper.plugins.joseki")
        settings.bind("move-speed", self, "move_speed", Gio.SettingsBindFlags.GET)
        settings.bind("joseki-file", self, "joseki_file", Gio.SettingsBindFlags.GET)
        LW.settings_bind_enum(settings, "joseki-corner", self, "joseki_corner", Gio.SettingsBindFlags.GET)

    def init_collection(self):
        with open(self.joseki_file) as f:
            self.joseki_collection = sgf.parse(f.read())

        self.current_variation = self.joseki_collection[0]
        self.node_ind = 0
        self.stones = []

    def do_get_property(self, prop):
        if prop.name == "move-speed":
            return self.move_speed
        elif prop.name == "joseki-file":
            return self.joseki_file
        elif prop.name == "joseki-corner":
            return self.new_joseki_corner
        else:
            raise AttributeError("unknown property %s" % prop.name)

    def do_set_property(self, prop, value):
        if prop.name == "move-speed":
            self.move_speed = value
        elif prop.name == "joseki-file":
            self.joseki_file = value
            self.init_collection()
        elif prop.name == "joseki-corner":
            self.new_joseki_corner = value
        else:
            raise AttributeError("unknown property %s" % prop.name)

    def do_paint_numbers(self):
        self.number_tex = LW.CairoTexture.new(self.board_size, self.board_size)
        self.number_tex.enable()
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        self.number_tex.disable()
        cr = self.number_tex.cairo_create()

        font_desc = Pango.FontDescription("Ubuntu Mono 18")

        for stone in self.stones:
            if stone.stone_color == Stone.WHITE:
                cr.set_source_rgba(0.0, 0.0, 0.0, 1.0)
            elif stone.stone_color == Stone.BLACK:
                cr.set_source_rgba(1.0, 1.0, 1.0, 1.0)
            layout = PangoCairo.create_layout(cr)

            pctx = layout.get_context()
            fo = cairo.FontOptions()
            fo.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
            PangoCairo.context_set_font_options(pctx, fo)

            layout.set_font_description(font_desc)
            layout.set_text(str(stone.number), -1)

            if stone.number > 9:
                x_shift = 4
            else:
                x_shift = 11
            y_shift = 5
            cr.move_to(stone.get_real_x() + self.board_size / 2 - self.square_size / 2 + x_shift,
                       -stone.get_real_y() + self.board_size / 2 - self.square_size / 2 + y_shift)
            PangoCairo.show_layout(cr, layout)

        self.number_tex.update()

    def do_paint_board(self):
        cr = self.board_tex.cairo_create()

        for i in range(int(self.board_size / self.kaya_img.get_width()) + 1):
            for j in range(int(self.board_size / self.kaya_img.get_height()) + 1):
                cr.set_source_surface(self.kaya_img, i * self.kaya_img.get_width(), j * self.kaya_img.get_height())
                cr.paint()

        cr.set_source_rgba(0.0, 0.0, 0.0, 1.0)

        cr.set_line_width(2.0)

        # draw outline
        cr.rectangle(self.square_size / 2.0, self.square_size / 2.0, self.board_size - self.square_size,
                     self.board_size - self.square_size)
        cr.stroke()

        # draw lines
        for i in range(19):
            cr.move_to(self.square_size / 2.0, self.square_size / 2.0 + i * self.square_size)
            cr.line_to(self.board_size - self.square_size / 2.0, self.square_size / 2.0 + i * self.square_size)
            cr.move_to(self.square_size / 2.0 + i * self.square_size, self.square_size / 2.0)
            cr.line_to(self.square_size / 2.0 + i * self.square_size, self.board_size - self.square_size / 2.0)
            cr.stroke()

        # draw hoshi
        hoshi_positions = [[3,3], [9,3], [15,3],
                           [3, 9], [9, 9], [15, 9],
                           [3, 15], [9, 15], [15, 15]]
        for hoshi_pos in hoshi_positions:
            hoshi_pos_x = self.square_size / 2.0 + hoshi_pos[0] * self.square_size
            hoshi_pos_y = self.square_size / 2.0 + hoshi_pos[1] * self.square_size
            cr.arc(hoshi_pos_x, hoshi_pos_y, self.square_size / 8, 0, 2 * math.pi)
            cr.fill()

        self.board_tex.update()

    def make_stone(self, node, number):
        if "B" in node.properties.keys():
            node_string = node.properties["B"]
            stone_color = Stone.BLACK
        elif "W" in node.properties.keys():
            node_string = node.properties["W"]
            stone_color = Stone.WHITE
        else:
            return None

        if len(node_string[0]) == 2:
            stone_x = ord(node_string[0][0]) - ord('a')
            stone_y = ord(node_string[0][1]) - ord('a')

            if self.joseki_corner == 1:  # top left
                stone_x = 18 - stone_x
                stone_y = 18 - stone_y
            elif self.joseki_corner == 2:  # top right
                stone_y = 18 - stone_y
            elif self.joseki_corner == 3:  # bottom left
                stone_x = 18 - stone_x
            elif self.joseki_corner == 4:  # bottom right
                stone_x = stone_x  # nothing to do here
            # elif self.joseki_corner == 5: #random

        else:
            # Pass
            return None

        return Stone(stone_x, stone_y, stone_color, number)

    def do_prepare_paint(self, ms_since_last_paint):
        self.update_tex -= ms_since_last_paint

        # Update main texture
        if self.update_tex <= 0:
            # self.do_paint_board()

            while self.node_ind >= len(self.current_variation.nodes):
                variations = len(self.current_variation.children)
                if variations == 0:
                    # move line finished, branching into a random variation
                    self.current_variation = self.joseki_collection[0]
                    self.node_ind = 0
                    self.stones = []
                    self.current_number = 1
                    if self.new_joseki_corner == 5: #random
                        self.joseki_corner = random.randint(1, 4)
                    elif self.new_joseki_corner != self.joseki_corner:
                        self.joseki_corner = self.new_joseki_corner
                else:
                    # move line finished, branching into a random variation
                    self.current_variation = self.current_variation.children[random.randint(0, variations - 1)]
                    self.node_ind = 0

            # try to make a move out of the current node
            new_stone = self.make_stone(self.current_variation.nodes[self.node_ind], self.current_number)
            while new_stone is None: #probably a comment node or something - move on to next one
                self.node_ind = self.node_ind + 1
                if self.node_ind == len(self.current_variation.nodes):
                    break
                new_stone = self.make_stone(self.current_variation.nodes[self.node_ind], self.current_number)

            if new_stone is not None:
                # successful in making stone object
                self.stones.append(new_stone)
                self.current_number += 1

                # capture stones
                if new_stone.stone_color == Stone.WHITE:
                    GoAlgorithm.remove_stones(self.stones, Stone.BLACK)
                elif new_stone.stone_color == Stone.BLACK:
                    GoAlgorithm.remove_stones(self.stones, Stone.WHITE)
                self.node_ind = self.node_ind + 1

            self.do_paint_numbers()
            self.update_tex = self.move_speed

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

    def draw_board(self):
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glTexCoord2d(1.0, 0.0)
        glVertex2f(self.board_size / 2, self.board_size / 2)
        glTexCoord2d(0.0, 0.0)
        glVertex2f(-self.board_size / 2, self.board_size / 2)
        glTexCoord2d(0.0, 1.0)
        glVertex2f(-self.board_size / 2, -self.board_size / 2)
        glTexCoord2d(1.0, 1.0)
        glVertex2f(self.board_size / 2, -self.board_size / 2)
        glEnd()

    def do_paint(self, output):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glTexParameteri(GL_TEXTURE_2D, GL_GENERATE_MIPMAP, GL_TRUE)
        self.background.draw(output)

        self.board_tex.enable()
        self.draw_board()
        self.board_tex.disable()

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glColor4f(1.0, 1.0, 1.0, 1.0)

        for stone in self.stones:
            stone.draw()

        self.number_tex.enable()
        self.draw_board()
        self.number_tex.disable()

    def do_restore_viewport(self):
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()

        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

        glDisable(GL_BLEND)

        glPopAttrib(GL_TEXTURE_BIT)
