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

from gi.repository import Adw, GLib, Gtk, GExiv2
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
    toast_overlay = Gtk.Template.Child()
    format = "JPEG"
    remove_meta = True

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

    @Gtk.Template.Callback()
    def on_remove_metadata_set(self, switch, checked):
        self.remove_meta = checked
        self.compress()

    def compress(self):
        temp_dir = os.path.join(GLib.get_user_cache_dir(), 'ImageCompressor')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        self.temp_path = os.path.join(temp_dir, 'temp.jpg')
        with Image.open(self.file_path) as image:
                scale_factor = self.resolution_scale.get_value() * 0.01
                quality = int(self.quality_scale.get_value())
                resized_image = image.resize([int(image.width * scale_factor), int(image.height * scale_factor)])
                resized_image.save(self.temp_path, format=self.format, quality=quality, method=6, optimize=True)

        if self.remove_meta:
            image = GExiv2.Metadata(self.temp_path)
            image.clear_exif()
            image.clear_xmp()
            image.save_file()

        with Image.open(self.temp_path) as image:
            self.info_label.set_label(str(image.width) + 'x' + str(image.height) + ' ' + self.format_size(Path(self.temp_path).stat().st_size))
            self.preview_image.set_from_file(self.temp_path)

    @Gtk.Template.Callback()
    def save_image(self, button):
        file_name = os.path.basename(self.file_path)
        save_name = os.path.splitext(file_name)[0] + '.' + self.format.lower()
        save_file_path = os.path.join(GLib.get_user_special_dir(GLib.USER_DIRECTORY_PICTURES), save_name)
        with open(self.temp_path, 'rb') as tmp_file:
            with open(save_file_path, 'wb') as save_file:
                save_file.write(tmp_file.read())

        self.toast_overlay.add_toast(Adw.Toast().new(title='Saved to Pictures'))

    @Gtk.Template.Callback()
    def set_format(self, button):
        if button.props.active:
            self.format = button.props.label
        self.compress()
    
    def format_size(self, size, decimal_places=1):
        for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
            if size < 1024:
                break
            size /= 1024.0
        return f'{size:.{decimal_places}f} {unit}'
