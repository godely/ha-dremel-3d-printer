"""Helper functions for Dremel 3D Printer."""

import os
import re
import shutil

from homeassistant.core import HomeAssistant
from homeassistant.util import raise_if_invalid_filename, raise_if_invalid_path
import imageio as io
import imageio.v3 as iio

from custom_components.dremel_3d_printer.const import _LOGGER

SNAPSHOTS_MAIN_FOLDER = ".dremel_3d_printer"


def extract_number(f):
    """Extract number from filename"""
    s = re.findall("(\d+)\.?[^\.]*$", f)
    return int(s[0]) if s else -1

def try_get_abs_path(hass: HomeAssistant, folder):
    """Tries to validate the given folder and if it passes, return its absolute path"""
    raise_if_invalid_path(folder)
    # If path is relative, we assume relative to Home Assistant config dir
    if not os.path.isabs(folder):
        return hass.config.path(folder)
    elif hass.config.is_allowed_path(folder):
        return folder
    else:
        raise Exception(f"Path not allowed: {folder}")

def try_setup_folder(folder, should_clear=False):
    """Tries to set up a new (empty) folder"""
    if os.path.exists(folder):
        if not os.path.isdir(folder):
            raise Exception(f"{folder} is not a folder")
        if not should_clear:
            return
        shutil.rmtree(folder, ignore_errors=True)
    os.mkdir(folder)

def write_snapshot(hass: HomeAssistant, output_dir: str, name, snapshot) -> None:
    """Writes the snapshot to the given output dir."""
    output_dir = try_get_abs_path(hass, output_dir)
    try_setup_folder(output_dir)
    raise_if_invalid_filename(name)
    image_full_path = os.path.join(output_dir, f"{name}.jpeg")
    iio.imwrite(image_full_path, snapshot)

class GifMaker():
    """Gif Maker class"""

    def __init__(self, hass: HomeAssistant, name: str) -> None:
        """Initialize a Gif Maker for the Dremel 3D Printer"""
        self.hass = hass
        snapshots_main_folder_abs = try_get_abs_path(hass, SNAPSHOTS_MAIN_FOLDER)
        try_setup_folder(snapshots_main_folder_abs)
        raise_if_invalid_filename(name)
        self.snapshots_folder = os.path.join(snapshots_main_folder_abs, name)


    def add_snapshot(self, image):
        """Adds an image to the folder "name" so it can be used when building the gif"""
        try_setup_folder(self.snapshots_folder)
        filenames = [extract_number(filename) for filename in os.listdir(self.snapshots_folder) if filename.endswith(".jpeg")]
        image_name = str(max(filenames) + 1 if len(filenames) > 0 else 0)
        image_full_path = os.path.join(self.snapshots_folder, f"{image_name}.jpeg")
        iio.imwrite(image_full_path, image)


    def make_gif(self, output_dir, fps=None, duration=None):
        """Builds a gif from the images in the folder "name" and writes it to the output_dir"""
        if not os.path.exists(self.snapshots_folder):
            raise f"Folder {self.snapshots_folder} does not exists"
        if not os.path.isdir(self.snapshots_folder):
            raise f"Folder {self.snapshots_folder} is not a directory"
        filenames = [filename for filename in os.listdir(self.snapshots_folder) if filename.endswith(".jpeg")]
        if len(filenames) == 0:
            raise f"Folder {self.snapshots_folder} has no snapshots"

        # If path is relative, we assume relative to Home Assistant config dir
        output_dir = try_get_abs_path(self.hass, output_dir)
        try_setup_folder(output_dir)

        try:
            gifname = os.path.basename(self.snapshots_folder)
            gif_full_path = os.path.join(output_dir, f"{gifname}.gif")
            with io.get_writer(gif_full_path, mode="I", fps=fps, duration=duration) as writer:
                filenames = sorted(filenames, key=extract_number)
                for filename in filenames:
                    file_full_path = f"{self.snapshots_folder}/{filename}"
                    writer.append_data(iio.imread(file_full_path))
            shutil.rmtree(self.snapshots_folder, ignore_errors=True)
        except Exception as exc:
            raise exc
