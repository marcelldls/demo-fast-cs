import asyncio
from dataclasses import dataclass
from typing import NamedTuple, Type

from .fast_cs import Controller, SubController
from .fast_cs.connections import IPConnection, IPConnectionSettings
from .fast_cs.wrappers import put, scan

FieldInfo = NamedTuple("FieldInfo", (("name", str), ("prefix", str), ("type", Type)))


@dataclass
class TempControllerSettings:
    num_ramp_controllers: int


class TempController(Controller):
    mode: int

    _fields = (FieldInfo("mode", "M", int),)

    def __init__(self, settings: TempControllerSettings):
        super().__init__()

        self._conn: IPConnection = IPConnection()

        self._ramp_controllers: list[TempRampController] = []
        for index in range(1, settings.num_ramp_controllers + 1):
            controller = TempRampController(index, self._conn)
            self._ramp_controllers.append(controller)
            self.register_sub_controller(controller)

    async def connect(self, settings: IPConnectionSettings):
        await self._conn.connect(settings)

    async def close(self):
        await self._conn.close()


class TempRampController(SubController):
    start: float
    end: float
    current: float
    enabled: int

    _fields = (
        FieldInfo("start", "S", float),
        FieldInfo("end", "E", float),
        FieldInfo("current", "T", float),
        FieldInfo("enabled", "N", int),
    )

    def __init__(self, index: int, conn: IPConnection) -> None:
        suffix: str = f"{index:02d}"
        super().__init__(f"ramp{suffix}")
        self._conn: IPConnection = conn
        self._suffix: str = suffix

    @scan(0.1)
    async def update(self):
        for field in self._fields:
            response = await self._conn.send_query(f"{field.prefix}{self._suffix}?\r\n")
            setattr(self, field.name, field.type(response))

        print(f"Start: {self.start}")
        print(f"End: {self.end}")
        print(f"Current: {self.current}")
        print(f"Enabled: {self.enabled}")

    @put
    async def put_enabled(self, value: int):
        await self._conn.send_command(f"N{self._suffix}={value}\r\n")

    @put
    async def put_start(self, value: float):
        await self._conn.send_command(f"S{self._suffix}={value}\r\n")

    @put
    async def put_end(self, value: float):
        await self._conn.send_command(f"E{self._suffix}={value}\r\n")

    @put
    async def put_current(self, value: float):
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
