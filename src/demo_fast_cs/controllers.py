from dataclasses import dataclass
from typing import NamedTuple, Sequence, cast

from .fast_cs import BaseController, Controller, SubController
from .fast_cs.attributes import AttrRead, AttrReadWrite
from .fast_cs.connections import IPConnection, IPConnectionSettings
from .fast_cs.wrappers import put, scan

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


class TempController(Controller):
    ramp_rate = AttrReadWrite(float)

    _attributes = (AttributeInfo("ramp_rate", "R"),)

    def __init__(self, settings: TempControllerSettings) -> None:
        super().__init__()

        self._settings = settings
        self._conn = IPConnection()

        self._ramp_controllers: list[TempRampController] = []
        for index in range(1, settings.num_ramp_controllers + 1):
            controller = TempRampController(index, self._conn)
            self._ramp_controllers.append(controller)
            self.register_sub_controller(controller)

    @put
    async def put_ramp_rate(self, value: float) -> None:
        await self._conn.send_command(f"R={value}\r\n")

    @scan(0.2)
    async def update(self) -> None:
        await update_values(self, self._conn, self._attributes)

    async def connect(self) -> None:
        await self._conn.connect(self._settings.ip_settings)

    async def close(self) -> None:
        await self._conn.close()


class TempRampController(SubController):
    start = AttrReadWrite(float)
    end = AttrReadWrite(float)
    current = AttrRead(float)
    enabled = AttrReadWrite(int)

    _attributes = (
        AttributeInfo("start", "S"),
        AttributeInfo("end", "E"),
        AttributeInfo("current", "T"),
        AttributeInfo("enabled", "N"),
    )

    def __init__(self, index: int, conn: IPConnection) -> None:
        suffix = f"{index:02d}"
        super().__init__(f"ramp{suffix}")
        self._conn = conn
        self._suffix = suffix

    @scan(0.2)
    async def update(self) -> None:
        await update_values(self, self._conn, self._attributes, self._suffix)

    @put
    async def put_enabled(self, value: int) -> None:
        await self._conn.send_command(f"N{self._suffix}={value}\r\n")

    @put
    async def put_start(self, value: float) -> None:
        await self._conn.send_command(f"S{self._suffix}={value}\r\n")

    @put
    async def put_end(self, value: float) -> None:
        await self._conn.send_command(f"E{self._suffix}={value}\r\n")

    @put
    async def put_current(self, value: float) -> None:
        await self._conn.send_command(f"T{self._suffix}={value}\r\n")
