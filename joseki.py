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
import cairo, math, random, datetime


class Circle(object):
    def __init__(self, radius, position, alpha):
        self.radius = radius
        self.position = position
        self.alpha = alpha

    def draw(self, pos_rad):
        center_x = pos_rad * math.cos(self.position)
        center_y = pos_rad * math.sin(self.position)

        glBegin(GL_QUADS)
        glTexCoord2d(1.0, 0.0)
        glVertex2f(center_x + self.radius, center_y + self.radius)
        glTexCoord2d(0.0, 0.0)
        glVertex2f(center_x - self.radius, center_y + self.radius)
        glTexCoord2d(0.0, 1.0)
        glVertex2f(center_x - self.radius, center_y - self.radius)
        glTexCoord2d(1.0, 1.0)
        glVertex2f(center_x + self.radius, center_y - self.radius)
        glEnd()


class JosekiPlugin(GObject.Object, LW.Wallpaper):
    __gproperties__ = {
        "main-size": (int, "Size", "Size of the main circle", 128, 512, 320, GObject.PARAM_READWRITE),
        "main-color": (Gdk.RGBA, "Color", "Color of the main circle", GObject.PARAM_READWRITE),
        "main-alpha": (
        float, "Transparency", "Transparency of the main circle", 0.0, 1.0, 0.85, GObject.PARAM_READWRITE),
        "font": (str, "Font", "The font to use for the time and the date", "Ubuntu Mono 40", GObject.PARAM_READWRITE),
        "font-color": (Gdk.RGBA, "Font color", "Color of the time and the date", GObject.PARAM_READWRITE),
        "use-24-hour-clock": (bool, "Use 24 hour clock", "Use 24 hour clock", True, GObject.PARAM_READWRITE),
        "date-format": (GObject.TYPE_UINT, "Date format", "Date format", 0, 5, 0, GObject.PARAM_READWRITE),
        "colors": (str, "Colors", "Get the colors of the circles from this image.", "", GObject.PARAM_READWRITE),
        "update-interval": (
        GObject.TYPE_UINT, "Update interval", "How often should the color change?", 1, 60, 60, GObject.PARAM_READWRITE),
        "fade-time": (
        int, "Fade time", "Time to switch from one color to another color", 0, 5000, 2000, GObject.PARAM_READWRITE)
    }

    date_formats = ("%d.%m.%Y", "%d-%m-%Y", "%Y.%m.%d", "%Y-%m-%d", "%m.%d.%Y", "%m-%d-%Y")

    def __init__(self):
        color1 = Gdk.Color(255 * 148, 255 * 77, 255 * 85)
        color2 = Gdk.Color(255 * 47, 255 * 9, 255 * 22)
        self.background = LW.Background.new_from_colors(color1, color2, LW.BackgroundShadingType.BACKGROUNDVERTICAL)

        self.use_24_hour_clock = True
        self.date_format = 0

        self.board_size = (Gdk.Screen.get_default().get_height() / 4.0) * 3.0
        self.board_tex = LW.CairoTexture.new(self.board_size, self.board_size)
        #self.do_paint_board()

        # Circles
        self.circle_tex = LW.CairoTexture.new(256, 256)
        cr = self.circle_tex.cairo_create()
        cr.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        cr.arc(128, 128, 128, 0, 2 * math.pi)
        cr.fill()
        self.circle_tex.update()

        self.circles = self.generate_circles()
        self.update_circles = datetime.datetime.now()
        self.update_interval = 60

        self.new_circles = []
        self.fade_time = 0  # The value that will be decreased
        self.fade_time_init = 2000  # The initial value

        # Main
        self.main_size = 320
        self.main_color = Gdk.RGBA(71.0 / 255, 27.0 / 255, 42.0 / 255, 1.0)
        self.main_alpha = 0.85
        self.update_main_texture()

        self.num_dots = 30

        self.font_color = Gdk.RGBA(1.0, 1.0, 1.0, 1.0)
        self.t_font = Pango.FontDescription("Ubuntu Mono 40")
        self.update_fonts()

    def do_paint_board(self):

        cr = self.board_tex.cairo_create()

        for i in range(int(self.board_size / self.kaya_img.get_width()) + 1):
            for j in range(int(self.board_size / self.kaya_img.get_height()) + 1):
                cr.set_source_surface(self.kaya_img, i * self.kaya_img.get_width(), j * self.kaya_img.get_height())
                cr.paint()

        cr.set_source_rgba(0.0, 0.0, 0.0, 1.0)
        square_size = self.board_size / 20.0

        cr.set_line_width(1.0)

        cr.rectangle(square_size / 2.0, square_size / 2.0, self.board_size - square_size, self.board_size - square_size)
        cr.stroke()

        for i in range(20):
            cr.move_to(square_size / 2.0, square_size / 2.0 + i * square_size)
            cr.line_to(self.board_size - square_size / 2.0, square_size / 2.0 + i * square_size)
            cr.move_to(square_size / 2.0 + i * square_size, square_size / 2.0)
            cr.line_to(square_size / 2.0 + i * square_size, self.board_size - square_size / 2.0)
            cr.stroke()

        self.board_tex.update()

    def do_init_plugin(self):
        datadir = self.plugin_info.get_data_dir()

        self.kaya_img = cairo.ImageSurface.create_from_png("kaya.png")

        self.colors_filename = datadir + "/color.svg"
        self.colors = GdkPixbuf.Pixbuf.new_from_file(self.colors_filename)

        self.circle_color = self.generate_color(0)
        self.new_circle_color = self.circle_color

        # Bind settings
        settings = Gio.Settings.new("net.launchpad.livewallpaper.plugins.joseki")
        settings.bind("main-size", self, "main-size", Gio.SettingsBindFlags.GET)
        LW.settings_bind_color(settings, "main-color", self, "main-color", Gio.SettingsBindFlags.GET)
        settings.bind("main-alpha", self, "main-alpha", Gio.SettingsBindFlags.GET)
        settings.bind("font", self, "font", Gio.SettingsBindFlags.GET)
        LW.settings_bind_color(settings, "font-color", self, "font-color", Gio.SettingsBindFlags.GET)
        settings.bind("use-24-hour-clock", self, "use-24-hour-clock", Gio.SettingsBindFlags.GET)
        LW.settings_bind_enum(settings, "date-format", self, "date-format", Gio.SettingsBindFlags.GET)
        settings.bind("colors", self, "colors", Gio.SettingsBindFlags.GET)
        LW.settings_bind_enum(settings, "update-interval", self, "update-interval", Gio.SettingsBindFlags.GET)
        settings.bind("fade-time", self, "fade-time", Gio.SettingsBindFlags.GET)

    def do_get_property(self, prop):
        if prop.name == "main-size":
            return self.main_size
        elif prop.name == "main-color":
            return self.main_color
        elif prop.name == "main-alpha":
            return self.main_alpha
        elif prop.name == "font":
            return self.t_font.to_string()
        elif prop.name == "font-color":
            return self.font_color
        elif prop.name == "use-24-hour-clock":
            return self.use_24_hour_clock
        elif prop.name == "date-format":
            return self.date_format
        elif prop.name == "colors":
            return self.colors_filename
        elif prop.name == "update-interval":
            return self.update_interval
        elif prop.name == "fade-time":
            return self.fade_time_init
        else:
            raise AttributeError("unknown property %s" % prop.name)

    def do_set_property(self, prop, value):
        if prop.name == "main-size":
            self.main_size = value
            self.update_main_texture()
        elif prop.name == "main-color":
            self.main_color = value
            self.update_main_texture()
        elif prop.name == "main-alpha":
            self.main_alpha = value
        elif prop.name == "font":
            self.t_font = Pango.FontDescription(value)
            self.update_fonts()
        elif prop.name == "font-color":
            self.font_color = value
        elif prop.name == "use-24-hour-clock":
            self.use_24_hour_clock = value
            self.update_fonts()
        elif prop.name == "date-format":
            self.date_format = value
            self.update_tex = 0
        elif prop.name == "colors":
            try:
                self.colors = GdkPixbuf.Pixbuf.new_from_file(value)
                self.colors_filename = value
            except:
                print("Could not load '%s' for colors, continue with previous file" % value)
            self.update_circles = datetime.datetime.now()
        elif prop.name == "update-interval":
            self.update_circles -= datetime.timedelta(minutes=self.update_interval)
            self.update_interval = value
            self.update_circles += datetime.timedelta(minutes=self.update_interval)
        elif prop.name == "fade-time":
            self.fade_time_init = value
            self.fade_time = 0
        else:
            raise AttributeError("unknown property %s" % prop.name)

    def update_main_texture(self):
        self.main_tex = LW.CairoTexture.new(self.main_size, self.main_size)
        self.update_pattern()
        self.main_circle = Circle(self.main_size / 2, 0, 1.0)
        self.update_tex = 0

    def update_pattern(self):
        center = radius = self.main_size / 2
        self.pattern = cairo.RadialGradient(center, center, radius - 5, center, center, radius)
        self.pattern.add_color_stop_rgba(0.0,
                                         self.main_color.red,
                                         self.main_color.green,
                                         self.main_color.blue,
                                         1.0)
        self.pattern.add_color_stop_rgba(1.0,
                                         self.main_color.red,
                                         self.main_color.green,
                                         self.main_color.blue,
                                         0.0)

    def update_fonts(self):
        cr = self.main_tex.cairo_create()

        if not self.use_24_hour_clock:
            self.p_font = self.t_font.copy()
            self.p_font.set_size(self.p_font.get_size() / 3.0)

        self.d_font = self.t_font.copy()
        size = self.d_font.get_size() / 2.0
        self.d_font.set_size(size)

        # Time font
        layout = PangoCairo.create_layout(cr)
        layout.set_font_description(self.t_font)
        layout.set_text("00:00", -1)
        t_width = layout.get_extents()[0].width / Pango.SCALE

        if not self.use_24_hour_clock:
            layout = PangoCairo.create_layout(cr)
            layout.set_font_description(self.p_font)
            layout.set_text("AM", -1)
            t_width += layout.get_extents()[0].width / Pango.SCALE + 5

        # Date font
        layout = PangoCairo.create_layout(cr)
        layout.set_font_description(self.d_font)
        layout.set_text("00.00.0000", -1)
        d_width = layout.get_extents()[0].width / Pango.SCALE

        if d_width > t_width:
            while d_width > t_width:
                size -= Pango.SCALE
                self.d_font.set_size(size)
                layout.set_font_description(self.d_font)
                d_width = layout.get_extents()[0].width / Pango.SCALE
        elif d_width < t_width:
            while d_width < t_width:
                size += Pango.SCALE
                self.d_font.set_size(size)
                layout.set_font_description(self.d_font)
                d_width = layout.get_extents()[0].width / Pango.SCALE
            self.d_font.set_size(size - Pango.SCALE)

    def generate_circles(self):
        circles = []
        for i in range(30):
            rad = 50.0 * random.uniform(0.1, 1.0)
            pos = 2.0 * math.pi * i / 30.0
            pos += random.uniform(-1.0, 1.0) * math.pi / 60.0
            alpha = 0.3 - rad / 500.0
            circles.append(Circle(rad, pos, alpha))

        for i in range(10):
            rad = random.uniform(75, 150)
            pos = 2.0 * math.pi * i / 10.0
            pos += random.uniform(-1.0, 1.0) * math.pi / 10.0
            alpha = 0.15 - rad / 1500.0
            circles.append(Circle(rad, pos, alpha))

        for i in range(15):
            rad = random.uniform(150, 300)
            pos = 2.0 * math.pi * random.random()
            alpha = 0.06 - rad / 6000.0
            circles.append(Circle(rad, pos, alpha))
        return circles

    def generate_color(self, position):
        x = int((self.colors.get_width() - 1) * position)

        pixels = self.colors.get_pixels()
        n_channels = self.colors.get_n_channels()
        red = ord(pixels[x * n_channels])
        green = ord(pixels[x * n_channels + 1])
        blue = ord(pixels[x * n_channels + 2])

        return Gdk.RGBA(red / 255.0, green / 255.0, blue / 255.0)

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

    def do_prepare_paint(self, ms_since_last_paint):
        self.update_tex -= ms_since_last_paint
        self.fade_time -= ms_since_last_paint
        now = datetime.datetime.now()

        # Update main texture
        if self.update_tex <= 0:
            self.do_paint_board()

            cr = self.main_tex.cairo_create()
            size = self.main_tex.get_width()

            # Clear texture
            cr.set_operator(cairo.OPERATOR_CLEAR)
            cr.rectangle(0, 0, size, size)
            cr.fill()
            cr.set_operator(cairo.OPERATOR_OVER)

            # Fill background
            cr.set_source(self.pattern)
            cr.rectangle(0, 0, size, size)
            cr.fill()

            # Show current time
            self.paint_time_and_date(cr, now)

            # Show dots
            self.paint_dots(cr, now.second / 2)

            self.main_tex.update()
            self.update_tex = 1000

        # Update color and circles
        if self.update_circles <= now:
            self.new_circles = self.generate_circles()
            if self.update_interval == 60 or self.update_interval == 30:
                position = (now.hour * 60.0 + now.minute) / (24.0 * 60.0)
            else:
                position = now.minute / 60.0
            self.new_circle_color = self.generate_color(position)
            self.fade_time = self.fade_time_init

            self.update_circles = now + datetime.timedelta(minutes=self.update_interval)

        if self.fade_time <= 0 and len(self.new_circles) != 0:
            self.circles = self.new_circles
            self.circle_color = self.new_circle_color
            self.new_circles = []

    def paint_time_and_date(self, cr, time):
        t_layout = PangoCairo.create_layout(cr)
        t_layout.set_font_description(self.t_font)
        if self.use_24_hour_clock:
            t_layout.set_text(time.strftime("%H:%M"), -1)
        else:
            t_layout.set_text(time.strftime("%I:%M"), -1)
        t_extents = t_layout.get_extents()[0]
        t_width = t_extents.width / Pango.SCALE
        t_height = t_extents.height / Pango.SCALE

        if not self.use_24_hour_clock:
            p_layout = PangoCairo.create_layout(cr)
            p_layout.set_font_description(self.p_font)
            if time.hour >= 12:
                p_layout.set_text("PM", -1)
            else:
                p_layout.set_text("AM", -1)
            p_extents = p_layout.get_extents()[0]
            p_width = p_extents.width / Pango.SCALE
            p_height = p_extents.height / Pango.SCALE
            t_width += p_width + 5

        d_layout = PangoCairo.create_layout(cr)
        d_layout.set_font_description(self.d_font)
        d_layout.set_text(time.strftime(self.date_formats[self.date_format]), -1)
        d_extents = d_layout.get_extents()[0]
        d_width = d_extents.width / Pango.SCALE
        d_height = d_extents.height / Pango.SCALE

        center = self.main_tex.get_width() / 2.0
        x1 = center - t_width / 2.0 - t_extents.x / Pango.SCALE
        x2 = center - d_width / 2.0 - d_extents.x / Pango.SCALE
        y = center - (t_height + d_height + 10.0) / 2.0
        y1 = y - t_extents.y / Pango.SCALE
        y2 = y - d_extents.y / Pango.SCALE + t_height + 10.0

        # Shadow
        shadow = self.t_font.get_size() / (20.0 * Pango.SCALE)
        cr.set_source_rgba(0.0, 0.0, 0.0, 0.5)
        cr.move_to(x1 + shadow, y1 + shadow)
        PangoCairo.show_layout(cr, t_layout)
        cr.move_to(x2 + shadow, y2 + shadow)
        PangoCairo.show_layout(cr, d_layout)
        if not self.use_24_hour_clock:
            x3 = center + t_width / 2.0 - p_width - p_extents.x / Pango.SCALE
            y3 = y + t_height - p_height - p_extents.y / Pango.SCALE - 3.0
            cr.move_to(x3 + shadow, y3 + shadow)
            PangoCairo.show_layout(cr, p_layout)

        # Date and time
        cr.set_source_rgb(self.font_color.red,
                          self.font_color.green,
                          self.font_color.blue)
        cr.move_to(x1, y1)
        PangoCairo.show_layout(cr, t_layout)
        cr.move_to(x2, y2)
        PangoCairo.show_layout(cr, d_layout)
        if not self.use_24_hour_clock:
            cr.move_to(x3, y3)
            PangoCairo.show_layout(cr, p_layout)

    def paint_dots(self, cr, highlight):
        center = self.main_tex.get_width() / 2
        radius = self.main_tex.get_width() * 0.4

        cr.move_to(center, center)
        cr.new_path()

        cr.set_line_width(1.0)
        cr.set_source_rgb(self.font_color.red,
                          self.font_color.green,
                          self.font_color.blue)

        for i in range(self.num_dots):
            pos = (float(i) / self.num_dots) * 2.0 * math.pi - 0.5 * math.pi

            if i == highlight:
                cr.arc(center + radius * math.cos(pos), center + radius * math.sin(pos), 3.0, 0.0, 2.0 * math.pi)
                cr.set_line_width(3.0)
                cr.stroke()
                cr.set_line_width(1.0)
            else:
                cr.arc(center + radius * math.cos(pos), center + radius * math.sin(pos), 2.0, 0.0, 2.0 * math.pi)
                if i < highlight:
                    cr.fill()
                else:
                    cr.stroke()

    def draw_board(self):
        glColor4f(1.0, 1.0, 1.0, 0.0)
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

        #glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        #self.circle_tex.enable()
        #for i in range(len(self.circles)):
        #    alpha = self.circles[i].alpha
        #    if self.fade_time > 0:
        #        alpha *= self.fade_time / float(self.fade_time_init)
        #    glColor4f(self.circle_color.red,
        #              self.circle_color.green,
        #              self.circle_color.blue,
        #              alpha)
        #    self.circles[i].draw(self.main_circle.radius)

        #if self.fade_time > 0:
        #    for i in range(len(self.new_circles)):
        #        glColor4f(self.new_circle_color.red,
        #                  self.new_circle_color.green,
        #                  self.new_circle_color.blue,
        #                  self.new_circles[i].alpha * (1.0 - self.fade_time / float(self.fade_time_init)))
        #        self.new_circles[i].draw(self.main_circle.radius)
        #self.circle_tex.disable()

        #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        #self.main_tex.enable()
        #glColor4f(1.0, 1.0, 1.0, self.main_alpha)
        #self.main_circle.draw(0)
        #self.main_tex.disable()

        self.board_tex.enable()
        self.draw_board()
        self.board_tex.disable()


    def do_restore_viewport(self):
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()

        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

        glDisable(GL_BLEND)

        glPopAttrib(GL_TEXTURE_BIT)
