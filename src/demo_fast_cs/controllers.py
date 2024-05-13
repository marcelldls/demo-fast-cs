from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from fastcs.attributes import AttrR, AttrW
from fastcs.connections.serial_connection import (
    SerialConnection,
    SerialConnectionSettings,
)
from fastcs.controller import Controller
from fastcs.datatypes import Bool


@dataclass
class ThorlabsMFFSettings:
    serial_settings: SerialConnectionSettings


class ThorlabsAPTProtocol:

    def get_info(self) -> bytes:
        return b'\x05\x00\x00\x00\x50\x01'

    def get_position(self) -> bytes:
        return b'\x29\x04\x00\x00\x50\x01'

    def read_position(self, responce: bytes) -> bool:
        return bool(int(responce[8])-1)

    def set_position(self, desired: bool) -> bytes:
        if desired:
            return b'\x6A\x04\x00\x02\x50\x01'
        else:
            return b'\x6A\x04\x00\x01\x50\x01'


protocol = ThorlabsAPTProtocol()


@dataclass
class ThorlabsMFFHandlerW:
    cmd: Callable

    async def put(
        self,
        controller: ThorlabsMFF,
        attr: AttrW,
        value: Any,
    ) -> None:
        if attr.dtype is bool:
            value = int(value)
        await controller.conn.send_command(
            self.cmd(value),
        )


@dataclass
class ThorlabsMFFHandlerR:
    cmd: Callable
    response_size: int
    response_handler: Callable
    update_period: float = 0.2

    async def update(
        self,
        controller: ThorlabsMFF,
        attr: AttrR,
    ) -> None:
        response = await controller.conn.send_query(
            self.cmd(),
            self.response_size,
        )
        response = self.response_handler(response)
        if attr.dtype is bool:
            await attr.set(int(response))
        else:
            await attr.set(response)


class ThorlabsMFF(Controller):
    position = AttrR(
        Bool(znam="Disabled", onam="Enabled"),
        handler=ThorlabsMFFHandlerR(
            protocol.get_position,
            12,
            protocol.read_position,
            update_period=0.2,
            ),
        )
    desired = AttrW(
        Bool(znam="Disabled", onam="Enabled"),
        handler=ThorlabsMFFHandlerW(
            protocol.set_position,
            ),
        )

    def __init__(self, settings: ThorlabsMFFSettings) -> None:
        super().__init__()

        self.suffix = ""
        self._settings = settings
        self.conn = SerialConnection()

    async def connect(self) -> None:
        await self.conn.connect(self._settings.serial_settings)

    async def close(self) -> None:
        await self.conn.close()
