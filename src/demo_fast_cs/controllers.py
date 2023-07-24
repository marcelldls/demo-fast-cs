from __future__ import annotations

from dataclasses import dataclass
from typing import Any, NamedTuple, Sequence, cast

from .fast_cs import BaseController, Controller, SubController
from .fast_cs.attributes import AttrRead, AttrReadWrite
from .fast_cs.connections import IPConnection, IPConnectionSettings
from .fast_cs.wrappers import command, scan

AttributeInfo = NamedTuple("AttributeInfo", (("name", str), ("prefix", str)))


async def update_values(
    controller: BaseController,
    conn: IPConnection,
    attr_infos: Sequence[AttributeInfo],
    suffix: str = "",
) -> None:
    for info in attr_infos:
        response = await conn.send_query(f"{info.prefix}{suffix}?\r\n")
        attr = cast(AttrRead, getattr(controller, info.name))
        await attr.set(response)


@dataclass
class TempControllerSettings:
    num_ramp_controllers: int
    ip_settings: IPConnectionSettings


@dataclass
class TempControllerSender:
    name: str

    async def put(
        self, controller: TempController | TempRampController, value: Any
    ) -> None:
        await controller.conn.send_command(
            f"{self.name}{controller.suffix}={value}\r\n"
        )


class TempController(Controller):
    ramp_rate = AttrReadWrite(float, sender=TempControllerSender("R"))

    _attributes = (AttributeInfo("ramp_rate", "R"),)

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

    @scan(0.2)
    async def update(self) -> None:
        await update_values(self, self.conn, self._attributes)

    @command
    async def cancel_all(self) -> None:
        for rc in self._ramp_controllers:
            await rc.enabled.process(0)

    async def connect(self) -> None:
        await self.conn.connect(self._settings.ip_settings)

    async def close(self) -> None:
        await self.conn.close()


class TempRampController(SubController):
    start = AttrReadWrite(float, sender=TempControllerSender("S"))
    end = AttrReadWrite(float, sender=TempControllerSender("E"))
    current = AttrRead(float)
    enabled = AttrReadWrite(int, sender=TempControllerSender("N"))

    _attributes = (
        AttributeInfo("start", "S"),
        AttributeInfo("end", "E"),
        AttributeInfo("current", "T"),
        AttributeInfo("enabled", "N"),
    )

    def __init__(self, index: int, conn: IPConnection) -> None:
        self.suffix = f"{index:02d}"
        super().__init__(f"ramp{self.suffix}")
        self.conn = conn

    @scan(0.2)
    async def update(self) -> None:
        await update_values(self, self.conn, self._attributes, self.suffix)
