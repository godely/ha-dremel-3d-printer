"""Services for the Dremel 3D Printer integration."""
from __future__ import annotations

import datetime
import os

from dremel3dpy import Dremel3DPrinter
from dremel3dpy.camera import Dremel3D45Timelapse
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv, device_registry
import voluptuous as vol

from custom_components.dremel_3d_printer.helper import GifMaker, write_snapshot

from .const import (
    _LOGGER,
    ATTR_DEVICE_ID,
    ATTR_DURATION,
    ATTR_FILEPATH,
    ATTR_FPS,
    ATTR_NAME,
    ATTR_OUTPUT_DIR,
    ATTR_URL,
    DOMAIN,
    EVENT_DATA_NEW_PRINT_STATS,
    SERVICE_ADD_SNAPSHOT_TO_GIF,
    SERVICE_MAKE_GIF,
    SERVICE_PAUSE_JOB,
    SERVICE_PRINT_JOB,
    SERVICE_RESUME_JOB,
    SERVICE_STOP_JOB,
    SERVICE_TAKE_SNAPSHOT,
)

SERVICE_COMMON_JOB_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_DEVICE_ID): cv.string,
    }
)

SERVICE_PRINT_JOB_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Optional(ATTR_FILEPATH): cv.string,
        vol.Optional(ATTR_URL): cv.string,
    }
)

SERVICE_TAKE_SNAPSHOT_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Required(ATTR_OUTPUT_DIR): cv.string,
    }
)

SERVICE_ADD_TO_GIF_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Optional(ATTR_NAME): cv.string,
    }
)

SERVICE_MAKE_GIF_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Required(ATTR_OUTPUT_DIR): cv.string,
        vol.Optional(ATTR_NAME): cv.string,
        vol.Optional(ATTR_FPS): cv.string,
        vol.Optional(ATTR_DURATION): cv.string,
    }
)


def file_exists(hass: HomeAssistant, filepath: str) -> bool:
    """Check if a file exists on disk and is in authorized path."""
    if not hass.config.is_allowed_path(filepath):
        _LOGGER.warning("Path not allowed: %s", filepath)
        return False
    if not os.path.isfile(filepath):
        _LOGGER.warning("Not a file: %s", filepath)
        return False
    return True


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for the Dremel 3D Printer integration."""

    def get_api(service: ServiceCall) -> Dremel3DPrinter:
        """Return the host ip of a Dremel 3D Printer device."""
        device_id = service.data[ATTR_DEVICE_ID]
        dev_reg = device_registry.async_get(hass)
        if (device_entry := dev_reg.async_get(device_id)) is None:
            raise vol.Invalid("Invalid device ID")
        config_list = list(device_entry.config_entries)
        if len(config_list) == 0:
            raise vol.Invalid("No config entries for device ID")
        config_entry = list(device_entry.config_entries)[0]
        return hass.data[DOMAIN][config_entry].api

    async def print_job(service: ServiceCall) -> None:
        """Service to start a printing job."""
        api = get_api(service)
        filepath = service.data.get(ATTR_FILEPATH)
        url = service.data.get(ATTR_URL)
        try:
            if (
                filepath is not None
                and file_exists(hass, filepath)
                and filepath.lower().endswith(".gcode")
            ):
                result = await hass.async_add_executor_job(
                    api.start_print_from_file, filepath
                )
            elif url is not None and url.lower().endswith(".gcode"):
                result = await hass.async_add_executor_job(
                    api.start_print_from_url, url
                )
            hass.bus.async_fire(
                EVENT_DATA_NEW_PRINT_STATS,
                result,
            )
        except Exception as exc:  # pylint: disable=broad-except
            _LOGGER.error(str(exc))

    async def pause_job(service: ServiceCall) -> None:
        """Service to pause a printing job."""
        api = get_api(service)
        await hass.async_add_executor_job(api.pause_print)

    async def resume_job(service: ServiceCall) -> None:
        """Service to resume a printing job."""
        api = get_api(service)
        await hass.async_add_executor_job(api.resume_print)

    async def stop_job(service: ServiceCall) -> None:
        """Service to stop a printing job."""
        api = get_api(service)
        await hass.async_add_executor_job(api.stop_print)

    async def take_snapshot(service: ServiceCall) -> None:
        """Service to take a snapshot and add it to the gif with the given name."""
        api = get_api(service)
        camera = Dremel3D45Timelapse(api, None)
        snapshot = await hass.async_add_executor_job(
            camera.get_snapshot_as_ndarray
        )
        output_dir = service.data.get(ATTR_OUTPUT_DIR)
        name = str(datetime.datetime.now())
        await hass.async_add_executor_job(
            write_snapshot, hass, output_dir, name, snapshot
        )

    async def add_snapshot_to_gif(service: ServiceCall) -> None:
        """Service to take a snapshot and add it to the gif with the given name."""
        api = get_api(service)
        camera = Dremel3D45Timelapse(api, None)
        snapshot = await hass.async_add_executor_job(
            camera.get_snapshot_as_ndarray
        )
        name = service.data.get(ATTR_NAME)
        if name is None:
            name = api.get_job_name()
        gifmaker = GifMaker(hass, name)
        await hass.async_add_executor_job(
            gifmaker.add_snapshot, snapshot
        )

    async def make_gif(service: ServiceCall) -> None:
        """Service to render the gif with the given name."""
        api = get_api(service)
        name = service.data.get(ATTR_NAME)
        if name is None:
            name = api.get_job_name()
        output_dir = service.data.get(ATTR_OUTPUT_DIR)
        fps = service.data.get(ATTR_FPS)
        duration = service.data.get(ATTR_DURATION)
        if fps is not None and duration is not None:
            raise Exception("You should specify exactly one of FPS or Duration.")
        elif fps is None and duration is None:
            fps = 10
        if fps:
            if not fps.replace('.','',1).isdigit():
                raise Exception("FPS must be a numeric value.")
            else:
                fps = float(fps)
        else:
            if not duration.replace('.','',1).isdigit():
                raise Exception("Duration must be a numeric value.")
            else:
                duration = float(duration)
        gifmaker = GifMaker(hass, name)
        await hass.async_add_executor_job(
            gifmaker.make_gif, output_dir, fps, duration
        )

    hass.services.async_register(
        DOMAIN, SERVICE_PRINT_JOB, print_job, schema=SERVICE_PRINT_JOB_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_PAUSE_JOB, pause_job, schema=SERVICE_COMMON_JOB_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_RESUME_JOB, resume_job, schema=SERVICE_COMMON_JOB_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_STOP_JOB, stop_job, schema=SERVICE_COMMON_JOB_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_TAKE_SNAPSHOT, take_snapshot, schema=SERVICE_TAKE_SNAPSHOT_SCHEMA
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_ADD_SNAPSHOT_TO_GIF,
        add_snapshot_to_gif,
        schema=SERVICE_ADD_TO_GIF_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_MAKE_GIF, make_gif, schema=SERVICE_MAKE_GIF_SCHEMA
    )
