"""Constants for the Dremel 3D Printer (3D20, 3D40, 3D45) integration."""
from __future__ import annotations

from datetime import timedelta
import logging

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=5)

DOMAIN = "dremel_3d_printer"

SERVICE_PRINT_JOB = "print_job"
SERVICE_PAUSE_JOB = "pause_job"
SERVICE_RESUME_JOB = "resume_job"
SERVICE_STOP_JOB = "stop_job"
SERVICE_TAKE_SNAPSHOT = "take_snapshot"
SERVICE_ADD_SNAPSHOT_TO_GIF = "add_snapshot_to_gif"
SERVICE_MAKE_GIF = "make_gif"

ATTR_FILEPATH = "filepath"
ATTR_URL = "url"
ATTR_DEVICE_ID = "device_id"
ATTR_NAME = "name"
ATTR_OUTPUT_DIR = "output_dir"
ATTR_FILENAME = "filename"
ATTR_FPS = "fps"
ATTR_DURATION = "duration"

EVENT_DATA_NEW_PRINT_STATS = "dremel_3d_printer_new_print_stats"
