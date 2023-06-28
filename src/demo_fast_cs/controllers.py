import asyncio
from dataclasses import dataclass
from typing import NamedTuple, Sequence, cast

from .fast_cs import Controller, SubController
from .fast_cs.attributes import Attribute
from .fast_cs.connections import IPConnection, IPConnectionSettings
from .fast_cs.wrappers import put, scan

AttributeInfo = NamedTuple("AttributeInfo", (("name", str), ("prefix", str)))


async def update_values(
    controller, conn, attr_infos: Sequence[AttributeInfo], suffix: str = ""
):
    for info in attr_infos:
        response = await conn.send_query(f"{info.prefix}{suffix}?\r\n")
        attr = cast(Attribute, getattr(controller, info.name))
        attr.set(attr.dtype(response))


@dataclass
class TempControllerSettings:
    num_ramp_controllers: int


class TempController(Controller):
    ramp_rate = Attribute(float)

    _attributes = (AttributeInfo("ramp_rate", "R"),)

    def __init__(self, settings: TempControllerSettings) -> None:
        super().__init__()

        self._conn: IPConnection = IPConnection()

        self._ramp_controllers: list[TempRampController] = []
        for index in range(1, settings.num_ramp_controllers + 1):
            controller = TempRampController(index, self._conn)
            self._ramp_controllers.append(controller)
            self.register_sub_controller(controller)

    @put
    async def put_ramp_rate(self, value: float) -> None:
        await self._conn.send_command(f"R={value}\r\n")

    @scan(0.1)
    async def update(self) -> None:
        await update_values(self, self._conn, self._attributes)

    async def connect(self, settings: IPConnectionSettings):
        await self._conn.connect(settings)

    async def close(self):
        await self._conn.close()


class TempRampController(SubController):
    start = Attribute(float)
    end = Attribute(float)
    current = Attribute(float)
    enabled = Attribute(int)

    _attributes = (
        AttributeInfo("start", "S"),
        AttributeInfo("end", "E"),
        AttributeInfo("current", "T"),
        AttributeInfo("enabled", "N"),
    )

    def __init__(self, index: int, conn: IPConnection) -> None:
        suffix: str = f"{index:02d}"
        super().__init__(f"ramp{suffix}")
        self._conn: IPConnection = conn
        self._suffix: str = suffix

    @scan(0.1)
    async def update(self) -> None:
        await update_values(self, self._conn, self._attributes, self._suffix)

        print(f"Start: {self.start.get()}")
        print(f"End: {self.end.get()}")
        print(f"Current: {self.current.get()}")
        print(f"Enabled: {self.enabled.get()}")

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


async def run_controller():
    tcont = await TempRampController.create(2)

    await tcont.update()
    await asyncio.sleep(1)
    await tcont.set_enabled(1)
    await asyncio.sleep(3)
    await tcont.update()
    await asyncio.sleep(3)
    await tcont.update()
    await tcont.set_enabled(0)
    await tcont.update()
    await tcont.close()


def main():
    asyncio.run(run_controller())
