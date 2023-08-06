from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .fast_cs import Controller, SubController
from .fast_cs.attributes import AttrR, AttrRW, AttrW
from .fast_cs.connections import IPConnection, IPConnectionSettings
from .fast_cs.datatypes import Bool, Float, Int
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
        attr: AttrW,
        value: Any,
    ) -> None:
        if attr.dtype is bool:
            value = int(value)
        await controller.conn.send_command(
            f"{self.name}{controller.suffix}={value}\r\n"
        )

    async def update(
        self,
        controller: TempController | TempRampController,
        attr: AttrR,
    ) -> None:
        response = await controller.conn.send_query(
            f"{self.name}{controller.suffix}?\r\n"
        )
        if attr.dtype is bool:
            await attr.set(int(response))
        else:
            await attr.set(response)


class TempController(Controller):
    ramp_rate = AttrRW(Float(), handler=TempControllerHandler("R"))

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
            await rc.enabled.process(False)

    async def connect(self) -> None:
        await self.conn.connect(self._settings.ip_settings)

    async def close(self) -> None:
        await self.conn.close()


class TempRampController(SubController):
    start = AttrRW(Int(), handler=TempControllerHandler("S"))
    end = AttrRW(Int(), handler=TempControllerHandler("E"))
    current = AttrR(Float(prec=3), handler=TempControllerHandler("T"))
    enabled = AttrRW(Bool(znam="Off", onam="On"), handler=TempControllerHandler("N"))

    def __init__(self, index: int, conn: IPConnection) -> None:
        self.suffix = f"{index:02d}"
        super().__init__(f"ramp{self.suffix}")
        self.conn = conn
