from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .fast_cs import Controller, SubController
from .fast_cs.attributes import AttrRead, AttrReadWrite, AttrWrite
from .fast_cs.connections import IPConnection, IPConnectionSettings
from .fast_cs.wrappers import command


@dataclass
class TempControllerSettings:
    num_ramp_controllers: int
    ip_settings: IPConnectionSettings


@dataclass
class TempControllerHandler:
    name: str
    update_period: float = 0.2

    async def put(
        self,
        controller: TempController | TempRampController,
        attr: AttrWrite,
        value: Any,
    ) -> None:
        await controller.conn.send_command(
            f"{self.name}{controller.suffix}={value}\r\n"
        )

    async def update(
        self,
        controller: TempController | TempRampController,
        attr: AttrRead,
    ) -> None:
        response = await controller.conn.send_query(
            f"{self.name}{controller.suffix}?\r\n"
        )
        await attr.set(response)


class TempController(Controller):
    ramp_rate = AttrReadWrite(float, handler=TempControllerHandler("R"))

    def __init__(self, settings: TempControllerSettings) -> None:
        super().__init__()

        self.suffix = ""
        self._settings = settings
        self.conn = IPConnection()

        self._ramp_controllers: list[TempRampController] = []
        for index in range(1, settings.num_ramp_controllers + 1):
            controller = TempRampController(index, self.conn)
            self._ramp_controllers.append(controller)
            self.register_sub_controller(controller)

    @command
    async def cancel_all(self) -> None:
        for rc in self._ramp_controllers:
            await rc.enabled.process(0)

    async def connect(self) -> None:
        await self.conn.connect(self._settings.ip_settings)

    async def close(self) -> None:
        await self.conn.close()


class TempRampController(SubController):
    start = AttrReadWrite(float, handler=TempControllerHandler("S"))
    end = AttrReadWrite(float, handler=TempControllerHandler("E"))
    current = AttrRead(float, handler=TempControllerHandler("T"))
    enabled = AttrReadWrite(int, handler=TempControllerHandler("N"))

    def __init__(self, index: int, conn: IPConnection) -> None:
        self.suffix = f"{index:02d}"
        super().__init__(f"ramp{self.suffix}")
        self.conn = conn
