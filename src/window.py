# window.py
#
# Copyright 2022 Axel
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
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw
from gi.repository import Gtk
from PIL import Image
from pathlib import Path
import os

@Gtk.Template(resource_path='/cu/axel/ImageCompressor/window.ui')
class ImagecompressorWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'ImagecompressorWindow'

    preview_image = Gtk.Template.Child()
    status_page = Gtk.Template.Child()
    info_label = Gtk.Template.Child()
    quality_scale = Gtk.Template.Child()
    resolution_scale = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @Gtk.Template.Callback()
    def open_image(self, button):
        dialog = Gtk.FileChooserDialog(transient_for=self,
                                       title='Select image',
                                       action=Gtk.FileChooserAction.OPEN)
        dialog.add_buttons("_Cancel", Gtk.ResponseType.CANCEL, "_Open",
                           Gtk.ResponseType.ACCEPT)
        dialog.connect('response', self.on_open_image)
        dialog.show()

    def on_open_image(self, dialog, response):
        dialog.destroy()
        
        if response == Gtk.ResponseType.ACCEPT:
            self.file_path = dialog.get_file().get_path()
            self.status_page.set_visible(False)
            self.preview_image.set_visible(True)
            self.info_label.set_visible(True)
            self.compress()

    @Gtk.Template.Callback()
    def on_resolution_changed(self, scale):
        self.compress()

    @Gtk.Template.Callback()
    def on_quality_changed(self, scale):
        self.compress()

    def compress(self):
        temp_path = os.path.join(Path.home(), '.cache', 'tmp.jpg')
        with Image.open(self.file_path) as image:
                scale_factor = self.resolution_scale.get_value() * 0.01
                quality = int(self.quality_scale.get_value())
                resized_image = image.resize([int(image.width * scale_factor), int(image.height * scale_factor)])
                print(str(int(image.width * scale_factor)))
                resized_image.save(temp_path, quality=quality)

        with Image.open(temp_path) as image:
            self.info_label.set_label(str(image.width) + 'x' + str(image.height) + ' ' + self.format_size(Path(temp_path).stat().st_size))
            self.preview_image.set_from_file(temp_path)
    
    def format_size(self, size, decimal_places=1):
        for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
            if size < 1024:
                break
            size /= 1024.0
        return f'{size:.{decimal_places}f} {unit}'