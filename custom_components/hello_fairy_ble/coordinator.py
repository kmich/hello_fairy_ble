"""Hello Fairy BLE coordinator for data updates.

Updated with aurora@aurora-smart-home (ha-integration-dev skill)
https://github.com/tonylofgren/aurora-smart-home
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import timedelta

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import HelloFairyAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class HelloFairyApiData:
    """Class to hold Hello Fairy API data."""

    state: bool | None = None
    brightness: int | None = None
    color: tuple[int, int, int] | None = None
    hsv: tuple[int, int, int] | None = None
    current_preset: int | None = None
    mode: int | None = None
    available_effects: list[str] | None = None


class HelloFairyCoordinator(DataUpdateCoordinator[HelloFairyApiData]):
    """Hello Fairy coordinator."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        self.device_name = config_entry.data[CONF_NAME]
        self.device_address = config_entry.data[CONF_ADDRESS]

        ble_device = bluetooth.async_ble_device_from_address(
            hass, self.device_address, connectable=False
        )
        self._api = HelloFairyAPI(ble_device, self._async_push_data)

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({config_entry.unique_id})",
            update_interval=timedelta(seconds=600),
            config_entry=config_entry,
        )

        config_entry.async_on_unload(
            bluetooth.async_register_callback(
                hass,
                self._async_device_discovered,
                bluetooth.BluetoothCallbackMatcher(address=self.device_address),
                bluetooth.BluetoothScanningMode.PASSIVE,
            )
        )

    @callback
    def _async_device_discovered(
        self,
        service_info: bluetooth.BluetoothServiceInfoBleak,
        change: bluetooth.BluetoothChange,
    ) -> None:
        self._api.set_ble_device(service_info.device)
        self.hass.async_create_task(self.async_request_refresh())

    @callback
    def _async_push_data(self) -> None:
        self.async_set_updated_data(
            HelloFairyApiData(
                state=self._api.state,
                brightness=self._api.brightness,
                color=self._api.color,
                hsv=self._api.hsv,
                current_preset=self._api.current_preset,
                mode=self._api.mode,
                available_effects=self._api.available_effects,
            )
        )

    async def _async_update_data(self) -> HelloFairyApiData:
        return HelloFairyApiData(
            state=self._api.state,
            brightness=self._api.brightness,
            color=self._api.color,
            hsv=self._api.hsv,
            current_preset=self._api.current_preset,
            mode=self._api.mode,
            available_effects=self._api.available_effects,
        )

    async def set_power(self, state: bool):
        await self._api.set_power(state)

    async def set_brightness(self, brightness: int):
        await self._api.set_brightness(brightness)

    async def set_color_rgb(self, r: int, g: int, b: int):
        await self._api.set_color_rgb(r, g, b)

    async def set_color_hsv(self, h: int, s: int, v: int):
        await self._api.set_color_hsv(h, s, v)

    async def set_preset(self, preset: int):
        await self._api.set_preset(preset)

    async def set_effect(self, effect_name: str):
        await self._api.set_effect(effect_name)

    # DIY / matrix wrappers
    async def enter_draw_mode(self) -> None:
        await self._api.enter_draw_mode()

    async def clear_pixels(self) -> None:
        await self._api.clear_pixels()

    async def set_pixel(self, x: int, y: int, color_byte: int) -> None:
        await self._api.set_pixel(x, y, color_byte)

    async def set_pixel_rgb(self, x: int, y: int, r: int, g: int, b: int) -> None:
        await self._api.set_pixel_rgb(x, y, r, g, b)

    async def set_pixels(self, updates: Sequence[tuple[int, int, int]]) -> None:
        await self._api.set_pixels(updates)

    async def set_two_picture_animation(self, frames: Sequence[Sequence[int]]) -> None:
        await self._api.set_two_picture_animation(frames)

    async def set_frame(self, pixels: Sequence[int]) -> None:
        await self._api.set_frame(pixels)

    @property
    def studio_snapshot(self) -> dict:
        return self._api.studio_snapshot

    async def request_status(self) -> dict:
        return await self._api.request_status()

    async def inspect_native(self) -> dict:
        return await self._api.inspect_native()

    async def set_native(self, action: str, payload: dict) -> dict:
        result = await self._api.set_native(action, payload)
        self._async_push_data()
        return result

    async def set_diy_playback(self, kind: str, movement: str, speed: int, brightness: int) -> None:
        await self._api.set_diy_playback(kind, movement, speed, brightness)

    @property
    def device_discovered(self) -> bool:
        return self._api.is_discovered

    async def async_shutdown(self) -> None:
        """Release this entry's BLE connection during removal/reload."""
        await self._api.disconnect()
