import asyncio
from dataclasses import dataclass
from typing import NamedTuple, Type

from .fast_cs import Controller, SubController
from .fast_cs.connections import IPConnection, IPConnectionSettings
from .fast_cs.wrappers import put

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
            self.register(controller)

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

    # @scan(0.1)
    async def update(self):
        for field in self._fields:
            response = await self._conn.send_query(f"{field.prefix}{self._suffix}?\r\n")
            setattr(self, field.name, field.type(response))

        print(f"Start: {self.start}")
        print(f"End: {self.end}")
        print(f"Current: {self.current}")
        print(f"Enabled: {self.enabled}")

    @put
    async def set_enabled(self, value: int):
        await self._conn.send_command(f"N{self._suffix}={value}\r\n")

    # @get("enabled")
    async def get_enabled(self) -> int:
        return int(await self._conn.send_query(f"N{self._suffix}?"))

    # # @get("start")
    # def get_start(self):
    #     pass

    # # @put("start")
    # def put_start(self, value: float):
    #     self._device_interface.set_start(self._index, value)
    #     self.update()

    # # @put("end")
    # def put_end(self, value: float):
    #     self._device_interface.set_start(self._index, value)
    #     self.update()


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
